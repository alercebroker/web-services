from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from pydantic import BaseModel

from compute_periodogram import PeriodogramComputer
from harmonics import compute_chi_squared


class LightcurveModel(BaseModel):
    mjd: List[float | int]
    brightness: List[float | int]
    e_brightness: List[float | int]
    fid: List[str]


class LightcurveWithPeriod(LightcurveModel):
    period: float | int


app = FastAPI()
periodogram_computer = PeriodogramComputer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/compute_periodogram/")
async def compute_periodogram(lightcurve: LightcurveModel):
    periodogram = periodogram_computer.compute(lightcurve)
    return periodogram


@app.post("/chi_squared/")
async def chi_squared(lightcurve_with_period: LightcurveWithPeriod):
    return {'reduced_chi_squared': compute_chi_squared(lightcurve_with_period)}

