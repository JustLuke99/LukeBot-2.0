# Root conftest — loaded first, BEFORE the pytest-django plugin.
# Sets required env vars before Django settings are imported.
import os

os.environ.setdefault("SETTINGS_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("BOT_SECRET", "fake_discord_token")
os.environ.setdefault("DISCORD_SERVER_IDS", "123456789")
os.environ.setdefault("REDDIT_CLIENT", "fake_reddit_client")
os.environ.setdefault("REDDIT_SECRET", "fake_reddit_secret")
os.environ.setdefault("LUNCH_ROOMS", "123456789")
os.environ.setdefault("GIPHY_CLIENT", "fake_giphy_token")
