import boto3
from fastavro import reader
import os
import io
from abc import abstractmethod
from .fits_to_png import transform
import gzip


def s3_client(bucket_region: str):
    s3_client = boto3.client(
        "s3",
        region_name=bucket_region,
    )
    return s3_client


class BaseS3Handler:
    def __init__(
        self,
        bucket_name: str,
        bucket_region: str,
        valid_stamps_type: list[str],
        compressed,
    ):
        print(f"config {bucket_name} --- {bucket_region}")
        self.valid_stamp_types = valid_stamps_type
        self.bucket_name = bucket_name
        self.compressed = compressed
        self.client = s3_client(bucket_region)

    def _get_file_from_s3(self, file_name: str) -> dict:
        print("\n\n\nget_stamp avro_name:", file_name, "\n\n\n")
        file = self.client.get_object(
            Bucket=self.bucket_name, Key=f"{file_name}.avro"
        )
        file_io = io.BytesIO(file["Body"].read())
        avro_data = next(reader(file_io))
        return avro_data

    @abstractmethod
    def _get_buffer_from_file(file_result):
        pass

    def _get_stamp(
        self,
        avro_name: str,
        avro_data: dict,
        stamp_type: str,
        file_format: str,
        is_compressed: bool,
    ):
        file_name = f"{avro_name}_{stamp_type}.{file_format}"

        fit_data = self._get_buffer_from_file(avro_data, stamp_type)

        if file_format == "fits":
            if is_compressed:
                compressed_fits = gzip.compress(fit_data)
                file = io.BytesIO(compressed_fits)
                mime = "application/gzip"
            else:
                file = io.BytesIO(fit_data)
                mime = "application/fits"
        elif file_format == "png":
            file = io.BytesIO(
                transform(fit_data, stamp_type, 2, self.compressed)
            )
            mime = "image/png"
        else:
            raise Exception(
                f"Format {file_format} is not valid. Only png and fits accepted."
            )
        return file_name, file, mime

    @abstractmethod
    def _get_avro_name(self, oid: str, measurement_id: str) -> str:
        pass

    @abstractmethod
    def get_avro(self, oid: str, measurement_id: str):
        pass

    def get_stamp(
        self, oid: str, measurement_id: str, stamp_type: str, file_format: str, is_compressed: bool = True
    ):
        avro_name = self._get_avro_name(oid, measurement_id)
        avro_data = self._get_file_from_s3(avro_name)

        file_name, file, mime = self._get_stamp(
            avro_name, avro_data, stamp_type, file_format, is_compressed
        )

        return file_name, file, mime

    def get_all_stamps(self, oid: str, measurement_id: str, file_format: str, is_compressed: bool = True):
        avro_name = self._get_avro_name(oid, measurement_id)
        avro_data = self._get_file_from_s3(avro_name)

        result = {}
        for stamp_type in self.valid_stamp_types:
            file_name, file, mime = self._get_stamp(
                avro_name, avro_data, stamp_type, file_format, is_compressed
            )
            result[stamp_type] = {
                "file_name": file_name,
                "file": file.getvalue(),
                "mime": mime,
            }

        return result
