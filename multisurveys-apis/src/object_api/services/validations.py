import math

from db_plugins.db.sql.models_pipeline import Object, Probability
from fastapi import HTTPException
from sqlalchemy import inspect

from core.idmapper.idmapper import MAX_OIDS_PER_REQUEST, encode_ids


def ndets_validation_front(n_det_min: int, n_det_max: int):
    if n_det_min is not None and n_det_max is not None:
        if n_det_min > n_det_max:
            raise HTTPException(
                status_code=422,
                detail={"detections_container": "Min value can't be greater than max."},
            )


def ndets_validation(ndets: list[int]):
    if ndets is not None and len(ndets) == 2:
        if ndets[0] > ndets[1]:
            raise HTTPException(
                status_code=422,
                detail={"detections_container": "Min value can't be greater than max."},
            )


ORDER_BY_COLUMNS = sorted({attr.key for model in (Object, Probability) for attr in inspect(model).column_attrs})


def order_by_validation(order_by: str | None):
    if order_by is not None and order_by != "oid_list" and order_by not in ORDER_BY_COLUMNS:
        raise ValueError(f"order_by must be oid_list or one of: {', '.join(ORDER_BY_COLUMNS)}.")


def order_mode_validation(order: str):
    available_orders = ["DESC", "ASC"]

    if order not in available_orders:
        raise HTTPException(
            status_code=422,
            detail={"search_filters": "Order can be only DESC or ASC."},
        )


def class_validation(classifier: str, class_name: str):
    if class_name is None or classifier is None:
        raise HTTPException(
            status_code=422,
            detail={"classes_container": "Select a class if you want to filter by classifier."},
        )


def classifier_validation(classifier: str):
    if classifier is None:
        raise HTTPException(
            status_code=422,
            detail={"taxonomy_container": "Select a classifier if you want to filter objects."},
        )


def consearch_validation(ra, dec, radius):
    nan_validation(ra, "ra")
    nan_validation(dec, "dec")
    nan_validation(radius, "radius")
    radius_validation(radius)


def nan_validation(single_coord, name):
    if single_coord is not None:
        if math.isnan(single_coord):
            raise HTTPException(
                status_code=422,
                detail={"conesearch_filters_container": f"{name} must have a value."},
            )


def radius_validation(radius):
    if radius is not None:
        if radius < 0:
            raise HTTPException(
                status_code=422,
                detail={"conesearch_filters_container": "Radius can't be negative."},
            )


def oids_format_validation(oids, survey):
    if oids is not None:
        try:
            encode_ids(survey, oids)
        except ValueError as e:
            raise HTTPException(status_code=422, detail={"objectIds": str(e)})


def oid_lenght_validation(oids):
    if oids is not None:
        if len(oids) > MAX_OIDS_PER_REQUEST:
            raise HTTPException(
                status_code=422,
                detail={"objectIds": f"You can only query for {MAX_OIDS_PER_REQUEST} object ids."},
            )


def probability_validation(probability, classifier, class_name):
    if probability is not None:
        if probability < 0:
            raise HTTPException(
                status_code=422,
                detail={"prob_range": "Probability must be greater than 0."},
            )

        if probability > 0:
            if class_name is None:
                raise HTTPException(
                    status_code=422,
                    detail={"prob_range": "Select a class if you want to filter by classifier."},
                )


def date_validation(mjd_min, mjd_max, container="discovery_date_filters_container"):
    if mjd_min is not None:
        if not isinstance(mjd_min, float):
            raise HTTPException(
                status_code=422,
                detail={container: "The date must be a float."},
            )

    if mjd_max is not None and mjd_min is not None:
        if mjd_min >= mjd_max:
            raise HTTPException(
                status_code=422,
                detail={container: "Min MJD must be lower than max MJD."},
            )


def prob_lastmjd_validation(prob_lastmjd_min, prob_lastmjd_max, classifier):
    if prob_lastmjd_min is None and prob_lastmjd_max is None:
        return

    if classifier is None:
        raise HTTPException(
            status_code=422,
            detail={"classifier_date_filters_container": "Select a classifier to filter by this date."},
        )

    if prob_lastmjd_min is not None and prob_lastmjd_max is not None and prob_lastmjd_min >= prob_lastmjd_max:
        raise HTTPException(
            status_code=422,
            detail={"classifier_date_filters_container": "Min MJD must be lower than max MJD."},
        )
