import os
from fastapi.middleware.cors import CORSMiddleware
from ralidator_fastapi.ralidator_fastapi import RalidatorStarlette
from fastapi import FastAPI
from .filters import get_filters_map
from .routes import router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RalidatorStarlette,
    config={"SECRET_KEY": os.getenv("SECRET_KEY")},
    filters_map=get_filters_map(),
    ignore_paths=["/metrics"],
)

app.include_router(router)
