from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import rest

app = FastAPI(openapi_url="/stamps/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rest.router)

@app.get("/openapi.json")
def custom_swagger_route():
    return app.openapi()
