from ..models.non_detections import NonDetections
from ..models.force_photometry import ZtfForcedPhotometry, LsstForcedPhotometry
from ..models.detections import ztfDetection, LsstDetection


def parse_sql_detection(sql_response, survey_id):

    data_parsed = []

    if survey_id == "ztf":
        ztf_data = ModelsParser(ztfDetection, sql_response, survey_id)
        data_parsed = ztf_data.parse_data_arr()
    if survey_id == "lsst":
        lsst_data = ModelsParser(LsstDetection, sql_response, survey_id)
        data_parsed = lsst_data.parse_data_arr()
    
    return data_parsed


def parse_sql_non_detections(sql_response, survey_id):

    non_detections = ModelsParser(NonDetections, sql_response, survey_id)

    return non_detections.parse_data_arr()


def parse_forced_photometry(sql_response, survey_id):


    if survey_id == "ztf":
        forced_photometry_data = ModelsParser(ZtfForcedPhotometry, sql_response, survey_id)
    if survey_id == "lsst":
        forced_photometry_data = ModelsParser(LsstForcedPhotometry, sql_response, survey_id)

    return forced_photometry_data.parse_data_arr()


class ModelsParser():
    
    def __init__(self, output_model, sql_response, survey_id):
        self.output_model = output_model
        self.sql_response = sql_response
        self.survey_id = survey_id

    
    def parse_data_arr(self):
        data_parsed = []
        for row in self.sql_response:
            model_dict = row[0].__dict__
            model_parsed = self.output_model(**model_dict, survey_id=self.survey_id)
            data_parsed.append(model_parsed)
        
        return data_parsed
