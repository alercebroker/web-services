import math
import re
from fastapi import HTTPException


def ndets_validation(ndets: list[int]):
    if ndets != None and len(ndets) == 2:
        if ndets[0] > ndets[1]:
            raise HTTPException(
                status_code=422,
                detail={
                    "detections_container": "Min value can't be greater than max."
                },
            )


def order_mode_validation(order: str):
    available_orders = ['DESC', 'ASC']
    
    if order not in available_orders:
        raise HTTPException(
            status_code=422,
            detail={
                "search_filters": "Order can be only DESC or ASC."
            },
        )
    

def class_validation(classifier: str, class_name: str):
    if class_name == None or classifier == None:
        raise HTTPException(
            status_code=422, 
            detail={
                "classes_container":"Select a class if you want to filter by classifier."
            }
        )
    
def classifier_validation(classifier: str):
    if classifier == None:
        raise HTTPException(
            status_code=422, 
            detail={
                "classifiers_container":"Select a classifier if you want to filter objects."
            }
        )
    

def consearch_validation(ra, dec, radius):
    nan_validation(ra, "ra")
    nan_validation(dec, "dec")
    nan_validation(radius, "radius")
    radius_validation(radius)


def nan_validation(single_coord, name):
    if single_coord != None:
        if math.isnan(single_coord):
            raise HTTPException(
                status_code=422,
                detail={
                    "conesearch_filters_container": f"{name} must have a value."
                }
            )
        

def radius_validation(radius):
    if radius != None:
        if radius < 0:
            raise HTTPException(
                status_code=422, 
                detail={
                    "conesearch_filters_container":"Radius can't be negative."
                }
            )
             
        

def oids_format_validation(oids):
    if oids != None:
        pattern = re.compile(r'(ZTF)\d{2,}\w+|[Ss]upernova')

        for oid in oids:
            if not pattern.search(oid):
                raise HTTPException(
                    status_code=422,
                    detail={
                        "objectIds": "Oid format is: /(ZTF)d{2,}w+/"
                    }
                )
            

def oid_lenght_validation(oids):
    if oids != None:
        if len(oids) > 200:
            raise HTTPException(
                status_code=422,
                detail={
                    "objectIds": "You can only query for 200 object ids."
                }
            )


def probability_validation(probability, classifier, class_name):
    if probability != None:
        if probability < 0:
            raise HTTPException(
                status_code=422,
                detail={
                    "prob_range": "Probability must be greater than 0."
                }
            )
        
        if probability > 0:
            if class_name == None:
                raise HTTPException(
                    status_code=422, 
                    detail={
                        "prob_range":"Select a class if you want to filter by classifier."
                    }
                )


def date_validation(firstmjd):
    if firstmjd != None:
        if len(firstmjd) > 2:
            raise HTTPException(
                status_code=422,
                detail={
                    "discovery_date_filters_container": "To filter by date, there must be a maximum of two dates."
                }
            )
        

        if len(firstmjd) == 2:
            if firstmjd[0] >= firstmjd[1]:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "discovery_date_filters_container": "Min MJD must be lower than max MJD."
                    }
                )