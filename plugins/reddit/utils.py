"""Reddit scraping, caching and URL validation.

Design decisions:
- PRAW calls are synchronous → offloaded to a thread pool via asyncio.to_thread()
- URL validation uses aiohttp (async, does not block the event loop)
- bulk_create with ignore_conflicts=True instead of per-URL saves
- Random selection via PK list instead of order_by("?") (slow on large tables)
"""

import asyncio
import logging
import random
from datetime import timedelta
from typing import Optional

import aiohttp
import praw
from asgiref.sync import sync_to_async
from decouple import config
from django.utils import timezone

from data.models import RedditImage
from .constants import SUBREDDITS, REDDIT_DATA_LOADS, BAD_REDDIT_SITES

logger = logging.getLogger(__name__)


class RedditManager:
    """Manages Reddit scraping, database persistence and URL validation."""

    def __init__(self) -> None:
        self.reddit = praw.Reddit(
            client_id=config("REDDIT_CLIENT"),
            client_secret=config("REDDIT_SECRET"),
            user_agent="DiscordBot",
            check_for_async=False,
        )

    # --- DB helpers ---

    @sync_to_async
    def _get_image_count(self) -> int:
        return RedditImage.objects.count()

    @sync_to_async
    def _save_batch(self, images_data: list[dict]) -> None:
        """Bulk insert with conflict handling — much faster than per-URL saves."""
        objects = [
            RedditImage(url=item["url"], subreddit=item["subreddit"])
            for item in images_data
        ]
        RedditImage.objects.bulk_create(objects, ignore_conflicts=True)

    @sync_to_async
    def _get_random_image(self) -> Optional[RedditImage]:
        """Efficient random selection via PK list instead of order_by('?')."""
        pks = list(RedditImage.objects.values_list("pk", flat=True))
        if not pks:
            return None
        try:
            return RedditImage.objects.get(pk=random.choice(pks))
        except RedditImage.DoesNotExist:
            return None

    @sync_to_async
    def _mark_sent(self, image: RedditImage) -> None:
        image.last_sent = timezone.now()
        image.save(update_fields=["last_sent"])

    @sync_to_async
    def _delete_image(self, image_id: int) -> None:
        RedditImage.objects.filter(pk=image_id).delete()

    @sync_to_async
    def delete_all_images(self) -> None:
        RedditImage.objects.all().delete()

    # --- Scraping ---

    def _fetch_subreddit_sync(self, subreddit_name: str, count: int, sort_by: str) -> list[dict]:
        """Synchronous PRAW call — must be run via asyncio.to_thread() to avoid blocking the event loop."""
        results = []
        try:
            for submission in self.reddit.subreddit(subreddit_name).top(sort_by, limit=count):
                if not submission.url:
                    continue
                if any(bad in submission.url for bad in BAD_REDDIT_SITES):
                    continue
                results.append({"url": submission.url, "subreddit": subreddit_name})
        except Exception as e:
            logger.error(f"PRAW error scraping r/{subreddit_name}: {e}")
        return results

    async def scrape_subreddit(self, subreddit_name: str, count: int, sort_by: str) -> None:
        """Runs PRAW in a thread pool and bulk-inserts the results into the DB."""
        images = await asyncio.to_thread(
            self._fetch_subreddit_sync, subreddit_name, count, sort_by
        )
        if images:
            await self._save_batch(images)
            logger.info(f"Saved {len(images)} images from r/{subreddit_name}")

    async def load_reddit_images(self) -> None:
        for subreddit in SUBREDDITS:
            for sort_by, count in REDDIT_DATA_LOADS.items():
                await self.scrape_subreddit(subreddit, count, sort_by)
                await asyncio.sleep(2)

    # --- Background task ---

    async def background_task(self) -> None:
        """Maintains the image cache — checks every 24 hours."""
        logger.info("Reddit background task started.")
        while True:
            try:
                count = await self._get_image_count()
                if count < 20_000:
                    logger.info(f"Image cache low ({count} images), starting scrape cycle.")
                    await self.load_reddit_images()
                else:
                    logger.info(f"Image cache sufficient ({count} images).")
            except Exception:
                logger.exception("Critical error in Reddit background task")
            await asyncio.sleep(60 * 60 * 24)  # 24 hours

    # --- URL validation ---

    async def _check_url(self, url: str) -> bool:
        """Async HEAD request via aiohttp — does not block the event loop."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False

    # --- Public API ---

    async def get_valid_image(self) -> Optional[RedditImage]:
        """Returns a valid image for display.

        Images older than 24h are verified via a HEAD request.
        Dead URLs are deleted and the selection retries (up to 10 attempts).
        Returns None if no valid image is found.
        """
        one_day_ago = timezone.now() - timedelta(days=1)

        for _ in range(10):
            image = await self._get_random_image()
            if not image:
                return None

            # Recently sent image — trusted, skip URL check
            if image.last_sent > one_day_ago:
                return image

            if await self._check_url(image.url):
                await self._mark_sent(image)
                return image

            logger.warning(f"Dead URL removed: {image.url}")
            await self._delete_image(image.pk)

        logger.warning("Failed to find a valid image after 10 attempts.")
        return None


reddit_manager = RedditManager()
