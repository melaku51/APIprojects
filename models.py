
import datetime
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from db import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    belt_rank = Column(String)
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    attendance = relationship("Attendance", back_populates="member")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    date = Column(Date)
    present = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member", back_populates="attendance")
