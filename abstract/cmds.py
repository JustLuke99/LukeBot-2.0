import os

from channels.db import database_sync_to_async
from discord.ext import commands

from data.models import RunningCommand
from constants import PLUGIN_DIRECTORY


def check_if_cmd_is_running(room_id: int, command_name: str):
    if RunningCommand.objects.filter(
        room_id=room_id, command_name=command_name
    ).exists():
        raise commands.BadArgument("Příkaz již běží.")


@database_sync_to_async
def cmd_running(room_id: int, command_name: str):
    return RunningCommand.objects.filter(
        room_id=room_id, command_name=command_name
    ).exists()


@database_sync_to_async
def add_command(room_id: int, command_name: str):
    check_if_cmd_is_running(room_id, command_name)

    model = RunningCommand(room_id=room_id, command_name=command_name)
    model.save()


@database_sync_to_async
def del_command(room_id: int, command_name: str):
    model = RunningCommand.objects.filter(room_id=room_id, command_name=command_name)
    model.delete()


@database_sync_to_async
def del_all_commands():
    RunningCommand.objects.all().delete()


def all_plugins():
    path = os.path.join(os.path.dirname(__file__).rsplit("\\", 1)[0], PLUGIN_DIRECTORY)
    files = os.listdir(path)

    plugins = []
    for file in files:
        if "__pycache__" in file:
            continue

        plugins.append(file)

    return plugins


all_plugins()
