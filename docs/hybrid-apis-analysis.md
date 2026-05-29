# API Bottleneck Analysis

## API + nginx-sidecar configuration update

**Status:** ✅ **RESOLVED** — All fixes deployed to production, chart updated to v25.6.183

### TODO

- [ ] Update `run_service()` in `scripts/run_api.py` to accept uvicorn settings from config (`workers`, `reload`, `proxy_headers`, `forwarded_allow_ips`, `timeout_keep_alive`) so the function is production-safe

```python
def run_service(config_dict: dict = {}):
    db_config = config_dict.get("db_config", {})
    uvicorn_config = config_dict.get("uvicorn", {})

    os.environ["API_URL"] = config_dict["url"]
    os.environ["PSQL_USER"] = db_config["psql_user"]
    # ... etc

    uvicorn.run(
        f"src.{config_dict['source_folder']}.api:app",
        port=config_dict["port"],
        workers=uvicorn_config.get("workers", 4),
        reload=uvicorn_config.get("reload", False),   # safe default
        proxy_headers=uvicorn_config.get("proxy_headers", True),
        forwarded_allow_ips=uvicorn_config.get("forwarded_allow_ips", "*"),
        timeout_keep_alive=uvicorn_config.get("timeout_keep_alive", 30),
    )
```
- [ ] Add a `uvicorn:` block to `configYaml` in values files with the correct settings (e.g. `workers: 4`, `reload: false`, `proxy_headers: true`)
- [ ] Remove the `command:` override and redundant `envVariables:` from values files — let `poetry run <service>` + the mounted `config.yaml` handle everything
- [ ] Rebuild and push the image, then redeploy

---
### Problem: API overwhelmed under load, health check failures, `Connection refused` errors

* Common to see this in nginx-sidecar in between successful requests:

```log
2026/03/02 15:33:36 [error] 23#23: *1340 connect() failed (111: Connection refused) while connecting to upstream, client: 10.10.6.153, server: , request: "GET / HTTP/1.1", upstream: "http://[::1]:8000/", host: "10.10.133.204"`
2026/03/02 15:33:36 [warn] 23#23: *1340 upstream server temporarily disabled while connecting to upstream, client: 10.10.6.153, server: , request: "GET / HTTP/1.1", upstream: "http://[::1]:8000/", host: "10.10.133.204"
```

```log
2026/03/02 15:34:58 [error] 22#22: *1367 connect() failed (111: Connection refused) while connecting to upstream, client: 10.10.22.100, server: , request: "GET /lightcurve_api/detections?oid=170028485864063195&survey_id=lsst HTTP/1.1", upstream: "http://[::1]:8000/detections?oid=170028485864063195&survey_id=lsst", host: "api-lsst.alerce.online"`
2026/03/02 15:34:58 [warn] 22#22: *1367 upstream server temporarily disabled while connecting to upstream, client: 10.10.22.100, server: , request: "GET /lightcurve_api/detections?oid=170028485864063195&survey_id=lsst HTTP/1.1", upstream: "http://[::1]:8000/detections?oid=170028485864063195&survey_id=lsst", host: "api-lsst.alerce.online"`
```

* The API looks overwhelmed and further requests fail, even health checks.

---

### Root cause: 1 effective worker per pod

The API is launched via `poetry run all` → `scripts/run_api.py`, which calls
`uvicorn.Server` with `reload=True` (the default, never overridden in the
ConfigMap). Uvicorn **silently drops to 1 worker when reload is enabled**.
With 8 pods, the entire cluster handles at most **8 concurrent requests**.
Average request time is 1–5 s (DB-bound), so the queue saturates quickly.

---

### Solution

| # | Change | Problem solved |
|---|--------|----------------|
| 1 | Removed `--reload` flag from uvicorn command | Single-worker file watcher was restarting the process on every code change detection, causing `Connection refused` |
| 2 | Added `--workers 4` to uvicorn | Single worker was serializing all requests — any slow DB query blocked everyone |
| 3 | Added `--proxy-headers --forwarded-allow-ips "*"` to uvicorn | Client IPs were showing as `0` in logs instead of real IPs |
| 4 | nginx `upstream` block with `keepalive 16` + `proxy_http_version 1.1` + `Connection ""` | nginx was opening a new TCP connection to uvicorn on every request |
| 5 | `server 127.0.0.1:8000` instead of `localhost` | nginx was trying `[::1]:8000` (IPv6) first, failing, then falling back to IPv4 — causing spurious errors on every Prometheus scrape |
| 6 | `keepalive_timeout 25s` (less than uvicorn's 30s) | nginx was reusing stale keepalive connections that uvicorn had already closed, causing occasional `Connection refused` |
| 7 | `location = /` served directly by nginx | Health checks were hitting uvicorn unnecessarily; nginx now responds instantly without touching the app |
| 8 | `set_real_ip_from 10.0.0.0/8` + `real_ip_header X-Forwarded-For` | Real client IPs were not visible in logs |
| 9 | `client_max_body_size 10M` | `POST /htmx/config_change` with ~1.4MB body was returning 413 |
| 10 | `client_body_buffer_size 256k` + `proxy_buffering on` with buffer sizes | Large POST bodies were being spilled to disk (`buffered to a temporary file`) |
| 11 | Readiness probe on port 8000 | Pod was receiving traffic before uvicorn finished starting, causing 502s for ~20s after every deploy |
| 12 | Liveness probe on port 8000 | Hung uvicorn workers would never be restarted automatically |
| 13 | `memory requests: 128M → 300M`, `limits: 700M` | Pods were being scheduled with unrealistically low memory requests; some were approaching OOMKill |
| 14 | `cpu requests: 40m` (kept) | Nodes are CPU-request-saturated — raising this caused pods to go Pending |
| 15 | `minReplicas: 1 → 4`, `maxReplicas: 1 → 8` | A single pod with a single worker was handling all production traffic |


## Explorer search bar checks for classifiers and their classes on every load

### Problem

multisurveys-apis/src/object_api/routes/htmx.py -> objects_form
is the endpoint that returns the search bar of the explorer. It does a query 
to the database to get the list of classifiers and their classes.

### Solution
This function should look for the classifier list and their classes in a cache, as they are not expected to 
change often. This will improve the loading time of the explorer and its Largest Contentful Paint (LCP) metric. 
A piece of code should refresh the cache periodically, for example every 5 minutes.

## Queries to replica db get killed when they take too long due to updates on the primary db

### Problem
The situation is that when there is a query against the replica db that takes a while and an update arrives from the other db, the query dies because its data becomes invalid.
I set the following:

### Solution

```SQL
-- ▶ On the REPLICA (postgresql.conf via ALTER SYSTEM)
ALTER SYSTEM SET hot_standby_feedback = 'on';
ALTER SYSTEM SET max_standby_streaming_delay = '90s';
SELECT pg_reload_conf();

