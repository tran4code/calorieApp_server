# MIT License
#
# Copyright 2023 BurnOut4
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


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
        self.app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
        self.mongo = PyMongo(self.app)

        self.app.config["MAIL_SERVER"] = "smtp.gmail.com"
        self.app.config["MAIL_PORT"] = 465
        self.app.config["MAIL_USE_SSL"] = True
        self.app.config["MAIL_USERNAME"] = "bogusdummy123@gmail.com"
        self.app.config["MAIL_PASSWORD"] = "helloworld123!"
        self.mail = Mail(self.app)
