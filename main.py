from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Avoid blocking startup on heavyweight model initialization.
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health_check():
    return JSONResponse(content="Monetra AI is up and grateful ☑️ 💯 ")


app.include_router(router)
