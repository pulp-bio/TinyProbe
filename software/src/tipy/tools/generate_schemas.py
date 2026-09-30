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

import argparse
import importlib
import json
import logging
from pathlib import Path

from ..protocol.protocol import ProtocolBase, camelcase_to_snakecase
from ..tools.logging import setup_logging

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
PACKAGE_DIR = Path(__file__).resolve().parent.parent
PROTOCOL_MODULE = "tipy.protocol"
MODALITIES_DIR = PACKAGE_DIR / "protocol"

SCHEMA_FILENAME_TEMPLATE = "protocol_{}.schema.json"
SCHEMA_FILEMATCH_TEMPLATE = "*{}*.json"


log = logging.getLogger().getChild("tools").getChild("schemas")


def import_modalities(
    workspace_dir: Path, modalities_dir: Path, protocol_module: str
) -> None:
    log.info(
        f"Importing all modalities from {modalities_dir.relative_to(workspace_dir).as_posix()!r}"
    )
    for file in modalities_dir.glob("./**/flow.py"):
        file_rel = file.relative_to(workspace_dir).as_posix()
        log.info(f"- Importing protocol from {file_rel!r}")
        protocol_path = file.relative_to(modalities_dir).with_suffix("")
        log.debug(
            f"  Protocol relative to modalities dir: {protocol_path.as_posix()!r}"
        )
        protocol_import = f"{protocol_module}.{'.'.join(protocol_path.parts)}"
        log.debug(f"  Importing as {protocol_import!r}")
        importlib.import_module(protocol_import)


def generate_schemas(output_dir: Path, workspace_dir: Path) -> None:
    log.info(
        f"Generating schemas into {output_dir.relative_to(workspace_dir).as_posix()!r}"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    settings_schemas = []

    for subclass in ProtocolBase.__subclasses__():
        if not hasattr(subclass, "config_model"):
            continue

        name = subclass.__name__.replace("Protocol", "")
        snake_name = camelcase_to_snakecase(name)
        config_model = subclass.config_model
        log.debug(f"  Protocol ID: {snake_name!r}")
        log.debug(f"  Config model: {config_model.__name__!r}")

        schema = config_model.model_json_schema()
        schema_filename = SCHEMA_FILENAME_TEMPLATE.format(snake_name)
        schema_path = output_dir / schema_filename

        with schema_path.open("w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)

        rel_schema_path = schema_path.relative_to(workspace_dir).as_posix()
        log.info(f"- Generated schema for {subclass.__name__!r} at {rel_schema_path!r}")

        settings_schemas.append(
            {
                "fileMatch": [SCHEMA_FILEMATCH_TEMPLATE.format(snake_name)],
                "url": f"./{rel_schema_path}",
            }
        )

    vscode_dir = workspace_dir / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    settings_file = vscode_dir / "settings.json"

    settings = {}
    try:
        with settings_file.open("r", encoding="utf-8") as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    existing_schemas = settings.get("json.schemas", [])

    # Remove existing protocol schemas to prevent duplicates
    existing_schemas = [
        s
        for s in existing_schemas
        if not (
            (url := s.get("url"))
            and isinstance(url, str)
            and url.endswith(".schema.json")
            and "protocol_" in url
        )
    ]

    existing_schemas.extend(settings_schemas)
    settings["json.schemas"] = existing_schemas

    with settings_file.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

    settings_rel = settings_file.relative_to(workspace_dir).as_posix()
    log.info(f"Updated '{settings_rel}' with JSON schema mappings.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate JSON schemas for all Protocol configs"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT_DIR / "schemas",
        help="Directory to save the schemas",
    )
    parser.add_argument(
        "-w",
        "--workspace-dir",
        type=Path,
        default=ROOT_DIR,
        help="Workspace root directory",
    )
    parser.add_argument(
        "-d",
        "--modalities-dir",
        type=Path,
        default=MODALITIES_DIR,
        help="Modalities directory",
    )
    parser.add_argument(
        "-m",
        "--protocol-module",
        type=str,
        default=PROTOCOL_MODULE,
        help="Protocol module",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    args = parser.parse_args()

    if args.verbose:
        setup_logging("DEBUG")
    else:
        setup_logging("INFO")

    import_modalities(args.workspace_dir, args.modalities_dir, args.protocol_module)
    generate_schemas(args.output_dir, args.workspace_dir)
