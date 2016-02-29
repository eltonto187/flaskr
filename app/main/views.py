from datetime import datetime
from flask import render_template, redirect, session, url_for, flash, \
    current_app

from . import main
from .. import db
from .forms import NameForm
from ..models import User
from ..email import send_email

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if current_app.config['FLASKR_ADMIN']:
                send_email(current_app.config['FLASKR_ADMIN'], '新用户',
                           'mail/new_user', user=user)
        else:
            session['known'] = True
        if old_name is not None and old_name != form.name.data:
            flash('看起来你已经改变了你输入的名字')
        session['name'] = form.name.data
        session['email'] = form.email.data
        return redirect(url_for('.index'))
    return render_template('index.html', name=session.get('name'),
        email=session.get('email'), form=form,
        known=session.get('known', False),
        current_time=datetime.utcnow())

@main.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

