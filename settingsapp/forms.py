from wtforms import validators
from wtforms import Form
from wtforms import TextField
from wtforms import IntegerField
from wtforms import validators


class EditForm(Form):
    name = TextField(u'Name', validators=[validators.required()])
    value_decrypted = TextField(u'Value', validators=[validators.optional()])
