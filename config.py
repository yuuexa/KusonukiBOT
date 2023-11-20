from dotenv import load_dotenv
load_dotenv()

import os

DEBUG = False
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
WEBHOOK_URI = 'https://8a09-240d-1a-da0-c200-9406-149b-4e03-f83c.ngrok-free.app'
SQLALCHEMY_DATABASE_URI = 'sqlite:///kusonuki.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True