def find_first_measurement_id(detections):
    for det in detections:
        if det.has_stamp:
            return det.measurement_id

    return detections[0].measurement_id
