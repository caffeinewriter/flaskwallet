import os
testdb = ''
os.environ["DATABASE"] = "sqlite:///%s" % testdb
import unittest
import tempfile

from flask import url_for

from app import otpapp
#from flaskwallet import app
from flaskwallet import init_db
#from flaskwallet import session
from flaskwallet import app
from settingsapp.models import Setting
from settingsapp.app import settingsapp
from walletapp.app import walletapp

from sqlalchemy.exc import IntegrityError


app.register_blueprint(otpapp)
app.register_blueprint(settingsapp)
app.register_blueprint(walletapp)
app.config['TESTING'] = True

def setUpModule():
    init_db()
    ctx = app.test_request_context()
    ctx.push()


class AccessTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_setup(self):
        url = url_for('otp.setup')
        r = self.client.get(url)
        self.assertEqual(
            r.status_code,
            200
        )

    def test_qr(self):
        url = url_for('otp.qr')
        r = self.client.get(url)
        self.assertEqual(
            r.status_code,
            200
        )
        # The secret is only accessible once
        r = self.client.get(url)
        self.assertEqual(
            r.status_code,
            404
        )

if __name__ == '__main__':
    unittest.main()
