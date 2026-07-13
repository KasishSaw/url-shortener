# URL Shortener API (FastAPI + PostgreSQL + JWT Auth)

A REST API that shortens URLs, tracks clicks, and now supports user accounts —
so links are owned by whoever created them.

## Features
- Register / login with hashed passwords (bcrypt) and JWT access tokens
- Create short URLs (requires login)
- Public redirect + public stats lookup (no login needed to use a link)
- List your own URLs (`/my-urls`, login required)
- Delete a URL you own (login required, owner-only)

## Tech Stack
FastAPI · PostgreSQL · SQLAlchemy · Pydantic · python-jose (JWT) · passlib (bcrypt)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file (see `.env.example`):
   ```
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/urlshortener
   BASE_URL=http://localhost:8000
   SECRET_KEY=replace_with_a_long_random_string
   ```

   Generate a strong `SECRET_KEY` with:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

4. Open `http://localhost:8000/docs` for the interactive Swagger UI.

## ⚠️ Important — migrating from the old (no-auth) version

The `urls` table now has a required `owner_id` column linking every link to a user.
If you already have a `urlshortener` database from before, the old `urls` table
won't have this column, and app startup won't add it automatically (no Alembic
in this small project — tables are only *created*, not altered).

Easiest fix for a portfolio project — drop and let it recreate clean:
```sql
DROP TABLE IF EXISTS urls;
DROP TABLE IF EXISTS users;
```
Then restart the server; both tables will be recreated with the new schema.

## API Endpoints

| Method | Endpoint | Auth required | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Create a new account |
| POST | `/auth/login` | No | Get a JWT access token |
| GET | `/auth/me` | Yes | Get your own user info |
| POST | `/shorten` | Yes | Create a short URL (tied to your account) |
| GET | `/{short_code}` | No | Redirect to the original URL |
| GET | `/info/{short_code}` | No | View stats for a short URL |
| GET | `/my-urls` | Yes | List all URLs you've created |
| DELETE | `/{short_code}` | Yes (owner only) | Delete a URL you created |

## Using auth in Swagger UI

1. `POST /auth/register` with an email + password.
2. Click the **Authorize** button (top right, lock icon).
3. Log in via `POST /auth/login` — Swagger's Authorize form uses `username` for
   the email field (that's just how OAuth2's standard form works).
4. Once authorized, `/shorten`, `/my-urls`, and `DELETE` will work directly
   from Swagger without manually pasting a token.

## Using auth via curl

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

# Login (form-encoded, not JSON — this is OAuth2 password flow)
curl -X POST http://localhost:8000/auth/login \
  -d "username=you@example.com&password=yourpassword"

# Use the returned access_token
curl -X POST http://localhost:8000/shorten \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://www.google.com"}'
```
