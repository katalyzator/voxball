from authe.models import MainUser
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client
from django.utils import timezone
from models import Article, PollTemplate, ArticlePollEntry
from polls.models import Poll, Category, PollAnswer, PollChoice
from utils import codes, token
from utils import password
from utils.time_utils import get_timestamp_in_milli
import json

User = get_user_model()
c = Client()

TEST_USERNAME_MODERATOR = u'test@test.ru'
TEST_USERNAME = u'test_moderator@test.ru'
TEST_PASSWORD = u'testpass'
AUTH_TOKEN_HEADER = "Auth-Token"
STATUS_OK = 200
CODE = "code"
TEST_ARTICLE_URL = u'https://tengrinews.kz/'


class ModeratorsTestCase(TestCase):
    def common_test_ok(self, response):
        self.assertEqual(response.status_code, STATUS_OK)
        self.assertEqual(response.json()[CODE], codes.OK)

    def common_test(self, response, status_code, code):
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.json()[CODE], code)

    def common_test_without_json(self, response, status_code):
        self.assertEqual(response.status_code, status_code)

    def create_user(self):
        user = MainUser.objects.create_user(username=TEST_USERNAME,
                                            password=TEST_PASSWORD)
        return user

    def get_token(self):
        user = MainUser.objects.create_superuser(username=TEST_USERNAME_MODERATOR,
                                                 password=TEST_PASSWORD)

        return token.create_token(user)

    def get_token_and_user(self):
        user = MainUser.objects.create_superuser(username=TEST_USERNAME_MODERATOR,
                                                 password=TEST_PASSWORD)
        user_info = {}
        user_info['token'] = token.create_token(user)
        user_info['user'] = user
        return user_info

    def test_poll_delete_ok(self):
        auth_token = self.get_token()
        user = self.create_user()

        poll, _ = Poll.objects.get_or_create(user=user, title="Test title")

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "poll_id": poll.id
        }
        response = c.post('/api/moderators/polls/delete/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_poll_feed_ok(self):
        auth_token = self.get_token()

        params = {
            AUTH_TOKEN_HEADER: auth_token
        }
        response = c.post('/api/moderators/polls/feed/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_get_polls_related_to_article_ok(self):
        auth_token = self.get_token()

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "article_url": TEST_ARTICLE_URL
        }
        response = c.post('/api/moderators/polls/feed/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_get_articles_ok(self):
        auth_token = self.get_token()

        params = {
            AUTH_TOKEN_HEADER: auth_token
        }
        response = c.post('/api/moderators/articles/get/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_delete_article_ok(self):
        auth_token = self.get_token()

        article, _ = Article.objects.get_or_create(article_url=TEST_ARTICLE_URL)

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "article_id": article.id
        }
        response = c.post('/api/moderators/articles/delete/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_add_article_ok(self):
        auth_token = self.get_token()
        user = self.create_user()

        poll = Poll.objects.create(user=user, title="Test title",
                                   is_active=True)

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "article_url": TEST_ARTICLE_URL,
            "poll_ids[]": [poll.id]
        }
        response = c.post('/api/moderators/articles/add/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_add_article_invalid_params(self):
        auth_token = self.get_token()

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "article_url": TEST_ARTICLE_URL,
            "poll_ids[]": '[1]'
        }
        response = c.post('/api/moderators/articles/add/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.INVALID_PARAMETERS)

    def test_add_article_invalid_params1(self):
        auth_token = self.get_token()

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "article_url": TEST_ARTICLE_URL,
            "poll_ids[]": [1]
        }
        response = c.post('/api/moderators/articles/add/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.POLL_COUNT_DONT_MATCH)

    def test_add_article_invalid_url(self):
        auth_token = self.get_token()
        user = self.create_user()

        poll = Poll.objects.create(user=user, title="Test title",
                                   is_active=True)

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "article_url": 'abcd',
            "poll_ids[]": [poll.id]
        }
        response = c.post('/api/moderators/articles/add/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.INVALID_URL)

    def test_add_article_already_exists(self):
        auth_token = self.get_token()
        user = self.create_user()

        poll = Poll.objects.create(user=user, title="Test title",
                                   is_active=True)
        Article.objects.create(article_url=TEST_ARTICLE_URL)

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "article_url": TEST_ARTICLE_URL,
            "poll_ids[]": [poll.id]
        }
        response = c.post('/api/moderators/articles/add/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.ALREADY_EXISTS)

    def test_update_article_ok(self):
        auth_token = self.get_token()
        user = self.create_user()

        poll = Poll.objects.create(user=user, title="Test title",
                                   is_active=True)
        article = Article.objects.create(article_url=TEST_ARTICLE_URL)

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "article_id": article.id,
            "poll_ids[]": [poll.id]
        }
        response = c.post('/api/moderators/articles/update/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_update_article_invalid_params(self):
        auth_token = self.get_token()

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "article_id": 1,
            "poll_ids[]": '[1]'
        }
        response = c.post('/api/moderators/articles/update/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.INVALID_PARAMETERS)

    def test_update_article_not_found(self):
        auth_token = self.get_token()

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "article_id": 1,
            "poll_ids[]": [1]
        }
        response = c.post('/api/moderators/articles/update/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.ARTICLE_NOT_FOUND)

    def test_get_polls_by_title_ok(self):
        auth_token = self.get_token()

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "poll_title": "Test title"
        }
        response = c.post('/api/moderators/polls/get_polls_by_title/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_create(self):
        auth_token = self.get_token()

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "title": "Test title",
            "poll_type": 1,
            "date_begin": get_timestamp_in_milli(),
            "date_end": get_timestamp_in_milli(),
            "sc_choices[]": ['{"value":"What is she?", "priority":"1"}',
                             '{"value":"What is he?", "priority":"2"}']
        }
        response = c.post('/api/moderators/template/create/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_create_categories_match(self):
        auth_token = self.get_token()

        category, _ = Category.objects.get_or_create(name="soccer")

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "title": "Test title",
            "poll_type": 1,
            "date_begin": get_timestamp_in_milli(),
            "date_end": get_timestamp_in_milli(),
            "sc_choices[]": ['{"value":"What is she?", "priority":"1"}',
                             '{"value":"What is he?", "priority":"2"}'],
            "category_ids[]": [category.id, 2]
        }
        response = c.post('/api/moderators/template/create/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.CATEGORIES_DOESNT_MATCH)

    def test_create_invalid_dates(self):
        auth_token = self.get_token()

        params = {
            AUTH_TOKEN_HEADER: auth_token,
            "title": "Test title",
            "poll_type": 3,
            "date_begin": get_timestamp_in_milli(),
            "date_end": get_timestamp_in_milli(),
            "sc_choices[]": ['{"value":"What is she?", "priority":"1"}',
                             '{"value":"What is he?", "priority":"2"}']
        }
        response = c.post('/api/moderators/template/create/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.INVALID_POLL_TYPE)

    def test_delete(self):
        user_info = self.get_token_and_user()

        poll, _ = PollTemplate.objects.get_or_create(user=user_info['user'],
                                                     id=1)

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            "poll_id": 1
        }
        response = c.post('/api/moderators/template/delete/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_read(self):
        user_info = self.get_token_and_user()

        poll, _ = PollTemplate.objects.get_or_create(id=1,
                                                     user=user_info['user'])

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            "poll_id": 1
        }
        response = c.post('/api/moderators/template/read/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_feed(self):
        auth_token = self.get_token()

        params = {
            AUTH_TOKEN_HEADER: auth_token
        }
        response = c.post('/api/moderators/template/feed/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_poll_approve_ok(self):
        user_info = self.get_token_and_user()

        poll, _ = Poll.objects.get_or_create(id=1, user=user_info['user'])

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'poll_id': 1,
            'status': 2
        }
        response = c.post('/api/moderators/polls/approve/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_poll_approve_not_found(self):
        user_info = self.get_token_and_user()

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'poll_id': 1,
            'status': 2
        }
        response = c.post('/api/moderators/polls/approve/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.POLL_NOT_FOUND)

    def test_poll_approve_invalid_status(self):
        user_info = self.get_token_and_user()

        Poll.objects.create(id=1, user=user_info['user'])

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'poll_id': 1,
            'status': 5
        }
        response = c.post('/api/moderators/polls/approve/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.INVALID_POLL_STATUS)

    def test_category_delete_ok(self):
        user_info = self.get_token_and_user()

        Category.objects.create(id=1)

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'category_id': 1
        }
        response = c.post('/api/moderators/category/delete/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_category_delete_not_found(self):
        user_info = self.get_token_and_user()

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'category_id': 1
        }
        response = c.post('/api/moderators/category/delete/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.CATEGORY_NOT_FOUND)

    def test_category_create_ok(self):
        user_info = self.get_token_and_user()

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'category_name': "soccer"
        }
        response = c.post('/api/moderators/category/create/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_category_create_not_found(self):
        user_info = self.get_token_and_user()

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'category_name': "soccer",
            'parent_id': 1
        }
        response = c.post('/api/moderators/category/create/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.CATEGORY_NOT_FOUND)

    def test_category_update_ok(self):
        user_info = self.get_token_and_user()

        Category.objects.create(id=1, name='soccer')
        Category.objects.create(id=2, name='sport')

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'category_id': 1,
            'category_name': 'football',
            'parent_id': 2
        }
        response = c.post('/api/moderators/category/update/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_category_update_invalid_parent(self):
        user_info = self.get_token_and_user()

        Category.objects.create(id=1, name='soccer')

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'category_id': 1,
            'category_name': 'football',
            'parent_id': 1
        }
        response = c.post('/api/moderators/category/update/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.SERVER_ERROR)

    def test_category_update_not_found(self):
        user_info = self.get_token_and_user()

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'category_id': 1
        }
        response = c.post('/api/moderators/category/update/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.CATEGORY_NOT_FOUND)

    def test_category_read_ok(self):
        user_info = self.get_token_and_user()

        Category.objects.create(id=1)

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'category_id': 1,
        }
        response = c.post('/api/moderators/category/read/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_category_read_not_found(self):
        user_info = self.get_token_and_user()

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'category_id': 1
        }
        response = c.post('/api/moderators/category/read/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.CATEGORY_NOT_FOUND)

    def test_get_articles_stat_ok(self):
        user_info = self.get_token_and_user()

        poll, _ = Poll.objects.get_or_create(id=1, user=user_info['user'])
        article, _ = Article.objects.get_or_create(id=1, article_url='https://tengrinews.kz/world_news/smi-soobschili-o-vzryive-okolo-aeroporta-v-londone-324449/')
        ArticlePollEntry.objects.create(poll=poll, article=article)

        params = {
            AUTH_TOKEN_HEADER: user_info['token'],
            'poll_id': 1,
        }
        response = c.post('/api/moderators/articles/statistics/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)
