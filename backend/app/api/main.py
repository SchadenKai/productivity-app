from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils, tasks, projects, google_oauth, habits
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(google_oauth.router, prefix="/login", tags=["login"])
api_router.include_router(habits.router, prefix="/habits", tags=["habits"])

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
