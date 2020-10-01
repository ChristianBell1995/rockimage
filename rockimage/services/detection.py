from abc import ABC, abstractmethod

from google.cloud import vision
import google.auth
from rockimage.storage import GoogleCloudStorage, Storage, storage


class DetectionService(ABC):
    @abstractmethod
    def get_labels(self, url: str) -> [str]:
        pass


class GoogleDetectionService(DetectionService):
    def __init__(self, storage: Storage):
        self.storage = storage
        self.client = vision.ImageAnnotatorClient()

    def get_labels(self, path: str) -> [str]:
        if not isinstance(self.storage, GoogleCloudStorage):
            with self.storage.open(url, "rb") as f:
                content = f.read()
                image = vision.Image(content=content)
        else:
            image = vision.Image()
            image.source.image_uri = path

        response = self.client.label_detection(image=image)
        labels = response.label_annotations
        return [label.description for label in labels]


detection = GoogleDetectionService(storage)
