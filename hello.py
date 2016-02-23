from flask import Flask
from flask.ext.script import Manager

app = Flask(__name__)
manager = Manager(app)

@app.route('/')
def index():
    return '<h1>Hello Flask</h1>'

@app.route('/user/<name>')
def user(name):
    return '<h1>欢迎来到%s的博客!</h1>' % name

if __name__ == '__main__':
    manager.run()
