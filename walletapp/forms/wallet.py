#from flask.ext.wtf import Form as WTForm
#from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import validators
from wtforms import BooleanField
from wtforms import DecimalField
from wtforms import Form
from wtforms import IntegerField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import TextField

from walletapp.models import Wallet
from walletapp.helpers import get_coin_choices


    #@validates('rpcuser')
    #def validate_rpcport(self, key, rpcport):
    #    assert rpcport >= 1
    #    assert rpcport <= 65535
    #    return rpcuser


class WalletForm(Form):
    label = TextField(u'Label', validators=[validators.required()])
    rpcuser_decrypted = TextField(u'RPC User', validators=[validators.required()])
    rpcpass_decrypted = PasswordField(u'RPC Password', validators=[validators.required()])
    rpchost = TextField(u'RPC Host', validators=[validators.required()])
    rpcport = IntegerField(u'RPC Port', validators=[validators.required()])
    rpchttps = BooleanField(u'RPC HTTPS')
    testnet = BooleanField(u'Testnet')
    coin = SelectField(u'Coin', choices=get_coin_choices())


class SendForm(Form):
    # TODO: validate address, or catch errors later?
    toaddress = TextField(u'To Address', validators=[validators.required()])
    amount = DecimalField(u'Amount', validators=[validators.required()])
    comment = TextField(u'Comment')
    to = TextField(u'To')


class EncryptForm(Form):
    passphrase = PasswordField(u'Passphrase', validators=[validators.required()])
    confirm = PasswordField(u'Confirm passphrase', validators=[validators.required()])


class UnlockForm(Form):
    passphrase = PasswordField(u'Passphrase', validators=[validators.required()])
    timeout = IntegerField(u'Seconds', validators=[validators.required()],
                           default=60)


class OTPUnlockForm(UnlockForm):
    otp = TextField(u'OTP', validators=[validators.required()])


class SetTXFeeForm(Form):
    fee = DecimalField(u'Transaction fee', validators=[validators.required()])
