from fastapi import FastAPI

from app.core.api import router as core_router
from app.core.cronjobs import cronjobs_router
from app.core.logs import logger

from app.reasoning.api import router as reasoning_router

app = FastAPI()

app.include_router(core_router)
app.include_router(reasoning_router)
app.include_router(cronjobs_router)

logger.info("Server started")