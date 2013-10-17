import os
testdb = ''
os.environ["DATABASE"] = "sqlite:///%s" % testdb
import unittest

from flask import url_for

from flaskwallet import app
from flaskwallet import init_db
from settingsapp.app import settingsapp
from walletapp.app import walletapp


app.register_blueprint(settingsapp)
app.register_blueprint(walletapp)
app.config['TESTING'] = True


class CreateTest(unittest.TestCase):
    def test_list(self):
        ctx = app.test_request_context()
        ctx.push()
        r = app.test_client().get(url_for('root'))
        self.assertEqual(
            r.status_code,
            200
        )


if __name__ == '__main__':
    unittest.main()
