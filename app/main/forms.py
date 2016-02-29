from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Email

class NameForm(Form):
    name = StringField('你的名字', validators=[Required()])
    email = StringField('你的电子邮箱', validators=[Email()])
    submit = SubmitField('提交')

