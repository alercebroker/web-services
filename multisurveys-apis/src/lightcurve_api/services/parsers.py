from ..models.non_detections import NonDetections, LsstNonDetection
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
    if survey_id == "lsst":
        non_detections = ModelsParser(
            LsstNonDetection, sql_response, survey_id
        )
    else:
        non_detections = ModelsParser(NonDetections, sql_response, "")

    return non_detections.parse_data_arr()


def parse_forced_photometry(sql_response, survey_id):
    if survey_id == "ztf":
        forced_photometry_data = ModelsParser(
            ZtfForcedPhotometry, sql_response, survey_id
        )
    if survey_id == "lsst":
        forced_photometry_data = ModelsParser(
            LsstForcedPhotometry, sql_response, survey_id
        )

    return forced_photometry_data.parse_data_arr()


class ModelsParser:
    def __init__(self, output_model, sql_response, survey_id):
        self.output_model = output_model
        self.sql_response = sql_response
        self.survey_id = survey_id

    def parse_data_arr(self):
        data_parsed = []
        for row in self.sql_response:
            model_dict = self.transform_models_to_dict(row)
            model_parsed = self.output_model(
                **model_dict, survey_id=self.survey_id
            )
            data_parsed.append(model_parsed)

        return data_parsed

    def transform_models_to_dict(self, models):
        model_dict = {}
        for model in models:
            model_dict.update(model.__dict__.copy())

        return model_dict
