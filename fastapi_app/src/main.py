from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import astroobject, classifier, feature, lightcurve, magstats, probability

app = FastAPI()

origins = [
    "https://alerce.online",
    "http://localhost:5000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(astroobject.router)
app.include_router(classifier.router)
app.include_router(feature.router)
app.include_router(lightcurve.router)
app.include_router(magstats.router)
app.include_router(probability.router)


@app.get("/")
def hello_world():
    return {"message": "Hello, ZA WARUDO!"}
