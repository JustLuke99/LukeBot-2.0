from channels.db import database_sync_to_async
from discord.ext import commands

from data.models import RunningCommand


def _check_if_cmd_is_running(room_id: int, command_name: str) -> None:
    if RunningCommand.objects.filter(room_id=room_id, command_name=command_name).exists():
        raise commands.BadArgument("Command is already running.")


@database_sync_to_async
def cmd_running(room_id: int, command_name: str) -> bool:
    return RunningCommand.objects.filter(room_id=room_id, command_name=command_name).exists()


@database_sync_to_async
def add_command(room_id: int, command_name: str) -> None:
    _check_if_cmd_is_running(room_id, command_name)
    RunningCommand(room_id=room_id, command_name=command_name).save()


@database_sync_to_async
def del_command(room_id: int, command_name: str) -> None:
    RunningCommand.objects.filter(room_id=room_id, command_name=command_name).delete()


@database_sync_to_async
def del_all_commands() -> None:
    RunningCommand.objects.all().delete()
