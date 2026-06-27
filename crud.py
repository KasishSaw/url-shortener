import secrets
from sqlalchemy.orm import Session
from models import URL


def generate_short_code(length: int = 6) -> str:
    return secrets.token_urlsafe(length)[:length]


def get_url_by_short_code(db: Session, short_code: str):
    return db.query(URL).filter(URL.short_code == short_code).first()


def get_url_by_original(db: Session, original_url: str):
    return db.query(URL).filter(URL.original_url == original_url).first()


def create_short_url(db: Session, original_url: str) -> URL:
    # Return existing if already shortened
    existing = get_url_by_original(db, original_url)
    if existing:
        return existing

    # Generate a unique short code
    short_code = generate_short_code()
    while get_url_by_short_code(db, short_code):
        short_code = generate_short_code()

    url_entry = URL(original_url=original_url, short_code=short_code)
    db.add(url_entry)
    db.commit()
    db.refresh(url_entry)
    return url_entry


def increment_click(db: Session, url_entry: URL) -> URL:
    url_entry.click_count += 1
    db.commit()
    db.refresh(url_entry)
    return url_entry
