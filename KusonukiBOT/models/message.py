from KusonukiBOT import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.String, primary_key = True)  # メッセージID
    user_id = db.Column(db.String, nullable = False)  # 名前
    user_name = db.Column(db.String, nullable = False) # ID
    content = db.Column(db.String, nullable = False) # 内容
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)  # 作成日時