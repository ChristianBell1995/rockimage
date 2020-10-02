import uuid
from dataclasses import asdict
from typing import Any

from rockimage.exceptions import NotFound
from rockimage.repository import repository
from rockimage.services.detection import detection
from rockimage.storage import storage


def get_image(uuid: str) -> dict:
    image = repository.get_image(uuid)
    if not image:
        raise NotFound()
    return asdict(image)


def list_images() -> [dict]:
    images = repository.get_images()
    return [asdict(image) for image in images]


def save_image(stream: Any) -> dict:
    key = str(uuid.uuid4())
    path = storage.write(key, stream)
    result = repository.save_image(key, path)
    result = detect(key, path)
    return asdict(result)


def detect(key: str, path: str):
    annotations = detection.get_labels(path)
    return repository.update_image(key, annotations=annotations)
