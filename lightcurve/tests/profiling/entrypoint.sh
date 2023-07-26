poetry run memray run -o /app/tests/profiling/memray_graph.bin --follow-fork -m uvicorn --host 0.0.0.0 --port $PORT api.api:app
