import sys
from datetime import datetime

from django.utils import timezone

try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()


class RunningCommand(models.Model):
    room_id = models.IntegerField()
    command_name = models.CharField(max_length=255)


class RedditImage(models.Model):
    url = models.CharField(max_length=255)
    subreddit = models.CharField(max_length=100)
    date_created = models.DateTimeField(default=timezone.now())
    last_sent = models.DateTimeField(
        default=timezone.make_aware(
            datetime(2000, 1, 1), timezone.get_default_timezone()
        )
    )

    def __str__(self):
        return f"url: {self.url}, reddit: {self.subreddit}"
