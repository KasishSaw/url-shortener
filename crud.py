import secrets

from sqlalchemy.orm import Session

import models
from auth import hash_password


# ---------- URL CRUD ----------

def generate_short_code(length: int = 6) -> str:
    return secrets.token_urlsafe(length)[:length]


def get_url_by_short_code(db: Session, short_code: str) -> models.URL | None:
    return db.query(models.URL).filter(models.URL.short_code == short_code).first()


def get_url_by_original(db: Session, original_url: str, owner_id: int) -> models.URL | None:
    return (
        db.query(models.URL)
        .filter(models.URL.original_url == original_url, models.URL.owner_id == owner_id)
        .first()
    )


def create_short_url(db: Session, original_url: str, owner_id: int) -> models.URL:
    existing = get_url_by_original(db, original_url, owner_id)
    if existing:
        return existing

    short_code = generate_short_code()
    while get_url_by_short_code(db, short_code):
        short_code = generate_short_code()

    url_entry = models.URL(
        original_url=original_url,
        short_code=short_code,
        owner_id=owner_id,
    )
    db.add(url_entry)
    db.commit()
    db.refresh(url_entry)
    return url_entry


def increment_click(db: Session, url_entry: models.URL) -> None:
    url_entry.click_count += 1
    db.commit()


def get_urls_by_owner(db: Session, owner_id: int) -> list[models.URL]:
    return db.query(models.URL).filter(models.URL.owner_id == owner_id).all()


def delete_url(db: Session, url_entry: models.URL) -> None:
    db.delete(url_entry)
    db.commit()


# ---------- User CRUD ----------

def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, email: str, password: str) -> models.User:
    user = models.User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
