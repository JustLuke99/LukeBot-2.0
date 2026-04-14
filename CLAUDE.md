# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

LukeBot-2.0 is a Czech-language Discord bot built with **py-cord** (a discord.py fork) and **Django ORM**. It provides entertainment and utility commands for a Czech Discord community. All user-facing messages and constants are in Czech.

## Running the Bot

```bash
pip install -r requirements.txt
python main.py
```

Required environment variables (via `.env` or shell):
- `BOT_SECRET` — Discord bot token
- `DISCORD_SERVER_IDS` — Comma-separated Discord server IDs for slash command sync
- `SETTINGS_SECRET_KEY` — Django secret key
- `REDDIT_CLIENT` / `REDDIT_SECRET` — Reddit API credentials
- `LUNCH_ROOMS` — Comma-separated Discord channel IDs for lunch notifications
- `GIPHY_CLIENT` — Giphy API token

Django database setup (SQLite, run once):
```bash
python manage.py migrate
```

## Architecture

### Plugin System

The bot uses py-cord's **Cog** system. Plugins live in `plugins/<name>/` and must expose a `setup(bot)` function. They are discovered and loaded dynamically via `abstract/cmds.py:all_plugins()` which scans the `plugins/` directory. On startup (`main.py`), the bot waits for the `on_ready` event then loads all active plugins and syncs slash commands to the configured servers.

Each plugin is activated/deactivated at runtime by the `plugins/core/core.py` cog (plugin_manager permission required).

### Current Plugins

| Plugin | Description |
|--------|-------------|
| `core` | Runtime plugin management (reload, activate, deactivate) |
| `reddit` | Auto-sends Reddit images to channels on a background loop; caches images in DB via `RedditImage` model |
| `misc` | Fun commands: ping, gay_calculator, sexymetr, message counting, bot shutdown |
| `responses` | Passive listener that matches Czech regex patterns and reacts with messages/emojis |
| `lunch` | Sends daily lunch menus at 10:10 AM from scraped restaurant websites |

### Shared Layer (`abstract/`)

- `abstract/cmds.py` — Plugin discovery + async DB helpers for `RunningCommand` (prevents duplicate concurrent command execution)
- `abstract/constants.py` — **Hardcoded** Discord role IDs, user-to-permission mappings, all user-facing Czech strings
- `abstract/permissions.py` — `Permissions` and `Roles` classes; permission check utilities used by commands

### Database (`data/`, `channels/`)

SQLite via Django ORM. Two models in `data/models.py`:
- `RunningCommand` — tracks in-flight commands to prevent duplicates
- `RedditImage` — caches Reddit image URLs per channel

### Lunch Parsers (`plugins/lunch/parsers/`)

Each file is a BeautifulSoup scraper for a specific restaurant (knoflik, radegast, budha, zlatalod). They are called by `lunch.py` at the scheduled time.

## Key Patterns

**Adding a new command:** Create a new cog in `plugins/<name>/<name>.py` with `setup(bot)`, implement slash commands using `@discord.slash_command`. The plugin auto-loads on next bot start (or via core's reload command).

**Permissions:** Check `abstract/constants.py` for role/user ID mappings and `abstract/permissions.py` for how to apply checks. Permissions are currently hardcoded (not DB-driven).

**Running command guard:** Use the `RunningCommand` model + helpers in `abstract/cmds.py` to prevent a command from running multiple times concurrently.

**Background tasks:** Use `@tasks.loop` from py-cord with `asyncio` for recurring operations (see `reddit.py` and `lunch.py`).
