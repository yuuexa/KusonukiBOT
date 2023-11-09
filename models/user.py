from KusonukiBOT import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String, primary_key = True)  # ユーザーID
    name = db.Column(db.String(255))  # 名前
    avatar = db.Column(db.String)  # アバター
    year = db.Column(db.Integer, default = 1) # 学年
    group = db.Column(db.String(1)) # クラス
    available = db.Column(db.Boolean, default = True) # 使用許可
    evaluation = db.Column(db.Integer, default = 10.0) # 評価値
    role = db.Column(db.String, default = 'DEFAULT') # 権限
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now)  # 作成日時
    updated_at = db.Column(db.DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)  # 更新日時