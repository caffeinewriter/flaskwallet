import urllib
from StringIO import StringIO
from base64 import b32encode

from flask import abort
from flask import flash
from flask import make_response
from flask import render_template
from flask import redirect
from flask import request
from flask import send_file
from flask import url_for
from flask.views import View

from flaskwallet import session
from settingsapp.models import Setting

import qrcode
from Crypto.Random import get_random_bytes


class OTPSetupView(View):
    def dispatch_request(self):
        return render_template('otp/setup.html')


class QRView(View):
    """
    http://www.brool.com/index.php/using-google-authenticator-for-your-website
    """
    def dispatch_request(self):
        secret = self.get_secret()
        if secret:
            return send_file(self.get_qr(secret), mimetype='image/png')
        else:
            abort(404)

    def get_secret(self):
        """
        Cryptographically-secure 10 byte random key, presented to the user as
        a base32 16-character string.
        """
        name = 'otpsecret'
        setting = session.query(Setting).get(name)
        if setting:
            ret = False
        else:
            secret = get_random_bytes(10)
            code = b32encode(secret)
            setting = Setting(name, code)
            session.add(setting)
            session.commit()
            ret = code
        return ret

    def get_qr(self, secret):
        img_io = StringIO()
        qr = self.build_qr_image(secret)
        qr.save(img_io, 'PNG')
        img_io.seek(0)
        return img_io

    def build_qr_image(self, secret):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.get_authenticator_url(secret))
        qr.make(fit=True)
        return qr.make_image()

    def get_authenticator_url(self, secret):
        """
        https://code.google.com/p/google-authenticator/wiki/KeyUriFormat
        """
        user = 'Flaskwallet'  # Yeah, we have no user model
        data = 'otpauth://totp/%s?secret=%s&issuer=%s' % (user, secret,
                                                                'Flaskwallet')
        return data
