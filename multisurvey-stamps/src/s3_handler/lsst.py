import os
from s3_handler.base_handler import BaseS3Handler

class LSSTS3Handler(BaseS3Handler):

    def __init__(self):
        bucket_region = os.getenv("LSST_BUCKET_REGION")
        bucket_name = os.getenv("LSST_BUCKET_NAME")
        super().__init__(
            bucket_name,
            bucket_region,
            [
                "cutoutDifference",
                "cutoutScience",
                "cutoutTemplate",
            ],
            compressed=False
        )


    def _get_avro_name(self, oid, measurement_id):
        return f"{oid}_{measurement_id}"

    def _get_buffer_from_file(self, file_result, stamp_type):
        if stamp_type in self.valid_stamp_types:
            return file_result[stamp_type]
        else:
            # error no valid type
            pass

    def get_avro(self, oid: str, measurement_id: str):
        raise Exception("No avro stored for LSST Alerts")