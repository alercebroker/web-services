"""
Compare the object API's list queries between versions of the code, with Postgres plans and timings.

`sql` writes, for each case, the SQL that this checkout's API sends for that website list (`/htmx/list_objects`),
built with the API's own code. `explain` runs each SQL file under EXPLAIN (ANALYZE, BUFFERS) twice in a row: the
first run is as cold as the database happens to be, the second is warm. A run stopped by the statement timeout
falls back to a plain EXPLAIN, and its second run is skipped.

To compare two versions, run `sql` from a checkout of each (copy this script into the older one if it lacks it),
then `explain` with both directories. The cases list (classifier, class, sort) is in CASES.

Read-only, but a slow query reads from disk for up to the timeout: mind the load on a production replica.
Credentials come from a JSON file (username, password, host, port, dbname), never from this repo.

    .venv/bin/python scripts/bench_list_objects.py sql --credentials creds.json --out bench/after
    .venv/bin/python scripts/bench_list_objects.py explain --credentials creds.json bench/before bench/after
"""

import argparse
import json
import pathlib
import re
import sys
import time
from contextlib import contextmanager

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

import psycopg2  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.dialects import postgresql  # noqa: E402
from sqlalchemy.engine import URL  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from core.repository.queries.objects import query_get_objects  # noqa: E402
from object_api.models.filters import Consearch, Filters, SearchParams  # noqa: E402
from object_api.models.pagination import Order, PaginationArgs  # noqa: E402
from object_api.services.classifier_data_matcher import update_filters  # noqa: E402
from object_api.services.object_services import get_classes_list  # noqa: E402
from object_api.services.parsers import parse_params  # noqa: E402

LC = "lc_classifier_BHRF_forced_phot"

# name: (classifier, class_name, order_by, order_mode). Numbers refer to the slow-requests doc.
CASES = {
    "lpv_ndet_asc": (LC, "LPV", "n_det", "ASC"),  # 1
    "snia_firstmjd_desc": (LC, "SNIa", "firstmjd", "DESC"),  # 7
    "snia_ndet_desc": (LC, "SNIa", "n_det", "DESC"),  # 7, from db2's log
    "noclass_probability_desc": (LC, None, "probability", "DESC"),  # 7, from db2's log
    "tde_lastmjd_desc": (LC, "TDE", "lastmjd", "DESC"),  # not in the doc, chosen to be cold
    "top_stochastic_firstmjd_desc": (LC + "_top", "Stochastic", "firstmjd", "DESC"),  # same
}


class Captured(Exception):
    pass


@contextmanager
def capturing_session():
    class Session:
        def execute(self, stmt):
            raise Captured(stmt)

    yield Session()


