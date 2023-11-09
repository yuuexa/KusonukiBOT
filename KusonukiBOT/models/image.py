from KusonukiBOT import db
from datetime import datetime

class Examination(db.Model):
    __tablename__ = 'examination'
    id = db.Column(db.Integer, primary_key = True)  # 試験ID
    name = db.Column(db.String)  # 名前
    subject = db.Column(db.String)  # 教科
    year = db.Column(db.Integer, default = 1) # 学年
    group = db.Column(db.String(1)) # クラス
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)  # 作成日時
    updated_at = db.Column(db.DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)  # 更新日時