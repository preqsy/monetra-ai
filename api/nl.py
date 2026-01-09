from fastapi import APIRouter, Depends, HTTPException, Query, Request

from api.models import NLRequest, PriceFormat
from services.nl import NLService, get_nl_service
from config import settings

router = APIRouter(prefix="/nl", tags=["Natural Language"])


@router.post("/resolve")
async def resolve_nl_query(
    req: Request,
    data_obj: NLRequest,
    nl_service: NLService = Depends(get_nl_service),
):
    backend_header = req.headers.get("monetra-ai-key")
    if backend_header != settings.BACKEND_HEADER:
        raise HTTPException(status_code=401, detail="Can't access this site")
    # print(f"Request App: {await req.body()}")
    return await nl_service.resolve_user_query(data_obj)


@router.post("/format")
async def format_price_with_category(
    req: Request,
    data_obj: PriceFormat,
    nl_service: NLService = Depends(get_nl_service),
):
    # print(f"Request: {req}")
    return await nl_service.format_price_with_category_stream(data_obj)
