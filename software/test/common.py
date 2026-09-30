"""
Copyright (C) 2026 ETH Zurich. All rights reserved.

Authors:
    - Cedric Hirschi, ETH Zurich

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import logging
from collections.abc import Iterable
from pathlib import Path

from tipy.control import methods

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"


OUTPUT_DIR.mkdir(exist_ok=True)


def load_binary(filename: str, dir: Path = DATA_DIR) -> bytes:
    """Load a binary file from the test data directory."""
    file_path = dir / filename
    with open(file_path, "rb") as f:
        return f.read()


def load_config(filename: str, dir: Path = DATA_DIR) -> dict:
    """Load a JSON config file from the test data directory."""
    file_path = dir / filename
    with open(file_path, "r") as f:
        return json.load(f)


def compare_writes(
    cmd_name: str,
    reg_addrs: Iterable[int],
    cmd_seq_a: list[methods.Method],
    cmd_seq_b: list[methods.Method],
) -> bool:
    result = True

    for reg_addr in reg_addrs:
        val_a = None
        val_b = None

        for cmd in cmd_seq_a:
            if (
                cmd.method == cmd_name
                and cmd.params is not None
                and cmd.params["address"] == reg_addr
            ):
                val_a = cmd.params["value"]
                break

        for cmd in cmd_seq_b:
            if (
                cmd.method == cmd_name
                and cmd.params is not None
                and cmd.params["address"] == reg_addr
            ):
                val_b = cmd.params["value"]
                break

        text_a = f"0x{val_a:08x}" if val_a is not None else "     -    "
        text_b = f"0x{val_b:08x}" if val_b is not None else "     -    "

        if val_a != val_b:
            result = False

        logging.info(
            f"Reg 0x{reg_addr:03x}: Old: {text_a} | New: {text_b} {'OK' if val_a == val_b else 'MISMATCH'}"
        )

    return result
