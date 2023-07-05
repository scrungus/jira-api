from sqlalchemy import Column, Integer, String, ForeignKey, Interval, DateTime, Text
from dataAPI.db_connection import Base

from datetime import datetime

class Ticket(Base):
    __tablename__ = "ticket"
    id = Column(Integer, primary_key=True)
    key = Column(String(120), nullable=False)
    issuetype = Column(String(120), nullable=False)
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
    ticket_id = Column(Integer, ForeignKey('ticket.id'), nullable=False)
    name = Column(String(120), nullable=False)
    started = Column(DateTime, nullable=False)
    time_spent = Column(Interval, nullable=False)
    work_des = Column(Text, nullable=False)