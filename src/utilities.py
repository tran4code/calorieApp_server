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


import random

from flask_mail import Message
from apps import App
import string


class Utilities:
    app = App()
    mail = app.mail
    mongo = app.mongo

    def send_email(self, email):
        msg = Message()
        msg.subject = "BURNOUT - Reset Password Request"
        msg.sender = "bogusdummy123@gmail.com"
        msg.recipients = [email]
        random = str(self.get_random_string(8))
        msg.body = (
            "Please use the following password to login to your account: " + random
        )
        self.mongo.db.ath.update({"email": email}, {"$set": {"temp": random}})
        if self.mail.send(msg):
            return "success"
        else:
            return "failed"

    def get_random_string(self, length):
        # choose from all lowercase letter
        letters = string.ascii_lowercase
        result_str = "".join(random.choice(letters) for i in range(length))
        print("Random string of length", length, "is:", result_str)
        return result_str
