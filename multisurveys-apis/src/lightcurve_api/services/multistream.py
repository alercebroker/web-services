from ..models.non_detections import nonDectectionMultistream

def detections_to_multistream(detections_models):

    # for detection in detections_models:
    #     print(detection)

    return detections_models


def non_detections_to_multistream(non_detections_models):
    response_arr = []
    for model in non_detections_models:
        model_multistream = nonDectectionMultistream(
            aid=None,
            tid=model.survey_id,
            mjd=model.mjd,
            fid=None,
            oid=model.oid,
            sid=model.band,
            diffmaglim=model.diffmaglim
        )
        response_arr.append(model_multistream)

    return response_arr
