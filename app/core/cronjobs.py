import os
from fastapi import APIRouter
from fastapi_utils.tasks import repeat_every
import requests
from dotenv import load_dotenv

load_dotenv()

cronjobs_router = APIRouter(tags=["Cronjobs Endpoints"])

@cronjobs_router.on_event("startup")
@repeat_every(seconds=int(os.getenv('CRONJOB_INTERVAL')))
def cronjob_wakeup():
    try:
        base_url = os.getenv("BASE_URL")
        requests.get(f"{base_url}/healthcheck")
    except Exception as e:
        print("error in running cronjob")