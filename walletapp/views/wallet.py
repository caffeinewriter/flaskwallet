import errno
import socket
import urllib
from ssl import SSLError
from httplib import BadStatusLine

from bitcoinrpc.exceptions import WalletUnlockNeeded
from bitcoinrpc.exceptions import WalletPassphraseIncorrect
from bitcoinrpc.exceptions import WalletAlreadyUnlocked
from bitcoinrpc.exceptions import TransportException
from flask import abort
from flask import flash
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask.views import View

from flaskwallet import cache
from flaskwallet import session
from settingsapp.helpers import get_setting
from settingsapp.models import Setting
from walletapp.lib import connection
from walletapp.forms.account import AccountMoveForm
from walletapp.forms.account import CreateAccountForm
from walletapp.forms.wallet import WalletForm
from walletapp.forms.wallet import SendForm
from walletapp.forms.wallet import EncryptForm
from walletapp.forms.wallet import UnlockForm
from walletapp.forms.wallet import OTPUnlockForm
from walletapp.forms.wallet import SetTXFeeForm
from walletapp.helpers import get_accounts
from walletapp.helpers import human_format
from walletapp.helpers import real_format
from walletapp.helpers import strtofloat
from walletapp.helpers import get_cachetime
from walletapp.models import Wallet

import onetimepass as otp


def get_wallet_info(wallet):
    """
    Add some info to a wallet object
    """
    info = cache.get('walletinfo%d' % wallet.id)
    if info == None:
        try:
            conn = connection.get_connection(wallet)
            info = conn.getinfo()
        except socket.error, v:  # pragma: no cover
            if v[0] == errno.ECONNREFUSED:
                info = False
                flash(u"%s: Connection refused" % wallet.label, 'error')
            elif v[0] == errno.ECONNRESET:
                info = False
                flash(u"%s: Connection reset" % wallet.label, 'error')
            elif v[0] == errno.EHOSTUNREACH:
                info = False
                flash(u"%s: Host unreachable" % wallet.label, 'error')
            elif v[0] == -2:  # WTF
                info = False
                flash(u"%s: Unknown error" % wallet.label, 'error')
            #elif type(v) == socket.cachetime:
            #    info = False
            #    flash(u"%s: cachetime" % wallet.label, 'error')
            else:
                print v[0]
                print dir(v)
                print type(v)
                flash(u"Unhandled exception!", 'error')
        except ValueError:  # pragma: no cover
            info = False
            flash(u"%s: Auth error (?)" % wallet.label, 'error')
        except BadStatusLine:  # pragma: no cover
            # I think this was too much load on the node box
            info = False
            flash(u"%s: Bad status line." % wallet.label, 'error')
        except SSLError:  # pragma: no cover
            info = False
            flash(u"%s: SSL error." % wallet.label, 'error')
        except TransportException, e:  # pragma: no cover
            if e.code == 403:
                info = False
                flash(u"%s: " % e.msg, 'error')
            else:
                flash(u"Unhandled transport exception!", 'error')
        except Exception, e:  # pragma: no cover
            print e
            print dir(e)
            print type(e)
            flash(u"Unhandled exception!", 'error')
    cache.set('walletinfo%d' % wallet.id, info, timeout=get_cachetime())
    return info


class WalletListView(View):
    def dispatch_request(self):
        wallets = Wallet.query.order_by('testnet').order_by('coin').all()
        index_connect = int(get_setting('index_connect', 1))
        if index_connect:
            for wallet in wallets:
                wallet.info = get_wallet_info(wallet)
        otp_secret = get_setting('otpsecret', False)
        if otp_secret:
            show_otp = False
        else:
            show_otp = True
        return render_template('wallet/wallet/list.html', wallets=wallets,
                               show_otp=show_otp)


class WalletAddView(View):
    methods = ['GET', 'POST']
    def dispatch_request(self):
        form = WalletForm(request.form)
        if request.method == 'POST' and form.validate():
            newwallet = Wallet(**form.data)
            session.add(newwallet)
            session.commit()
            flash("%s: Wallet added" % newwallet.label)
            return redirect(url_for("wallet.wallet_list"))
        return render_template("wallet/wallet/add.html", form=form)


