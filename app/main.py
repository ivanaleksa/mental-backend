import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.ml_service import ThreadSafeModelHandler
from app.api.v1.auth_routes import router as api_router
from app.api.v1.user_routes import router as user_router
from app.api.v1.admin_routes import router as admin_router
from app.api.v1.note_routes import router as note_router
from app.api.v1.psychologist_routes import router as psychologist_router


# Ensure the directories for storing user photos exist
def ensure_directories():
    target_dir = os.path.join(settings.MEDIA_DIRECTORY)
    os.makedirs(target_dir, exist_ok=True)

    target_dir = os.path.join(settings.DOCUMENTS_DIRECTORY)
    os.makedirs(target_dir, exist_ok=True)


ensure_directories()


app = FastAPI(title="Mental Platform")
model_handler = ThreadSafeModelHandler(settings.MODEL_PATH)
app.dependency_overrides[ThreadSafeModelHandler] = lambda: model_handler
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # TODO: take this out
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/public", StaticFiles(directory="public"), name="public")
app.include_router(api_router, prefix="/app/v1")
app.include_router(user_router, prefix="/app/v1")
app.include_router(psychologist_router, prefix="/app/v1")
app.include_router(admin_router, prefix="/app/v1")
app.include_router(note_router, prefix="/app/v1")
