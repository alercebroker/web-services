import re
import os
from typing import Annotated
from fastapi import Query

from core.object_service import get_object, get_mag_stats
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from ..result_handler import handle_error, handle_success

router = APIRouter()
templates = Jinja2Templates(
    directory="src/api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8000"
)


def setup_ralidator(request: Request):
    # el objeto ralidator viene en request.state
    request_ralidator = request.state.ralidator
    # permissions logic
    request_ralidator.set_required_permissions(["admin", "basic_user"])
    auth_header = request.headers.get("Authorization", None)
    token = None
    if auth_header:
        if re.search("bearer", auth_header, re.IGNORECASE) is None:
            raise ValueError("Malformed Authorization header")
        try:
            token = auth_header.split()[1]
        except Exception:
            raise ValueError("Malformed Authorization header")
    request_ralidator.authenticate_token(token)
    allowed, code = request_ralidator.check_if_allowed()
    if not allowed:
        if code == 401:
            raise HTTPException(status_code=code, detail="Expired Token")
        raise HTTPException(status_code=code, detail="Unauthorized")
    
@router.get("/object/{oid}", response_class=HTMLResponse)
async def object_info_app(
    request: Request,
    oid: str
):
  
    link='https://acortar.link/ba5kba'
    

    object = get_object(oid,session_factory = request.app.state.psql_session)

    return templates.TemplateResponse(
      name='basicInformationPreview.html.jinja',
      context={'request': request,
               'object': object.oid,
               'corrected': "Yes" if object.corrected else "No",
                'stellar' : "Yes" if object.stellar else "No",
                'detections' : object.ndet,
                'discoveryDateMJD' : object.firstmjd,
                'lastDetectionMJD' : object.lastmjd,
                'nonDetections' : '8', # Esto de donde aparece???
                'ra' : object.meanra ,
                'dec': object.meandec,
                'link':link
               },
  )

@router.get("/mag_stats/{oid}", response_class=HTMLResponse)
async def object_magStat_app(
    request: Request,
    oid: str
):
  
    mag_stats = get_mag_stats(oid,session_factory = request.app.state.psql_session)
    
    #print(mag_stats.__dict__)
    ##stat = ['stellar', 'corrected', 'ndet', 'ndubious','magmean','magmedian','magmax','magmin',
    ##                'magsigma','maglast','magfirst','firstmjd','lastmjd','step_id_corr'
    ##            ];
    ##
    ##r = ['false','true','1','0','17.933','17.933','17.933','17.933','0','17.933','17.933',
    ##            '60432.473','60432.473','24.4.1'
    ##            ];
    
    #stat_r = dict(zip(stat, r))


    return templates.TemplateResponse(
      name='magStatsPreview.html.jinja',
      context={'request': request,
               'stat_r': mag_stats.__dict__
               },
  )

@router.get("/crossmatch/", response_class=HTMLResponse)
async def object_crossmatch_app(
    request: Request,
):
    
    #print(mag_stats.__dict__)
    ##stat = ['stellar', 'corrected', 'ndet', 'ndubious','magmean','magmedian','magmax','magmin',
    ##                'magsigma','maglast','magfirst','firstmjd','lastmjd','step_id_corr'
    ##            ];
    ##
    ##r = ['false','true','1','0','17.933','17.933','17.933','17.933','0','17.933','17.933',
    ##            '60432.473','60432.473','24.4.1'
    ##            ];
    
    #stat_r = dict(zip(stat, r))


    return templates.TemplateResponse(
      name='crossmatchCard.html.jinja',
      context={'request': request,
               },
  )

@router.get("/mag/{oid}", response_class=HTMLResponse)
async def object_mag_app(
    request: Request,
    oid: str
):
  
    mag_stats = get_mag_stats(oid,session_factory = request.app.state.psql_session)
    
    #print(mag_stats.__dict__)
    ##stat = ['stellar', 'corrected', 'ndet', 'ndubious','magmean','magmedian','magmax','magmin',
    ##                'magsigma','maglast','magfirst','firstmjd','lastmjd','step_id_corr'
    ##            ];
    ##
    ##r = ['false','true','1','0','17.933','17.933','17.933','17.933','0','17.933','17.933',
    ##            '60432.473','60432.473','24.4.1'
    ##            ];
    
    #stat_r = dict(zip(stat, r))


    return templates.TemplateResponse(
      name='magstatRebuild.html.jinja',
      context={'request': request,
               'stat_r': mag_stats.__dict__
               },
  )
