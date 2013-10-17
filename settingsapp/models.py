from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.hybrid import hybrid_property

from flaskwallet import Base
from flaskwallet import cipher


class Setting(Base):
    __tablename__ = 'settings'
    # I'm really not sure why the imports create circular imports in this app
    # but not the wallet app...create circular imports in this app
    __table_args__ = {
        'extend_existing': True,
    }
    name = Column(String(50), primary_key=True)
    value = Column(String(255))

    def __init__(self, name, value_decrypted):
        self.name = name
        self.value = cipher.encrypt(str(value_decrypted))

    def __repr__(self):
        return '<Setting: %s %s>' % (self.name, repr(self.value))

    @hybrid_property
    def value_decrypted(self):
        return cipher.decrypt(self.value)

    @value_decrypted.setter
    def set_value_encrypted(self, value):
        self.value = cipher.encrypt(value)
