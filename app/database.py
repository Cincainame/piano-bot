import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

# Postgres connection string for your Supabase database, e.g.
# postgresql+psycopg2://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass
