from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from core.concurrency import add_concurrency_limit
from .router import router

# root_path: the prefix nginx strips, so /docs fetches /status_api/openapi.json
app = FastAPI(
    root_path="/status_api",
    title="ALeRCE status API",
    description="Is each ALeRCE pipeline up to date, and how many alerts it received and processed recently.",
)
add_concurrency_limit(app)
instrumentator = Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