def build_sql(case, classes_list):
    classifier, class_name, order_by, order_mode = CASES[case]
    search_params = SearchParams(
        filter_args=Filters(survey="ztf", classifier=classifier, class_name=class_name, ranking=1),
        conesearch_args=Consearch(),
        pagination_args=PaginationArgs(page=1, page_size=20, count=False),
        order_args=Order(order_by=order_by, order_mode=order_mode),
    )
    search_params = update_filters(search_params, classes_list)

    try:
        query_get_objects(capturing_session, search_params, parse_params(search_params))
    except Captured as captured:
        stmt = captured.args[0]

    return str(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def explain(conn, sql, analyze):
    options = "ANALYZE, BUFFERS" if analyze else "COSTS"
    with conn.cursor() as cur:
        cur.execute(f"EXPLAIN ({options}) {sql}")
        return "\n".join(row[0] for row in cur.fetchall())


def run(conn, sql):
    """EXPLAIN ANALYZE, or plain EXPLAIN if the statement timeout stops it."""
    started = time.monotonic()
    try:
        plan = explain(conn, sql, analyze=True)
        return {"plan": plan, "wall_s": time.monotonic() - started, "timed_out": False, **plan_numbers(plan)}
    except psycopg2.errors.QueryCanceled:
        wall = time.monotonic() - started
        return {"plan": explain(conn, sql, analyze=False), "wall_s": wall, "timed_out": True}


def plan_numbers(plan):
    numbers = {}
    if m := re.search(r"Execution Time: ([\d.]+) ms", plan):
        numbers["exec_ms"] = float(m.group(1))
    # The first Buffers line belongs to the top node, so it is the query's total.
    if m := re.search(r"^\s*Buffers: (.*)$", plan, re.M):
        for kind in ("hit", "read"):
            k = re.search(rf"shared .*?{kind}=(\d+)", m.group(1))
            numbers[kind] = int(k.group(1)) if k else 0
    if m := re.search(r"actual time=[\d.]+\.\.[\d.]+ rows=(\d+)", plan):
        numbers["rows"] = int(m.group(1))
    return numbers


def fmt(result):
    if result is None:
        return "—"
    if result["timed_out"]:
        return f"timeout at {result['wall_s']:.1f} s"
    return f"{result['exec_ms'] / 1000:.2f} s, {result['rows']} rows, hit {result['hit']:,} read {result['read']:,}"


def write_sql(args, creds, options):
    url = URL.create(
        "postgresql+psycopg2",
        username=creds["username"],
        password=creds["password"],
        host=creds["host"],
        port=int(creds["port"]),
        database=creds["dbname"],
    )
    engine = create_engine(url, connect_args={"options": options, "application_name": "bench_list_objects"})
    classes_list = get_classes_list(sessionmaker(engine))

    args.out.mkdir(parents=True, exist_ok=True)
    for case in args.cases:
        (args.out / f"{case}.sql").write_text(build_sql(case, classes_list) + "\n")
    print(f"wrote {len(args.cases)} cases to {args.out}")


def explain_dirs(args, creds, options):
    # Autocommit, so a run stopped by the timeout doesn't abort the session for the next statement.
    conn = psycopg2.connect(
        user=creds["username"],
        password=creds["password"],
        host=creds["host"],
        port=creds["port"],
        dbname=creds["dbname"],
        options=options,
        application_name="bench_list_objects",
    )
    conn.autocommit = True

    rows = []
    try:
        for case in args.cases:
            results = []
            for sql_dir in args.sql_dirs:
                sql = (sql_dir / f"{case}.sql").read_text()
                first = run(conn, sql)
                second = None if first["timed_out"] else run(conn, sql)
                for n, result in enumerate([first, second], 1):
                    if result:
                        (sql_dir / f"{case}.run{n}.plan.txt").write_text(result["plan"] + "\n")
                results.append((first, second))
                print(f"{case} {sql_dir.name}: 1st {fmt(first)}; 2nd {fmt(second)}", flush=True)
            rows.append((case, results))
    finally:
        conn.close()

    names = [d.name for d in args.sql_dirs]
    header = " | ".join(f"{name}, 1st | {name}, 2nd" for name in names)
    lines = [
        f"Run order per case: {', '.join(names)}; each one's 1st run then its 2nd (warm) run.",
        "",
        f"| Case | {header} |",
        "|---" * (1 + 2 * len(names)) + "|",
    ]
    for case, results in rows:
        lines.append(f"| {case} | " + " | ".join(fmt(r) for pair in results for r in pair) + " |")
    print("\n" + "\n".join(lines))


def case_list(value):
    cases = value.split(",")
    if unknown := [case for case in cases if case not in CASES]:
        raise argparse.ArgumentTypeError(f"unknown cases {unknown}, choose from {list(CASES)}")
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--credentials", required=True, help="JSON file: username, password, host, port, dbname")
    parser.add_argument("--schema", default="multisurvey")
    parser.add_argument("--timeout", default="55s", help="statement_timeout, as ms_api_object has (default 55s)")
    parser.add_argument("--cases", type=case_list, default=list(CASES), help="comma-separated (default: all)")
    commands = parser.add_subparsers(dest="command", required=True)
    sql = commands.add_parser("sql", help="write this checkout's SQL for each case")
    sql.add_argument("--out", required=True, type=pathlib.Path)
    exp = commands.add_parser("explain", help="EXPLAIN ANALYZE each case from each directory, in the order given")
    exp.add_argument("sql_dirs", nargs="+", type=pathlib.Path)
    args = parser.parse_args()

    creds = json.loads(pathlib.Path(args.credentials).read_text())
    options = f"-csearch_path={args.schema} -cstatement_timeout={args.timeout}"
    if args.command == "sql":
        write_sql(args, creds, options)
    else:
        explain_dirs(args, creds, options)


if __name__ == "__main__":
    main()
