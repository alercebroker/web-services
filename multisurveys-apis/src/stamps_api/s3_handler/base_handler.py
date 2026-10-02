import boto3
from fastapi import HTTPException
from fastavro import reader
import io
import threading
from abc import abstractmethod
from .fits_to_png import transform
import gzip

_clients = {}
_clients_lock = threading.Lock()


def s3_client(bucket_region: str):
    """
    One S3 client per region, created once and shared by every request.

    A client, once created, is safe to share between threads; creating one is not, because boto3.client() goes
    through boto3's shared default session. So clients are built from their own Session, under a lock.
    """
    with _clients_lock:
        client = _clients.get(bucket_region)
        if client is None:
            client = boto3.session.Session().client("s3", region_name=bucket_region)
            _clients[bucket_region] = client
        return client


class BaseS3Handler:
    def __init__(
        self,
        bucket_name: str,
        bucket_region: str,
        valid_stamps_type: list[str],
        compressed,
    ):
        self.valid_stamp_types = valid_stamps_type
        self.bucket_name = bucket_name
        self.compressed = compressed
        self.client = s3_client(bucket_region)

    def _get_file_from_s3(self, file_name: str) -> dict:
        key = f"{file_name}.avro"
        try:
            file = self.client.get_object(Bucket=self.bucket_name, Key=key)
        except self.client.exceptions.NoSuchKey:
            raise HTTPException(status_code=404, detail=f"Alert file {key} not found")
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
            file = io.BytesIO(transform(fit_data, stamp_type, 2, self.compressed))
            mime = "image/png"
        else:
            raise Exception(f"Format {file_format} is not valid. Only png and fits accepted.")
        return file_name, file, mime

    @abstractmethod
    def _get_avro_name(self, oid: str, measurement_id: str) -> str:
        pass

    @abstractmethod
    def get_avro(self, oid: str, measurement_id: str):
        pass

    def get_stamp(self, oid: str, measurement_id: str, stamp_type: str, file_format: str, is_compressed: bool = True):
        avro_name = self._get_avro_name(oid, measurement_id)
        avro_data = self._get_file_from_s3(avro_name)

        file_name, file, mime = self._get_stamp(avro_name, avro_data, stamp_type, file_format, is_compressed)

        return file_name, file, mime

    def get_all_stamps(self, oid: str, measurement_id: str, file_format: str, is_compressed: bool = True):
        avro_name = self._get_avro_name(oid, measurement_id)
        avro_data = self._get_file_from_s3(avro_name)

        result = {}
        for stamp_type in self.valid_stamp_types:
            file_name, file, mime = self._get_stamp(avro_name, avro_data, stamp_type, file_format, is_compressed)
            result[stamp_type] = {
                "file_name": file_name,
                "file": file.getvalue(),
                "mime": mime,
            }

        return result
