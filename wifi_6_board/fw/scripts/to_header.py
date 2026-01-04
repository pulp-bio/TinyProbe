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

import argparse


def parse_conf_file(file_path: str) -> dict:
    """Parse a simple configuration file with KEY=VALUE pairs.
    
    Args:
        file_path (str): Path to the configuration file.
        
    Returns:
        dict: A dictionary with keys and values from the file.
        
    Raises:
        FileNotFoundError: If the file does not exist.
    """

    env_vars = {}

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                # Remove surrounding quotes if present
                val = val.strip().strip('"').strip("'")
                env_vars[key.strip()] = val

    return env_vars


def write_header_file(header_path: str, configs: dict) -> None:
    """Write the configurations to a C header file.

    Args:
        header_path (str): Path to the output C header file.
        configs (dict): Dictionary of configurations to write.

    Returns:
        None

    Raises:
        IOError: If there is an error writing to the file.
    """

    # Create a unique include guard based on the header filename
    guard = header_path.upper().replace(".", "_").replace("/", "_").replace("\\", "_")
    with open(header_path, "w") as f:
        f.write(f"/* Auto-generated C header file from file {header_path} */\n")
        f.write(f"#ifndef {guard}\n")
        f.write(f"#define {guard}\n\n")
        for key, val in configs.items():
            # Emit the value as a string literal
            f.write(f'#define {key} "{val}"\n')
        f.write(f"\n#endif /* {guard} */\n")

    print(f"Wrote {len(configs)} configurations to {header_path}")
    for key, val in configs.items():
        print("  - {}: {}".format(key, val))


def main():
    parser = argparse.ArgumentParser(
        description="Generate a C header file from a configuration file"
    )
    parser.add_argument("conf_file", help="Path to the configuration file")
    parser.add_argument("header_file", help="Path to the output C header file")
    args = parser.parse_args()

    configs = parse_conf_file(args.conf_file)
    write_header_file(args.header_file, configs)


if __name__ == "__main__":
    main()
