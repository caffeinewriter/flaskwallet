import urllib

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy import event
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

from flaskwallet import Base
from flaskwallet import cipher
from walletapp.helpers import human_format


class Wallet(Base):
    __tablename__ = 'wallets'
    __table_args__ = (
        UniqueConstraint(u'rpchost', u'rpcport'),
    )
    id = Column(Integer, primary_key=True)
    label = Column(String(50))
    rpcuser = Column(String(255))
    rpcpass = Column(String(255))
    rpchost = Column(String(255))
    rpcport = Column(Integer)
    rpchttps = Column(Boolean)
    testnet = Column(Boolean)
    coin = Column(String(50))

    def __init__(self, label, rpcuser_decrypted, rpcpass_decrypted, rpchost, rpcport=8883, rpchttps=False, testnet=False, coin='BTC'):
        self.label = label
        self.rpcuser = cipher.encrypt(rpcuser_decrypted)
        self.rpcpass = cipher.encrypt(rpcpass_decrypted)
        self.rpchost = rpchost
        self.rpcport = rpcport
        self.rpchttps = rpchttps
        self.testnet = testnet
        self.coin = coin

    def __repr__(self):
        if self.id:
            ret = '<Wallet: %s %s:%d>' % (self.label, self.rpchost, self.rpcport)
        else:
            ret = '<Wallet, not saved>'
        return ret

    @hybrid_property
    def rpcuser_decrypted(self):
        return cipher.decrypt(self.rpcuser)

    @rpcuser_decrypted.setter
    def set_rpcuser_encrypted(self, value):
        self.rpcuser = cipher.encrypt(value)

    @hybrid_property
    def rpcpass_decrypted(self):
        return cipher.decrypt(self.rpcpass)

    @rpcpass_decrypted.setter
    def set_rpcpass_encrypted(self, value):
        self.rpcpass = cipher.encrypt(value)

    #@validates('rpcuser')
    #def validate_rpcport(self, key, rpcport):
    #    assert type(rpcport) == int
    #    assert rpcport >= 1
    #    assert rpcport <= 65535
    #    return rpcuser
