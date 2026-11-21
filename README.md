# RealTone – Movie Review Platform

ReelTone Reviews is a Next.js frontend and Flask backend. Use the [workspace Compose stack](../util/README.md) to start both with ReelTone Auth.

---

## Movie API

```text
https://developer.themoviedb.org/reference/intro/getting-started
```

---

## 🧱 Project Structure

```text
reeltone-reviews/
├── client/     # Frontend - Next.js
└── server/     # Backend - Flask
```
---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/realtone.git
cd realtone
```

---

## 🔁 Git Basics – Push & Pull

### Pull latest changes:

```bash
git pull origin main
```

### Add your changes:

```bash
git add .
git commit -m "your message here"
git push origin main
```

> 🔒 Make sure you're working on a branch or feature PR if you're collaborating in a team.

---

## 🎬 Frontend Setup (Next.js)

```bash
cd client
npm ci
cp .env.example .env.local
npm run dev -- --port 3101
```

> Access Reviews at `http://localhost:3101`.

---

## 🎯 Backend Setup (Flask)

```bash
cd server
pip install -r requirements.txt
cp .env.example .env
python app.py
```

> Backend should run on `http://localhost:5000` unless otherwise specified.

Reviews uses the `reeltone_reviews` PostgreSQL database. The workspace Compose stack provisions it and runs the schema migration. If you run Flask on the host, use the `PG*` settings in `server/.env` and apply the schema with `python migrate.py` before starting Flask.

## ReelTone Auth

Start the Auth service at `http://localhost:3000`. Register a confidential client in its `OIDC_CLIENTS` configuration with these values.

| Client setting | Local value |
| --- | --- |
| `client_id` | `reviews-local` |
| `client_name` | `ReelTone Reviews` |
| `client_uri` | `http://localhost:3101` |
| `redirect_uris` | `["http://localhost:3101/api/reeltone/auth/callback"]` |
| `token_endpoint_auth_method` | `client_secret_basic` |
| `client_secret` | Generate with `openssl rand -hex 32` |

Set `AUTH_CLIENT_SECRET` in `server/.env` to the registered client secret. Generate a separate `REVIEWS_SESSION_SECRET` using the same command. Set `TMDB_API_KEY` for movie data. Local sign-in and community pages also work without it.

For production, use the deployed Reviews origin for `REVIEWS_ORIGIN` and `NEXT_PUBLIC_SITE_URL`, set `AUTH_ISSUER=https://auth.reeltone.site`, and register the exact Reviews callback on a separate production OIDC client. Set `REVIEWS_BACKEND_URL` in the Next.js runtime environment to the internal Flask URL. Reviews data and sessions survive app restarts in the PostgreSQL volume.

---

## 🛠️ Notes

* Ensure Python 3.10+ and Node.js 18+ are installed.
* Use a virtual environment for Python dependencies (e.g., `venv`, `conda`).
* Consider using `.env` files for configuration in both `client/` and `server/`.

---

## 📬 Questions or Issues?

* Open an issue or start a discussion in the GitHub repo!

---
