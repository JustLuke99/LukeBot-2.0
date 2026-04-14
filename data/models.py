import sys
from datetime import datetime

from django.utils import timezone

try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()


def _default_last_sent():
    """Default value for last_sent — year 2000, so every new image is immediately eligible to be sent."""
    return timezone.make_aware(datetime(2000, 1, 1), timezone.get_default_timezone())


class RunningCommand(models.Model):
    """Tracks active bot commands to prevent duplicate concurrent execution.

    A record is created when a command starts and deleted when it finishes.
    The unique_together constraint ensures that the same command can only run
    once per channel at a time.
    """

    room_id = models.IntegerField(
        verbose_name="Room ID",
        help_text="Discord channel ID where the command is running.",
        db_index=True,
    )
    command_name = models.CharField(
        verbose_name="Command name",
        help_text="Full module name of the command (e.g. 'plugins.reddit.reddit').",
        max_length=255,
    )

    class Meta:
        verbose_name = "Running command"
        verbose_name_plural = "Running commands"
        unique_together = [("room_id", "command_name")]

    def __str__(self):
        return f"{self.command_name} in room {self.room_id}"


class RedditImage(models.Model):
    """Cache of Reddit images for fast delivery without repeated scraping.

    The url field is unique to prevent duplicates and to allow
    bulk_create(ignore_conflicts=True) to work correctly.
    last_sent is used to ensure the same image is not sent too frequently.
    """

    url = models.CharField(
        verbose_name="Image URL",
        help_text="Direct URL to the image (png, jpg, gif). Must be unique.",
        max_length=255,
        unique=True,
    )
    subreddit = models.CharField(
        verbose_name="Subreddit",
        help_text="Name of the subreddit the image was scraped from (without r/).",
        max_length=100,
        db_index=True,
    )
    date_created = models.DateTimeField(
        verbose_name="Date added",
        help_text="When the image was saved to the database.",
        default=timezone.now,  # callable — each instance gets the current time
    )
    last_sent = models.DateTimeField(
        verbose_name="Last sent",
        help_text="When the image was last sent to Discord. Default year 2000 means never sent.",
        default=_default_last_sent,  # callable — each instance gets its own value
    )

    class Meta:
        verbose_name = "Reddit image"
        verbose_name_plural = "Reddit images"

    def __str__(self):
        return f"url: {self.url}, reddit: {self.subreddit}"