-- ▶ On the PRIMARY (applies to replica too via role config)
ALTER ROLE read_user SET statement_timeout = '60s';
```

## APIs should query the replica db, not the primary db

### Problem and solution
The multisurvey APIs configs were updated to point to the replica db instead of the primary. This will reduce the load on the primary and improve the performance of the APIs.

Some postgres configurations were missing in the replica db, so they were added to the replica db as well. These configurations are:

```SQL
-- Memory (match master — same RAM presumably)
ALTER SYSTEM SET shared_buffers = '8GB';
ALTER SYSTEM SET effective_cache_size = '280GB';
ALTER SYSTEM SET work_mem = '256MB';
ALTER SYSTEM SET maintenance_work_mem = '4GB';
ALTER SYSTEM SET huge_pages = 'try';

-- BGWriter (match master)
ALTER SYSTEM SET bgwriter_lru_maxpages = '1000';
ALTER SYSTEM SET bgwriter_lru_multiplier = '10.0';
ALTER SYSTEM SET bgwriter_delay = '50';

-- WAL
ALTER SYSTEM SET max_wal_size = '16GB';

-- Autovacuum: replica doesn't run autovacuum on live data
-- (it replays WAL from master) but keep workers available
-- for any local catalog maintenance
ALTER SYSTEM SET autovacuum_max_workers = '3';   -- fewer than master, it's not needed

-- Query timeouts for API safety
ALTER SYSTEM SET idle_in_transaction_session_timeout = '60000';  -- 60s in ms

-- Planner: replica is SSD/read-heavy, random I/O is cheaper
-- Only set this if your replica storage is SSD:
ALTER SYSTEM SET random_page_cost = '1.1';       -- SSD default is 1.1, HDD is 4.0
ALTER SYSTEM SET effective_io_concurrency = '200'; -- SSD: 200, HDD: 2

-- Logging: visibility into slow queries hitting the replica
ALTER SYSTEM SET log_min_duration_statement = '5000';   -- log queries > 5s
ALTER SYSTEM SET log_recovery_conflict_waits = 'on';    -- log conflict events
ALTER SYSTEM SET log_autovacuum_min_duration = '0';     -- log all autovacuum

SELECT pg_reload_conf();
```

## CloudWatch dashboard for multisurvey APIs

A CloudWatch dashboard was created to monitor the multisurvey APIs. The dashboard includes the following widgets:
- TargetResponseTime: shows the response time of the APIs, percentiles 20, 50, and 90.
- RequestCountPerTarget: shows the number of requests per target (API).
- HTTP code 4XX: shows the number of 4XX errors per target.
- HTTP code 5XX: shows the number of 5XX errors per target.

##

* When interacting with the lightcurve widget, the request (not the response) weights more than 1 MB!!!
