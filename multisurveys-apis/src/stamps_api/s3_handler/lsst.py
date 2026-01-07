import os
from .base_handler import BaseS3Handler


class LSSTS3Handler(BaseS3Handler):
    def __init__(self):
        bucket_region = 'us-east-1' #os.getenv("LSST_BUCKET_REGION")
        bucket_name = 'lsst-stream-staging-bucket' #os.getenv("LSST_BUCKET_NAME")
        super().__init__(
            bucket_name,
            bucket_region,
            [
                "cutoutDifference",
                "cutoutScience",
                "cutoutTemplate",
            ],
            compressed=False,
        )

    def _get_avro_name(self, oid, measurement_id):
        return f"{oid}_{measurement_id}"

    def _get_buffer_from_file(self, file_result, stamp_type):
        if stamp_type in self.valid_stamp_types:
            return file_result[stamp_type]
        else:
            raise Exception(
                f"Type {stamp_type} not valid. Valid types are {self.valid_stamp_types}"
            )

    def get_avro(self, oid: str, measurement_id: str):
        raise Exception("No avro stored for LSST Alerts")
