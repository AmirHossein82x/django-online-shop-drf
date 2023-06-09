from celery import shared_task
from django.core.mail import send_mail
from django.http import BadHeaderError

from config import settings
from .models import Review
from datetime import datetime, timedelta


@shared_task
def delete_disable_comments():
    time_of_now = datetime.now()
    two_days_ago = time_of_now - timedelta(days=2)
    comments = Review.objects.filter(is_show=False, date_time_created__lt=two_days_ago)
    for comment in comments:
        try:
            send_mail('comment warning',
                      "your comment goes against out community and we can not show it in the comments",
                      settings.ADMIN_EMAIL, [comment.user.email]
                      )
        except BadHeaderError:
            pass

    comments.delete()
