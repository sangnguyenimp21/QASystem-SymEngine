from fastapi import APIRouter

from starlette import status

from .models import LNNReasoningModel

from .services import lnn_reasoning

router = APIRouter(tags=["Reasoning Endpoints"])

@router.post("/reasoning-lnn", status_code=status.HTTP_200_OK)
async def reasoning_lnn(item: LNNReasoningModel):
    # Call the service
    try:
        result = lnn_reasoning(item)
    except Exception as e:
        return {"error": str(e)}

    return result

@router.post("/reasoning-lnn-explanation", status_code=status.HTTP_200_OK)
async def reasoning_lnn_explanation(item: LNNReasoningModel):
    # Call the service
    try:
        result = lnn_reasoning(item, using_explanation=True)
    except Exception as e:
        return {"error": str(e)}

    return result

    