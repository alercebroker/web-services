import os
from .base_handler import BaseS3Handler


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
            compressed=False,
        )

    def _get_avro_name(self, oid, measurement_id):
        return f"{oid}_{measurement_id}"

    def _get_buffer_from_file(self, file_result, stamp_type):
        return file_result[stamp_type]

    def get_avro(self, oid: str, measurement_id: str):
        raise ValueError("The avro of LSST alerts isn't available")
