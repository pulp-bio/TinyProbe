"""
Copyright (C) 2025 ETH Zurich. All rights reserved.

Author: Cedric Hirschi, ETH Zurich

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

from pathlib import Path
import json
import re
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class InstallInfo:
    id: Optional[str]
    pattern: str
    get_new_path: Callable[[Path], str]

    def __repr__(self) -> str:
        return f"InstallInfo(id={self.id}, pattern={self.pattern})"

    def __str__(self) -> str:
        return self.id or "None"


REQUIRED_INSTALLS = [
    # SLT Packages path (<project>.cmake)
    InstallInfo(
        None,
        r'"[^"]*.silabs/slt/installs"',
        lambda base: f'"{base.as_posix()}/installs"',
    ),
    # Wiseconnect and Simplicity SDK paths (<project>.cmake)
    InstallInfo(
        "wiseconnect",
        r"wisec[a-zA-Z0-9]+/p",
        lambda base: (Path(base.parent.stem) / "p").as_posix(),
    ),
    InstallInfo(
        "simplicity-sdk",
        r"\".*/simple[a-zA-Z0-9]+/p",
        lambda base: '"' + base.as_posix(),
    ),
    # Build tools paths (toolchain.cmake)
    InstallInfo(
        "gcc-arm-none-eabi",
        r"\".*/conan/p/gcc-[a-zA-Z0-9]+",
        lambda base: f'"{base.parent.as_posix()}',
    ),
    InstallInfo(
        "ninja",
        r"\".*/conan/p/ninja[a-zA-Z0-9]+",
        lambda base: f'"{base.parent.as_posix()}',
    ),
    # Commander (toolchain.cmake, windows only)
    InstallInfo(
        "commander",
        r"POST_BUILD_EXE \".*Simplicity Commander/commander.exe\"",
        lambda base: f'POST_BUILD_EXE "{base.as_posix()}/commander.exe"',
    ),
]

HOME_DIR = Path.home()
SLT_DIR = HOME_DIR / ".silabs" / "slt"
LOCAL_JSON_PATH = SLT_DIR / "local.json"

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
CMAKE_DIR = PROJECT_ROOT / "cmake_gcc"


def cmake_files(cmake_dir: Path) -> list[Path]:
    """Return the list of CMake files to process, excluding certain patterns.

    Args:
        cmake_dir (Path): The directory containing CMake files.

    Returns:
        list[Path]: List of CMake file paths to process.

    Raises:
        None
    """

    cmake_files = []

    for item in cmake_dir.glob("*.cmake"):
        # *_project files are excluded since they do not reference SLT paths
        if item.stem.endswith("_project"):
            continue

        cmake_files.append(item.resolve())

    return cmake_files


def pattern_replace(content: str, install: InstallInfo, base: Path) -> tuple[str, bool]:
    """Replace occurrences of a pattern in the content with a new path.

    Args:
        content (str): The original content.
        pattern (str): The regex pattern to search for.
        new_path (str): The new path to replace the pattern with.

    Returns:
        tuple[str, bool]: The modified content and a boolean indicating if changes were made.

    Raises:
        None
    """
    replacement = install.get_new_path(base)

    new_content, n = re.subn(install.pattern, replacement, content)
    if n:
        print(f"  Updated {n} occurrence(s) for {install.id or 'SLT packages path'}")
        return new_content, True

    return content, False


def main(
    slt_dir: Path,
    cmake_dir: Path,
    required_installs: list[InstallInfo],
    dry_run: bool = False,
) -> int:
    """Main function to migrate CMake files to new SLT paths.

    Args:
        slt_dir (Path): The SLT directory path.
        cmake_dir (Path): The CMake files directory path.
        required_installs (list[str]): List of required install IDs.
        dry_run (bool): If True, do not write changes to files.

    Returns:
        None

    Raises:
        SystemExit: If required installs are missing or files cannot be processed.
    """

    local_json_path = slt_dir / "local.json"

    if not slt_dir.exists():
        print(f"ERROR: SLT directory does not exist at {slt_dir.as_posix()}")
        print("       Did you install the correct toolchain? Check the docs.")
        return 1
    elif not local_json_path.exists():
        print(f"ERROR: local.json does not exist in {slt_dir.as_posix()}")
        print("       Did you install the correct toolchain? Check the docs.")
        return 1

    local_config = json.loads(local_json_path.read_text())

    installed_ids = [install.get("id") for install in local_config]
    required_install_ids = [ri.id for ri in required_installs if ri.id is not None]
    if not all(req_id in installed_ids for req_id in required_install_ids):
        print(
            f"ERROR: Not all required installs are present in {local_json_path.as_posix()}"
        )
        print("       Did you install the correct toolchain? Check the docs.")

        print("\nRequired installs:")
        for req in required_install_ids:
            print(f"- {req}", end="")
            if req not in installed_ids:
                print("  (MISSING)")
            else:
                print()

        return 2

    print(f"All required installs are present in {local_json_path.as_posix()}")
    local_paths = {
        req_id: Path(
            next(
                install.get("path").replace("\\\\?\\", "")
                for install in local_config
                if install.get("id") == req_id
            )
        ).resolve()
        for req_id in required_install_ids
    }
    print("\nRequired install paths:")
    for req, path in local_paths.items():
        print(f"- {req:<20s}  {path.as_posix()}")

    for cmake_file in cmake_files(cmake_dir):
        print(f"\nProcessing {cmake_file.as_posix()}:")
        content = cmake_file.read_text()

        modified = False
        for install_info in required_installs:
            base = local_paths[install_info.id] if install_info.id else slt_dir
            content, did_modify = pattern_replace(content, install_info, base)
            modified |= did_modify

        if modified and not dry_run:
            cmake_file.write_text(content)
        else:
            print(f"  No changes done to {cmake_file.as_posix()}")

    return 0


if __name__ == "__main__":
    exit(main(SLT_DIR, CMAKE_DIR, REQUIRED_INSTALLS, False))
