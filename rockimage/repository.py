from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

import sqlalchemy as sa
from google.cloud import firestore

from rockimage import config, db, models


@dataclass
class ImageRecord:
    path: str
    uuid: str
    annotations: List[str] = field(default_factory=lambda: [])


class Repository(ABC):
    @abstractmethod
    def get_image(self, uuid: str) -> Optional[ImageRecord]:
        pass

    @abstractmethod
    def get_images() -> List[ImageRecord]:
        pass

    @abstractmethod
    def save_image(self, uuid: str, path: str) -> ImageRecord:
        pass

    @abstractmethod
    def update_image(self, uuid: str, **kwargs) -> ImageRecord:
        pass


class SQLRepository(Repository):
    def get_image(self, uuid: str) -> Optional[ImageRecord]:
        result = (
            db.session.query(models.Image).filter(models.Image.uuid == uuid).first()
        )
        if not result:
            return None
        return ImageRecord(path=result.path, uuid=result.uuid)

    def get_images(self) -> Optional[ImageRecord]:
        results = db.session.query(models.Image).all()
        return [ImageRecord(path=result.path, uuid=result.uuid) for result in results]

    def save_image(self, uuid: str, path: str) -> ImageRecord:
        image = models.Image(uuid=uuid, path=path)
        db.session.add(image)
        db.session.commit()
        return ImageRecord(uuid=uuid, path=path)

    def update_image(
        self, uuid: str, annotations: Optional[List[str]] = None
    ) -> Optional[ImageRecord]:
        result = (
            db.session.query(models.Image).filter(models.Image.uuid == uuid).first()
        )
        if not result:
            return None
        if annotations:
            result.annotations = annotations

        db.session.add(result)
        db.session.commit()
        return ImageRecord(path=result.path, uuid=result.uuid, annotations=result.annotations)


class FirestoreRepository(Repository):
    def __init__(self):
        self.client = firestore.Client()

    def get_image(self, uuid: str) -> Optional[ImageRecord]:
        result = self.client.collection(u"images").document(uuid).get()
        if not result.exists:
            return None
        return ImageRecord(path=result.get("path"), uuid=result.get("uuid"))

    def get_images(self) -> Optional[ImageRecord]:
        results = self.client.collection(u"images").stream()
        return [ImageRecord(path=result.path, uuid=result.uuid) for result in results]

    def save_image(self, uuid: str, path: str) -> ImageRecord:
        self.client.collection(u"images").document(uuid).set(
            {
                "uuid": uuid,
                "path": path,
            }
        )
        return ImageRecord(uuid=uuid, path=path)


impls = {"sql": SQLRepository, "firestore": FirestoreRepository}

repository = impls[config.DATASTORE]()
