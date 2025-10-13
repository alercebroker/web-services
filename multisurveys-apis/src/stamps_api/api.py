from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

# Mount static files
app.mount("/static", StaticFiles(directory="src/multisurvey_stamps/static"), name="static")
app.mount("/htmx", StaticFiles(directory="src/multisurvey_stamps/static/htmx"), name="htmx")


@app.get("/openapi.json")
def custom_swagger_route():
    return app.openapi()
