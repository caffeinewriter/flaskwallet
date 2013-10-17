import os
testdb = ''
os.environ["DATABASE"] = "sqlite:///%s" % testdb
import unittest
import tempfile

from flask import url_for

from app import settingsapp
from flaskwallet import app
from flaskwallet import init_db
from flaskwallet import session
from settingsapp.models import Setting
from walletapp.app import walletapp

from sqlalchemy.exc import IntegrityError


app.register_blueprint(settingsapp)
app.register_blueprint(walletapp)
app.config['TESTING'] = True

def setUpModule():
    init_db()


class CreateTest(unittest.TestCase):
    def test_setval_dupe(self):
        newsetting = Setting('testkey', u'teststring')
        session.add(newsetting)
        session.commit()
        newsetting = Setting('testkey', u'teststring')
        session.add(newsetting)
        dupe = False
        try:
            session.commit()
            dupe = True
        except IntegrityError:
            session.rollback()
        self.assertFalse(
            dupe,
            "Could set the same key twice",
        )

    def test_setval_string(self):
        key = 'test_setval_stringX'
        value = u'test_setval_string'
        newsetting = Setting(key, value)
        session.add(newsetting)
        session.commit()
        setting = Setting.query.get(key)
        self.assertEqual(
            setting.value_decrypted,
            value,
            "Setting incorrectly saved",
        )

    def test_setval_int(self):
        key = 'test_setval_int'
        value = '94'
        newsetting = Setting(key, value)
        session.add(newsetting)
        session.commit()
        setting = session.query(Setting).get(key)
        self.assertEqual(
            setting.value_decrypted,
            value,
            "Setting incorrectly saved",
        )


class ViewTest(unittest.TestCase):
    """
    Destroying and re-creating the db after each test lead to race
    conditions. It's better to avoid it for performance reasons
    anyway.
    """
    @classmethod
    def setUpClass(cls):
        setting_name = Setting('name', u'Bob')
        setting_mail = Setting('mail', u'test@example.com')
        setting_number = Setting('number', 66)
        session.add(setting_name)
        session.add(setting_mail)
        session.add(setting_number)
        session.commit()

    def setUp(self):
        self.client = app.test_client()
        ctx = app.test_request_context()
        ctx.push()

    def test_list(self):
        r = self.client.get(url_for('settings.list'))
        self.assertEqual(
            r.status_code,
            200
        )

    def test_add(self):
        url = url_for('settings.list')
        data = {
            'name': 'testsetting',
            'value': 'testvalue',
        }
        r = self.client.post(url, data=data)
        self.assertEqual(
            r.status_code,
            302,
        )

    def test_edit(self):
        url = url_for('settings.list')
        name = 'testsettingedit'
        data = {
            'name': name,
            'value_decrypted': 'testvalue',
        }
        r = self.client.post(url, data=data)
        self.assertEqual(
            r.status_code,
            302,
        )

        url = url_for('settings.edit', name=name)
        r = self.client.get(url)

        value = 'newvalue'
        data = {
            'name': name,
            'value_decrypted': value,
        }
        r = self.client.post(url, data=data)
        self.assertEqual(
            r.status_code,
            302,
        )
        updated = Setting.query.filter(Setting.name==name).first()
        self.assertEqual(
            updated.value_decrypted,
            value,
            "Value was not updated"
        )

    def test_delete(self):
        url = url_for('settings.list')
        name = 'testsettingdelete'
        data = {
            'name': name,
            'value': 'testvalue',
        }
        r = self.client.post(url, data=data)
        self.assertEqual(
            r.status_code,
            302,
        )

        url = url_for('settings.delete', name=name)
        r = self.client.post(url, data={})
        self.assertEqual(
            r.status_code,
            302,
        )

        exists = Setting.query.filter(Setting.name==name).first()
        self.assertEqual(
            exists,
            None,
            "Setting was not deleted",
        )


if __name__ == '__main__':
    unittest.main()
