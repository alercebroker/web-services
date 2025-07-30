from fastapi import HTTPException
import math

def ndets_validation(ndets: list[int]):
    if ndets != None and len(ndets) == 2:
        if ndets[0] != None or ndets[1] != None:
            if ndets[0] > ndets[1]:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "detections_container": "Min value can't be greater than max"
                    },
                )


def order_mode_validation(order: str):
    available_orders = ['DESC', 'ASC']
    
    if order not in available_orders:
        raise HTTPException(
            status_code=422,
            detail={
                "order_mode": "Order can be only DESC or ASC"
            },
        )
    

def classifier_validation(classifier: str, class_name: str):
    if class_name == None or class_name == "":
        raise HTTPException(
            status_code=422, 
            detail={
                "classes_container":"Select a class if you want to filter by classifier"
            }
        )
    

def consearch_validation(ra, dec, radius):
    nan_validation(ra, "ra")
    nan_validation(dec, "dec")
    nan_validation(radius, "radius")


def nan_validation(single_coord, name):
    print(single_coord)
    if single_coord != None:
        if math.isnan(single_coord):
            raise HTTPException(
                status_code=422,
                detail={
                    "conesearch_filters_container": f"{name} must have a value"
                }
            )