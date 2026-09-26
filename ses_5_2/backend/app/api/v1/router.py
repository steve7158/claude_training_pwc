from fastapi import APIRouter

from app.api.v1.endpoints import auth, documents, metrics, taxonomy

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(taxonomy.router)
api_router.include_router(metrics.router)
