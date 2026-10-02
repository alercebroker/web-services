import ast
import pathlib

SRC = pathlib.Path(__file__).resolve().parents[3] / "src"
# Handlers that really await, so they may stay async. (file, function)
ALLOWED_ASYNC = {
    ("lightcurve_api/api.py", "static_files"),
    ("lightcurve_api/api.py", "versioned_static_files"),
}
ROUTE_DECORATORS = {"get", "post", "put", "patch", "delete", "api_route"}


def is_route(node: ast.AsyncFunctionDef) -> bool:
    return any(
        isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr in ROUTE_DECORATORS
        for d in node.decorator_list
    )


def test_route_handlers_are_plain_def():
    """
    An `async def` handler that calls blocking code (SQLAlchemy, boto3, requests, matplotlib) freezes the whole pod
    while it runs. Plain `def` handlers run in FastAPI's thread pool instead.
    """
    offenders = []
    for path in SRC.rglob("*.py"):
        rel = str(path.relative_to(SRC))
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.AsyncFunctionDef) and is_route(node) and (rel, node.name) not in ALLOWED_ASYNC:
                offenders.append(f"{rel}:{node.lineno} {node.name}")
    assert offenders == []
