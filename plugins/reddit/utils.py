import asyncio
from datetime import timedelta

import praw
import requests
from channels.db import database_sync_to_async
from decouple import config

from data.models import *
from .constants import SUBREDDITS, REDDIT_DATA_LOADS, BAD_REDDIT_SITES

reddit = praw.Reddit(client_id='S7bh82OEvGc70A', client_secret=config("REDDIT_SECRET"),
                     user_agent='DiscordBot', check_for_async=False)


@database_sync_to_async
def get_image_count() -> int:
    return RedditImage.objects.all().count()


async def check_reddit_images():
    while True:
        if await get_image_count() < 20_000:
            await load_reddit_images()

        await asyncio.sleep(15)


@database_sync_to_async
def save_photo(url: str, subreddit_name: str):
    if not RedditImage.objects.filter(url=url).exists():
        image = RedditImage(url=url, subreddit=subreddit_name)
        image.save()


async def load_subreddit(subreddit_name: str, count: int, sort_by: str):
    try:
        for submission in reddit.subreddit(subreddit_name).top(sort_by, limit=count):
            if not any(substr in submission.url for substr in BAD_REDDIT_SITES):
                await save_photo(submission.url, subreddit_name)
    except Exception as e:
        print(f"An error occurred in load_subreddit: {e}")


async def load_reddit_images():
    for reddit_name in SUBREDDITS:
        for sort_by, count in REDDIT_DATA_LOADS.items():
            await load_subreddit(reddit_name, count, sort_by)
            await asyncio.sleep(2)


def del_image_if_not_found(image: RedditImage) -> bool:
    req_response = requests.head(image.url)
    if req_response.status_code != 200:
        image.delete()
        return True

    return False


@database_sync_to_async
def get_image() -> RedditImage:
    while True:
        image = RedditImage.objects.order_by('?').first()
        if image.last_sent < (timezone.now() - timedelta(days=1)):
            deleted = del_image_if_not_found(image)
            if not deleted:
                return image


@database_sync_to_async
def del_all_images():
    RedditImage.objects.all().delete()
