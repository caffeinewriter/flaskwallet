import urllib

from flask import flash
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
#from flask.views import View

from settingsapp.helpers import get_setting
from walletapp.forms.wallet import SendForm
from walletapp.forms.account import CreateAccountForm
from walletapp.helpers import human_format
from walletapp.helpers import real_format
from walletapp.helpers import strtofloat
from walletapp.views.wallet import WalletConnectedBase
from walletapp.views.wallet import WalletUnlockedBase


class AccountBase(WalletConnectedBase):
    """
    Add the account name to the view object
    """
    def dispatch_request(self, id, account):
        super(AccountBase, self).dispatch_request(id)
        account = urllib.unquote(account).decode('utf8')
        self.account = real_format(account)


class AccountCreateView(WalletConnectedBase):
    methods=['POST']
    def dispatch_request(self, id):
        super(AccountCreateView, self).dispatch_request(id)
        form = CreateAccountForm(request.form)
        if form.validate():
            address = self.conn.getnewaddress(form.label.data)
            account = self.conn.getaccount(address)
        return redirect(url_for("wallet.account_detail", id=id, account=account))


class AccountUnlockedBase(WalletUnlockedBase):
    """
    Hrm, shouldn't there be a mixin somewhere?
    """
    def dispatch_request(self, id, account):
        super(AccountUnlockedBase, self).dispatch_request(id)
        account = urllib.unquote(account).decode('utf8')
        self.account = real_format(account)


class AccountDetailView(AccountBase):
    def dispatch_request(self, id, account):
        super(AccountDetailView, self).dispatch_request(id, account)
        data = {}
        data['balance'] = self.conn.getbalance(self.account)
        data['address'] = self.conn.getaccountaddress(self.account)
        data['addresses'] = self.conn.getaddressesbyaccount(self.account)
        #if len(data['addresses']) > 1:
        #    # FIXME getaccountaddress can create a new address under unclair
        #    # circumstances
        #    data['address'] = self.conn.getaccountaddress(account)
        #else:
        #    data['address'] = data['addresses'][0]
        data['transactions'] = self.conn.listtransactions(self.account)
        received = 0
        receivedbyaccounts = self.conn.listreceivedbyaccount()
        for account in receivedbyaccounts:
            if account.account == self.account:
                received = account.amount
        data['received'] = received
        return render_template("wallet/account/detail.html",
                           wallet=self.wallet, account=self.account, data=data)


class AccountNewAddressView(AccountBase):
    def dispatch_request(self, id, account):
        super(AccountNewAddressView, self).dispatch_request(id, account)
        newaddress = self.conn.getnewaddress(self.account)
        flash(u"New address for %s: %s" % (self.account, newaddress),
              'success')
        return redirect(url_for("wallet.account_detail", id=id,
                        account=human_format(self.account)))


class AccountSendView(AccountUnlockedBase):
    methods=['GET', 'POST']
    def dispatch_request(self, id, account):
        super(AccountSendView, self).dispatch_request(id, account)
        form = SendForm(request.form)
        balance = self.conn.getbalance(self.account)
        if request.method == 'POST' and form.validate():
            amount = strtofloat(form.data['amount'])
            txid = self.conn.sendfrom(
                self.account,
                form.toaddress.data,
                amount,
                int(get_setting('minconf', 6)),
                form.comment.data,
                form.to.data
            )
            flash(u"%f coins sent to from %s to %s" % (amount,
                  self.account, form.toaddress.data), 'success')
            return redirect(url_for("wallet.tx_detail", id=id, txid=txid))
        return render_template('wallet/account/send.html', wallet=self.wallet,
                               form=form, balance=balance, account=self.account)
