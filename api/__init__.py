from fastapi import APIRouter

from .nl import router as nl_router

router = APIRouter()

router.include_router(nl_router)
