from fastapi import APIRouter
from routes.v1 import companies, ask, news, admin, notifications

api_router = APIRouter()
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(ask.router, prefix="/ask", tags=["Ask AI"])
api_router.include_router(news.router, prefix="/news", tags=["News Pipeline"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin Discovery"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
