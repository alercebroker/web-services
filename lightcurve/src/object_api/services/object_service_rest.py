from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Callable
from contextlib import AbstractContextManager
from core.repository.queries.object import query_psql_object_list
from .object_parser import serialize_items, _convert_filters_to_sqlalchemy_statement
from fastapi.encoders import jsonable_encoder


def get_object_list(
        session_factory: Callable[..., AbstractContextManager[Session]],
        filter_args: dict, 
        pagination_args: dict, 
        order_args: dict, 
        conesearch_args: dict, 
        default_classifier: str, 
        default_version: str, 
        default_ranking: int
    ):
    try:

        default = use_default(filter_args)
        filters = _convert_filters_to_sqlalchemy_statement(filter_args)
        conesearch_args = _convert_conesearch_args(conesearch_args)
        conesearch = _create_conesearch_statement(conesearch_args)

        result = query_psql_object_list(
            session_factory=session_factory,
            oids=filter_args["oid"],
            page=pagination_args["page"],
            page_size=pagination_args["page_size"],
            count=pagination_args["count"],
            order_by=order_args["order_by"],
            order_mode=order_args["order_mode"],
            filters=filters,
            conesearch_args=conesearch_args,
            conesearch=conesearch,
            use_default=default,
            default_classifier=default_classifier,
            default_version=default_version,
            default_ranking=default_ranking,
        )

        
        response = {
                "total": result.total,
                "next": result.next_num(),
                "has_next": result.has_next(),
                "prev": result.prev_num(),
                "has_prev": result.has_prev(),
                "items": serialize_items(result.items),
            }
        
        response = jsonable_encoder(response, sqlalchemy_safe=True)
        
        return response
    except Exception as e:
        print({str(e)})
        raise Exception(f"Error fetching object list")
    

def _convert_conesearch_args(args):
    try:
        ra, dec, radius = args["ra"], args["dec"], args.get("radius")
        if radius is None:
            radius = 30.0
    except KeyError:
        ra, dec, radius = None, None, None

    if ra and dec and radius:
        radius /= 3600.0  # From arcsec to deg
    return {"ra": ra, "dec": dec, "radius": radius}


def _create_conesearch_statement(args):
    try:
        ra, dec, radius = args["ra"], args["dec"], args["radius"]
    except KeyError:
        ra, dec, radius = None, None, None

    if ra and dec and radius:
        return text("q3c_radial_query(meanra, meandec,:ra, :dec, :radius)")
    else:
        return True
    

def use_default(filter_args):
    return (
        False
        if (filter_args.get("classifier") is not None)
        or (filter_args.get("classifier_version") is not None)
        or (filter_args.get("ranking") is not None)
        or (filter_args.get("probability") is not None)
        or (filter_args.get("class") is not None)
        else True
    )
