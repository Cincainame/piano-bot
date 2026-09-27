from datetime import datetime
import os
from contextlib import contextmanager
from sqlite3 import Time
from typing import Iterator

from dotenv import load_dotenv
from sqlalchemy import String, create_engine, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    start: Mapped[time] = mapped_column(Time)
    end: Mapped[time] = mapped_column(Time)
    day_of_week: Mapped[str] = mapped_column(String(9), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    term: Mapped[str] = mapped_column(String(255))
    absent_date: Mapped[str] = mapped_column(String(255), default="")
    replacement_date: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
def get_engine():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set in the environment.")
    return create_engine(DATABASE_URL, pool_pre_ping=True)


@contextmanager
def session_scope() -> Iterator[Session]:
    with Session(get_engine()) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def create_tables() -> None:
    Base.metadata.create_all(get_engine())