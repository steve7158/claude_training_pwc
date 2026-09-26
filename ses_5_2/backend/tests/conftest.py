import os
import tempfile

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ["GROQ_API"] = ""  # force the mock extractor - tests must not depend on network access
os.environ.setdefault("STORAGE_ROOT", os.path.join(tempfile.gettempdir(), "carta_test_documents"))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 - registers all tables on Base.metadata
from app.db.base import Base
from app.worker.celery_app import celery_app

celery_app.conf.task_always_eager = True
celery_app.conf.task_eager_propagates = True


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
