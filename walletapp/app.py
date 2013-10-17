from datetime import datetime
from decimal import Decimal

from flask import Blueprint

from flaskwallet import app
from walletapp.helpers import human_format
from walletapp.views.address import AddressDetailView
from walletapp.views.address import AddressSignView
from walletapp.views.address import AddressDumpPrivKeyView
from walletapp.views.account import AccountCreateView
from walletapp.views.account import AccountDetailView
from walletapp.views.account import AccountNewAddressView
from walletapp.views.account import AccountSendView
from walletapp.views.wallet import BlockDetailView
from walletapp.views.wallet import TXDetailView
from walletapp.views.wallet import WalletListView
from walletapp.views.wallet import WalletListView
from walletapp.views.wallet import WalletAddView
from walletapp.views.wallet import WalletDetailBase
from walletapp.views.wallet import WalletEditView
from walletapp.views.wallet import WalletConnectedBase
from walletapp.views.wallet import WalletDetailView
from walletapp.views.wallet import WalletTransactionsView
from walletapp.views.wallet import WalletReceivedView
from walletapp.views.wallet import WalletGroupingsView
from walletapp.views.wallet import WalletPeersView
from walletapp.views.wallet import WalletMoveView
from walletapp.views.wallet import WalletUnlockedBase
from walletapp.views.wallet import WalletSendView
from walletapp.views.wallet import WalletDeleteView
from walletapp.views.wallet import WalletStopView
from walletapp.views.wallet import WalletHelpView
from walletapp.views.wallet import WalletMiningInfoView
from walletapp.views.wallet import WalletEncryptView
from walletapp.views.wallet import WalletUnlockView
from walletapp.views.wallet import WalletLockView
from walletapp.views.wallet import WalletSetTXFeeView

walletapp = Blueprint(
    'wallet',
    __name__,
    url_prefix='/wallets',
    template_folder='templates/',
)

# Template filters
@walletapp.app_template_filter()
def coinformat(amount, short=False):
    if amount == Decimal(0):
        ret = 0
    else:
        if short:
            if float(amount) >= 1000:
                ret = "%.0f" % amount
            elif float(amount) >= 100:
                ret = "%.1f" % amount
            else:
                ret = "%.2f" % amount
        else:
            ret = "%.8f" % amount
            ret = ret.rstrip('0')
            ret = ret.rstrip('.')
    return ret

@walletapp.app_template_filter()
def timeformat(timestamp, short=False):
    dt = datetime.fromtimestamp(timestamp)
    if short:
        ret = dt.strftime('%m/%d %H:%M')
    else:
        ret = dt.strftime('%Y/%m/%d %H:%M:%S')
    return ret

@walletapp.app_template_filter()
def timedelta(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    delta = (dt - datetime.now()).total_seconds()
    return "%d seconds" % delta

@walletapp.app_template_filter()
def accountformat(account):
    return human_format(account)

@walletapp.app_template_filter()
def byteformat(num):
    for unit in ['kB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, unit)
        num = num / 1024.0
    return "%3.1f%s" % (num, 'TB')

@walletapp.app_template_filter()
def coinname(code):
    if code in app.config['COINS']:
        ret = app.config['COINS'][code]['name']
    else:
        ret = 'Unknown'
    return ret

# Wallet views
walletapp.add_url_rule(
    '/',
    view_func=WalletListView.as_view('wallet_list')
)
walletapp.add_url_rule(
    '/add/',
    view_func=WalletAddView.as_view('wallet_add')
)
walletapp.add_url_rule(
    '/<int:id>/edit/',
    view_func=WalletEditView.as_view('wallet_edit')
)
walletapp.add_url_rule(
    '/<int:id>/',
    view_func=WalletDetailView.as_view('wallet_detail')
)
walletapp.add_url_rule(
    '/<int:id>/transactions/',
    view_func=WalletTransactionsView.as_view('wallet_transactions')
)
walletapp.add_url_rule(
    '/<int:id>/received/',
    view_func=WalletReceivedView.as_view('wallet_received')
)
walletapp.add_url_rule(
    '/<int:id>/addressgroupings/',
    view_func=WalletGroupingsView.as_view('wallet_addressgroupings')
)
walletapp.add_url_rule(
    '/<int:id>/peers/',
    view_func=WalletPeersView.as_view('wallet_peers')
)
walletapp.add_url_rule(
    '/<int:id>/move/',
    view_func=WalletMoveView.as_view('wallet_move')
)
walletapp.add_url_rule(
    '/<int:id>/send/',
    view_func=WalletSendView.as_view('wallet_send')
)
walletapp.add_url_rule(
    '/<int:id>/delete/',
    view_func=WalletDeleteView.as_view('wallet_delete')
)
walletapp.add_url_rule(
    '/<int:id>/stop/',
    view_func=WalletStopView.as_view('wallet_stop')
)
walletapp.add_url_rule(
    '/<int:id>/help/',
    view_func=WalletHelpView.as_view('wallet_help')
)
walletapp.add_url_rule(
    '/<int:id>/mininginfo/',
    view_func=WalletMiningInfoView.as_view('wallet_mininginfo')
)
walletapp.add_url_rule(
    '/<int:id>/unlock/',
    view_func=WalletUnlockView.as_view('wallet_unlock')
)
walletapp.add_url_rule(
    '/<int:id>/lock/',
    view_func=WalletLockView.as_view('wallet_lock')
)
walletapp.add_url_rule(
    '/<int:id>/encrypt/',
    view_func=WalletEncryptView.as_view('wallet_encrypt')
)
walletapp.add_url_rule(
    '/<int:id>/settxfee/',
    view_func=WalletSetTXFeeView.as_view('wallet_settxfee')
)

# Account views
walletapp.add_url_rule(
    '/<int:id>/newaccount/',
    view_func=AccountCreateView.as_view('account_create')
)
walletapp.add_url_rule(
    '/<int:id>/account/<string:account>/',
    view_func=AccountDetailView.as_view('account_detail')
)
walletapp.add_url_rule(
    '/<int:id>/account/<string:account>/newaddress/',
    view_func=AccountNewAddressView.as_view('account_newaddress')
)
walletapp.add_url_rule(
    '/<int:id>/account/<string:account>/send/',
    view_func=AccountSendView.as_view('account_send')
)

# Address views
walletapp.add_url_rule(
    '/<int:id>/address/<string:address>/',
    view_func=AddressDetailView.as_view('address_detail')
)
walletapp.add_url_rule(
    '/<int:id>/address/<string:address>/sign/',
    view_func=AddressSignView.as_view('address_sign')
)
walletapp.add_url_rule(
    '/<int:id>/signaddress/',
    view_func=AddressSignView.as_view('address_sign_any')
)
walletapp.add_url_rule(
    '/<int:id>/address/<string:address>/dumpprivkey/',
    view_func=AddressDumpPrivKeyView.as_view('address_dumpprivkey')
)

# Misc views
walletapp.add_url_rule(
    '/<int:id>/tx/<string:txid>/',
    view_func=TXDetailView.as_view('tx_detail')
)
walletapp.add_url_rule(
    '/<int:id>/block/<string:block>/',
    view_func=BlockDetailView.as_view('block_detail')
)
