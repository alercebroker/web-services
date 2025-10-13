from fastapi import APIRouter, Request
from fastapi import APIRouter, HTTPException, Request, Response
from ...s3_handler import handler_selector
from fastapi.templating import Jinja2Templates
from astropy.time import Time

router = APIRouter()

###
# We need a get method that return all the stamps and get the 
# detections list from the db
# and a post method that comes with the detections list
# both return the same template
###

def form_stamps_response(
    oid: str,
    measurement_id: str | None = None,
    survey_id: str,
    detections_list: list[dict] | None = None,

):
    pass




@router.get("/stamp_card")
async def stamp_card(
    request: Request,
    oid: str,
    measurement_id: str,
    survey_id: str,
    detections_list: list[dict] = None,
):
    handler = handler_selector(survey_id)()

    stamps = handler.get_all_stamps(oid, measurement_id, "png")
    """
    {
        "cutoutScience": {"file": str_binario "mime": png
        "cutoutTemplate": {"file": str_binario "mime": png
        "cutoutDifference": {"file": str_binario "mime": png
    }
    """

    # falta obtener lista de detecciones.
    if detections_list is None:
        # pedir a db    
        detections_list = []

    return Response(
        
    )


######
######

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