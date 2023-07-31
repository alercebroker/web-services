from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI, Depends
from pydantic import ValidationError

from .container import ApiContainer
from .routes import router as AstroObjectRouter

def create_app():
    container = ApiContainer()
    container.config.from_yaml("config.yml")
    app = FastAPI()
    app.container = container

    app.include_router(AstroObjectRouter)

    @app.get("/")
    def health_check():
        return "OK!"

    return app