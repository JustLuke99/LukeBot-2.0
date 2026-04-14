"""
Django settings pro testování.
Používá pevné hodnoty místo config() — pytest-django načítá settings
ještě před tím, než conftest.py nastaví env proměnné.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # In-memory DB — rychlejší, automaticky smazaná po testování
    }
}

INSTALLED_APPS = (
    "data",
    "channels",
)

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

SECRET_KEY = "test-secret-key-not-for-production-only"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
