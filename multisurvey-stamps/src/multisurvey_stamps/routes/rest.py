from fastapi import APIRouter, Request, Response
# from ...s3_handler import handler_selector
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from alerce.ms_stamps import AlerceStampsMultisurvey
from alerce.search import AlerceSearch
from alerce.ms_search import AlerceSearchMultiSurvey
from astropy.time import Time

router = APIRouter()
templates = Jinja2Templates(
    directory="src/multisurvey_stamps/templates", autoescape=True, auto_reload=True
)

router = APIRouter()


@router.get("/")
async def ping():
    return "This is the Stamps API"


# @router.get("/stamp")
# async def stamp(
#     request: Request,
#     oid: str,
#     measurement_id: str,
#     stamp_type: str,
#     file_format: str,
#     survey_id: str,
# ):
#     handler = handler_selector(survey_id)()

#     _, file_buffer, mime = handler.get_stamp(
#         oid, measurement_id, stamp_type, file_format
#     )

#     return Response(content=file_buffer.getvalue(), media_type=mime)


# @router.get("/avro")
# async def stamp(
#     request: Request, oid: str, measurement_id: str, survey_id: str
# ):
#     handler = handler_selector(survey_id)()

#     avro_json = handler.get_avro(oid, measurement_id)

#     return avro_json

def _has_stamp(d):
    return d['has_stamp'] 

def _get_measurement_ids(survey_id, detections):

    measurement_ids = []

    if survey_id == 'ztf':
        for d in detections:
            if _has_stamp(d):
                measurement_ids.append(d['candid'])
    elif survey_id == 'lsst':
        for d in detections:
            measurement_ids.append(d['measurement_id'])
    
    return measurement_ids

def _get_dates(survey_id, detections):

    dates = []
    if survey_id == 'ztf':
        for d in detections:
            if _has_stamp(d):
                dates.append(str(Time(d['mjd'], format='mjd').isot))
    elif survey_id == 'lsst':
        for d in detections:
            dates.append(str(Time(d['mjd'], format='mjd').isot))
    

    return dates


#temporal router to develop card
@router.get('/temp/stamp')
def temp_stamp(
    oid: str,
    survey_id: str,
    request: Request,
):
    total_links = []

    alerce_stamps = AlerceStampsMultisurvey()
    alerce_search = AlerceSearch()
    alerce_search_ms = AlerceSearchMultiSurvey()

    if survey_id == "ztf":
        detections = alerce_search.query_detections(oid)
    elif survey_id == "lsst":
        detections = alerce_search_ms.multisurvey_query_detections(oid=oid, survey_id=survey_id)

    measurement_ids = _get_measurement_ids(survey_id, detections)
    dates = _get_dates(survey_id, detections)

    image_types = ['science', 'template', 'difference']

    for i in  range(len(measurement_ids)):
        stamps = alerce_stamps._get_pgn_stamps(oid = oid, measurement_id = measurement_ids[i], survey_id=survey_id)
        stamps_dict = dict(zip(image_types, stamps))
        stamps_with_date = {dates[i]: stamps_dict}

        total_links.append(stamps_with_date)
        
    return templates.TemplateResponse(
      name='stamps_card.html.jinja',
      context={'request': request,
               'stamps': total_links,
               'dates': dates,
               'measurement_ids': measurement_ids
               },
  )