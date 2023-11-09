from KusonukiBOT import db
from datetime import datetime

class Assignment(db.Model):
    __tablename__ = 'assignment'
    id = db.Column(db.Integer, primary_key = True)  # 課題ID
    year = db.Column(db.Integer, default = 1) # 学年
    group = db.Column(db.String(1), default = 'G') # クラス
    name = db.Column(db.String)  # 名前
    subject = db.Column(db.String)  # 教科
    method = db.Column(db.String) # 提出手段
    deadline = db.Column(db.Date, nullable = False, default = datetime.now)  # 作成日時
    updated_at = db.Column(db.DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)  # 更新日時