import random
import urllib

from flaskwallet import app
from flaskwallet import session
from settingsapp.helpers import get_setting


def real_format(account):
    if account == '__DEFAULT_ACCOUNT__':
        account = ''
    return account

def human_format(account):
    if account == '':
        account = '__DEFAULT_ACCOUNT__'
    return account

def get_accounts(conn, getbalance=False, getchoice=False):
    """
    Returns the list of accounts for a wallet
    """
    if getbalance:
        ret = conn.listaccounts(as_dict=True)
    elif getchoice:
        accounts = conn.listaccounts()
        ret = []
        for account in accounts:
            account = human_format(account)
            ret.append((urllib.quote_plus(str(account)), account))
    return ret

def strtofloat(value):
    """
    This is used to convert form inputs into floats.
    Heh.. why exactly is this a function?
    """
    return float(value)

def get_cachetime():
    """
    TODO: configurable
    """
    cachetime_min = int(get_setting('cachetime_min', 5))
    cachetime_max = int(get_setting('cachetime_max', 15))
    return random.randint(cachetime_min, cachetime_max)

def get_coin_choices():
    ret = []
    for key, data in app.config['COINS'].iteritems():
        ret.append((key, '%s (%s)' % (key, data['name'])))
    ret = sorted(ret, key=lambda tup: tup[0])
    return ret
