import pandas as pd
from db.db_connection import SessionLocal
import db.models as models
import json 

def get_data(start_date, end_date):
    db = SessionLocal()
    
    # get all worklogs 
    worklogs = pd.read_sql(db.query(models.WorkLog).filter(models.WorkLog.started>=start_date,models.WorkLog.started<=end_date).statement,db.bind)

    # get date of monday of each week worklogs are in 
    def get_monday_of_week(date):
        return (date - pd.to_timedelta(date.weekday(), unit='d')).date()
    worklogs['weekstarted'] = worklogs['started'].apply(get_monday_of_week)

    # convert timespent (seconds) to hours
    worklogs['time_hours'] = worklogs['time_spent'] / 3600

    # convert Timestamps to str, to make JSON-serialisable for frontend
    worklogs['started'] = worklogs['started'].astype(str)
    worklogs['updated'] = worklogs['updated'].astype(str)
    worklogs['weekstarted'] = worklogs['weekstarted'].astype(str)

    employees = pd.read_sql(db.query(models.Employee).statement,db.bind)

    print(employees)
    print("TOJASON!!")
    print(pd.read_json(employees.to_json(date_format='iso')))

    return worklogs.to_json(), employees.to_json(date_format='iso')