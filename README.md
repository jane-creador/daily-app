# Daily

A minimal personal daily tracker — expenses, notes, to-dos, and a calendar view.

## Stack

- **Backend:** Python · Flask · SQLAlchemy
- **Database:** PostgreSQL (SQLite fallback for local dev)
- **Frontend:** Vanilla JS · Custom CSS (no frameworks)

## Local development

```bash
# 1. Create virtualenv and install dependencies
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Copy env file (SQLite is used automatically if DATABASE_URL is not set)
cp .env.example .env

# 3. Run
python app.py
```

Visit `http://127.0.0.1:5000`.

## Deploy to Railway

1. Push this repo to GitHub.
2. Create a new Railway project → "Deploy from GitHub repo".
3. Add a PostgreSQL plugin — Railway will inject `DATABASE_URL` automatically.
4. Set `SECRET_KEY` in the Railway environment variables panel.
5. Railway picks up `railway.json` and starts the app with gunicorn.

The `/init-db` route re-creates all tables if needed.
