# ReelTone Reviews

This repository contains the ReelTone Reviews Next.js frontend. Its API is served by [ReelTone Server](../reeltone-server/README.md). The workspace [Compose stack](../reeltone-util/README.md) runs the backend and this frontend together.

## Frontend setup

```sh
npm ci
cp .env.example .env.local
npm run dev -- --port 3101
```

For a backend on the same host, use `REVIEWS_BACKEND_URL=http://127.0.0.1:3000/reviews`. Compose sets the equivalent internal URL automatically.

Build the production image from the repository root with `docker build .`.

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

Set `AUTH_CLIENT_SECRET` in `../reeltone-server/reviews/.env` to the registered client secret. Generate a separate `REVIEWS_SESSION_SECRET` using the same command. Set `TMDB_API_KEY` for movie data. Local sign-in and community pages also work without it.

For production, use the deployed Reviews origin for `REVIEWS_ORIGIN` and `NEXT_PUBLIC_SITE_URL`, set `AUTH_ISSUER=https://auth.reeltone.site`, and register the exact Reviews callback on a separate production OIDC client. Set `REVIEWS_BACKEND_URL` in the Next.js runtime environment to the internal NestJS URL ending in `/reviews`. Reviews data and sessions survive app restarts in the PostgreSQL volume.
