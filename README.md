# 🌌 STREAMFLIX

**Unlimited stories. One place to watch.**

A full-stack, Netflix-inspired streaming platform with a cosmic/astro dark theme. Built with a Flask REST API backend and a Streamlit frontend. Users can register, log in securely, browse and search a movie catalog, and manage a personal watchlist — all backed by a real database with hashed passwords.

---

## 1. Project Overview

StreamFlix is a student recruitment project demonstrating frontend development, backend development, database management, authentication, CRUD operations, and deployment. It is a fully functional application — not a static mockup. Every button does something real: accounts are created and verified against the database, and the watchlist is stored per-user and persists across logins.

---

## 2. Features

- 🔐 **Secure registration & login** — passwords hashed with Werkzeug, never stored in plaintext
- 🎬 **Movie catalog** loaded entirely from the backend API (not hardcoded in the UI)
- 🔎 **Search** by title or genre
- ⭐ **Personal watchlist** — add, view, and remove titles (full CRUD), persisted per user in the database
- 🚫 Duplicate-proof: can't register the same email twice, can't add the same movie to your watchlist twice
- 🛡️ Friendly error handling everywhere (bad login, weak password, backend down, empty results, etc.)
- 🌌 Custom cosmic/nebula "astro" theme with red streaming-platform accents

---

## 3. Technology Stack

**Frontend:** Python, Streamlit, Requests, custom CSS
**Backend:** Python, Flask, Flask-CORS, Flask-SQLAlchemy, Werkzeug
**Database:** SQLite (local) / PostgreSQL (recommended for production persistence)
**Deployment:** Streamlit Community Cloud (frontend) + Render (backend)

---

## 4. Folder Structure

```text
StreamFlix/
│
├── backend/
│   ├── app.py               # Flask app: models, routes, everything
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app.py                # Streamlit UI
│   ├── requirements.txt
│   └── .streamlit/
│       └── secrets.toml.example
│
├── .gitignore
├── README.md
└── requirements.txt          # convenience: installs both, for local dev
```

---

## 5. Installation & Local Development Setup

### Prerequisites
- Python 3.10+
- pip

### Windows PowerShell

```powershell
# Clone the repo
git clone https://github.com/<your-username>/StreamFlix.git
cd StreamFlix

# Backend virtual environment
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS / Linux

```bash
git clone https://github.com/<your-username>/StreamFlix.git
cd StreamFlix/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 6. How to Run the Backend

**Windows PowerShell:**
```powershell
cd backend
venv\Scripts\Activate.ps1
python app.py
```

**macOS / Linux:**
```bash
cd backend
source venv/bin/activate
python app.py
```

The API starts on **http://localhost:5000**. On first run it automatically creates `streamflix.db` (SQLite) and seeds the 6 sample titles. Verify it's alive:

```
GET http://localhost:5000/api/health
```

---

## 7. How to Run the Frontend

Open a **second** terminal (leave the backend running in the first one).

**Windows PowerShell:**
```powershell
cd frontend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

**macOS / Linux:**
```bash
cd frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit opens automatically at **http://localhost:8501**. It talks to the backend at `http://localhost:5000` by default (no configuration needed locally).

---

## 8. API Endpoint Documentation

Base URL (local): `http://localhost:5000`

| Method | Endpoint                              | Auth-ish*     | Description                          |
|--------|----------------------------------------|:-------------:|----------------------------------------|
| GET    | `/api/health`                          | No            | Returns `{status: "ok"}`               |
| POST   | `/api/register`                        | No            | Body: `name, email, password` → creates account |
| POST   | `/api/login`                           | No            | Body: `email, password` → returns user profile |
| GET    | `/api/movies`                          | No            | Full catalog. Optional `?q=` filters by title/genre |
| GET    | `/api/watchlist/<user_id>`             | No*           | Returns that user's watchlist |
| POST   | `/api/watchlist`                       | No*           | Body: `user_id, movie_id` → adds to watchlist |
| DELETE | `/api/watchlist/<user_id>/<movie_id>`  | No*           | Removes a title from the watchlist |

`*` — see the **Security Notes** section below; this project identifies the user by `user_id` for simplicity (matching the brief), which is fine for a student demo but not for real production use.

### Example: register
```json
POST /api/register
{ "name": "Ava Kapoor", "email": "ava@example.com", "password": "supersecret1" }

→ 201
{ "message": "Account created successfully.", "user": { "id": 1, "name": "Ava Kapoor", "email": "ava@example.com" } }
```

### Example: add to watchlist
```json
POST /api/watchlist
{ "user_id": 1, "movie_id": 3 }

→ 201
{ "message": "Added to watchlist." }
```

All error responses look like: `{ "error": "human readable message" }` with an appropriate HTTP status code (400, 401, 404, 409, 500).

---

## 9. Database Information

