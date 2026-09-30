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

from rich.logging import RichHandler


def setup_logging(level: int | str | None = None) -> logging.Logger:
    logging.basicConfig(
        level=level,
        format="%(name)s.%(funcName)s\t%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )

    # JAX is very verbose, so set it to warning level by default
    logging.getLogger("jax").setLevel(logging.WARNING)

    return logging.getLogger()
