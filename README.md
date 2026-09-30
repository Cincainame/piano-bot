# piano-bot
Piano bot that helps schedule student's timetable through telegram

## Supabase setup

The bot connects to the Supabase Postgres database through SQLAlchemy. The
schedule seed data is in `scripts/seed_schedule.py`; `pg8000` (pure Python) is the
PostgreSQL driver used by SQLAlchemy — set `DATABASE_URL` to a
`postgresql+pg8000://...` connection string.

1. Run `pipenv install`.
2. Copy `.env.example` to `.env` and replace `DATABASE_URL` with your Supabase
   Postgres connection string.
3. Make sure the existing `students` table has an integer primary key plus
   `name`, `start_time`, `end_time`, and `day_of_week` columns. If the table
   does not exist, `scripts/seed_schedule.py` creates it.
   4. Run `pipenv run python scripts/seed_schedule.py`.

   ## Project layout

   - `bot/` contains the Telegram bot and scheduling/database logic.
   - `app/` contains the FastAPI API, routers, schemas, and services.
   - `scripts/` contains database seed scripts.
   - `data/` contains roster and student data files.
   - `alembic/` contains database migrations.

   Run the bot with `pipenv run python -m bot.main` and the API with
   `pipenv run uvicorn app.main:app --reload`.

The script inserts one row per student. `Edelle and Ellysha` becomes two rows
with the same lesson time. Do not commit `.env`.
