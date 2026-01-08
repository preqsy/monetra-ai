from fastapi import APIRouter, Depends

from api.models import NLRequest
from services.nl import NLService, get_nl_service

router = APIRouter(prefix="/nl", tags=["Natural Language"])


@router.post("/resolve")
async def resolve_nl_query(
    data_obj: NLRequest,
    nl_service: NLService = Depends(get_nl_service),
):
    return await nl_service.resolve_user_query(data_obj)
