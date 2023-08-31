from sqlalchemy import Column, Integer, String, ForeignKey, Interval, DateTime, Text, Float
from dataAPI.db_connection import Base

from datetime import datetime

class Ticket(Base):
    __tablename__ = "ticket"
    id = Column(Integer, primary_key=True)
    project = Column(String(120), nullable=False)
    key = Column(String(120), nullable=False)
    issuetype = Column(String(120), nullable=False)
    priority = Column(String(120), nullable=False)
    summary = Column(String(500), nullable=False)
    customer = Column(String(120), nullable=True)
    status = Column(String(120), nullable=False)
    assignee = Column(String(120), nullable=True)
    epic_name = Column(String(120), nullable=True)
    epic_link = Column(String(120), nullable=True)
    parent = Column(String(120), nullable=True)

class WorkLog(Base):
    __tablename__ = "worklog"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    updated = Column(DateTime, nullable=False)
    started = Column(DateTime, nullable=False)
    time_spent = Column(Integer, nullable=False)
    work_des = Column(Text, nullable=True)
    ticket_id = Column(Integer, nullable=False)
    epic_id = Column(Integer, ForeignKey('ticket.id'), nullable=False)

class WorkLogChangeLog(Base):
    __tablename__ = "worklog_changelog"
    id = Column(Integer, primary_key=True)
    worklog_id = Column(Integer, nullable=False)
    updated = Column(DateTime, nullable=False)
    prev_started = Column(DateTime, nullable=False)
    new_started = Column(DateTime, nullable=True)
    prev_time_spent = Column(Interval, nullable=False)
    new_time_spent = Column(Interval, nullable=True)
    ticket_id = Column(Integer, ForeignKey('ticket.id'), nullable=False)

class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    role = Column(String(120), nullable=False)
    rate_card_description = Column(String(120), nullable=False)
    hours_pw = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)