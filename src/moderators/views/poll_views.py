# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.validators import URLValidator
from django.views.decorators.csrf import csrf_exempt

from authe.models import MainUser, get_cdn_url
from moderators.models import Article, ArticlePollEntry
from polls.models import Poll, Category
from utils import codes, messages, http, Constants
from utils.Constants import POLL_NUMBER
from utils.image_utils import get_favicon
from utils.page_parsing_utils import get_keywords, get_title
from utils.time_utils import get_timestamp_in_milli
from utils.search_utils import search_by_date
from utils.string_utils import integer_list, handle_param
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(['poll_id'])
@http.moderators_token()
def poll_delete(request, user):
    """
    @api {post} /moderators/polls/delete/ Poll delete method
    @apiName poll_delete
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} poll_id Id of poll.
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            poll = Poll.objects.get(id=request.POST['poll_id'])
        except:
            return http.code_response(codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        poll.is_active = False
        poll.save()
        return {
            "result": poll.full(user)
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.moderators_token()
def poll_feed(request, user):
    """
    @api {post} /moderators/polls/feed/ Poll feed method
    @apiName poll_feed
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} date_begin Date Begin of poll, returns open polls with start time before entered time.
    @apiParam {Number} limit Limit per request.
    @apiParam {Number} _poll_type Filters with that poll type.
    @apiParam {String[]} keywords[] list of keywords to filter.
    @apiParam {Number} country_id ID of country to filter
    @apiParam {Number} city_id ID of city to filter
    @apiParam {Number} category_id category id to filter.
    @apiParam {Number} status status REJECTED = 0
                                     UNKNOWN = 1
                                     APPROVED = 2
    @apiSuccess {Json[]} result Json representation of polls.
    """
    try:
        poll_type = handle_param(request.POST.get("_poll_type"), int)
        date_begin = handle_param(request.POST.get("date_begin"), int,
                                  default=Constants.TIMESTAMP_MAX)
        limit = handle_param(request.POST.get('limit'), int,
                             default=Constants.FEED_LIMIT)
        city_id = handle_param(request.POST.get("city_id"), int)
        country_id = handle_param(request.POST.get("country_id"), int)
        status = handle_param(request.POST.get("status"), int,
                              default=Constants.UNKNOWN)
        search_text = handle_param(request.POST.get('search'), unicode,
                                   default=u'')
        keywords = request.POST.getlist("keywords[]")
        query = {}
        query["date_begin__lt"] = date_begin
        query["is_active"] = True
        query["status"] = status
        query["date_end__gt"] = get_timestamp_in_milli()
        query["is_template"] = False
        if request.POST.get("category_id"):
            query["category_id"] = int(request.POST["category_id"])
        if keywords:
            query["keywords_array__overlap"] = keywords
        if poll_type in [Poll.RATING_SCALE, Poll.SINGLE_CHOICE,
                         Poll.MULTIPLE_CHOICE]:
            query["poll_type"] = poll_type
        if country_id:
            query["city__country_id"] = country_id
        if city_id:
            query["city_id"] = city_id
        if search_text != u"None":
            query["title__icontains"] = u"{}".format(search_text)
        polls = Poll.objects.filter(**query).order_by('-date_begin')[:limit]
        return {
            'result': [p.full(is_admin=True) for p in polls]
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(['article_url'])
@http.moderators_token()
def get_polls_related_to_article(request, user):
    """
    @api {post} /moderators/articles/related/ Get polls related to article method (for matching url)
    @apiName get_polls_related_to_article
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} article_url url of an article.
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        article_url = request.POST["article_url"]
        article_keywords = get_keywords(article_url)
        polls = Poll.objects.all()
        scores = {}
        for poll in polls:
            score = len(set(poll.keywords_array).intersection(
                set(article_keywords)))
            scores[poll.id] = score
        poll_id_array = sorted(scores, key=scores.__getitem__,
                               reverse=True)[:POLL_NUMBER]
        polls = Poll.objects.filter(
            id__in=poll_id_array).select_related("user")
        return {
            'polls': [{"id": p.id,
                       "user": p.user.short(),
                       "title": p.title,
                       "date_begin": p.date_begin,
                       } for p in polls]
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.moderators_token()
def get_articles(request, user):
    """
    @api {post} /moderators/articles/get/ Get articles
    @apiName get_articles
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} last_id ID of last article (optional).
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        last_id = handle_param(request.POST.get("last_id"), int,
                               default=settings.DEFAULT_LAST_ID)
        articles = Article.objects.filter(is_active=True, id__lt=last_id)
        return {
            "result": [x.full() for x in articles]
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(["article_id"])
@http.moderators_token()
def delete_article(request, user):
    """
    @api {post} /moderators/articles/delete/ Delete articles
    @apiName delete_articles
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} article_id ID of article to delete
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            article = Article.objects.get(id=request.POST["article_id"])
        except:
            return http.code_response(code=codes.BAD_REQUEST,
                                      message=messages.POLL_NOT_FOUND)
        article.is_active = False
        article.save()
        return http.ok_response()
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(["article_url"])
@http.moderators_token()
def add_article(request, user):
    """
    @api {post} /moderators/articles/add/ Add article
    @apiName add_article
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {String} article_url URL of article
    @apiParam {Number[]} poll_ids[] IDs of poll (optional)
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            poll_ids = integer_list(request.POST.getlist("poll_ids[]"))
        except:
            return http.code_response(code=codes.INVALID_PARAMETERS,
                                      message=messages.INVALID_PARAMETERS)
        if len(poll_ids) != Poll.objects.filter(id__in=poll_ids).count():
            return http.code_response(code=codes.POLL_COUNT_DONT_MATCH,
                                      message=messages.POLL_COUNT_DONT_MATCH)
        try:
            validator = URLValidator()
            validator(request.POST["article_url"])
        except:
            return http.code_response(code=codes.INVALID_URL,
                                      message=messages.INVALID_URL)
        try:
            article_keywords = get_keywords(request.POST["article_url"])
            favicon = get_favicon(request.POST["article_url"])
            title = get_title(request.POST["article_url"])
            article = Article.objects.create(
                title=title,
                article_url=request.POST["article_url"],
                poll_ids=poll_ids,
                icon=favicon,
                keywords=article_keywords)
        except Exception as e:
            logger.warning(e)
            return http.code_response(code=codes.ALREADY_EXISTS,
                                      message=messages.ALREADY_EXISTS)
        for poll in Poll.objects.filter(id__in=poll_ids):
            ArticlePollEntry.objects.create(
                article=article, poll=poll)
        return {
            "result": article.full()
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(["article_id"])
@http.moderators_token()
def update_article(request, user):
    """
    @api {post} /moderators/articles/update/ Update article
    @apiName update_article
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {String} article_id ID of article
    @apiParam {Number[]} poll_ids[] IDs of polls
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            poll_ids = integer_list(request.POST.getlist("poll_ids[]"))
        except:
            return http.code_response(code=codes.INVALID_PARAMETERS,
                                      message=messages.INVALID_PARAMETERS)
        try:
            article = Article.objects.get(id=request.POST["article_id"])
        except:
            return http.code_response(code=codes.ARTICLE_NOT_FOUND,
                                      message=messages.ARTICLE_NOT_FOUND)
        add_list = list(set(poll_ids) - set(article.poll_ids))
        delete_list = list(set(article.poll_ids) - set(poll_ids))
        article.poll_ids = poll_ids
        article.save()
        ArticlePollEntry.objects.filter(
            article=article, poll_id__in=delete_list).update(is_active=False)
        for poll in Poll.objects.filter(id__in=add_list):
            ape, created = ArticlePollEntry.objects.get_or_create(
                article=article, poll=poll)
            if not created and not ape.is_active:
                ape.is_active = True
                ape.save()
        return {
            "result": article.full()
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(['poll_title'])
@http.moderators_token()
def get_polls_by_title(request, user):
    """
    @api {post} /moderators/polls/get_polls_by_title/ Get polls by title
    @apiName get_polls_by_title
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {String} poll_title Poll title.
    @apiParam {String} last_id for scrolling (optional)
    @apiSuccess {Json[]} result Poll title and id.
    """
    try:
        last_id = handle_param(request.POST.get('last_id'), int,
                               default=settings.DEFAULT_LAST_ID)
        poll_title = request.POST["poll_title"]
        polls = Poll.objects.filter(
            title__search=poll_title, id__lt=last_id).select_related(
            "user")[:settings.POLL_TITLE_COUNT]
        return {
            'result': [{"id": p.id,
                        "user": p.user.short(),
                        "title": p.title,
                        "date_begin": p.date_begin,
                        } for p in polls]
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.extract_token_or_cookie_from_request()
@http.required_parameters(['poll_id'])
@http.require_http_methods("POST")
def poll_read(request, user, cookie):
    """
    @api {post} /moderators/polls/read/ Poll read method
    @apiName poll_read
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {String} poll_id id of poll.
    @apiSuccess {Json} result Json representation of poll.
    """
    try:
        try:
            poll = Poll.objects.get(id=request.POST["poll_id"])
        except:
            return http.code_response(code=codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        return {
            "result": poll.full(is_admin=True, with_fb=True)
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(['poll_id', 'status'])
@http.moderators_token()
def poll_approve(request, user):
    """
    @api {post} /moderators/polls/approve/ Poll approve method
    @apiName poll_approve
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {String} poll_id id of poll.
    @apiParam {String} status status of poll.
    @apiSuccess {Object} result http ok response.
    """
    try:
        try:
            poll = Poll.objects.get(id=request.POST["poll_id"])
        except:
            return http.code_response(code=codes.POLL_NOT_FOUND,
                                      message=messages.POLL_NOT_FOUND)
        try:
            status = int(request.POST["status"])
        except:
            return http.code_response(code=codes.INVALID_POLL_STATUS,
                                      message=messages.INVALID_POLL_STATUS)

        if status in [Constants.UNKNOWN, Constants.APPROVED,
                      Constants.REJECTED]:
            poll.status = status
            poll.save()
            return http.ok_response()
        elif status == 10:
            poll.is_delete = True
            poll.save()
            return http.ok_response()
        else:
            return http.code_response(code=codes.INVALID_POLL_STATUS,
                                      message=messages.INVALID_POLL_STATUS)
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(['category_id'])
@http.moderators_token()
def category_delete(request, user):
    """
    @api {post} /moderators/category/delete/ Category delete method
    @apiName category_delete
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} category_id Id of category.
    @apiSuccess {Json} result http ok response.
    """
    try:
        try:
            category = Category.objects.get(id=request.POST['category_id'])
        except:
            return http.code_response(code=codes.CATEGORY_NOT_FOUND,
                                      message=messages.CATEGORY_NOT_FOUND)
        children = category.get_descendants(include_self=True)
        children.update(is_active=False)
        return http.ok_response()
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(['category_name'])
@http.moderators_token()
def category_create(request, user):
    """
    @api {post} /moderators/category/create/ Category create method
    @apiName category_create
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {String} category_name Name of category.
    @apiParam {Number} parent_id ID of parent.
    @apiSuccess {Json} result Json representation of category.
    """
    try:
        category_name = request.POST['category_name']
        parent = None
        if request.POST.get("parent_id", ""):
            try:
                parent = Category.objects.get(id=int(request.POST['parent_id']))
            except:
                return http.code_response(
                    code=codes.CATEGORY_NOT_FOUND,
                    message=messages.CATEGORY_NOT_FOUND)
        category, _ = Category.objects.get_or_create(name=category_name,
                                                     parent=parent)
        return {
            "result": category.full()
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(['category_id'])
@http.moderators_token()
def category_update(request, user):
    """
    @api {post} /moderators/category/update/ Category update method
    @apiName category_update
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} category_id ID of category.
    @apiParam {String} category_name Name of category.
    @apiParam {Number} parent_id Parent of category.
    @apiSuccess {Json} result Json representation of category.
    """
    try:
        try:
            category = Category.objects.get(id=int(request.POST['category_id']))
        except:
            return http.code_response(code=codes.CATEGORY_NOT_FOUND,
                                      message=messages.CATEGORY_NOT_FOUND)
        if request.POST.get("parent_id", ""):
            try:
                parent = Category.objects.get(id=int(request.POST['parent_id']))
            except:
                return http.code_response(code=codes.CATEGORY_NOT_FOUND,
                                          message=messages.CATEGORY_NOT_FOUND)
            category.parent = parent
        if request.POST.get("category_name", ""):
            try:
                category.name = request.POST['category_name']
            except:
                return http.code_response(code=codes.CATEGORY_NOT_FOUND,
                                          message=messages.CATEGORY_NOT_FOUND)
        category.save()
        return http.ok_response()
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(['category_id'])
@http.moderators_token()
def category_read(request, user):
    """
    @api {post} /moderators/category/read/ Category read method
    @apiName category_read
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} category_id ID of category.
    @apiSuccess {Json} result result Json representation of category.
    """
    try:
        try:
            category = Category.objects.get(id=int(request.POST['category_id']))
        except:
            return http.code_response(code=codes.CATEGORY_NOT_FOUND,
                                      message=messages.CATEGORY_NOT_FOUND)
        return {
            "result": category.full()
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
@http.verify_csrf()
@http.requires_token()
@http.require_http_methods("POST")
@http.required_parameters(["poll_id"])
def get_articles_stat(request, user):
    """
    @api {post} /moderators/articles/statistics/ Article statistics
    @apiName get_articles_stat
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiParam {Number} poll_id ID of poll.
    @apiSuccess {Json} result Json representation of article's statistics.
    """
    try:
        if not user.is_moderator:
            try:
                _ = Poll.objects.get(id=request.POST["poll_id"], user=user)
            except:
                return http.code_response(codes.POLL_NOT_FOUND,
                                          messages.POLL_NOT_FOUND)
        article_poll_entries = ArticlePollEntry.objects.filter(
            poll=int(request.POST["poll_id"])).select_related("article")
        article_stat = []
        for article_poll_entry in article_poll_entries:
            article_json = article_poll_entry.article.short()
            article_json["statistics"] = search_by_date(
                time_begin=0, time_end=Constants.TIMESTAMP_MAX,
                article_id=article_poll_entry.article.id, widget=True)
            article_stat.append(article_json)
        return {
            'result': article_stat
        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


@csrf_exempt
@http.json_response()
# @http.verify_csrf()
# @http.requires_token()
@http.require_http_methods("POST")
# @http.moderators_token()
def get_polls(request):
    """
    @api {post} /moderators/get_polls/ Poll feed method
    @apiName get_polls
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiSuccess {Json[]} result Json representation of polls.
    """
    try:
        polls = Poll.objects.all().order_by('-date_begin')
        return {
            'result': [{
                "title": u"{}".format(p.title).encode("utf-8"),
                "user": u"{}".format(p.user).encode("utf-8"),
                "date_begin": p.date_begin,
                "date_end": p.date_end,
                "total_answered_count": u"{}".format(p.total_answered_count).encode("utf-8"),
            } for p in polls]

        }
    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))


#
@csrf_exempt
@http.json_response()
@http.verify_csrf()
# @http.requires_token()
@http.require_http_methods("POST")
# @http.moderators_token()
def get_users(request):
    """
    @api {post} /moderators/get_users/ Poll feed method
    @apiName get_users
    @apiGroup Moderators
    @apiHeader {String} Csrf-Token CSRF token.
    @apiHeader {String} Auth-Token Authentication token.
    @apiSuccess {Json[]} result Json representation of users.
    """

    try:

        users = MainUser.objects.all().defer('avatar')

        return {
            'result': [
                i.get_object()
                for i in users
            ]
        }

    except Exception as exc:
        logger.error(exc)
        return http.code_response(codes.SERVER_ERROR, message=str(exc))