class WalletDetailBase(View):
    def dispatch_request(self, id):
        self.wallet = session.query(Wallet).get(id)
        if not self.wallet:
            abort(404)


class WalletEditView(WalletDetailBase):
    methods = ['GET', 'POST']
    def dispatch_request(self, id):
        super(WalletEditView, self).dispatch_request(id)
        form = WalletForm(request.form, self.wallet)
        if request.method == 'POST' and form.validate():
            form.populate_obj(self.wallet)
            session.commit()
            flash(u"%s: Wallet updated" % self.wallet.label, 'info')
            return redirect(url_for("wallet.wallet_list"))
        return render_template("wallet/wallet/edit.html", wallet=self.wallet,
                               form=form)


class WalletConnectedBase(WalletDetailBase):
    """
    This base adds the bitcoin connection to the view. Needed for all views
    that use the API.
    """
    def dispatch_request(self, id):
        super(WalletConnectedBase, self).dispatch_request(id)
        self.conn = connection.get_connection(self.wallet)


class WalletDetailView(WalletConnectedBase):
    def dispatch_request(self, id):
        super(WalletDetailView, self).dispatch_request(id)
        data = {}
        data['info'] = self.conn.getinfo()
        data['accounts'] = get_accounts(self.conn, getbalance=True)
        data['global_send'] = int(get_setting('global_send', 1))
        data['forms'] = {}
        data['forms']['account'] = CreateAccountForm()
        data['forms']['txfee'] = SetTXFeeForm()
        form = CreateAccountForm(request.form)
        return render_template("wallet/wallet/detail.html", wallet=self.wallet,
                               data=data, form=form)


class WalletTransactionsView(WalletConnectedBase):
    def dispatch_request(self, id):
        super(WalletTransactionsView, self).dispatch_request(id)
        transactions = self.conn.listtransactions()
        return render_template("wallet/wallet/transactions.html",
                                     wallet=self.wallet, transactions=transactions)


class WalletReceivedView(WalletConnectedBase):
    def dispatch_request(self, id):
        super(WalletReceivedView, self).dispatch_request(id)
        data = {}
        data['receivedbyaddress'] = self.conn.listreceivedbyaddress()
        data['receivedbyaccount'] = self.conn.listreceivedbyaccount()
        return render_template("wallet/wallet/received.html", wallet=self.wallet,
                               data=data)


class WalletGroupingsView(WalletConnectedBase):
    def dispatch_request(self, id):
        super(WalletGroupingsView, self).dispatch_request(id)
        try:
            groupings = self.conn.listaddressgroupings()
        except AttributeError:  # pragma: no cover
            flash(u"Your bitcoinrpc version doesn't support this function",
                  'error')
            return redirect(url_for('wallet.wallet_detail', id=self.wallet.id))
        return render_template("wallet/wallet/addressgroupings.html", wallet=self.wallet,
                               groupings=groupings)


class WalletPeersView(WalletConnectedBase):
    def dispatch_request(self, id):
        super(WalletPeersView, self).dispatch_request(id)
        peers = self.conn.getpeerinfo()
        return render_template("wallet/wallet/peers.html", wallet=self.wallet,
                               peers=peers)


class WalletMoveView(WalletConnectedBase):
    methods=['GET', 'POST']
    def dispatch_request(self, id):
        super(WalletMoveView, self).dispatch_request(id)
        form = AccountMoveForm(request.form)
        choices = get_accounts(self.conn, getchoice=True)
        form.fromaccount.choices = choices
        form.toaccount.choices = choices
        accounts = get_accounts(self.conn, getbalance=True)
        fromaccount = urllib.unquote_plus(form.data['fromaccount'])
        toaccount = urllib.unquote_plus(form.data['toaccount'])
        fromaccount = real_format(fromaccount)
        toaccount = real_format(toaccount)
        if request.method == 'POST' and form.validate():
            amount = strtofloat(form.data['amount'])
            self.conn.move(
                fromaccount,
                toaccount,
                amount,
                int(get_setting('minconf', 6)),
                form.data['comment'],
            )
            flash(u"%f coins moved from %s to %s" % (amount,
                  human_format(fromaccount), human_format(toaccount)),
                  'success')
            return redirect(url_for('wallet.wallet_detail', id=id))
        return render_template("wallet/wallet/move.html", wallet=self.wallet,
                               form=form, accounts=accounts)


