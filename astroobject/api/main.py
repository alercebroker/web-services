from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI, Depends
from pydantic import ValidationError

from .container import ApiContainer
from .routes import router as AstroObjectRouter

def create_app():
    container = ApiContainer()
    app = FastAPI()
    app.container = container

    app.include_router(AstroObjectRouter)
    return app