import asyncio
import logging
import random
from datetime import timedelta
from typing import List, Optional

import aiohttp
import praw
from asgiref.sync import sync_to_async
from decouple import config
from django.db.models import QuerySet
from django.utils import timezone

from data.models import RedditImage
from .constants import SUBREDDITS, REDDIT_DATA_LOADS, BAD_REDDIT_SITES

logger = logging.getLogger(__name__)


class RedditManager:
    """Manages Reddit scraping, database persistence, and image validation.

    This class handles the interaction with the PRAW API to fetch content,
    manages a local database cache of images, and ensures URLs are valid
    before serving them to the application.
    """

    def __init__(self) -> None:
        """Initializes the RedditManager with PRAW configuration."""
        self.reddit = praw.Reddit(
            client_id=config("REDDIT_CLIENT_ID", default="S7bh82OEvGc70A"),
            client_secret=config("REDDIT_SECRET"),
            user_agent="DiscordBot/2.6.4",
            check_for_async=False,
        )

    @sync_to_async
    def _get_image_count(self) -> int:
        """Returns the total number of images in the database.

        Returns:
            int: The count of RedditImage objects.
        """
        return RedditImage.objects.count()

    @sync_to_async
    def _save_batch(self, images_data: List[dict]) -> None:
        """Bulk saves a list of image data to the database.

        Uses ignore_conflicts to handle duplicate URLs gracefully without
        multiple database hits.

        Args:
            images_data (List[dict]): A list of dictionaries containing 'url'
                and 'subreddit'.
        """
        objects = [
            RedditImage(url=item["url"], subreddit=item["subreddit"])
            for item in images_data
        ]
        RedditImage.objects.bulk_create(objects, ignore_conflicts=True)

    @sync_to_async
    def _get_random_image_from_db(self) -> Optional[RedditImage]:
        """Fetches a random image from the database efficiently.

        Instead of using high-offset slicing which performs poorly on large tables,
        this fetches all IDs, picks one, and retrieves the specific object.

        Returns:
            Optional[RedditImage]: A random image object or None if the DB is empty.
        """
        # Fetching IDs is significantly faster than slicing large QuerySets
        pks = list(RedditImage.objects.values_list("pk", flat=True))
        if not pks:
            return None
        random_pk = random.choice(pks)
        try:
            return RedditImage.objects.get(pk=random_pk)
        except RedditImage.DoesNotExist:
            return None

    @sync_to_async
    def _delete_image(self, image_id: int) -> None:
        """Deletes a specific image from the database by ID.

        Args:
            image_id (int): The primary key of the image to delete.
        """
        RedditImage.objects.filter(id=image_id).delete()

    @sync_to_async
    def delete_all_images(self) -> None:
        """Truncates the RedditImage table."""
        RedditImage.objects.all().delete()

    async def _check_url_validity(self, url: str) -> bool:
        """Checks if a URL is reachable via a HEAD request.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the status code is 200, False otherwise.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=5) as response:
                    return response.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False

    def _fetch_subreddit_sync(
            self, subreddit_name: str, count: int, sort_by: str
    ) -> List[dict]:
        """Synchronous helper method to fetch data via PRAW.

        This method is intended to be run in a separate thread to avoid
        blocking the asyncio event loop.

        Args:
            subreddit_name (str): The name of the subreddit.
            count (int): Number of posts to fetch.
            sort_by (str): Sorting method (e.g., 'hot', 'top').

        Returns:
            List[dict]: A list of valid submission data found.
        """
        results = []
        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            for submission in subreddit.top(sort_by, limit=count):
                if not submission.url:
                    continue

                if any(bad in submission.url for bad in BAD_REDDIT_SITES):
                    continue

                results.append(
                    {"url": submission.url, "subreddit": subreddit_name}
                )
        except Exception as e:
            logger.error(f"PRAW error scraping {subreddit_name}: {e}")

        return results

    async def scrape_subreddit(
            self, subreddit_name: str, count: int, sort_by: str
    ) -> None:
        """Orchestrates scraping of a subreddit in a non-blocking manner.

        Offloads the synchronous PRAW network calls to a thread and performs
        a bulk database insert upon completion.

        Args:
            subreddit_name (str): The name of the subreddit.
            count (int): Number of posts to fetch.
            sort_by (str): Sorting method.
        """
        valid_images = await asyncio.to_thread(
            self._fetch_subreddit_sync, subreddit_name, count, sort_by
        )

        if valid_images:
            await self._save_batch(valid_images)
            logger.info(
                f"Saved {len(valid_images)} images from r/{subreddit_name}"
            )

    async def load_reddit_images(self) -> None:
        """Iterates through configured subreddits and triggers scraping."""
        for reddit_name in SUBREDDITS:
            for sort_by, count in REDDIT_DATA_LOADS.items():
                await self.scrape_subreddit(reddit_name, count, sort_by)
                # Small buffer to be polite to APIs and DB
                await asyncio.sleep(2)

    async def background_task(self) -> None:
        """Continuous background task to maintain the image cache.

        Checks the database count periodically. If the count is below the
        threshold, it triggers a scrape job. Runs indefinitely.
        """
        logger.info("Starting Reddit background task.")
        while True:
            try:
                count = await self._get_image_count()
                if count < 20_000:
                    logger.info("Image cache low. Starting scrape cycle.")
                    await self.load_reddit_images()
                else:
                    logger.info("Image cache sufficient.")
            except Exception as e:
                logger.exception("Critical error in Reddit background task")

            await asyncio.sleep(60 * 60 * 24)  # 24 hours

    async def get_valid_image(self) -> Optional[RedditImage]:
        """Retrieves a valid image for display.

        Tries to find an image that is either recently cached (trusted) or
        verifies the URL availability in real-time. If an image URL is dead,
        it is removed from the database and a retry occurs.

        Returns:
            Optional[RedditImage]: A valid image object or None if exhausted.
        """
        max_retries = 10
        # Determine threshold for "trusted" cache (checked within last 24h)
        one_day_ago = timezone.now() - timedelta(days=1)

        for attempt in range(max_retries):
            image = await self._get_random_image_from_db()

            if not image:
                return None

            # Optimization: logic assumes if we interacted with it recently, it works.
            # Depending on model definition, ensure 'last_sent' is nullable/handled.
            if image.last_sent and image.last_sent > one_day_ago:
                return image

            is_valid = await self._check_url_validity(image.url)

            if is_valid:
                return image

            # URL is dead, cleanup and retry
            logger.warning(f"Removing dead URL: {image.url}")
            await self._delete_image(image.id)

        logger.warning(
            f"Failed to find valid image after {max_retries} attempts."
        )
        return None


reddit_manager = RedditManager()