from flask import Blueprint

from otpapp.views import OTPSetupView
from otpapp.views import QRView


otpapp = Blueprint(
    'otp',
    __name__,
    url_prefix='/otp',
    template_folder='templates/',
)

otpapp.add_url_rule(
    '/setup/',
    view_func=OTPSetupView.as_view('setup')
)
otpapp.add_url_rule(
    '/qr.png',
    view_func=QRView.as_view('qr')
)
