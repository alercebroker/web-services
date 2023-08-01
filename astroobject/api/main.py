from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .container import ApiContainer
from .routes import router as AstroObjectRouter

def create_app():
    container = ApiContainer()
    container.config.from_yaml("config.yml")
    app = FastAPI()
    app.container = container

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(AstroObjectRouter)

    @app.get("/")
    def health_check():
        return "OK!"

    return app