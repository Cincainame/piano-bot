import os
from datetime import date, time

from dotenv import load_dotenv
from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String, Time, create_engine
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "student"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    phone_no: Mapped[str] = mapped_column(String(32), nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(32), nullable=False)
    terms: Mapped[list["Term"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    created_at: Mapped[date] = mapped_column(Date, nullable=False, server_default="now()")
    
class Term(Base):
    __tablename__ = "term"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("student.id", ondelete="CASCADE"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    term: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)

    student: Mapped[Student] = relationship(back_populates="terms")
    replacements: Mapped[list["Replacement"]] = relationship(
        back_populates="term", cascade="all, delete-orphan"
    )
    absences: Mapped[list["Absence"]] = relationship(
        back_populates="term", cascade="all, delete-orphan"
    )


class Replacement(Base):
    __tablename__ = "replacement"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("student.id", ondelete="CASCADE"), nullable=False
    )
    term_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("term.id", ondelete="CASCADE"), nullable=False
    )
    replacement_date: Mapped[date] = mapped_column(Date, nullable=False)

    term: Mapped[Term] = relationship(back_populates="replacements")

    is_waived: Mapped[bool] = mapped_column(nullable=False, default=False)

class Absence(Base):
    __tablename__ = "absence"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("student.id", ondelete="CASCADE"), nullable=False
    )
    term_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("term.id", ondelete="CASCADE"), nullable=False
    )
    absent_date: Mapped[date] = mapped_column(Date, nullable=False)

    term: Mapped[Term] = relationship(back_populates="absences")
