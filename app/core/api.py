from fastapi import APIRouter

from starlette import status
from starlette.requests import Request

router = APIRouter(tags=["Core Endpoints"])

@router.get("/healthcheck", status_code=status.HTTP_200_OK)
async def healthcheck(request: Request):
    return {
        "status": "ok",
        "code": status.HTTP_200_OK
    }