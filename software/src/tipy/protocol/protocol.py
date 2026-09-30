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

import logging
import re
import time
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import ClassVar, Literal, TypeVar, cast

import jsonc
from pydantic import BaseModel, ConfigDict

from tipy.transport.transport import TransportProtocol

from ..control.methods import Method, TinyprobeMethods
from ..runtime.session import Session, SessionHardware

ProtocolPhase = Literal["setup", "acquire", "teardown"]
DEFAULT_PROTOCOL_PHASES: tuple[ProtocolPhase, ...] = ("setup", "acquire", "teardown")

ProtocolConfigT = TypeVar("ProtocolConfigT", bound=BaseModel)


class ProtocolConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProtocolLifecycleState(Enum):
    INITIAL = "initial"
    SETUP_COMPLETE = "setup_complete"
    ACQUIRED = "acquired"
    TORN_DOWN = "torn_down"


def camelcase_to_snakecase(input_str: str) -> str:
    """Convert CamelCase string to snake_case.

    Source: https://stackoverflow.com/a/1176023

    Args:
        input_str (str): The CamelCase string to convert.

    Returns:
        str: The converted snake_case string.
    """

    return re.sub(r"(?<!^)(?=[A-Z])", "_", input_str).lower()


class ProtocolBase[ProtocolConfigT: BaseModel](ABC):
    """Base class for protocol flows.

    Provides a planning surface over a shared `Session`, with HAL
    access grouped under `hw`, a command queue via `TinyprobeMethods`,
    and pull-based register flushing that generates correctly muxed
    write commands.

    Subclasses implement lifecycle methods (`setup`, `acquire`,
    `teardown`) and call `pull()` when HAL register writes must
    become queued commands before subsequent direct method calls.

    Typical usage::

        protocol = MyProtocol(config)
        protocol.execute_setup()
        frame_a = protocol.execute_acquire()
        frame_b = protocol.execute_acquire()
        protocol.execute_teardown()
    """

    config: ProtocolConfigT
    config_model: ClassVar[type[BaseModel]]

    def __init__(
        self,
        config_path: Path,
        name: str | None = None,
        session: Session | None = None,
        autopull: bool = True,
    ):
        """Initialize protocol with config and optional autopull setting.

        Args:
            config_path (Path): Path to the protocol-specific configuration file.
            session (Session | None): Shared execution session. If omitted, a new session is created from `get_transports()`.
            autopull (bool): If True, automatically call `pull()` before any method that is not a direct write (e.g. `writefpga`, `writeafe`, `writetx`).
        """

        self.name = name or camelcase_to_snakecase(
            self.__class__.__name__.replace("Protocol", "")
        )
        self.log = logging.getLogger().getChild("proto").getChild(self.name)

        self.config = self._parse_config(config_path)
        self.autopull = autopull
        if session is None:
            session = Session(*self.get_transports())
        self.session: Session = session
        self.hw: SessionHardware = self.session.hw
        self.lifecycle_state = ProtocolLifecycleState.INITIAL
        self._pending_phase: ProtocolPhase | None = None
        self._pending_methods: list[Method] = []
        self._acquire_count = 0

        # Command queue
        self.methods = TinyprobeMethods(self._append_method)

    def _parse_config(self, path: Path) -> ProtocolConfigT:
        if path.suffix != ".json":
            raise FileNotFoundError("Only JSON files are supported")

        try:
            config_model = self.__class__.config_model
        except AttributeError as exc:
            raise AttributeError(
                f"{self.__class__.__name__} must define class attribute 'config_model'"
            ) from exc

        return cast(
            ProtocolConfigT, config_model.model_validate(jsonc.loads(path.read_text()))
        )

    def _append_method(self, method: Method) -> None:
        """Append a method to the command queue, with optional autopull before non-write methods."""

        if self.autopull and method.method not in ("writefpga", "writeafe", "writetx"):
            self.pull()

        self.session.append_method(method)

    @abstractmethod
    def get_transports(self) -> tuple[TransportProtocol, TransportProtocol]:
        """Return the command and data transport protocols to use for this protocol.

        Returns:
            tuple[TransportProtocol, TransportProtocol]: (transport_command, transport_bulk)
        """
        raise NotImplementedError

    def pull(self) -> dict[str, dict[int, int]]:
        """Flush all dirty register memories as mux-switch + write commands.

        Returns:
            dict[str, dict[int, int]]: Dictionary of pulled register changes by device.
        """
        return self.session.pull()

    def _get_phase_hook(self, phase: ProtocolPhase):
        fn = getattr(self, phase, None)
        if fn is None or not callable(fn):
            return None
        return fn

    def _validate_phase(self, phase: ProtocolPhase) -> None:
        if self._pending_phase is not None and self._pending_phase != phase:
            raise RuntimeError(
                f"Phase '{self._pending_phase}' is already planned; execute it before '{phase}'"
            )

        if self.lifecycle_state == ProtocolLifecycleState.TORN_DOWN:
            raise RuntimeError("No phases can be executed after teardown")

        if phase == "setup":
            if self.lifecycle_state != ProtocolLifecycleState.INITIAL:
                raise RuntimeError(
                    "Setup must be the first phase and can only run once"
                )
            return

        if phase == "acquire":
            if (
                self._get_phase_hook("setup") is not None
                and self.lifecycle_state == ProtocolLifecycleState.INITIAL
            ):
                raise RuntimeError(
                    f"Setup must be executed before acquire for '{self.name}'"
                )
            return

        if phase == "teardown":
            return

        if (
            self._get_phase_hook("setup") is not None
            and self.lifecycle_state == ProtocolLifecycleState.INITIAL
        ):
            raise RuntimeError(
                f"Setup must be executed before teardown for '{self.name}'"
            )

    def _advance_lifecycle(self, phase: ProtocolPhase) -> None:
        if phase == "setup":
            self.lifecycle_state = ProtocolLifecycleState.SETUP_COMPLETE
        elif phase == "acquire":
            self._acquire_count += 1
            self.lifecycle_state = ProtocolLifecycleState.ACQUIRED
        elif phase == "teardown":
            self.lifecycle_state = ProtocolLifecycleState.TORN_DOWN

    def plan(self, phase: ProtocolPhase) -> list[Method]:
        hook = self._get_phase_hook(phase)
        if hook is None:
            return []

        if self._pending_phase == phase:
            return self._pending_methods.copy()

        self._validate_phase(phase)

        self.log.debug(f"Planning '{phase}' phase")
        hook()
        if self.autopull:
            self.pull()

        self._pending_phase = phase
        self._pending_methods = self.session.collect()
        self.log.debug(f"{phase}: {len(self._pending_methods)} planned commands")

        return self._pending_methods.copy()

    def execute(self, phase: ProtocolPhase) -> list[Method]:
        hook = self._get_phase_hook(phase)
        if hook is None:
            return []

        if self._pending_phase not in (None, phase):
            raise RuntimeError(
                f"Phase '{self._pending_phase}' is already planned; execute it before '{phase}' for '{self.name}'"
            )

        methods = (
            self.plan(phase)
            if self._pending_phase is None
            else self._pending_methods.copy()
        )

        self.log.info(f"Executing '{phase}' phase")
        start_time = time.perf_counter()
        self.session.execute(methods)
        elapsed_time = time.perf_counter() - start_time
        self.log.info(f"'{phase}' phase executed in {elapsed_time:.3f} s")

        self._pending_phase = None
        self._pending_methods = []
        self._advance_lifecycle(phase)

        return methods

    def plan_setup(self) -> list[Method]:
        return self.plan("setup")

    def execute_setup(self) -> list[Method]:
        return self.execute("setup")

    def plan_acquire(self) -> list[Method]:
        return self.plan("acquire")

    def execute_acquire(self) -> list[Method]:
        return self.execute("acquire")

    def plan_teardown(self) -> list[Method]:
        return self.plan("teardown")

    def execute_teardown(self) -> list[Method]:
        return self.execute("teardown")

    def run(
        self,
        phases: tuple[ProtocolPhase, ...]
        | list[ProtocolPhase]
        | ProtocolPhase = DEFAULT_PROTOCOL_PHASES,
    ) -> dict[str, list[Method]]:
        """Execute all implemented lifecycle phases, return commands per phase.

        Lifecycle phases are executed in order chosen by the caller. The
        default order is `setup`, `acquire`, `teardown`.

        Returns:
            dict[str, list[Method]]: Dictionary mapping phase names to lists of generated commands.
        """
        result: dict[str, list[Method]] = {}

        if isinstance(phases, str):
            phases = [phases]

        for phase in phases:
            if self._get_phase_hook(phase) is None:
                continue
            result[phase] = self.execute(phase)

        return result
