from fastapi import FastAPI
from config.config import settings

app = FastAPI()


@app.get("/")
async def read_root():
    print(f"Using LLM Model: {settings.LLM_MODEL_NAME}")
    return {"Hello": "World"}