class WalletUnlockedBase(WalletConnectedBase):
    """
    Display a warning if the wallet is locked
    """
    def dispatch_request(self, id):
        super(WalletUnlockedBase, self).dispatch_request(id)
        try:
            unlocked = self.conn.getinfo().unlocked_until
            if not unlocked:
                url = url_for('wallet.wallet_unlock', id=self.wallet.id)
                flash('Wallet is currently locked. <a href="%s">Unlock</a>' % url,
                      "warning")
        except AttributeError:
            #  Wallet is not encrypted
            pass


class WalletSendView(WalletUnlockedBase):
    methods=['GET', 'POST']
    def dispatch_request(self, id):
        super(WalletSendView, self).dispatch_request(id)
        form = SendForm(request.form)
        balance = self.conn.getbalance()
        if request.method == 'POST' and form.validate():
            amount = strtofloat(form.data['amount'])
            txid = self.conn.sendtoaddress(
                form.toaddress.data,
                amount,
                form.comment.data,
                form.to.data
            )
            flash(u"%f coins sent to %s" % (amount, form.toaddress.data),
                  'success')
            return redirect(url_for("wallet.tx_detail", id=id, txid=txid))
        return render_template('wallet/wallet/send.html', wallet=self.wallet,
                               form=form, balance=balance)


class WalletDeleteView(WalletDetailBase):
    methods=['POST']
    def dispatch_request(self, id):
        super(WalletDeleteView, self).dispatch_request(id)
        session.delete(self.wallet)
        session.commit()
        flash(u"%s: Wallet deleted" % self.wallet.label, 'success')
        return redirect(url_for("wallet.wallet_list"))


class WalletStopView(WalletConnectedBase):
    methods=['POST']
    def dispatch_request(self, id):
        super(WalletStopView, self).dispatch_request(id)
        self.conn.stop()
        flash(u"%s: Node stopped" % self.wallet.label, 'success')
        return redirect(url_for("wallet.wallet_list"))


class WalletHelpView(WalletConnectedBase):
    def dispatch_request(self, id):
        super(WalletHelpView, self).dispatch_request(id)
        implemented = (
            'dumpprivkey',
            'encryptwallet',
            'getaccount',
            'getaccountaddress',
            'getaddressesbyaccount',
            'getbalance',
            'getblock',
            'getblockcount',
            'getinfo',
            'getmininginfo',
            'getnewaddress',
            'getpeerinfo',
            'getreceivedbyaddress',
            'gettransaction',
            'help',
            'listaccounts',
            'listaddressgroupings',
            'listreceivedbyaccount',
            'listreceivedbyaddress',
            'listtransactions',
            'move',
            'sendfrom',
            'sendtoaddress',
            'signmessage',
            'stop',
            'walletlock',
            'walletpassphrase',
        )
        interested = (
            'keypoolrefill',
            'listunspent',
            'sendmany',
            'sendtoname',
            'setaccount',
            'setgenerate',
            'setmininput',
            'settxfee',
            'validateaddress',
            'verifymessage',
            'walletpassphrasechange',
        )
        ignored = (
            'backupwallet',
            'getblocknumber',
            'getconnectioncount',
            'getdifficulty',
            'getgenerate',
            'gethashespersec',
            'getreceivedbyaccount',
            'getwork',
            'name_clean',
            'name_debug',
            'name_debug1',
            'name_filter',
            'name_firstupdate',
            'name_history',
            'name_list',
            'name_new',
            'name_scan',
            'name_show',
            'name_update',
        )
        # I think this is all mining stuff...
        #getwork
        #getmemorypool
        #buildmerkletree
        #deletetransaction
        #getauxblock
        #getblockbycount
        #getblockbyhash
        #getworkaux
        resp = self.conn.help()
        data = {
            'help': [],
            'done': 0,
            'len': 0,
            'implemented': implemented,
            'ignored': ignored,
            'interested': interested,
            'unknown': [],
        }
        lines = sorted(resp.split("\n"))
        for line in lines:
            command = line.split(' ')[0]
            if command in implemented:
                data['done'] += 1
            data['help'].append((command, line))
        # Make list of commands the node doesn't document
        for command in implemented:
            unknown = True
            for cmd, val in data['help']:
                if command == cmd:
                    unknown = False
                    break
            if unknown:
                data['unknown'].append(command)
        data['len'] = len(data['help'])
        data['additional'] = len(implemented) - data['done']
        return render_template('wallet/wallet/help.html', wallet=self.wallet,
                               data=data)


