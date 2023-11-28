from KusonukiBOT import db
from datetime import datetime

class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)  # ID
    user_id = db.Column(db.String, nullable = False)  # 名前
    user_name = db.Column(db.String, nullable = False) # ID
    content = db.Column(db.String, nullable = False) # 内容
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)  # 作成日時