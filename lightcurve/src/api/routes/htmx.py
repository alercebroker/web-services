from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, PackageLoader, select_autoescape

from core.models import Detection

router = APIRouter()
env = Environment(
    loader=PackageLoader("api"),
    autoescape=select_autoescape(),
)


@router.get("/")
def test() -> HTMLResponse:
    template = env.get_template("test.html.j2")
    return HTMLResponse(template.render(text="Hello, World!"))


@router.get("/plot/difference")
def diff_plot() -> HTMLResponse:
    detections = [
        Detection(
            **{
                "candid": 123,
                "oid": "oid1",
                "sid": None,
                "aid": None,
                "tid": "0",
                "mjd": 59000.0,
                "fid": 1,
                "ra": 10.0,
                "e_ra": None,
                "dec": 20,
                "e_dec": None,
                "mag": 15,
                "e_mag": 0.5,
                "mag_corr": None,
                "e_mag_corr": None,
                "e_mag_corr_ext": None,
                "parent_candid": None,
                "corrected": False,
                "dubious": False,
                "has_stamp": False,
                "isdiffpos": True,
                "extra_fields": {
                    "pid": 1,
                    "step_id_corr": "test",
                },
            }
        ).__dict__
    ]

    return HTMLResponse(
        env.get_template("plot.html.j2").render(data=detections)
    )
