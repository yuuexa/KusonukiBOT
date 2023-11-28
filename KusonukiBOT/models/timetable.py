from KusonukiBOT import db
from datetime import datetime

class Timetable(db.Model):
    __tablename__ = 'timetable'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)  # ID
    year = db.Column(db.Integer, default = 1, nullable = False) # 学年
    group = db.Column(db.String(1), default = 'G', nullable = False) # クラス
    week_day = db.Column(db.String, nullable = False)  # 週+曜日
    first = db.Column(db.String, nullable = False)  # 1時間目
    second = db.Column(db.String, nullable = False)  # 2時間目
    third = db.Column(db.String, nullable = False)  # 3時間目
    fourth = db.Column(db.String, nullable = False)  # 4時間目
    fifth = db.Column(db.String, nullable = False)  # 5時間目
    author = db.Column(db.String) # 作成者ID
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)  # 作成日時
    updated_at = db.Column(db.DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)  # 更新日時