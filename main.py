import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import models
import crud
import schemas
from database import engine, get_db

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener",
    description="A simple URL shortener built with FastAPI and PostgreSQL",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "URL Shortener API is running. Visit /docs for Swagger UI."}


@app.post("/shorten", response_model=schemas.URLResponse, status_code=201)
def shorten_url(payload: schemas.URLCreate, db: Session = Depends(get_db)):
    """
    Accept a long URL and return a shortened version.
    If the URL was already shortened, returns the existing short code.
    """
    original_url = str(payload.original_url)
    url_entry = crud.create_short_url(db, original_url)

    return schemas.URLResponse(
        short_url=f"{BASE_URL}/{url_entry.short_code}",
        short_code=url_entry.short_code,
        original_url=url_entry.original_url,
    )


@app.get("/info/{short_code}", response_model=schemas.URLInfo)
def get_url_info(short_code: str, db: Session = Depends(get_db)):
    """
    Get stats for a short URL: original URL, click count, and creation date.
    """
    url_entry = crud.get_url_by_short_code(db, short_code)
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short code not found")

    return schemas.URLInfo(
        original_url=url_entry.original_url,
        short_code=url_entry.short_code,
        short_url=f"{BASE_URL}/{url_entry.short_code}",
        click_count=url_entry.click_count,
        created_at=url_entry.created_at,
    )


@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    """
    Redirect to the original URL and increment the click counter.
    """
    url_entry = crud.get_url_by_short_code(db, short_code)
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    crud.increment_click(db, url_entry)
    return RedirectResponse(url=url_entry.original_url, status_code=307)
