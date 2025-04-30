from fastapi import FastAPI
from app.api.v1.routes import router as api_router

from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Mental Platform")
app.include_router(api_router, prefix="/app/v1")
