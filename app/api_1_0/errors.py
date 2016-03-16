from flask import jsonify
from app.exceptions import ValidationError
from . import api


def bad_request(message):
    response = jsonify({'error': '坏请求', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': '未授权', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': '禁止', 'message': message})
    response.status_code = 403
    return response


def method_not_allowed(message):
    response = jsonify({'error': '不允许使用的方法', 'message': message})
    response.status_code = 405
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
