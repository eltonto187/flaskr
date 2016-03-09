from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, \
    BooleanField, SelectField
from wtforms.validators import Required, Email, Length, Regexp
from wtforms import ValidationError
from ..models import Role, User


class EditProfileForm(Form):
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')


class EditProfileAdminForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                            Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1, 64), Regexp(
            '^[A-Za-z\u4e00-\u9fa5][A-Za-z0-9\u4e00-\u9fa5._]*$', 0,
            '用户名必须以中文或字母开头,'
            '只能包含中文，字母，数字，点或下划线')])
    confirmed = BooleanField('通过确认')
    role = SelectField('角色', coerce=int)
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                            for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被使用')


class PostForm(Form):
    body = TextAreaField('随手写下你的心情', validators=[Required()])
    submit = SubmitField('提交')