class WalletMiningInfoView(WalletConnectedBase):
    def dispatch_request(self, id):
        super(WalletMiningInfoView, self).dispatch_request(id)
        data = self.conn.getmininginfo()
        return render_template('wallet/wallet/mininginfo.html',
                                                 wallet=self.wallet, data=data)


class WalletEncryptView(WalletConnectedBase):
    """
    This can't be tested as encrypting the wallet stops the daemon.
    """
    methods = ['GET', 'POST']
    def dispatch_request(self, id):  # pragma: no cover
        super(WalletEncryptView, self).dispatch_request(id)
        form = EncryptForm(request.form)
        if request.method == 'POST' and form.validate():
            if form.passphrase.data == form.confirm.data:
                ret = self.conn.encryptwallet(form.passphrase.data)
                flash(ret, 'success')
                # The daemon apparently tries to restart, but this didn't
                # work in my testing, so redirect to wallet_list
                return redirect(url_for("wallet.wallet_list"))
            else:
                flash("Passphrases don't match", "error")
        return render_template('wallet/wallet/encrypt.html', wallet=self.wallet,
                               form=form)


class WalletUnlockView(WalletConnectedBase):
    """
    TODO should have an OTP validator for the form...
    """
    methods = ['GET', 'POST']
    def dispatch_request(self, id):
        super(WalletUnlockView, self).dispatch_request(id)
        otpsetting = session.query(Setting).get('otpsecret')
        if otpsetting:
            form = OTPUnlockForm(request.form)
            secret = otpsetting.value
            otp_valid = otp.valid_totp(token=form.otp.data, secret=secret)
        else:
            form = UnlockForm(request.form)
            otp_valid = True
        if request.method == 'POST' and form.validate() and otp_valid:
            flash("OTP valid", "success")
            try:
                ret = self.conn.walletpassphrase(form.passphrase.data,
                                                             form.timeout.data)
                flash('Wallet unlocked', 'success')
                return redirect(url_for('wallet.wallet_detail',
                                                            id=self.wallet.id))
            except WalletPassphraseIncorrect:
                flash('Passphrase incorrect', 'error')
            except WalletAlreadyUnlocked:
                flash('Wallet already unlocked', 'error')
        elif request.method == 'POST' and form.validate() and not otp_valid:
            flash("OTP invalid", "error")
        return render_template('wallet/wallet/unlock.html', wallet=self.wallet,
                               form=form)


class WalletLockView(WalletConnectedBase):
    methods = ['POST']
    def dispatch_request(self, id):
        super(WalletLockView, self).dispatch_request(id)
        self.conn.walletlock()
        flash('Wallet locked', 'success')
        return redirect(url_for('wallet.wallet_detail', id=self.wallet.id))


class TXDetailView(WalletConnectedBase):
    def dispatch_request(self, id, txid):
        super(TXDetailView, self).dispatch_request(id)
        tx = self.conn.gettransaction(txid)
        return render_template("wallet/transaction_detail.html",
                               wallet=self.wallet, tx=tx)


class BlockDetailView(WalletConnectedBase):
    def dispatch_request(self, id, block):
        super(BlockDetailView, self).dispatch_request(id)
        block = self.conn.getblock(block)
        return render_template("wallet/block_detail.html", wallet=self.wallet,
                               block=block)


class WalletSetTXFeeView(WalletConnectedBase):
    methods = ['POST']
    def dispatch_request(self, id):
        super(WalletSetTXFeeView, self).dispatch_request(id)
        form = SetTXFeeForm(request.form)
        if form.validate():
            self.conn.settxfee(float(form.data['fee']))
            flash(u"Transaction fee set to %f" % form.data['fee'],
                  'success')
        else:
            self.conn.settxfee(0)
            flash(u"Transaction fee set to 0", 'error')
        return redirect(url_for("wallet.wallet_detail", id=id))
