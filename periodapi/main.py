from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from compute_periodogram import PeriodogramComputer


class LightcurveModel(BaseModel):
    mjd: List[float]
    brightness: List[float]
    e_brightness: List[float]
    fid: List[str]


app = FastAPI()
periodogram_computer = PeriodogramComputer()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/compute_periodogram/")
async def compute_periodogram(lightcurve: LightcurveModel):
    periodogram = periodogram_computer.compute(lightcurve)
    return periodogram
