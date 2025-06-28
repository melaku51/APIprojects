from fastapi import FastAPI
from typing import List, Annotated, Optional
import datetime

from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
import models
import db 
from db import engine, SessionLocal
from sqlalchemy.orm import Session

# Load environment variables from .env file
import os
from dotenv import load_dotenv

class MemberBase(BaseModel):
    name: str
    belt_rank: str
    age: int

class MemberCreate(MemberBase):
    pass

class MemberResponse(MemberBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True
class AttendanceCreate(BaseModel):
    member_id: int
    date: datetime.date
    present: bool       
class AttendanceBase(BaseModel):
    member_id: int
    date: datetime.date
    present: bool
class AttendanceResponse(AttendanceBase):
    id: int
    member_id: int
    belt_rank: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

#FastAPI app
app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/members/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    #check if the member already exists
    db_member = db.query(models.Member).filter(models.Member.name == member.name).first()
    if db_member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member already exists")
    #create a new member
    new_member = member(
        name=member.name,
        belt_rank=member.belt_rank,
        age=member.age
    )
    
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@app.post("/attendance/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def mark_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
   #find the member
   member = db.query(models.Member).filter(models.Member.id == attendance.member_id).first()
   if not member:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")    
    #create a new attendance record
   new_attendance = models.Attendance(
       member_id=attendance.member_id,
       date=attendance.date,
       present=attendance.present
   )
   db.add(new_attendance)
   db.commit()
   db.refresh(new_attendance)
    # Enrich the response with member details
   return AttendanceResponse(
    id=new_attendance.id,
    member_id=new_attendance.member_id,
    date=new_attendance.date,
    present=new_attendance.present,
    belt_rank=member.belt_rank,
    created_at=new_attendance.created_at
)

@app.get("/attendance/", response_model=List[AttendanceResponse])
async def get_all_attendance(db: Session = Depends(get_db)):

    #calculate the date one month ago
    one_month_ago = datetime.date.today() - datetime.timedelta(days=30)

    #query the attendance with member details
    attendance_records = db.query(models.Attendance, models.Member)\
        .join(models.Member)\
        .filter(models.Attendance.date >= one_month_ago)\
        .order_by(models.Attendance.date.desc())\
        .all()
    #format the response
    return [
    AttendanceResponse(
        id=record[0].id,
        member_id=record[1].id,
        date=record[0].date,
        present=record[0].present,
        belt_rank=record[1].belt_rank,
        created_at=record[0].created_at
    )
    for record in attendance_records
]