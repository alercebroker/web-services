import asyncio
import os
import sys

import uvicorn


def run(services=["ALL"], port=8000):
    port = int(os.getenv("PORT", default=port))
    all_services = filter(lambda dir: dir.endswith("_api"), os.listdir("src"))
    if services == ["ALL"]:
        services = all_services
    else:
        services = filter(lambda service: service in services, all_services)

    asyncio.run(run_services(services, port))


def run_object():
    port = int(os.getenv("PORT", default=8000))
    root_path = os.getenv("ROOT_PATH", default="")
    env = os.getenv("ENV", default="dev").lower()
    reload = "developement".startswith(env)

    asyncio.run(run_service("object_api", port, root_path, reload))


async def run_services(services, port):
    tasks = []
    for i, service in enumerate(services):
        tasks.append(asyncio.create_task(run_service(service, port + i)))

    first = asyncio.as_completed(tasks).__next__()
    await first
    for task in tasks:
        task.cancel("Shutting down")


async def run_service(
    service: str, port: int, root_path: str = "/", reload: bool = True
):
    server_config = uvicorn.Config(
        f"{service}.api:app",
        port=int(port),
        reload=reload,
        reload_dirs=[".", "../libs"],
        root_path=root_path,
    )
    server = uvicorn.Server(server_config)
    os.environ["API_URL"] = f"http://localhost:{port}"
    await server.serve()


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    else:
        port = int(os.getenv("PORT", default=8000))

    if len(sys.argv) >= 3:
        services = sys.argv[2:]
    else:
        services = os.getenv("SERVICE", default="ALL").split(",")

    services = filter(
        lambda dir: dir.endswith("_api") and dir in services, os.listdir("src")
    )

    run(services, port)
