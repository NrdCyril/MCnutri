import os
from datetime import timedelta

class Config:

    SECRET_KEY = "supersecret"

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db") 
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = "jwt-secret"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)