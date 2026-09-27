# piano-bot
Piano bot that helps schedule student's timetable through telegram

## Supabase setup

The bot connects to the Supabase Postgres database through SQLAlchemy. The
schedule seed data is in `seed_schedule.py`; `psycopg2` remains the PostgreSQL
driver used by SQLAlchemy.

1. Run `pipenv install`.
2. Copy `.env.example` to `.env` and replace `DATABASE_URL` with your Supabase
   Postgres connection string.
3. Make sure the existing `students` table has an integer primary key plus
   `name`, `start_time`, `end_time`, and `day_of_week` columns. If the table
   does not exist, `seed_schedule.py` creates it.
4. Run `pipenv run python seed_schedule.py`.

The script inserts one row per student. `Edelle and Ellysha` becomes two rows
with the same lesson time. Do not commit `.env`.
