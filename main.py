from fastapi import FastAPI
from api import router

app = FastAPI()


@app.get("/")
def read_root():
    return {"Message": "Hello World"}


app.include_router(router)
