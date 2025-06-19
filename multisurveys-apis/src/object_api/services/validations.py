from fastapi import HTTPException


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
