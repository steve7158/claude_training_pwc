"""Document storage behind a small interface. LocalDiskStorage is the
default (LLD calls for AWS S3; this is the local-dev/docker-compose
stand-in referenced in the plan) - swapping in a real S3-backed
implementation later means adding a class here, not touching callers.
"""
import os
import uuid
from abc import ABC, abstractmethod

from app.core.config import settings


class Storage(ABC):
    @abstractmethod
    def save(self, data: bytes, subdir: str, filename: str) -> str:
        ...

    @abstractmethod
    def read(self, path: str) -> bytes:
        ...

    @abstractmethod
    def delete(self, path: str) -> None:
        ...


class LocalDiskStorage(Storage):
    def __init__(self, root: str | None = None):
        self.root = root or settings.storage_root
        os.makedirs(self.root, exist_ok=True)

    def save(self, data: bytes, subdir: str, filename: str) -> str:
        dir_path = os.path.join(self.root, subdir)
        os.makedirs(dir_path, exist_ok=True)
        safe_name = f"{uuid.uuid4().hex}_{filename}"
        full_path = os.path.join(dir_path, safe_name)
        with open(full_path, "wb") as f:
            f.write(data)
        return full_path

    def read(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def delete(self, path: str) -> None:
        if os.path.exists(path):
            os.remove(path)


storage: Storage = LocalDiskStorage()
