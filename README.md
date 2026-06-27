# URL Shortener

A lightweight URL shortener REST API built with **FastAPI** and **PostgreSQL**.

## Tech Stack

- **FastAPI** — API framework
- **PostgreSQL** — Database
- **SQLAlchemy** — ORM
- **Pydantic v2** — Input validation
- **python-dotenv** — Environment config
- **Uvicorn** — ASGI server

## Project Structure

```
url-shortener/
├── main.py        # App entry point & route handlers
├── database.py    # DB engine & session
├── models.py      # SQLAlchemy table definition
├── schemas.py     # Pydantic request/response models
├── crud.py        # DB operations & short code generation
├── .env           # Environment variables
└── requirements.txt
```

## Setup

1. **Clone & install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env .env.local
   # Edit .env with your PostgreSQL credentials
   ```

   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/urlshortener
   BASE_URL=http://localhost:8000
   ```

3. **Create the PostgreSQL database**
   ```sql
   CREATE DATABASE urlshortener;
   ```

4. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

5. **Visit Swagger UI**
   ```
   http://localhost:8000/docs
   ```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/shorten` | Submit a long URL, get a short link |
| `GET` | `/{short_code}` | Redirect to original URL |
| `GET` | `/info/{short_code}` | View click stats & metadata |

## Example Usage

**Shorten a URL**
```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://www.example.com/very/long/url"}'
```

**Response**
```json
{
  "short_url": "http://localhost:8000/aB3xZ9",
  "short_code": "aB3xZ9",
  "original_url": "https://www.example.com/very/long/url"
}
```

**Get URL Info**
```bash
curl http://localhost:8000/info/aB3xZ9
```

**Response**
```json
{
  "original_url": "https://www.example.com/very/long/url",
  "short_code": "aB3xZ9",
  "short_url": "http://localhost:8000/aB3xZ9",
  "click_count": 5,
  "created_at": "2026-06-27T10:30:00Z"
}
```

## Key Features

- ✅ Auto-generated short codes using `secrets.token_urlsafe`
- ✅ Input validation with Pydantic (`HttpUrl` type)
- ✅ Duplicate URL detection — same URL always returns same short code
- ✅ Click tracking on every redirect
- ✅ Environment-based config with python-dotenv
- ✅ Auto Swagger docs at `/docs`
