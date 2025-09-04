"""
Copyright (C) 2025 ETH Zurich. All rights reserved.

Author: Cedric Hirschi, ETH Zurich
        Sergei Vostrikov, ETH Zurich

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

from enum import IntEnum
import time
import logging
from queue import Queue
import attr

import numpy as np

from tinyprobe.comlink import TPCom
from tinyprobe.protocol.commands import TinyProbeCmdSeq
from tinyprobe.visualizer import TPVisualizer


class TPExecBase:
    name: str = attr.ib(default="", init=False)


@attr.s(auto_attribs=True, kw_only=True, frozen=True, slots=True)
class TPExecNOP(TPExecBase):
    name: str = attr.ib(default="NOP", init=False)

    delay_ms: float = attr.ib(default=0.0)


@attr.s(auto_attribs=True, kw_only=True, frozen=True, slots=True)
class TPExecSend(TPExecBase):
    name: str = attr.ib(default="SEND", init=False)

    cmd_seq: TinyProbeCmdSeq = attr.ib(default=None)


@attr.s(auto_attribs=True, kw_only=True, frozen=True, slots=True)
class TPExecWait(TPExecBase):
    name: str = attr.ib(default="WAIT", init=False)

    prompt: str = attr.ib(default="Press Enter to continue...")


@attr.s(auto_attribs=True, kw_only=True, frozen=True, slots=True)
class TPExecVis(TPExecBase):
    class Mode(IntEnum):
        NOP = 0
        PLOT_CHANNELS = 1
        PLOT_TRACE = 2
        LIVE_PLOT_START = 3
        LIVE_PLOT_STOP = 4

    name: str = attr.ib(default="VIS", init=False)

    mode: int = attr.ib(default=0)
    settings: dict = attr.ib(default={}, repr=lambda x: f"settings=<{len(x)} items>")


@attr.s(auto_attribs=True, kw_only=True, frozen=True, slots=True)
class TPExecRecv(TPExecBase):
    name: str = attr.ib(default="RECV", init=False)

    n_packets: int = attr.ib(default=1)
    n_shots: int = attr.ib(default=1)
    print_stats: bool = attr.ib(default=True)
    push: bool = attr.ib(default=True)


@attr.s(auto_attribs=True, kw_only=True, frozen=True, slots=True)
class TPExecPush(TPExecBase):
    name: str = attr.ib(default="PUSH", init=False)

    data: np.ndarray = attr.ib(
        default=None, repr=lambda x: f"data=<{len(x.data)} items>"
    )


@attr.s(auto_attribs=True, kw_only=True, frozen=True, slots=True)
class TPExecSave(TPExecBase):
    name: str = attr.ib(default="SAVE", init=False)

    filename: str = attr.ib(default="data.npy")
    clear: bool = attr.ib(default=False)


class TPExecutor:
    def __init__(self, log: int = logging.WARNING) -> None:
        self._log = logging.getLogger("TP/Exe") if log is not None else None
        if log is not None:
            self._log.setLevel(log)

        self._cmds = {
            "NOP": self._cmd_nop,
            "SEND": self._cmd_send,
            "WAIT": self._cmd_wait,
            "VIS": self._cmd_vis,
            "RECV": self._cmd_recv,
            "PUSH": self._cmd_push,
            "SAVE": self._cmd_save,
        }

        self._command_queue: Queue = Queue()
        self._data: bytes = b""

        self._com_link: TPCom = None
        self._visualizer: TPVisualizer = TPVisualizer()

    def set_com_link(self, com_link: TPCom):
        """Set the communication link for the executor.

        Arguments:
            com_link (TPCom): The communication link to set.

        Returns:
            None

        Raises:
            ValueError: If the provided communication link is not of type TPCom.
        """
        if not isinstance(com_link, TPCom):
            raise ValueError("Invalid communication link type.")
        self._com_link = com_link
        self._log.debug(f"Set communication link: {com_link.__class__.__name__}")

    def add(self, command: TPExecBase) -> int:
        """Add a command to the queue.

        Arguments:
            command (Command): The command to add.
            **kwargs: The arguments for the command.

        Returns:
            queue_length (int): Current command queue length.

        Raises:
            ValueError: If the command is invalid or if the arguments do not match the command.
        """
        if not isinstance(command, TPExecBase):
            raise ValueError("Command has to be of type TPExecBase (or subclass).")

        if command.name not in self._cmds:
            raise ValueError(f"Unknown command: {command}")

        self._command_queue.put(command)
        self._log.debug(f"Added {command}")

        return self._command_queue.qsize()

    def execute(self, skip_errors: bool = False, keep_queue: bool = False) -> list:
        """Execute the all current commands in the command queue.

        Arguments:
            skip_errors (bool): Whether to skip errors during execution. Defaults to False.
            keep_queue (bool): Whether to keep the command queue after execution. Defaults to False.

        Returns:
            None

        Raises:
            Exception: If an error occurs during command execution and skip_errors is False.
            ValueError: If an unknown command is encountered.

        """
        results = []

        if keep_queue:
            queue_copy = self._command_queue.queue.copy()

        self._log.info(f"Executing {self._command_queue.qsize()} commands.")

        while not self._command_queue.empty():
            command = self._command_queue.get()
            self._log.debug(f"Executing {command}")
            try:
                result = self._cmds[command.name](command)
            except Exception as e:
                self._log.error(f"Error executing {command}")
                if not skip_errors:
                    raise e
                else:
                    self._log.exception(e)

            results.append(result)

        if keep_queue:
            for item in queue_copy:
                self._command_queue.put(item)
            self._log.debug("Command queue preserved after execution.")

        self._log.info(f"Executed {self._command_queue.qsize()} commands.")

        return results

    def _cmd_nop(self, command: TPExecNOP) -> None:
        """No operation command.

        Arguments:
            command (TPExecNOP): The command to execute.

        Returns:
            None
        """
        self._log.debug(f"{command.name} waiting {command.delay_ms} ms")
        time.sleep(command.delay_ms / 1000)

    def _cmd_send(self, command: TPExecSend) -> bool:
        """Send command sequence.

        Arguments:
            command (TPExecSend): The command to execute.

        Returns:
            success (bool): True if the command sequence was sent successfully, False otherwise.

        Raises:
            ValueError: If the communication link is not set.
        """
        if self._com_link is None:
            raise ValueError("Communication link is not set.")

        self._log.debug(f"{command.name} sending {command.cmd_seq}")
        return self._com_link.send_cmd_seq(command.cmd_seq)

    def _cmd_wait(self, command: TPExecWait) -> str:
        """Wait for user input.

        Arguments:
            command (TPExecWait): The command to execute.

        Returns:
            pressed (str): The user input.
        """
        return input(command.prompt)

    def _cmd_vis(self, command: TPExecVis) -> None:
        """Configure visualization.

        Arguments:
            command (TPExecVis): The command to execute.

        Returns:
            None
        """
        self._log.debug(f"{command.name} applying {command.settings}")
        self._visualizer.configure(command.settings)

        self._log.debug(f"{command.name} mode {command.mode}")
        match command.mode:
            case TPExecVis.Mode.NOP:
                pass  # No operation for mode 0
            case TPExecVis.Mode.PLOT_CHANNELS:
                self._visualizer.plot_channels()
            case TPExecVis.Mode.PLOT_TRACE:
                self._visualizer.plot_trace()
            case TPExecVis.Mode.LIVE_PLOT_START:
                self._visualizer.start_live_plot()
            case TPExecVis.Mode.LIVE_PLOT_STOP:
                self._visualizer.stop_live_plot()
            case _:
                self._log.warning(f"Unknown mode: {command.mode}")

    def _cmd_recv(self, command: TPExecRecv) -> tuple[int, float]:
        """Receive data from the communication link.

        Arguments:
            command (TPExecRecv): The command to execute.

        Returns:
            data (bytes): Received data.
            elapsed_time (float): Time taken to receive the data.

        Raises:
            ValueError: If the communication link is not set.
        """
        if self._com_link is None:
            raise ValueError("Communication link is not set.")

        self._log.debug(
            f"{command.name} receiving "
            f"{command.n_packets} packets "
            f"and{command.n_shots} shots. "
            f"Print stats: {command.print_stats}. "
            f"Push data: {command.push}."
        )

        data, elapsed_time = self._com_link.receive_shots(
            command.n_packets, command.n_shots, command.print_stats
        )

        if command.push:
            self._cmd_push(data)

        return len(data), elapsed_time

    def _cmd_push(self, data: bytes | TPExecPush) -> None:
        """Push data to the internal buffer (for testing purposes).

        Arguments:
            data (bytes): Data to push.

        Returns:
            None
        """
        if isinstance(data, TPExecPush):
            data = data.data
        if not isinstance(data, bytes) and not isinstance(data, np.ndarray):
            raise ValueError(
                "Data must be of type bytes or np.ndarray, not", type(data)
            )

        if not isinstance(data, np.ndarray):
            # If we pushed parsed data (is of type np.ndarray), we dont want to push it into own data buffer
            self._data += data
            self._log.debug(f"Pushed data of size {len(data)}")

        self._visualizer.push_data(data)

    def _cmd_save(self, command: TPExecSave) -> None:
        """Save the current data to a file.

        Arguments:
            filename (str): The name of the file to save the data to.

        Returns:
            None
        """
        if len(self._data) == 0:
            self._log.warning(f"{command.name} has no data to save.")
            return

        np.save(command.filename, self._data)
        self._log.info(f"{command.name} saved to {command.filename}.")

        if command.clear:
            self._data = b""
            self._log.debug(f"{command.name} cleared data buffer.")
