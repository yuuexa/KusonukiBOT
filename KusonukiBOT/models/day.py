from KusonukiBOT import db
from datetime import datetime

class Day(db.Model):
    __tablename__ = 'day'
    id = db.Column(db.Integer, primary_key = True)  # 試験ID
    date = db.Column(db.Date)  # 日付
    week = db.Column(db.String)  # 週