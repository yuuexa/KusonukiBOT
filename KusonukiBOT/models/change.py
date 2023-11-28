from KusonukiBOT import db
from datetime import datetime

class Change(db.Model):
    __tablename__ = 'change'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)  # ID
    year = db.Column(db.Integer, default = 1, nullable = False) # 学年
    group = db.Column(db.String(1), default = 'G', nullable = False) # クラス
    date = db.Column(db.Date)  # 日付
    period = db.Column(db.Integer, nullable = False)  # 時間
    subject = db.Column(db.String, nullable = False)  # 教科
    author = db.Column(db.String) # 作成者ID
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)  # 作成日時
    updated_at = db.Column(db.DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)  # 更新日時