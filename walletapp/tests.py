import datetime
import os
import random
import unittest
import tempfile
from decimal import Decimal
testdb = ''
os.environ["DATABASE"] = "sqlite:///%s" % testdb

from flask import url_for

from flaskwallet import app
from flaskwallet import init_db
from flaskwallet import session
from otpapp.app import otpapp
from settingsapp.app import settingsapp
from walletapp.app import walletapp
from walletapp.app import coinformat
from walletapp.forms.wallet import WalletForm
from walletapp.helpers import strtofloat
from walletapp.lib.connection import get_connection
from walletapp.models import Wallet

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import InvalidRequestError


app.register_blueprint(otpapp)
app.register_blueprint(settingsapp)
app.register_blueprint(walletapp)
app.config['TESTING'] = True
pp = 'testpassphrase'

def setUpModule():
    init_db()
    ctx = app.test_request_context()
    ctx.push()
    wallet1 = Wallet(
        'box1',
        'admin1',
        '123',
        'localhost',
        19001,
        False,
        True,
    )
    wallet2 = Wallet(
        'box2',
        'admin2',
        '123',
        'localhost',
        19011,
        False,
        True,
    )
    session.add(wallet1)
    session.add(wallet2)
    session.commit()
    # DONTFIXME encryption should be done through the webapp
    # Actually, no, this can't be done as it makes the daemon stop..
    # Unless we let this code restart it...
    conn = get_connection(wallet2)
    info = conn.getinfo()
    if not hasattr(info, 'unlocked_until'):
        conn.encryptwallet(pp)
    else:
        # Unlock and refill the keypool
        conn.walletpassphrase(pp, 1)
        conn.keypoolrefill()


def tearDownModule():
    wallets = Wallet.query.all()
    for wallet in wallets:
        session.delete(wallet)
        session.commit()


class CreateTest(unittest.TestCase):
    def get_wallet(self, num, port=8332):
        return Wallet(
            label = 'testlabel%d' % num,
            rpcuser_decrypted = 'testuser%d' % num,
            rpcpass_decrypted = 'testpass%d' % num,
            rpchost = 'localhost',
            rpcport = port,
            rpchttps = False,
            testnet = True,
        )

    def test_wallet_dupes(self):
        """
        Rather pointless to test the ORM itself, but I had gotten
        this wrong initially.
        """
        newwallet0 = self.get_wallet(0)
        session.add(newwallet0)
        session.commit()

        dupe = False
        newwallet1 = self.get_wallet(1)
        try:
            session.add(newwallet1)
            session.commit()
            dupe = True
        except IntegrityError:
            session.rollback()
        self.assertFalse(
            dupe,
            'Unique DB constraint was ignored',
        )
        session.delete(newwallet0)
        session.commit()


class FilterTest(unittest.TestCase):
    def _test_coinformat(self, valin, expected):
        valout = coinformat(valin)
        self.assertEqual(
            valout,
            expected,
            'Coinformat of %s(%s) is %s, not %s' % (str(type(valin)),
                                   str(valin), valout, expected)
        )
        self.assertEqual(
            type(valout),
            str
        )

    def test_coinformat(self):
        self._test_coinformat(float(0.8), '0.8')
        self._test_coinformat(float(0.08), '0.08')
        self._test_coinformat(float(0.0008), '0.0008')
        self._test_coinformat(float(0.0000008), '0.0000008')
        self._test_coinformat(float(0.00000001), '0.00000001')
        self._test_coinformat(float(1), '1')
        self._test_coinformat(float(10), '10')
        self._test_coinformat(float(1000), '1000')
        self._test_coinformat(float(100000), '100000')


class HelperTest(unittest.TestCase):
    def _test_strtofloat(self, valin, expected):
        valout = strtofloat(valin)
        self.assertEqual(
            valout,
            expected,
            'Coinformat of %s is %s, not %s' % (repr(valin), valout, expected)
        )
        self.assertEqual(
            type(valout),
            type(expected),
            'Coinformat of %s is %s, not %s' % (repr(valin), type(valout),
                                               type(expected))
        )

    def test_strtofloat(self):
        """
        This is a rather pointless test, isn't it?
        """
        self._test_strtofloat('0.1', 0.1)
        self._test_strtofloat('0.01', 0.01)
        self._test_strtofloat('0.001', 0.001)
        self._test_strtofloat('0.00001', 0.00001)
        self._test_strtofloat('0.0000001', 0.0000001)
        self._test_strtofloat('0.00000001', 0.00000001)
        self._test_strtofloat('1', float(1))
        self._test_strtofloat('10', float(10))
        self._test_strtofloat('1000', float(1000))
        self._test_strtofloat('100000', float(100000))


class WithDataTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.wallet = Wallet.query.filter(Wallet.label=='box1').first()
        cls.conn = get_connection(cls.wallet)
        cls.account = 'testaccount-%s' % datetime.datetime.now().isoformat()
        cls.info = cls.conn.getinfo()



