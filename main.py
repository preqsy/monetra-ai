from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Avoid blocking startup on heavyweight model initialization.
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Message": "Hello World"}


app.include_router(router)
