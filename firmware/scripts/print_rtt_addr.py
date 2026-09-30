"""
Copyright (C) 2026 ETH Zurich. All rights reserved.

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

import pathlib
import re
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: print_rtt_addr.py <map-file>", file=sys.stderr)
        return 2

    map_file = pathlib.Path(sys.argv[1])
    if not map_file.exists():
        print(
            f"Map file not found: {map_file}. Run a successful build first.",
            file=sys.stderr,
        )
        return 1

    text = map_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"0x([0-9A-Fa-f]+)\s+_SEGGER_RTT\b", text)
    if match is None:
        print(f"Could not find _SEGGER_RTT in {map_file}", file=sys.stderr)
        return 1

    print(f"0x{match.group(1)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
