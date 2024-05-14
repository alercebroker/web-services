import pandas as pd
from fastapi import APIRouter

from core.compute_periodogram import PeriodogramComputer
from core.harmonics import compute_chi_squared
from core.models import LightcurveModel, LightcurveWithPeriod

periodogram_computer = PeriodogramComputer()


router = APIRouter()


@router.post("/compute_periodogram/")
async def compute_periodogram(lightcurve: LightcurveModel):
    lightcurve_df = pd.DataFrame(lightcurve.model_dump())
    periodogram = periodogram_computer.compute(lightcurve_df)
    return periodogram


@router.post("/chi_squared/")
async def chi_squared(lightcurve_with_period: LightcurveWithPeriod):
    return {"reduced_chi_squared": compute_chi_squared(lightcurve_with_period)}
