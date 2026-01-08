from fastapi import APIRouter, Depends, Query

from api.models import NLRequest, PriceFormat
from services.nl import NLService, get_nl_service

router = APIRouter(prefix="/nl", tags=["Natural Language"])


@router.post("/resolve")
async def resolve_nl_query(
    data_obj: NLRequest,
    nl_service: NLService = Depends(get_nl_service),
):
    return await nl_service.resolve_user_query(data_obj)


@router.post("/format")
async def format_price_with_category(
    data_obj: PriceFormat,
    nl_service: NLService = Depends(get_nl_service),
):
    return await nl_service.format_price_with_category_stream(data_obj)
