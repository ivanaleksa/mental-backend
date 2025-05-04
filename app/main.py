import os

from fastapi import FastAPI
from app.core.config import settings

from app.api.v1.auth_routes import router as api_router
from app.api.v1.user_routes import router as user_router


# Ensure the directories for storing user photos exist
def ensure_directories():
    target_dir = os.path.join(settings.MEDIA_DIRECTORY)
    os.makedirs(target_dir, exist_ok=True)

ensure_directories()

app = FastAPI(title="Mental Platform")
app.include_router(api_router, prefix="/app/v1")
app.include_router(user_router, prefix="/app/v1")
