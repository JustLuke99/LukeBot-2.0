# LukeBot 2.0

Czech Discord bot built with py-cord and Django ORM. Provides entertainment and utility commands for a Czech Discord community.

## Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv)
- Chrome + ChromeDriver (for lunch parsers using Selenium)

## Setup

```bash
# Clone & install dependencies
uv sync

# Copy env template and fill in values
cp env.example .env

# Apply database migrations
uv run python manage.py migrate

# Run the bot
uv run python main.py
```

## Environment Variables

| Variable | Description |
|---|---|
| `BOT_SECRET` | Discord bot token |
| `SETTINGS_SECRET_KEY` | Django secret key |
| `DISCORD_SERVER_IDS` | Comma-separated server IDs for slash command sync |
| `REDDIT_CLIENT` | Reddit API client ID |
| `REDDIT_SECRET` | Reddit API client secret |
| `GIPHY_CLIENT` | Giphy API token |
| `LUNCH_ROOMS` | Comma-separated Discord channel IDs for lunch menus |

## Docker

```bash
cp env.example .env
# fill in .env
docker compose up -d
```

## Running Tests

```bash
uv run pytest
```

Tests use an in-memory SQLite database and mock all external APIs (Reddit, Giphy, HTTP requests).

## Project Structure

```
bot/                  # Core layer (permissions, plugin loader, DB helpers)
plugins/              # Bot plugins (each is a py-cord Cog)
  core/               # Runtime plugin management (reload/activate/deactivate)
  lunch/              # Daily lunch menus scraped from restaurant websites
    parsers/          # One file per restaurant (knoflik, radegast, budha, ...)
  misc/               # Fun commands (ping, sexymetr, gay_calculator, ...)
  reddit/             # Auto-sends images from configured subreddits
  responses/          # Passive listener — reacts to Czech text patterns
data/                 # Django app with SQLite models
tests/                # pytest test suite
```

## Architecture Notes

- **Plugin loading** happens in `LukeBot.setup_hook()` via `bot.plugin_loader.all_plugins()` — loads each `plugins/<name>/<name>.py` that exposes `setup(bot)`.
- **Permissions** are hardcoded in `bot/constants.py` (Discord user/role IDs). Moving these to the database is a known TODO.
- **Reddit** uses a `RedditManager` class: PRAW calls run in a thread pool (`asyncio.to_thread`), URL validation uses `aiohttp`, images are bulk-inserted via `bulk_create(ignore_conflicts=True)`.
- **RunningCommand** model prevents duplicate concurrent execution of long-running commands.
- **Lunch parsers** run at 10:10 AM Europe/Prague time and scrape restaurant websites. `vlk` and `orel` require Chrome (Selenium).
