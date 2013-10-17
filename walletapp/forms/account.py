from wtforms import DecimalField
from wtforms import Form
from wtforms import SelectField
from wtforms import TextField
from wtforms import validators


class CreateAccountForm(Form):
    label = TextField(u'Label', validators=[validators.required()])


class AccountMoveForm(Form):
    fromaccount = SelectField(u'From account', choices=[],
                              validators=[validators.required()])
    toaccount = SelectField(u'To account', choices=[],
                            validators=[validators.required()])
    amount = DecimalField(u'Amount', validators=[validators.required()])
    comment = TextField(u'Comment')
