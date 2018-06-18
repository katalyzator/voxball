# -*- coding: utf-8 -*-
from copy import copy
from django.conf import settings
from django.utils.log import AdminEmailHandler
from django.views.debug import ExceptionReporter
from django.core.mail import EmailMessage
from utils.Constants import MINUTES
from utils.email_utils import valid_email
import celery


@celery.task(default_retry_delay=2 * MINUTES, max_retries=2)
def email(to, subject, message):
    """
    Sends email to user/users. 'to' parameter must be a string or list.
    """
    # Converto to list if one user's email is passed
    if isinstance(to, basestring):  # Python 2.x only
        to = [to]
    try:
        email_list = list(filter(lambda email: valid_email(email), to))
        msg = EmailMessage(subject, message, from_email=settings.FROM_EMAIL,
                           to=email_list)
        msg.content_subtype = "html"
        msg.send()
    except Exception as exc:
        raise email.retry(exc=exc)


class MainAdminEmailHandler(AdminEmailHandler):
    """
    Custom class for handling logging emails
    """
    def emit(self, record):
        """
        Construct body of message here
        """
        try:
            request = record.request
            subject = '%s (%s IP): %s' % (
                record.levelname,
                ('internal' if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS
                 else 'EXTERNAL'),
                record.getMessage()
            )
        except Exception:
            subject = '%s: %s' % (
                record.levelname,
                record.getMessage()
            )
            request = None
        subject = self.format_subject(subject)

        # Since we add a nicely formatted traceback on our own, create a copy
        # of the log record without the exception data.
        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        session = ''
        post = ''
        get = ''
        meta = ''
        if request is not None:
            try:
                session = str(request.session.__dict__)
                post = str(request.POST.__dict__)
                get = str(request.GET.__dict__)
                meta = str(request.META.__dict__)
            except:
                # try to log exception in logging xa xa
                pass
        reporter = ExceptionReporter(request, is_email=True, *exc_info)
        message = u"%s\n\n%s" % (self.format(no_exc_record), \
            "SESSION: \n" + session + "POST: \n" + post + "GET: \n" + get + "META: \n" + meta)
        html_message = reporter.get_traceback_html()
        # html is being added
        message = u"{}\n{}".format(message, html_message)
        self.send_mail(subject, message)

    def send_mail(self, subject, message, *args, **kwargs):
        admins = [x[1] for x in settings.ADMINS]
        email(to=admins, subject=subject, message=message)
