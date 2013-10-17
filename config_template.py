DATABASE = 'sqlite:///flaskwallet.db'
SECRET_KEY = '<Check the readme>'
INTERFACE = '127.0.0.1'
PORT = 8000
DEBUG = True
COINS = {
    'BTC': {
        'name': 'Bitcoin',
        'altsymbol': ('XBT',),
    },
    'LTC': {
        'name': 'Litecoin',
    },
    'NMC': {
        'name': 'Namecoin',
        'features': ('namecoin',),
    },
    'XPM': {
        'name': 'Primecoin',
    },
    'FTC': {
        'name': 'Feathercoin',
    },
    'NVC': {
        'name': 'Novacoin',
    },
    'PPC': {
        'name': 'PPCoin',
    },
    'ZZZ': {
        'name': 'Unknown',
    },
}
