import json
from pathlib import Path

from command_sequence import CommandSequence
import commands


SCRIPT_PATH = Path(__file__).parent.resolve()
CONFIG_PATH = SCRIPT_PATH / "commands_config.json"
ACQUIRE_PATH = SCRIPT_PATH / "commands_acquire.json"


def load_sequence(file: Path) -> CommandSequence:
    result = CommandSequence()

    with open(file, "r") as f:
        cmds = json.load(f)

    for pkg in cmds["commands"]:
        for cmd in pkg:
            cmd_type = cmd["type"]
            cmd_class = getattr(commands, cmd_type)
            cmd_instance = cmd_class()
            cmd_instance.from_dict(cmd)
            result.add_command(cmd_instance)

    return result


def load_sequence_config() -> CommandSequence:
    return load_sequence(CONFIG_PATH)


def load_sequence_acquire() -> CommandSequence:
    return load_sequence(ACQUIRE_PATH)


if __name__ == "__main__":
    load_sequence_config()
    load_sequence_acquire()
