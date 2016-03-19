import re
import json
import unittest
from base64 import b64encode
from flask import url_for
from app import create_app, db
from app.models import User, Role, Comment, Post


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self):
        response = self.client.get(
            '/wrong/url',
            headers=self.get_api_headers('email', 'password'))
        self.assertTrue(response.status_code == 404)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_response['error'] == '找不到')

    def test_no_auth(self):
        response = self.client.get(url_for('api.get_posts'),
                                   content_type='application/json')
        self.assertTrue(response.status_code == 200)

    def test_bad_auth(self):
        # 添加一个用户
        r = Role.query.filter_by(name='用户').first()
        self.assertIsNotNone(r)
        u = User(email='bin@example.com', password='cat', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # 用错误的密码进行身份认证
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('bin@example.com', 'dog'))
        self.assertTrue(response.status_code == 401)

    def test_token_auth(self):
        # 添加一个用户
        r = Role.query.filter_by(name='用户').first()
        self.assertIsNotNone(r)
        u = User(email='bin@example.com', password='cat', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # 用错误令牌进行请求
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('bad-token', ''))
        self.assertTrue(response.status_code == 401)

        # 获取一个令牌
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('bin@example.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # 用令牌访问
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers(token, ''))
        self.assertTrue(response.status_code == 200)

    def test_anonymous(self):
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('', ''))
        self.assertTrue(response.status_code == 200)

    def test_unconfirmed_account(self):
        # 添加一个未认证用户
        r = Role.query.filter_by(name='用户').first()
        self.assertIsNotNone(r)
        u = User(email='bin@example.com', password='cat', confirmed=False,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # 用未认证用户获取文章列表
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('bin@example.com', 'cat'))
        self.assertTrue(response.status_code == 403)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_response['message'] == '未经验证的账户')

    def test_posts(self):
        # 添加一个用户
        r = Role.query.filter_by(name='用户').first()
        self.assertIsNotNone(r)
        u = User(email='bin@example.com', password='cat', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # 发表一篇空文章
        response = self.client.post(
            url_for('api.new_post'),
            headers=self.get_api_headers('bin@example.com', 'cat'),
            data=json.dumps({'body': ''}))
        self.assertTrue(response.status_code == 400)

        # 发布一篇文章
        response = self.client.post(
            url_for('api.new_post'),
            headers=self.get_api_headers('bin@example.com', 'cat'),
            data=json.dumps({'body': '新发表的*博客*文章'}))
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # 获取刚刚发表的文章
        response = self.client.get(
            url,
            headers=self.get_api_headers('bin@example.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['body'] == '新发表的*博客*文章')
        self.assertTrue(json_response['body_html'] ==
                        '<p>新发表的<em>博客</em>文章</p>')
        json_post = json_response

        # 从用户获取文章
        response = self.client.get(
            url_for('api.get_user_posts', id=u.id),
            headers=self.get_api_headers('bin@example.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('posts'))
        self.assertTrue(json_response.get('count', 0) == 1)
        self.assertTrue(json_response['posts'][0] == json_post)

        # 获取用户所关注用户的文章(存在自关注)
        response = self.client.get(
            url_for('api.get_user_followed_posts', id=u.id),
            headers=self.get_api_headers('bin@example.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('posts'))
        self.assertTrue(json_response.get('count', 0) == 1)
        self.assertTrue(json_response['posts'][0] == json_post)

        # 编辑文章(更新)
        response = self.client.put(
            url,
            headers=self.get_api_headers('bin@example.com', 'cat'),
            data=json.dumps({'body':'更新文章'}))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['body'] == '更新文章')
        self.assertTrue(json_response['body_html'] == '<p>更新文章</p>')

    def test_users(self):
        # 添加两个用户
        r = Role.query.filter_by(name='用户').first()
        self.assertIsNotNone(r)
        u1 = User(email='bin@example.com', username='bin',
                  password='cat', confirmed=True, role=r)
        u2 = User(email='zhang@example.com', username='zhang',
                  password='dog', confirmed=True, role=r)
        db.session.add_all([u1, u2])
        db.session.commit()

        # 获取用户
        response = self.client.get(
            url_for('api.get_user', id=u1.id),
            headers=self.get_api_headers('zhang@example.com', 'dog'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_response['username'] == 'bin')
        response = self.client.get(
            url_for('api.get_user', id=u2.id),
            headers=self.get_api_headers('bin@example.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_response['username'] == 'zhang')

    def test_comments(self):
        # 添加两个用户
        r = Role.query.filter_by(name='用户').first()
        self.assertIsNotNone(r)
        u1 = User(email='bin@example.com', username='bin',
                  password='cat', confirmed=True, role=r)
        u2 = User(email='zhang@example.com', username='zhang',
                  password='dog', confirmed=True, role=r)
        db.session.add_all([u1, u2])
        db.session.commit()

        # 添加一篇文章
        post = Post(body='测试API评论功能', author=u1)
        db.session.add(post)
        db.session.commit()

        # 写一条评论
        response = self.client.post(
            url_for('api.new_post_comment', id=post.id),
            headers=self.get_api_headers('zhang@example.com', 'dog'),
            data=json.dumps({'body': '好[文章](http://example.com)!'}))
        self.assertTrue(response.status_code == 201)
        json_response = json.loads(response.get_data(as_text=True))
        url = response.headers.get('Location')
        self.assertIsNotNone(url)
        self.assertTrue(json_response['body'] ==
                        '好[文章](http://example.com)!')
        self.assertTrue(
            re.sub('<.*?>', '', json_response['body_html']) == '好文章!')

        # 获取刚发布的评论
        response = self.client.get(
            url,
            headers=self.get_api_headers('bin@example.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['body'] ==
                        '好[文章](http://example.com)!')

        # 添加另一条评论
        comment = Comment(body='另一评论', author=u1, post=post)
        db.session.add(comment)
        db.session.commit()

        # 从文章获取刚刚添加的俩条评论
        response = self.client.get(
            url_for('api.get_post_comments', id=post.id),
            headers=self.get_api_headers('zhang@example.com', 'dog'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('comments'))
        self.assertTrue(json_response.get('count', 0) == 2)

        # 获取所有评论
        response =self.client.get(
            url_for('api.get_comments'),
            headers=self.get_api_headers('bin@example.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('comments'))
        self.assertTrue(json_response.get('count', 0) == 2)
