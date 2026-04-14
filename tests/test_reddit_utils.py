"""Tests for RedditManager (plugins/reddit/utils.py)."""
import asyncio
import pytest
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from asgiref.sync import sync_to_async
from django.utils import timezone

from data.models import RedditImage


def _create_image(url: str, last_sent=None, subreddit: str = "test") -> RedditImage:
    kwargs = {"url": url, "subreddit": subreddit}
    if last_sent is not None:
        kwargs["last_sent"] = last_sent
    return RedditImage.objects.create(**kwargs)


_async_create_image = sync_to_async(_create_image)


@pytest.mark.django_db
class TestDbOperations:
    """Basic DB sanity tests independent of RedditManager."""

    def test_image_create_and_delete(self):
        img = _create_image("https://example.com/test.jpg")
        assert RedditImage.objects.filter(url="https://example.com/test.jpg").exists()
        img.delete()
        assert not RedditImage.objects.filter(url="https://example.com/test.jpg").exists()

    def test_bulk_create_ignores_duplicates(self):
        """bulk_create with ignore_conflicts=True must not raise on duplicate URLs."""
        _create_image("https://example.com/dup.jpg")

        objects = [
            RedditImage(url="https://example.com/dup.jpg", subreddit="test"),
            RedditImage(url="https://example.com/new.jpg", subreddit="test"),
        ]
        RedditImage.objects.bulk_create(objects, ignore_conflicts=True)

        assert RedditImage.objects.filter(url="https://example.com/dup.jpg").count() == 1
        assert RedditImage.objects.filter(url="https://example.com/new.jpg").count() == 1


@pytest.mark.django_db(transaction=True)
class TestRedditManagerCheckUrl:
    async def test_valid_url_returns_true(self):
        from plugins.reddit.utils import reddit_manager

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.head = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await reddit_manager._check_url("https://example.com/img.jpg")

        assert result is True

    async def test_404_returns_false(self):
        from plugins.reddit.utils import reddit_manager

        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.head = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await reddit_manager._check_url("https://example.com/dead.jpg")

        assert result is False

    async def test_network_error_returns_false(self):
        import aiohttp
        from plugins.reddit.utils import reddit_manager

        with patch("aiohttp.ClientSession") as mock_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session.head = MagicMock(side_effect=aiohttp.ClientError)
            mock_cls.return_value = mock_session

            result = await reddit_manager._check_url("https://example.com/err.jpg")

        assert result is False


@pytest.mark.django_db(transaction=True)
class TestGetValidImage:
    async def test_returns_none_when_db_empty(self):
        from plugins.reddit.utils import reddit_manager

        result = await reddit_manager.get_valid_image()
        assert result is None

    async def test_returns_old_image_after_url_check(self):
        """An image older than 24h that passes URL validation is returned."""
        from plugins.reddit.utils import reddit_manager

        old_time = timezone.now() - timedelta(days=2)
        await _async_create_image("https://example.com/old.jpg", last_sent=old_time)

        with patch.object(reddit_manager, "_check_url", return_value=True):
            result = await reddit_manager.get_valid_image()

        assert result is not None
        assert result.url == "https://example.com/old.jpg"

    async def test_deletes_dead_url_and_returns_none(self):
        """A dead URL is deleted and the loop retries; returns None when no valid image found."""
        from plugins.reddit.utils import reddit_manager

        old_time = timezone.now() - timedelta(days=2)
        await _async_create_image("https://example.com/dead.jpg", last_sent=old_time)

        with patch.object(reddit_manager, "_check_url", return_value=False):
            result = await reddit_manager.get_valid_image()

        assert result is None
        count = await sync_to_async(RedditImage.objects.count)()
        assert count == 0

    async def test_returns_recent_image_without_url_check(self):
        """An image sent recently (<24h) is returned without a HEAD request."""
        from plugins.reddit.utils import reddit_manager

        recent_time = timezone.now() - timedelta(hours=1)
        await _async_create_image("https://example.com/recent.jpg", last_sent=recent_time)

        with patch.object(reddit_manager, "_check_url") as mock_check:
            result = await reddit_manager.get_valid_image()

        assert result is not None
        mock_check.assert_not_called()  # URL check must not run for recently-sent images

    async def test_updates_last_sent_on_return(self):
        """last_sent must be updated after a valid image is returned."""
        from plugins.reddit.utils import reddit_manager

        old_time = timezone.now() - timedelta(days=2)
        await _async_create_image("https://example.com/update.jpg", last_sent=old_time)

        with patch.object(reddit_manager, "_check_url", return_value=True):
            result = await reddit_manager.get_valid_image()

        assert result is not None
        refreshed = await sync_to_async(RedditImage.objects.get)(pk=result.pk)
        delta = timezone.now() - refreshed.last_sent
        assert delta.total_seconds() < 5


@pytest.mark.django_db(transaction=True)
class TestRedditManagerDb:
    async def test_get_image_count(self):
        from plugins.reddit.utils import reddit_manager

        assert await reddit_manager._get_image_count() == 0
        await _async_create_image("https://a.com/1.jpg")
        assert await reddit_manager._get_image_count() == 1

    async def test_delete_all_images(self):
        from plugins.reddit.utils import reddit_manager

        await _async_create_image("https://a.com/x.jpg")
        await _async_create_image("https://a.com/y.jpg")
        await reddit_manager.delete_all_images()
        assert await reddit_manager._get_image_count() == 0

    async def test_save_batch(self):
        from plugins.reddit.utils import reddit_manager

        images = [
            {"url": "https://a.com/batch1.jpg", "subreddit": "test"},
            {"url": "https://a.com/batch2.jpg", "subreddit": "test"},
        ]
        await reddit_manager._save_batch(images)
        assert await reddit_manager._get_image_count() == 2

    async def test_save_batch_ignores_duplicates(self):
        from plugins.reddit.utils import reddit_manager

        await _async_create_image("https://a.com/dup.jpg")
        images = [
            {"url": "https://a.com/dup.jpg", "subreddit": "test"},
            {"url": "https://a.com/new_from_batch.jpg", "subreddit": "test"},
        ]
        await reddit_manager._save_batch(images)
        dup_count = await sync_to_async(RedditImage.objects.filter(url="https://a.com/dup.jpg").count)()
        assert dup_count == 1
