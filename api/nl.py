from fastapi import APIRouter, Depends, HTTPException, Query, Request

from api.models import NLRequest, NLFormatRequest
from services.nl import NLService, get_nl_service
from config import settings

router = APIRouter(prefix="/nl", tags=["Natural Language"])


@router.post("/resolve")
async def resolve_nl_query(
    data_obj: NLRequest,
    nl_service: NLService = Depends(get_nl_service),
):

    return await nl_service.resolve_user_query(data_obj)


@router.post("/format")
async def format_price_with_category(
    data_obj: NLFormatRequest,
    nl_service: NLService = Depends(get_nl_service),
):

    return await nl_service.format_price_with_category_stream(data_obj)


@router.post("/interpret")
async def interpret_nl_query(
    data_obj: NLRequest,
    nl_service: NLService = Depends(get_nl_service),
):

    return await nl_service.interpret_user_query(data_obj.query)
