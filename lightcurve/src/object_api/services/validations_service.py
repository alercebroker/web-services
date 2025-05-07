import re
from fastapi import HTTPException


# def ndets_length_validation(ndets: list[int]):
#     if len(ndets) < 2:
#         raise HTTPException(status_code=422, detail={"detections_container":"Select Min and Max value"})


def ndets_validation(ndets: list[int]):
    if ndets != None and len(ndets) == 2:
        if ndets[0] != None or ndets[1] != None:
            if ndets[0] > ndets[1]:
                raise HTTPException(status_code=422, detail={"detections_container": "Min value can't be greater than max"})


def classifier_validation(classifier: str, class_name: str):
    if classifier == None and class_name == None:
        raise HTTPException(status_code=422, detail={"class_classifier":"Select a class if you want to filter by classifier"})


def oids_format_validation(oids: list[str]):
    pattern = re.compile(r'(ZTF)\d{2,}\w+|[Ss]upernova')

    for oid in oids:
        if pattern.search(oid) == None:
            raise HTTPException(status_code=422, detail={"objectIds": "Oid format is: /(ZTF)d{2,}w+/"})
        else:
            pass


def oids_length_validation(oids: list[str]):
    if len(oids) <= 200:
        return True
    else:
        raise HTTPException(status_code=422, detail={"objectIds": 'You can only query for 200 object ids'})

def probability_validation(probability: float):
    if probability < 0 or probability > 1:
        raise HTTPException(status_code=422, detail={"prob_range": 'Probability has to be between 0 and 1'}) 
