"""Tests for Django models (data/models.py)."""
import pytest
from django.utils import timezone

from data.models import RunningCommand, RedditImage


@pytest.mark.django_db
class TestRunningCommand:
    def test_create_and_retrieve(self):
        cmd = RunningCommand(room_id=12345, command_name="test_cmd")
        cmd.save()
        assert RunningCommand.objects.filter(room_id=12345, command_name="test_cmd").exists()

    def test_str_representation(self):
        cmd = RunningCommand(room_id=12345, command_name="test_cmd")
        result = str(cmd)
        assert "test_cmd" in result
        assert "12345" in result

    def test_filter_by_room_and_command(self):
        RunningCommand(room_id=111, command_name="cmd_a").save()
        RunningCommand(room_id=222, command_name="cmd_a").save()
        assert RunningCommand.objects.filter(room_id=111, command_name="cmd_a").count() == 1
        assert RunningCommand.objects.filter(room_id=222, command_name="cmd_a").count() == 1

    def test_delete(self):
        RunningCommand(room_id=999, command_name="del_me").save()
        RunningCommand.objects.filter(room_id=999, command_name="del_me").delete()
        assert not RunningCommand.objects.filter(room_id=999, command_name="del_me").exists()

    def test_same_command_different_rooms(self):
        """The same command can run simultaneously in different channels."""
        RunningCommand(room_id=1, command_name="shared").save()
        RunningCommand(room_id=2, command_name="shared").save()
        assert RunningCommand.objects.filter(command_name="shared").count() == 2


@pytest.mark.django_db
class TestRedditImage:
    def test_create_and_retrieve(self):
        img = RedditImage(url="https://example.com/a.jpg", subreddit="test")
        img.save()
        assert RedditImage.objects.filter(url="https://example.com/a.jpg").exists()

    def test_str_representation(self):
        img = RedditImage(url="https://example.com/b.jpg", subreddit="mysubreddit")
        result = str(img)
        assert "https://example.com/b.jpg" in result
        assert "mysubreddit" in result

    def test_date_created_default_is_recent(self):
        """date_created must use a callable default — each instance gets the current time."""
        img = RedditImage(url="https://example.com/c.jpg", subreddit="test")
        img.save()
        delta = timezone.now() - img.date_created
        assert delta.total_seconds() < 5, "date_created should be the current time"

    def test_last_sent_default_is_year_2000(self):
        """last_sent must default to year 2000 so every new image is immediately eligible."""
        img = RedditImage(url="https://example.com/d.jpg", subreddit="test")
        img.save()
        assert img.last_sent.year == 2000

    def test_two_instances_have_independent_date_created(self):
        """Each instance must receive its own timestamp, not a shared hardcoded value."""
        img1 = RedditImage(url="https://example.com/e.jpg", subreddit="test")
        img1.save()
        img2 = RedditImage(url="https://example.com/f.jpg", subreddit="test")
        img2.save()
        assert img1.date_created is not None
        assert img2.date_created is not None
        delta = timezone.now() - img1.date_created
        assert delta.total_seconds() < 5

    def test_update_last_sent(self):
        img = RedditImage(url="https://example.com/g.jpg", subreddit="test")
        img.save()
        now = timezone.now()
        img.last_sent = now
        img.save()
        refreshed = RedditImage.objects.get(url="https://example.com/g.jpg")
        assert abs((refreshed.last_sent - now).total_seconds()) < 1

    def test_filter_by_subreddit(self):
        RedditImage(url="https://a.com/1.jpg", subreddit="cats").save()
        RedditImage(url="https://a.com/2.jpg", subreddit="dogs").save()
        RedditImage(url="https://a.com/3.jpg", subreddit="cats").save()
        assert RedditImage.objects.filter(subreddit="cats").count() == 2
        assert RedditImage.objects.filter(subreddit="dogs").count() == 1

    def test_delete_all(self):
        RedditImage(url="https://b.com/1.jpg", subreddit="test").save()
        RedditImage(url="https://b.com/2.jpg", subreddit="test").save()
        RedditImage.objects.all().delete()
        assert RedditImage.objects.count() == 0
