import asyncio
import copy
import os
import sys
from typing import Any

import uvicorn
from uvicorn.config import LOGGING_CONFIG, LoopSetupType


def run(services=["ALL"], port=8000):
    port = int(os.getenv("PORT", default=port))
    all_services = filter(lambda dir: dir.endswith("_api"), os.listdir("src"))
    if services == ["ALL"]:
        services = all_services
    else:
        services = filter(lambda service: service in services, all_services)

    asyncio.run(run_services(services, port))


def run_lightcurve():
    port = int(os.getenv("PORT", default=8000))
    asyncio.run(run_service("lightcurve_api", port))


def run_magstats():
    port = int(os.getenv("PORT", default=8000))
    asyncio.run(run_service("magstats_api", port))


def run_object():
    port = int(os.getenv("PORT", default=8000))
    asyncio.run(run_service("object_api", port))


def run_crossmatch():
    port = int(os.getenv("PORT", default=8000))
    asyncio.run(run_service("crossmatch_api", port))

    
def run_probability():
    port = int(os.getenv("PORT", default=8000))
    asyncio.run(run_service("probability_api", port))


def run_tns():
    port = int(os.getenv("PORT", default=8000))
    asyncio.run(run_service("tns_api", port))


async def run_services(services, port):
    tasks = []
    for i, service in enumerate(services):
        tasks.append(asyncio.create_task(run_service(service, port + i)))

    first = asyncio.as_completed(tasks).__next__()
    await first
    for task in tasks:
        task.cancel("Shutting down")


async def run_service(service: str, port: int):
    server_config = uvicorn.Config(
        f"{service}.api:app",
        port=int(port),
        reload=True,
        reload_dirs=[".", "../libs"],
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
