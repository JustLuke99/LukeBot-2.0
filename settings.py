import os

from decouple import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
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

SECRET_KEY = config("SETTINGS_SECRET_KEY")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
