from wtforms import Form
from wtforms import TextField
from wtforms import TextAreaField
from wtforms import validators


class SignForm(Form):
    address = TextField(u'Address', validators=[validators.required()])
    message = TextAreaField(u'Message', validators=[validators.required()])
