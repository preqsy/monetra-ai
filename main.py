from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from config import settings
from api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Avoid blocking startup on heavyweight model initialization.
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def check_backend_header(req: Request, call_next):
    backend_header = req.headers.get("monetra-ai-key")

    if not backend_header or backend_header != settings.BACKEND_HEADER:
        return JSONResponse(
            content={"detail": "You don't have the permission to access this service"},
            status_code=401,
        )

    return await call_next(req)


@app.get("/health")
def health_check():
    return JSONResponse(content="Monetra AI is up and grateful ☑️ 💯 ")


app.include_router(router)
