from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .container import ApiContainer
from .routes import router as AstroObjectRouter

def create_app():
    container = ApiContainer()
    container.config.from_yaml("config.yml")
    app = FastAPI()
    app.container = container

    instrumentator = Instrumentator().instrument(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(AstroObjectRouter)

    @app.on_event("startup")
    async def _startup():
        instrumentator.expose(app)

    @app.get("/")
    def health_check():
        return "OK!"

    return app