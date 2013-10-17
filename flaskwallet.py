import os

from flask import Flask
from flask import render_template

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.contrib.cache import SimpleCache
from cipher import AESCipher


# TODO cache should be easily configurable
cache = SimpleCache()

app = Flask(__name__)
app.config.from_object('config')

cipher = AESCipher(app.config['SECRET_KEY'])

if 'DATABASE' in os.environ:  # For tests...
    app.config['DATABASE'] = os.environ['DATABASE']

def rst2html(path):
    try:
        from docutils.core import publish_parts
        f = open(path, 'r')
        readme = publish_parts(
            f.read(),
            writer_name='html',
        )['html_body']
        f.close()
    except ImportError:  # pragma: no cover
        readme = False
    return readme

@app.route("/")
def root():
    readme = rst2html('doc/index.rst')
    readme += rst2html('doc/Changelog.rst')
    readme += rst2html('doc/Todo.rst')
    return render_template('index.html', readme=readme)

engine = create_engine(app.config['DATABASE'], convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = session.query_property()


def init_db():
    from walletapp.models import Wallet
    from settingsapp.models import Setting
    Base.metadata.create_all(bind=engine)
