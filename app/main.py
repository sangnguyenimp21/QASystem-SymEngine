from fastapi import FastAPI

from app.core.api import router as core_router
from app.core.logs import logger

app = FastAPI()
app.include_router(core_router)
logger.info("Server started")