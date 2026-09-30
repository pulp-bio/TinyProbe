# Copyright (C) 2026 ETH Zurich. All rights reserved.
#
# Authors:
#     - Cedric Hirschi, ETH Zurich
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import shutil
from pathlib import Path
import pathspec

from mkdocs.config.defaults import MkDocsConfig

# from mkdocs.structure.files import Files
# from mkdocs.structure.pages import Page
from mkdocs.utils import log


DOCS_DIR = Path(__file__).parent
ROOT_DIR = DOCS_DIR.parent


def copy_external(
    config: MkDocsConfig, filename: str, src_subdir: str | None = None, dest_subdir: str | None = None, replacements: list[tuple[str, str]] | None = None
):
    """Safely copy a file from source to destination."""
    root_dir = Path(config["config_file_path"]).resolve().parent
    docs_dir = Path(config["docs_dir"]).resolve()

    source_dir = root_dir / (src_subdir or "")
    dest_dir = docs_dir / (dest_subdir or "")

    log.info(f"Copying {filename} from {source_dir.as_posix()} to {dest_dir.as_posix()}")

    source_file = source_dir / filename
    dest_file = dest_dir / filename

    # Skip if source and destination are the same file
    if source_file.resolve() == dest_file.resolve():
        log.debug(f"Skipping {source_file} (already in place)")
        return

    # Copy the file if it exists
    if source_file.exists():
        # Create destination directory if it doesn't exist
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, dest_file)
        if replacements is not None:
            dest_text = dest_file.read_text()
            for old, new in replacements:
                dest_text = dest_text.replace(old, new)
                log.info(f"- Replaced '{old}' with '{new}' in {dest_file}")
            dest_file.write_text(dest_text)
        log.info(f"Copied {source_file} to {dest_file}")
    else:
        log.warning(f"{source_file} not found")


def on_post_build(config: MkDocsConfig, **kwargs):
    copy_external(config, "README.md", replacements=[("docs/images/", "images/")])
    log.info("Post build hook completed")





with open(DOCS_DIR / ".gitignore") as file:
    GITIGNORE = pathspec.PathSpec.from_lines(
        pathspec.patterns.GitWildMatchPattern, file
    )


def on_serve(server, config, builder):
    def callback_wrapper(callback):
        def wrapper(event):
            if GITIGNORE.match_file(
                Path(event.src_path).relative_to(config.docs_dir).as_posix()
            ):
                log.info(f"Skipping {event.src_path} (matched .gitignore)")
                return

            return callback(event)

        return wrapper

    handler = (
        next(
            handler
            for watch, handler in server.observer._handlers.items()
            if watch.path == config.docs_dir
        )
        .copy()
        .pop()
    )

    # The callback getting wrapped can be found at
    # https://github.com/mkdocs/mkdocs/blob/828f4685f29dd9e986f18306d58d1cb383d00222/mkdocs/livereload/__init__.py#L142-L148
    handler.on_any_event = callback_wrapper(handler.on_any_event)
