from flask import Flask
import os
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'
from .models import user

import KusonukiBOT.views
import KusonukiBOT.message