import asyncio
import logging
import random
from datetime import timedelta

import aiohttp
import praw
from channels.db import database_sync_to_async
from decouple import config
from django.utils import timezone

from data.models import RedditImage
from .constants import SUBREDDITS, REDDIT_DATA_LOADS, BAD_REDDIT_SITES

logger = logging.getLogger(__name__)

class RedditManager:

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=config("REDDIT_CLIENT_ID", default="S7bh82OEvGc70A"),
            client_secret=config("REDDIT_SECRET"),
            user_agent="DiscordBot/2.0",
            check_for_async=False,
        )

    @database_sync_to_async
    def _get_image_count(self) -> int:
        return RedditImage.objects.count()

    @database_sync_to_async
    def _save_photo(self, url: str, subreddit_name: str) -> None:
        RedditImage.objects.get_or_create(
            url=url,
            defaults={'subreddit': subreddit_name}
        )

    @database_sync_to_async
    def _get_random_image_from_db(self) -> RedditImage | None:
        count = RedditImage.objects.count()
        if count == 0:
            return None

        random_index = random.randint(0, count - 1)
        return RedditImage.objects.all()[random_index]

    @database_sync_to_async
    def _delete_image(self, image_id: int) -> None:
        RedditImage.objects.filter(id=image_id).delete()

    @database_sync_to_async
    def delete_all_images(self) -> None:
        RedditImage.objects.all().delete()

    async def _check_url_validity(self, url: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=5) as response:
                    return response.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False

    async def scrape_subreddit(self, subreddit_name: str, count: int, sort_by: str) -> None:
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            sorter = getattr(subreddit, sort_by)

            for submission in sorter(limit=count):
                if not submission.url:
                    continue

                if any(bad_site in submission.url for bad_site in BAD_REDDIT_SITES):
                    continue

                await self._save_photo(submission.url, subreddit_name)

        except Exception as e:
            logger.error(f"Failed to load subreddit {subreddit_name}: {e}")

    async def load_reddit_images(self) -> None:
        for reddit_name in SUBREDDITS:
            for sort_by, count in REDDIT_DATA_LOADS.items():
                await self.scrape_subreddit(reddit_name, count, sort_by)
                await asyncio.sleep(2)  # Prevence rate-limitingu

    async def background_task(self) -> None:
        logger.info("Starting Reddit background task.")
        while True:
            try:
                count = await self._get_image_count()
                if count < 20_000:
                    await self.load_reddit_images()
            except Exception as e:
                logger.error(f"Error in background task: {e}")

            await asyncio.sleep(60)

    async def get_valid_image(self) -> RedditImage | None:
        max_retries = 10
        one_day_ago = timezone.now() - timedelta(days=1)

        for _ in range(max_retries):
            image = await self._get_random_image_from_db()

            if not image:
                return None

            if image.last_sent > one_day_ago:
                return image

            is_valid = await self._check_url_validity(image.url)

            if not is_valid:
                await self._delete_image(image.id)
                continue

            return image

        logger.warning("Could not find a valid image after max retries.")
        return None

reddit_manager = RedditManager()