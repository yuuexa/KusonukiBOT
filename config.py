from dotenv import load_dotenv
load_dotenv()

import os

DEBUG = False
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
WEBHOOK_URI = 'https://8752-240d-1a-da0-c200-50a-a794-1a4e-35e2.ngrok-free.app'
SQLALCHEMY_DATABASE_URI = 'sqlite:///kusonuki.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True