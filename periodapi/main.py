from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from compute_periodogram import PeriodogramComputer


class LightcurveModel(BaseModel):
    mjd: List[float]
    brightness: List[float]
    e_brightness: List[float]
    fid: List[str]


app = FastAPI()
periodogram_computer = PeriodogramComputer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/compute_periodogram/")
async def compute_periodogram(lightcurve: LightcurveModel):
    periodogram = periodogram_computer.compute(lightcurve)
    return periodogram
