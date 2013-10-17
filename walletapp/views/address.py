from flask import render_template
from flask import request

from walletapp.forms.address import SignForm
from walletapp.views.wallet import WalletConnectedBase
from walletapp.views.wallet import WalletUnlockedBase


class AddressDetailView(WalletConnectedBase):
    def dispatch_request(self, id, address):
        super(AddressDetailView, self).dispatch_request(id)
        data = {}
        data['address'] = address
        data['received_amount'] = self.conn.getreceivedbyaddress(address)
        data['account'] = self.conn.getaccount(address)
        if data['account']:
            data['transactions'] = self.conn.listtransactions(data['account'])
        return render_template("wallet/address/detail.html", wallet=self.wallet,
                               data=data)


class AddressSignView(WalletUnlockedBase):
    methods = ['GET', 'POST']
    def dispatch_request(self, id, address=''):
        super(AddressSignView, self).dispatch_request(id)
        data = {}
        data['address'] = address
        if address:
            data['account'] = self.conn.getaccount(address)
            template = 'wallet/address/sign.html'
        else:
            data['account'] = False
            template = 'wallet/wallet/sign.html'
        form = SignForm(request.form)
        if not form.address.data:
            form.address.data = address
        if request.method == 'POST' and form.validate():
            try:
                data['signed_message'] = self.conn.signmessage(
                                          form.address.data, form.message.data)
            except WalletUnlockNeeded:
                form = UnlockForm()
                data['signed_message'] = 'Wallet needs to be unlocked first'
        return render_template(template, wallet=self.wallet, data=data,
                               form=form)


class AddressDumpPrivKeyView(WalletUnlockedBase):
    def dispatch_request(self, id, address):
        super(AddressDumpPrivKeyView, self).dispatch_request(id)
        data = {}
        data['address'] = address
        data['account'] = self.conn.getaccount(address)
        template = 'wallet/address/sign.html'
        try:
            data['privkey'] = self.conn.dumpprivkey(address)
        except:
            pass  # Parent class handles already flashes a warning
        return render_template("wallet/address/dumpprivkey.html", wallet=self.wallet,
                               data=data)
