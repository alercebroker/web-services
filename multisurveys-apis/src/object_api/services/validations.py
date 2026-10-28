import math

from fastapi import HTTPException

from core.idmapper.idmapper import encode_ids


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


def pagination_validation(page: int | None, page_size: int | None):
    if page is not None and page < 1:
        raise HTTPException(status_code=400, detail="page must be 1 or greater.")
    if page_size is not None and page_size < 1:
        raise HTTPException(status_code=400, detail="page_size must be 1 or greater.")


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
        if len(oids) > 200:
            raise HTTPException(
                status_code=422,
                detail={"objectIds": "You can only query for 200 object ids."},
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


def date_validation(firstmjd_min, firstmjd_max):
    if firstmjd_min is not None:
        if not isinstance(firstmjd_min, float):
            raise HTTPException(
                status_code=422,
                detail={"discovery_date_filters_container": "The date must be a float."},
            )

    if firstmjd_max is not None and firstmjd_min is not None:
        if firstmjd_min >= firstmjd_max:
            raise HTTPException(
                status_code=422,
                detail={"discovery_date_filters_container": "Min MJD must be lower than max MJD."},
            )
