from flaskwallet import app
from flaskwallet import session
from flaskwallet import init_db
from otpapp.app import otpapp
from settingsapp.app import settingsapp
from walletapp.app import walletapp

try:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = True
except:
    toolbar = False


app.config.from_envvar('FLASK_ADMIN', silent=True)
app.register_blueprint(otpapp)
app.register_blueprint(settingsapp)
app.register_blueprint(walletapp)
init_db()

if not app.debug and 'FLASK_ADMIN' in app.config:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler(
        '127.0.0.1',
        'server-error@example.com',
        app.config['FLASK_ADMIN'],
        'Your application Failed'
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

# Init, teardown
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

if __name__ == '__main__':
    #if toolbar:
    #    toolbar = DebugToolbarExtension(app)
    app.run(host=app.config['INTERFACE'], port=int(app.config['PORT']))
