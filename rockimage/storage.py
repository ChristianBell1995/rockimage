import os
import tempfile
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any

from google.cloud import storage

from rockimage import config


class Storage(ABC):
    @abstractmethod
    def write(self, path: str, stream: Any) -> str:
        pass

    @abstractmethod
    @contextmanager
    def open(self, path: str):
        pass

class FileNotFound(Exception):
    pass


class GoogleCloudStorage(Storage):
    def __init__(self, bucket: str = config.STORAGE_BUCKET):
        self.client = storage.Client()
        self.bucket_name = bucket
        self.bucket = self.client.get_bucket(bucket)

    def write(self, path: str, stream: Any) -> str:
        blob = self.bucket.blob(path)
        blob.upload_from_file(stream)
        return f"gs://{self.bucket_name}/{path}"

    @contextmanager
    def open(self, path, mode='r'):
        blob = self.bucket.blob(path)
        if not blob.exists():
            raise FileNotFound()
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        blob.download_to_file(tmp_file)
        with open(tmp_file, mode) as f:
            yield f
        os.remove(tmp_file.name)

storage = GoogleCloudStorage()
