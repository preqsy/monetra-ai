from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.nl import get_nl_service
from api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting NLServic...")
    get_nl_service()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Message": "Hello World"}


app.include_router(router)
