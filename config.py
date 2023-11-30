from dotenv import load_dotenv
load_dotenv()

import os

DEBUG = False
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
WEBHOOK_URI = 'https://4431-240d-1a-da0-c200-c8cf-4bd5-5110-9eab.ngrok-free.app'
SQLALCHEMY_DATABASE_URI = 'sqlite:///kusonuki.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True