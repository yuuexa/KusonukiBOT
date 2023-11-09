from dotenv import load_dotenv
load_dotenv()

import os

DEBUG = False
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
SQLALCHEMY_DATABASE_URI = 'sqlite:///kusonuki.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True