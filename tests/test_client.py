import re
import unittest
from flask import url_for
from app import create_app, db
from app.models import User, Role


class FalskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue('Stranger' in response.get_data(as_text=True))

    def test_register_and_login(self):
        # 注册新账户
        response = self.client.post(url_for('auth.register'), data={
            'email': 'bin@example.com',
            'username': 'bin',
            'password': 'cat',
            'password2': 'cat'
        })
        self.assertTrue(response.status_code == 302)

        # 使用新注册的账户登录
        response = self.client.post(url_for('auth.login'), data={
            'email': 'bin@example.com',
            'password': 'cat'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(re.search('你好,\s+bin!', data))
        self.assertTrue('你还没有确认你的账户' in data)

        # 发送确认令牌并使用令牌登录
        # 测试中处理电子邮件很复杂。这里采用直接重新生成新令牌方法
        # (也可以通过解析邮件正文来提取令牌)
        user = User.query.filter_by(email='bin@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('你已经激活你的账户，谢谢！' in data)

        # 退出
        response = self.client.get(url_for('auth.logout'),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('你已经登出' in data)
