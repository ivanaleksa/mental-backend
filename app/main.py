from fastapi import FastAPI
from app.api.v1.user_auth_routes import router as api_router
from app.api.v1.user_routes import router as user_router


app = FastAPI(title="Mental Platform")
app.include_router(api_router, prefix="/app/v1")
app.include_router(user_router, prefix="/app/v1")
