from typing import Any, Sequence, Tuple

from sqlalchemy import Row

from ..models.detections import LsstDetection, ZtfDataReleaseDetection, ztfDetection
from ..models.force_photometry import LsstForcedPhotometry, ZtfForcedPhotometry
from ..models.non_detections import ZtfNonDetections
from ..models.object import ZtfDrObject


def parse_sql_detection(args: Tuple[Sequence[Row[Any]], str]):
    sql_response, survey_id = args

    data_parsed = []

    if survey_id.lower() == "ztf":
        ztf_data = ModelsParser(ztfDetection, sql_response, survey_id)
        data_parsed = ztf_data.parse_data_arr()
    elif survey_id.lower() == "lsst":
        lsst_data = ModelsParser(LsstDetection, sql_response, survey_id)
        data_parsed = lsst_data.parse_data_arr()
    else:
        Exception("Survey not supported")

    return data_parsed


def parse_sql_non_detections(args: Tuple[Sequence[Row[Any]], str]):
    sql_response, survey_id = args

    if survey_id.lower() != "ztf":
        return []

    return ModelsParser(ZtfNonDetections, sql_response, survey_id).parse_data_arr()


def parse_forced_photometry(args: Tuple[Sequence[Row[Any]], str]):
    sql_response, survey_id = args

    if survey_id.lower() == "ztf":
        forced_photometry_data = ModelsParser(
            ZtfForcedPhotometry, sql_response, survey_id
        )
    elif survey_id.lower() == "lsst":
        forced_photometry_data = ModelsParser(
            LsstForcedPhotometry, sql_response, survey_id
        )
    else:
        raise ValueError(f"Survey not supported: {survey_id}")

    return forced_photometry_data.parse_data_arr()


class ModelsParser:
    class ParseError(Exception):
        pass

    def __init__(self, output_model, sql_response, survey_id):
        self.output_model = output_model
        self.sql_response = sql_response
        self.survey_id = survey_id

    def parse_data_arr(self):
        data_parsed = []
        for row in self.sql_response:
            model_dict = self.transform_models_to_dict(row)
            try:
                model_parsed = self.output_model(**model_dict, survey_id=self.survey_id)
                data_parsed.append(model_parsed)
            except Exception as e:
                raise self.ParseError(
                    f"Error parsing {self.output_model.__name__} model: {e}"
                )

        return data_parsed

    def transform_models_to_dict(self, models):
        model_dict = {}
        for model in models:
            model_dict.update(model.__dict__.copy())

        return model_dict


def parse_ztf_dr_detection(
    detections: list[dict], object_ids: list[str] = []
) -> list[ZtfDataReleaseDetection]:
    parsed_detections = []
    for det in detections:
        if str(det["_id"]) not in object_ids and len(object_ids) > 0:
            continue
        for epoch in range(det["nepochs"]):
            parsed_detections.append(
                ZtfDataReleaseDetection(
                    band=det["filterid"],
                    fid=det["filterid"],
                    field=det["fieldid"],
                    objectid=det["_id"],
                    mjd=det["hmjd"][epoch],
                    mag_corr=det["mag"][epoch],
                    e_mag_corr_ext=det["magerr"][epoch],
                    ra=det["objra"],
                    dec=det["objdec"],
                )
            )

    return parsed_detections


def parse_ztf_dr_object(objects: list[dict]) -> list[ZtfDrObject]:
    return [
        ZtfDrObject(
            objectId=str(obj["_id"]),
            filterid=obj["filterid"],
            nepochs=obj["nepochs"],
            fieldid=obj["fieldid"],
            rcid=obj["rcid"],
            ra=obj["objra"],
            dec=obj["objdec"],
        )
        for obj in objects
    ]
