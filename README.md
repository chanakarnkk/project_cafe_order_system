# Cafe Order System

Simple Django-based cafe ordering web app.

This repository contains a small Django project for managing a cafe menu and customer orders. The project is configured to run locally with SQLite, but for production deployment (for example on Render) you should switch to a managed PostgreSQL database and adjust settings for secure, static and media file handling.

**Contents**
- `manage.py` - Django management
- `cafe_order_system/` - Django project settings and WSGI/ASGI entrypoints
- `orders/` - app for menu and order functionality
- `requirements.txt` - Python dependencies

## Quick local setup

- Create and activate a virtual environment
  - Windows (PowerShell):
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```
- Install dependencies
  ```powershell
  pip install -r requirements.txt
  ```
- Run migrations and start server
  ```powershell
  python manage.py migrate
  python manage.py createsuperuser  # optional
  python manage.py runserver
  ```

## Production notes (Render)

Render is a good choice to host this app. Below are recommended steps, environment variables and code changes you should make before deploying.

1) Use PostgreSQL (do not rely on SQLite in production)
- In Render: create a new **Postgres** managed database and copy the `DATABASE_URL` connection string.

2) Update `requirements.txt` to include these production packages if not already present:
- `gunicorn` — WSGI server used in production
- `whitenoise` — serve static files directly from the app
- `dj-database-url` — parse `DATABASE_URL` environment variable
- `psycopg2-binary` — PostgreSQL driver

Example additions to `requirements.txt`:
```
gunicorn
whitenoise
dj-database-url
psycopg2-binary
```

3) Adjust `settings.py` for environment-driven config
- Use environment variables for sensitive and environment-specific values:
  - `SECRET_KEY` (do NOT hardcode for production)
  - `DEBUG` (set to `False` in production)
  - `DATABASE_URL` (provided by Render Postgres)
  - `ALLOWED_HOSTS` (set to `.onrender.com` or specific hostnames)

Suggested snippets to add/replace in `cafe_order_system/settings.py`:

```python
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-for-local')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Middleware: add WhiteNoise after SecurityMiddleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... the rest of your middleware ...
]
```

4) Render service configuration

- In Render, create a new **Web Service** connected to your Git repository (branch `main` or whichever branch you use).
- Build command (Render's **Build Command**):
  ```bash
  pip install -r requirements.txt
  ```
- Start command (Render's **Start Command**) — run migrations, collect static, then start gunicorn. Example:
  ```bash
  python manage.py migrate --noinput; python manage.py collectstatic --noinput; gunicorn cafe_order_system.wsgi --bind 0.0.0.0:$PORT
  ```

- Environment variables to set in Render Dashboard (Service -> Environment):
  - `SECRET_KEY` = (generate a long random string)
  - `DEBUG` = `False`
  - `DATABASE_URL` = (from the managed Postgres service)
  - `ALLOWED_HOSTS` = `.onrender.com,your-custom-domain.com` (comma-separated)

5) Media files
- Render's filesystem is ephemeral. If your app serves uploaded files (media), use an external storage provider (S3, Cloudinary) and configure Django's `DEFAULT_FILE_STORAGE` accordingly.

6) Optional: start script
- You can add a small `start.sh` in the repo and set the Render start command to run it. Example `start.sh`:
  ```bash
  #!/usr/bin/env bash
  set -e
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
  exec gunicorn cafe_order_system.wsgi --bind 0.0.0.0:$PORT
  ```

Make sure to `chmod +x start.sh` locally before committing.

7) Optional: `render.yaml` (in-repo infra-as-code)
- For reproducible deployments you can add a `render.yaml` describing the web service and the postgres service. Refer to Render's docs for the exact schema; it's optional but useful for advanced workflows.

## Common issues & troubleshooting
- 500 or secret-key errors: ensure `SECRET_KEY` is set in Render env.
- Database connection errors: confirm `DATABASE_URL` and that the Postgres service allows connections from the web service (Render wiring usually handles this).
- Static files 404: ensure `whitenoise` is installed and `collectstatic` ran successfully. Check `STATIC_ROOT` and `STATICFILES_STORAGE` settings.
- Migrations fail during build: if the DB isn't ready during build, run migrations on startup (see `start.sh`) instead of build step.

## Useful Render documentation
- Render Python + Django quickstart: https://render.com/docs/deploy-django
- Render `render.yaml` docs: https://render.com/docs/render-manifest

---
If you'd like, I can:
- add a sample `start.sh` and a small `render.yaml` for this repo;
- update `cafe_order_system/settings.py` with the environment-driven snippets;
- update `requirements.txt` to include the production packages.

Tell me which of those you'd like me to do next and I'll apply the changes.