class ViewTest(WithDataTestBase):
    """
    Theses are expensive tests that just verify that pages can be accessed.
    """
    def test_list(self):
        r = self.client.get(url_for('wallet.wallet_list'))
        self.assertEqual(
            r.status_code,
            200
        )

    def test_detail(self):
        for wallet in Wallet.query.all():
            r = self.client.get(url_for('wallet.wallet_detail', id=wallet.id))
            self.assertEqual(
                r.status_code,
                200
            )
        r = self.client.get(url_for('wallet.wallet_detail', id=1337))
        self.assertEqual(
            r.status_code,
            404,
            "Didn't get 404 for inexistent wallet"
        )

    def test_transactions(self):
        for wallet in Wallet.query.all():
            r = self.client.get(url_for('wallet.wallet_transactions', id=wallet.id))
            self.assertEqual(
                r.status_code,
                200
            )

    def test_received(self):
        for wallet in Wallet.query.all():
            r = self.client.get(url_for('wallet.wallet_received', id=wallet.id))
            self.assertEqual(
                r.status_code,
                200
            )

    def test_addressgroupings(self):
        for wallet in Wallet.query.all():
            r = self.client.get(url_for('wallet.wallet_addressgroupings', id=wallet.id))
            self.assertEqual(
                r.status_code,
                200
            )

    def test_help(self):
        for wallet in Wallet.query.all():
            r = self.client.get(url_for('wallet.wallet_help', id=wallet.id))
            self.assertEqual(
                r.status_code,
                200
            )

    def test_mininginfo(self):
        for wallet in Wallet.query.all():
            r = self.client.get(url_for('wallet.wallet_mininginfo', id=wallet.id))
            self.assertEqual(
                r.status_code,
                200
            )

    def test_peers(self):
        for wallet in Wallet.query.all():
            r = self.client.get(url_for('wallet.wallet_peers', id=wallet.id))
            self.assertEqual(
                r.status_code,
                200
            )

    def test_add(self):
        for wallet in Wallet.query.all():
            url = url_for('wallet.wallet_add')
            r = self.client.get(url)
            self.assertEqual(
                r.status_code,
                200
            )

    def test_edit(self):
        for wallet in Wallet.query.all():
            r = self.client.get(url_for('wallet.wallet_edit', id=wallet.id))
            self.assertEqual(
                r.status_code,
                200
            )

    def test_move(self):
        for wallet in Wallet.query.all():
            r = self.client.get(url_for('wallet.wallet_move', id=wallet.id))
            self.assertEqual(
                r.status_code,
                200
            )

    def test_send(self):
        for wallet in Wallet.query.all():
            r = self.client.get(url_for('wallet.wallet_send', id=wallet.id))
            self.assertEqual(
                r.status_code,
                200
            )

    def test_unlock(self):
        # FIXME need to do the same for encrypted wallets!
        for wallet in Wallet.query.all():
            r = self.client.get(url_for('wallet.wallet_unlock', id=wallet.id))
            self.assertEqual(
                r.status_code,
                200
            )


