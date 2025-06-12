import pprint
from fastapi.encoders import jsonable_encoder
from ..models.non_detections import NonDetections
from ..models.force_photometry import ZtfForcedPhotometry
from ..models.detections import ztfDetection

def parse_sql_detection(sql_response, survey_id):

    data_parsed = []
    for row in sql_response:
        model_dict = row[0].__dict__.copy()
        model_parsed = ztfDetection(**model_dict, survey_id=survey_id)
        data_parsed.append(model_parsed)

    
    return data_parsed


def parse_sql_non_detections(sql_response, survey_id):

    response_arr = []
    for row in sql_response:
        model_dict = row[0].__dict__.copy()
        model_parsed = NonDetections(**model_dict, survey_id=survey_id)
        response_arr.append(model_parsed)

    return response_arr



def parse_forced_photometry(sql_response, survey_id):

    response_arr = []
    for row in sql_response:
        model_dict = row[0].__dict__.copy()
        model_parsed = ZtfForcedPhotometry(**model_dict, survey_id=survey_id)
        response_arr.append(model_parsed)
    
    return response_arr
