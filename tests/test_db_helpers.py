"""Tests for async DB helpers (bot/db_helpers.py)."""
import pytest
from discord.ext import commands

from bot.db_helpers import add_command, del_command, cmd_running, del_all_commands


@pytest.mark.django_db(transaction=True)
class TestDbHelpers:
    async def test_cmd_not_running_initially(self):
        result = await cmd_running(11111, "test_cmd")
        assert result is False

    async def test_add_command_marks_as_running(self):
        await add_command(22222, "test_cmd")
        result = await cmd_running(22222, "test_cmd")
        assert result is True

    async def test_add_duplicate_command_raises(self):
        await add_command(33333, "dup_cmd")
        with pytest.raises(commands.BadArgument, match="Command is already running"):
            await add_command(33333, "dup_cmd")

    async def test_del_command_removes_entry(self):
        await add_command(44444, "del_cmd")
        await del_command(44444, "del_cmd")
        result = await cmd_running(44444, "del_cmd")
        assert result is False

    async def test_del_nonexistent_command_is_safe(self):
        """Deleting a non-existent entry must not raise an exception."""
        await del_command(55555, "nonexistent")

    async def test_del_all_commands_clears_everything(self):
        await add_command(1, "cmd1")
        await add_command(2, "cmd2")
        await add_command(3, "cmd3")
        await del_all_commands()
        assert await cmd_running(1, "cmd1") is False
        assert await cmd_running(2, "cmd2") is False
        assert await cmd_running(3, "cmd3") is False

    async def test_same_command_different_rooms(self):
        """The same command can run in multiple channels simultaneously."""
        await add_command(100, "shared_cmd")
        await add_command(200, "shared_cmd")
        assert await cmd_running(100, "shared_cmd") is True
        assert await cmd_running(200, "shared_cmd") is True

    async def test_different_commands_same_room(self):
        """Different commands can run in the same channel simultaneously."""
        await add_command(300, "cmd_a")
        await add_command(300, "cmd_b")
        assert await cmd_running(300, "cmd_a") is True
        assert await cmd_running(300, "cmd_b") is True

    async def test_cmd_running_after_del_all(self):
        await add_command(400, "cleanup_cmd")
        await del_all_commands()
        assert await cmd_running(400, "cleanup_cmd") is False
