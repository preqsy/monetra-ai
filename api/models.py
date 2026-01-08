from pydantic import BaseModel, Field


class NLRequest(BaseModel):
    user_id: int
    query: str = Field(min_length=3, max_length=500)
