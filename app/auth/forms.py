from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1,64),
                                            Email()])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1,64),
                                            Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1,64), Regexp(
            '^[A-Za-z\u4e00-\u9fa5][A-Za-z0-9\u4e00-\u9fa5._]*$', 0,
            '用户名必须以中文或字母开头,'
            '只能包含中文，字母，数字，点或下划线')])
    password = PasswordField('密码', validators=[
        Required(), EqualTo('password2', message='密码必段匹配')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被使用')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='密码必须匹配')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('提交')


class PasswordResetRequestForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                            Email()])
    submit = SubmitField('重设密码')


class PasswordResetForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                            Email()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password1', message='输入的密码必须相同')])
    password1 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('重设密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('未知邮箱地址')


class ChangeEmailForm(Form):
    email = StringField('新邮箱', validators=[Required(), Length(1, 64),
                                              Email()])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('修改邮箱')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')
