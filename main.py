import os

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import models
import schemas
import crud
import auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

app = FastAPI(title="URL Shortener API", description="A URL shortener with FastAPI, PostgreSQL, and JWT auth.")


@app.get("/")
def root():
    return {"message": "URL Shortener API is running. Visit /docs for Swagger UI."}


# ---------- Auth routes ----------

@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, payload.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, payload.email, payload.password)


@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm sends "username" - we treat that field as email
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return schemas.Token(access_token=access_token)


@app.get("/auth/me", response_model=schemas.UserResponse)
def read_current_user(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# ---------- URL routes ----------

@app.post("/shorten", response_model=schemas.URLResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(
    payload: schemas.URLCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    url_entry = crud.create_short_url(db, str(payload.original_url), current_user.id)
    return schemas.URLResponse(
        short_url=f"{BASE_URL}/{url_entry.short_code}",
        short_code=url_entry.short_code,
        original_url=url_entry.original_url,
    )


@app.get("/my-urls", response_model=list[schemas.URLInfo])
def list_my_urls(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    urls = crud.get_urls_by_owner(db, current_user.id)
    return [
        schemas.URLInfo(
            original_url=u.original_url,
            short_code=u.short_code,
            short_url=f"{BASE_URL}/{u.short_code}",
            click_count=u.click_count,
            created_at=u.created_at,
        )
        for u in urls
    ]


@app.get("/info/{short_code}", response_model=schemas.URLInfo)
def get_url_info(short_code: str, db: Session = Depends(get_db)):
    url_entry = crud.get_url_by_short_code(db, short_code)
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return schemas.URLInfo(
        original_url=url_entry.original_url,
        short_code=url_entry.short_code,
        short_url=f"{BASE_URL}/{url_entry.short_code}",
        click_count=url_entry.click_count,
        created_at=url_entry.created_at,
    )


@app.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_short_url(
    short_code: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    url_entry = crud.get_url_by_short_code(db, short_code)
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    if url_entry.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this URL")
    crud.delete_url(db, url_entry)
    return None


@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    url_entry = crud.get_url_by_short_code(db, short_code)
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    crud.increment_click(db, url_entry)
    return RedirectResponse(url=url_entry.original_url, status_code=307)
