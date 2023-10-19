import os
from dotenv import load_dotenv
from flask import Flask
from flask_pymongo import PyMongo
from flask_mail import Mail

# Load from .env file
load_dotenv()


class App:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = "secret"
        print(os.environ.get("MONGO_URI"), "<--- MONGO_URI")
        self.app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
        self.mongo = PyMongo(self.app)

        self.app.config["MAIL_SERVER"] = "smtp.gmail.com"
        self.app.config["MAIL_PORT"] = 465
        self.app.config["MAIL_USE_SSL"] = True
        self.app.config["MAIL_USERNAME"] = "bogusdummy123@gmail.com"
        self.app.config["MAIL_PASSWORD"] = "helloworld123!"
        self.mail = Mail(self.app)
