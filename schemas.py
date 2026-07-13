from datetime import datetime
from pydantic import BaseModel, HttpUrl, EmailStr


# ---------- URL schemas ----------

class URLCreate(BaseModel):
    original_url: HttpUrl


class URLResponse(BaseModel):
    short_url: str
    short_code: str
    original_url: str


class URLInfo(BaseModel):
    original_url: str
    short_code: str
    short_url: str
    click_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- User / Auth schemas ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
