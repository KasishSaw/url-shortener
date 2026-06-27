from pydantic import BaseModel, HttpUrl
from datetime import datetime


class URLCreate(BaseModel):
    original_url: HttpUrl


class URLInfo(BaseModel):
    original_url: str
    short_code: str
    short_url: str
    click_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class URLResponse(BaseModel):
    short_url: str
    short_code: str
    original_url: str