class WalletIntegrationTest(WithDataTestBase):
    # Todo: move, send, unlock, lock
    def _test_set_txfee(self):
        for fee in (0.1, 0.001, 0.00000001, 0):
            fee = Decimal(fee)
            url = url_for('wallet.wallet_settxfee', id=self.wallet.id)
            data = {
                'fee': fee,
            }
            r = self.client.post(url, data=data)
            self.assertEqual(
                r.status_code,
                302
            )
            info = self.conn.getinfo()
            self.assertEqual(
                "%.8f" % info.paytxfee,
                "%.8f" % fee,
                "TX fee wasn't adjusted correctly"
            )

    def test_add_delete_wallet(self):
        url = url_for('wallet.wallet_add')
        label = 'testwallet-%s' % datetime.datetime.now().isoformat()
        host = 'testhost'
        data = {
            'label': label,
            'rpcuser_decrypted': 'testuser',
            'rpcpass_decrypted': 'testpass',
            'rpchost': host,
            'rpchttps': False,
            'rpcport': 1337,
            'testnet': True,
            'coin': 'BTC',
        }
        r = self.client.post(url, data=data, follow_redirects=False)
        self.assertEqual(
            r.status_code,
            302
        )
        wallet = Wallet.query.filter(Wallet.label==label).first()
        self.assertTrue(
            wallet
        )
        self.assertEqual(
            wallet.testnet,
            True
        )

        count = len(Wallet.query.all())
        wallet = Wallet.query.filter(Wallet.label==label).first()
        url = url_for('wallet.wallet_delete', id=wallet.id)
        r = self.client.post(url, data={}, follow_redirects=False)
        self.assertEqual(
            r.status_code,
            302,
            "No redirect after wallet deletion: %d" % r.status_code,
        )
        self.assertEqual(
            len(Wallet.query.all()),
            count - 1,
            "Not all wallets were deleted"
        )

    def test_edit_doesnt_break_values(self):
        for wallet in Wallet.query.all():
            url = url_for('wallet.wallet_edit', id=wallet.id)
            rpcuser = wallet.rpcuser_decrypted
            rpcpass = wallet.rpcpass_decrypted
            label = wallet.label
            data = {
                'label': wallet.label,
                'rpcuser_decrypted': wallet.rpcuser_decrypted,
                'rpcpass_decrypted': wallet.rpcpass_decrypted,
                'rpchost': wallet.rpchost,
                'rpcport': wallet.rpcport,
                'coin': wallet.coin,
            }
            rpchttps = wallet.rpchttps
            if rpchttps:
                data['rpchttps'] = 'y'
            testnet = wallet.testnet
            if testnet:
                data['testnet'] = 'y'
            r = self.client.post(url, data=data)
            self.assertEqual(
                r.status_code,
                302
            )
            verify = Wallet.query.filter(Wallet.label==label).first()
            self.assertEqual(
                verify.rpcuser_decrypted,
                rpcuser,
                "Editing broke the rpc user: %s vs %s" % (rpcuser, verify.rpcuser_decrypted)
            )
            self.assertEqual(
                verify.rpcpass_decrypted,
                rpcpass,
                "Editing broke the rpc pass: %s vs %s" % (rpcpass, verify.rpcpass_decrypted)
            )
            self.assertEqual(
                verify.label,
                label,
                "Editing broke the label",
            )
            self.assertEqual(
                verify.rpchttps,
                rpchttps,
                "Editing broke the rpchttps",
            )
            self.assertEqual(
                verify.testnet,
                testnet,
                "Editing broke the testnet setting",
            )


class AccountIntegrationTest(WithDataTestBase):
    # TODO sending
    def test_create(self):
        url = url_for('wallet.account_create', id=self.wallet.id)
        accountname = 'newtestaccount-%s' % datetime.datetime.now().isoformat()
        data = {
            'label': accountname,
        }
        r = self.client.post(url, data=data)
        address = self.conn.getaccountaddress(accountname)
        account = self.conn.getaccount(address)
        self.assertEqual(
            accountname,
            account,
            "Well, creating an account apparently didn't create an address"
        )

    def test_detail(self):
        url = url_for('wallet.account_detail', id=self.wallet.id, account=self.account)
        r = self.client.get(url)
        self.assertEqual(
            r.status_code,
            200
        )

    def test_getnewaddress(self):
        oldaddresses = self.conn.getaddressesbyaccount(self.account)
        url = url_for('wallet.account_newaddress', id=self.wallet.id, account=self.account)
        r = self.client.get(url)
        newaddresses = self.conn.getaddressesbyaccount(self.account)
        self.assertEqual(
            len(oldaddresses) + 1,
            len(newaddresses),
            "Number of addresses is incorrect, %d != %d" % (len(oldaddresses), len(newaddresses))
        )

    def test_send(self):
    # TODO well, send coins
        url = url_for('wallet.account_send', id=self.wallet.id, account=self.account)
        r = self.client.get(url)
        self.assertEqual(
            r.status_code,
            200
        )


class AddressIntegrationTest(WithDataTestBase):
    def setUp(self):
        super(AddressIntegrationTest, self).setUp()
        accountname = 'addresstestaccount-%s' % datetime.datetime.now().isoformat()
        self.address = self.conn.getaccountaddress(accountname)

    def test_detail(self):
        url = url_for('wallet.address_detail', id=self.wallet.id,
                                                       address=self.address)
        r = self.client.get(url)
        self.assertEqual(
            r.status_code,
            200,
            "Address detail view isn't 200, %i" % r.status_code,
        )

    def test_sign(self):
        # TODO unlock wallet
        # TODO submit form
        url = url_for('wallet.address_sign', id=self.wallet.id,
                                                       address=self.address)
        r = self.client.get(url)
        self.assertEqual(
            r.status_code,
            200,
            "GET address sign view isn't 200, %i" % r.status_code,
        )

    def test_sign_any(self):
        # TODO unlock wallet
        # TODO submit form
        url = url_for('wallet.address_sign_any', id=self.wallet.id,
                                                       address=self.address)
        r = self.client.get(url)
        self.assertEqual(
            r.status_code,
            200,
            "GET address sign any view isn't 200, %i" % r.status_code,
        )

    def test_dumpprivkey(self):
        # TODO unlock wallet
        url = url_for('wallet.address_dumpprivkey', id=self.wallet.id,
                                                       address=self.address)
        r = self.client.get(url)
        self.assertEqual(
            r.status_code,
            200,
            "GET address dumpprivkey view isn't 200, %i" % r.status_code,
        )


if __name__ == '__main__':
    unittest.main()