Three tables, created automatically on backend startup:

- **users** — `id, name, email (unique), password (hash), created_at`
- **movies** — `id, title, genre, year, description` (seeded once, 6 sample titles)
- **watchlist** — `id, user_id (FK), movie_id (FK), added_at`, with a unique constraint on `(user_id, movie_id)` so a title can't be added twice

Locally this is a SQLite file at `backend/streamflix.db` (excluded from git via `.gitignore`).

---

## 10. Environment Variables

**Backend** (`backend/.env`, copy from `.env.example`):
```
DATABASE_URL=postgresql://user:password@host:5432/dbname   # optional; omit for SQLite
PORT=5000
```

**Frontend** (`frontend/.streamlit/secrets.toml`, copy from `secrets.toml.example`):
```toml
BACKEND_URL = "https://your-backend-service.onrender.com"
```

Never commit real `.env` or `secrets.toml` files — both are already in `.gitignore`.

---

## 11. Deployment Instructions

### Backend → Render
1. Push this repo to GitHub (public).
2. On [render.com](https://render.com): New → Web Service → connect the repo, **Root Directory: `backend`**.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add a **Render PostgreSQL** database (free tier) and copy its Internal Connection String into the `DATABASE_URL` environment variable on the web service — this is what makes your data survive redeploys, since local SQLite files on Render's free tier are wiped on redeploy.
6. Deploy. Note the public URL, e.g. `https://streamflix-api.onrender.com`.

### Frontend → Streamlit Community Cloud
1. On [share.streamlit.io](https://share.streamlit.io): New app → connect the repo, **Main file path: `frontend/app.py`**.
2. In the app's Settings → Secrets, paste:
   ```toml
   BACKEND_URL = "https://streamflix-api.onrender.com"
   ```
3. Deploy. You'll get a public URL like `https://streamflix.streamlit.app`.

Do not hardcode `localhost` anywhere for production — the frontend already reads `BACKEND_URL` from secrets/env for exactly this reason.

---

## 12. Screenshots

_Add screenshots here after deploying:_

| Landing / Auth | Dashboard | Watchlist |
|---|---|---|
| _screenshot placeholder_ | _screenshot placeholder_ | _screenshot placeholder_ |

---

## 13. Security Notes

- Passwords are hashed with Werkzeug's `generate_password_hash` / `check_password_hash` (PBKDF2) — plaintext passwords are never stored or returned.
- All database access goes through SQLAlchemy's ORM (parameterized queries — no raw SQL string building, no SQL injection surface).
- Duplicate emails and duplicate watchlist entries are rejected at the database level (unique constraints), not just in the UI.
- **Known simplification, called out honestly:** endpoints like `GET /api/watchlist/<user_id>` currently trust the `user_id` the frontend sends, with no session token verifying that the caller actually *is* that user. That's acceptable for a local/demo project but is **not** how you'd ship this for real users. For production, the next step would be adding token-based sessions (e.g. Flask-JWT-Extended or Flask-Login with secure cookies) so every watchlist request is verified against a signed session token instead of a raw ID, plus serving everything over HTTPS.

---

## 14. Testing Checklist

- [ ] Register a new account
- [ ] Attempt registration with an already-registered email → rejected
- [ ] Attempt registration with a password under 8 characters → rejected
- [ ] Log in with correct credentials → dashboard loads
- [ ] Log in with incorrect credentials → friendly error, no crash
- [ ] Browse the movie catalog → all 6 seed titles visible
- [ ] Search by title (e.g. "Dark") → correct result
- [ ] Search by genre (e.g. "Documentary") → correct result
- [ ] Search with no matches → friendly "no results" message
- [ ] Add a movie to the watchlist → appears in "My Watchlist"
- [ ] Attempt to add the same movie twice → rejected with a clear message
- [ ] Remove a movie from the watchlist → disappears immediately
- [ ] Log out, log back in → watchlist is still there (proves persistence)
- [ ] Register a second account and confirm its watchlist is separate from the first user's
- [ ] `GET /api/health` returns `{"status": "ok"}`
- [ ] Stop the backend and confirm the frontend shows a friendly "can't reach backend" message instead of crashing

---

## 15. Future Improvements

- Real session/token-based authentication (JWT or server-side sessions) instead of trusting a raw `user_id`
- Movie poster images and richer metadata (cast, rating, trailer link)
- Pagination or infinite scroll for larger catalogs
- "Continue watching" / viewing history
- Admin panel for managing the movie catalog
- Rate limiting on login/register to slow down brute-force attempts

---

## GitHub Setup

```bash
git init
git add .
git commit -m "Initial commit: StreamFlix full-stack app"
git branch -M main
git remote add origin https://github.com/<your-username>/StreamFlix.git
git push -u origin main
```

Repository name: **StreamFlix** — make sure it's set to **Public** before submitting.
