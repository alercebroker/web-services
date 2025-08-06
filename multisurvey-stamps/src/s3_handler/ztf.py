import os
from .base_handler import BaseS3Handler
import json

class ZTFS3Handler(BaseS3Handler):
    
    def __init__(self):
        bucket_region = os.getenv("ZTF_BUCKET_REGION")
        bucket_name = os.getenv("ZTF_BUCKET_NAME")
        super().__init__(
            bucket_name,
            bucket_region,
            [
                "cutoutDifference",
                "cutoutScience",
                "cutoutTemplate",
            ],
            compressed=True
        )


    def _get_avro_name(self, oid, measurement_id):
        file_name = measurement_id[::-1]
        print(f"HERE! ZTF\n{measurement_id}")
        print(f"HERE! ZTF\n{file_name}")
        return file_name
    
    def _get_buffer_from_file(self, file_result, stamp_type):
        if stamp_type in self.valid_stamp_types:
            return file_result[stamp_type]["stampData"]
        else:
            # error no valid type
            pass
    
    def get_avro(self, oid: str, measurement_id: str):
        avro_name = self._get_avro_name(oid, measurement_id)
        avro_data = self._get_file_from_s3(avro_name)

        del avro_data["cutoutTemplate"]
        del avro_data["cutoutScience"]
        del avro_data["cutoutDifference"]
        avro_data["candidate"]["candid"] = str(avro_data["candidate"]["candid"])

        return avro_data