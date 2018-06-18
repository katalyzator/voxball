from authe.models import MainUser
from Cookie import SimpleCookie
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory
from django.test import TestCase
from models import Poll, PollChoice, PollAnswer, Category
from moderators.models import Article, ArticlePollEntry
from utils import codes, token
from utils.string_utils import json_list_from_string_list
from utils.time_utils import get_timestamp_in_milli
import json
import time

User = get_user_model()
c = Client()

TEST_USERNAME = u'test@test.ru'
TEST_PASSWORD = u'testpass'
TEST_ARTICLE_URL = u'https://tengrinews.kz/'

AUTH_TOKEN_HEADER = "Auth-Token"
STATUS_OK = 200
CODE = "code"


class PollCreateTestCase(TestCase):

    def common_test_ok(self, response):
        self.assertEqual(response.status_code, STATUS_OK)
        self.assertEqual(response.json()[CODE], codes.OK)

    def common_test(self, response, status_code, code):
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.json()[CODE], code)

    def get_token(self):
        user, _ = User.objects.get_or_create(username=TEST_USERNAME)
        user.set_password(TEST_PASSWORD)
        user.is_active = True
        user.save()
        self.token = token.create_token(user)
        return user

    def create_user(self):
        user = MainUser.objects.create_user(username=TEST_USERNAME,
                                            password=TEST_PASSWORD)
        return user

    def test_create(self):
        self.get_token()

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "title": "Test title",
            "poll_type": 1,
            "date_begin": get_timestamp_in_milli(),
            "date_end": get_timestamp_in_milli(),
            "sc_choices[]": ['{"value":"What is she?", "priority":"1"}',
                             '{"value":"What is he?", "priority":"2"}']
        }
        response = c.post('/api/polls/create/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_create_categories_match(self):
        self.get_token()

        category, _ = Category.objects.get_or_create(name="soccer")

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "title": "Test title",
            "poll_type": 1,
            "date_begin": get_timestamp_in_milli(),
            "date_end": get_timestamp_in_milli(),
            "sc_choices[]": ['{"value":"What is she?", "priority":"1"}',
                             '{"value":"What is he?", "priority":"2"}'],
            "category_ids[]": [category.id, 2]
        }
        response = c.post('/api/polls/create/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.CATEGORIES_DOESNT_MATCH)

    def test_create_invalid_dates(self):
        self.get_token()

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "title": "Test title",
            "poll_type": 3,
            "date_begin": get_timestamp_in_milli(),
            "date_end": get_timestamp_in_milli(),
            "sc_choices[]": ['{"value":"What is she?", "priority":"1"}',
                             '{"value":"What is he?", "priority":"2"}']
        }
        response = c.post('/api/polls/create/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.INVALID_POLL_TYPE)

    def test_delete(self):
        user = self.get_token()

        poll, _ = Poll.objects.get_or_create(user=user, title="Test title")

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "poll_id": poll.id
        }
        response = c.post('/api/polls/delete/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_read(self):
        user = self.get_token()

        poll, _ = Poll.objects.get_or_create(user=user, title="Test title")

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "poll_id": poll.id
        }
        response = c.post('/api/polls/read/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_feed(self):
        self.get_token()

        params = {
            AUTH_TOKEN_HEADER: self.token,
        }
        response = c.post('/api/polls/feed/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_answer_to_poll(self):
        user = self.get_token()

        poll, _ = Poll.objects.get_or_create(user=user, title="Test title",
                                             is_active=True,
                                             date_end=9999999999999)
        choice, _ = PollChoice.objects.get_or_create(poll=poll, is_active=True)

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "poll_id": poll.id,
            "choice_ids[]": [choice.id]
        }
        response = c.post('/api/polls/answer_to_poll/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_answer_to_poll_not_found(self):
        self.get_token()

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "poll_id": 1,
            "choice_ids[]": [1, 2]
        }
        response = c.post('/api/polls/answer_to_poll/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.POLL_NOT_FOUND)

    def test_answer_to_poll_choice_not_found(self):
        user = self.get_token()

        poll, _ = Poll.objects.get_or_create(user=user, title="Test title",
                                             is_active=True,
                                             date_end=9999999999999)

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "poll_id": poll.id,
            "choice_ids[]": [1, 2]
        }
        response = c.post('/api/polls/answer_to_poll/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.POLL_CHOICE_NOT_FOUND)

    def test_answer_to_poll_invalid_answer_count(self):
        user = self.get_token()

        poll, _ = Poll.objects.get_or_create(user=user, title="Test title",
                                             poll_type=0, is_active=True,
                                             date_end=9999999999999)
        choice = PollChoice.objects.create(poll=poll)
        choice1 = PollChoice.objects.create(poll=poll)

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "poll_id": poll.id,
            "choice_ids[]": [choice.id, choice1.id]
        }
        response = c.post('/api/polls/answer_to_poll/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.INVALID_POLL_ANSWER_COUNT)

    def test_answer_to_poll_answered_poll1(self):
        user = self.get_token()

        poll, _ = Poll.objects.get_or_create(user=user, title="Test title",
                                             poll_type=0, is_active=True,
                                             date_end=9999999999999)
        choice = PollChoice.objects.create(poll=poll)
        PollAnswer.objects.get_or_create(poll=poll, user=user,
                                         poll_choice=choice)

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "poll_id": poll.id,
            "choice_ids[]": [choice.id]
        }
        response = c.post('/api/polls/answer_to_poll/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.ANSWERED_POLL)

    def test_answer_to_poll_answered_poll2(self):

        poll, _ = Poll.objects.get_or_create(user=self.create_user(),
                                             title="Test title",
                                             poll_type=0,
                                             is_active=True,
                                             date_end=9999999999999)
        choice = PollChoice.objects.create(poll=poll)
        pollanswer, _ = PollAnswer.objects.get_or_create(poll=poll,
                                                         user_cookie=c.cookies["user_cookie"].value,
                                                         poll_choice=choice)

        params = {
            "poll_id": poll.id,
            "choice_ids[]": [choice.id]
        }
        response = c.post('/api/polls/answer_to_poll/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.ANSWERED_POLL)

    def test_view_poll(self):
        user = self.get_token()

        poll, _ = Poll.objects.get_or_create(user=user, title="Test title",
                                             poll_type=0, is_active=True)

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "poll_id": poll.id
        }
        response = c.post('/api/polls/view_poll/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_view_poll_not_found(self):
        self.get_token()

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "poll_id": 1
        }
        response = c.post('/api/polls/view_poll/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.POLL_NOT_FOUND)

    def test_get_random_poll(self):
        user = self.get_token()

        poll, _ = Poll.objects.get_or_create(user=user, title="Test title",
                                             poll_type=0, is_active=True)

        params = {
            AUTH_TOKEN_HEADER: self.token,
        }
        response = c.post('/api/polls/get_random_poll/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_get_random_poll_not_found(self):
        self.get_token()

        params = {
            AUTH_TOKEN_HEADER: self.token,
        }
        response = c.post('/api/polls/get_random_poll/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.POLL_NOT_FOUND)

    def test_get_widget_poll(self):
        user = self.get_token()

        poll, _ = Poll.objects.get_or_create(user=user, title="Test title",
                                             poll_type=0, is_active=True)

        params = {
            AUTH_TOKEN_HEADER: self.token,
        }
        response = c.post('/api/polls/widget/get/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_get_article_poll_ok(self):
        user = self.get_token()

        article, _ = Article.objects.get_or_create(article_url=TEST_ARTICLE_URL)
        poll, _ = Poll.objects.get_or_create(user=user, title="Test title",
                                             poll_type=0, is_active=True)
        ArticlePollEntry.objects.create(poll=poll, article=article, is_active=True)

        params = {
            AUTH_TOKEN_HEADER: self.token,
            "article_id": article.id
        }
        response = c.post('/api/polls/article/get/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test_ok(response)

    def test_get_article_poll_article_not_found(self):
        self.get_token()
        params = {
            AUTH_TOKEN_HEADER: self.token,
            "article_id": 1
        }
        response = c.post('/api/polls/article/get/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.ARTICLE_NOT_FOUND)

    def test_get_article_poll_article_poll_none(self):
        self.get_token()
        article, _ = Article.objects.get_or_create(article_url=TEST_ARTICLE_URL)
        params = {
            AUTH_TOKEN_HEADER: self.token,
            "article_id": article.id
        }
        response = c.post('/api/polls/article/get/', params,
                          HTTP_CSRF_TOKEN=token.generate_csrf('m'))
        self.common_test(response, status_code=STATUS_OK,
                         code=codes.ARTICLE_POLL_NONE)


