from pathlib import Path
import json
import re


REQUIRED_INSTALLS = ("commander", "gcc-arm-none-eabi", "simplicity-sdk", "wiseconnect")

HOME_DIR = Path.home()
SLT_DIR = HOME_DIR / ".silabs" / "slt"

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
CMAKE_DIR = PROJECT_ROOT / "cmake_gcc"


def cmake_files(cmake_dir: Path) -> list[Path]:
    cmake_files = []

    for item in cmake_dir.glob("*.cmake"):
        if item.stem.endswith("_project"):
            continue

        cmake_files.append(item.resolve())

    return cmake_files


# # List eveything in the SLT_DIR
# items = list(SLT_DIR.glob("*"))
# for item in items:
#     print(("D" if item.is_dir() else " ") + "  " + str(item))

# Read local.json if it exists
local_json_path = SLT_DIR / "local.json"
if local_json_path.exists():
    with open(local_json_path, "r") as f:
        local_config = json.load(f)

    # print("\nInstalls:")
    # for install in local_config:
    #     install["path"] = install.get("path").replace("\\\\?\\", "")

    #     print(
    #         f"- {install.get("id")}: {Path(install.get("path")).resolve().relative_to(SLT_DIR).as_posix()}"
    #     )

    if not all(
        any(install.get("id") == req for install in local_config)
        for req in REQUIRED_INSTALLS
    ):
        print("Warning: Not all required installs are present in local.json")
    else:
        print("All required installs are present in local.json")
        REQUIRED_INSTALL_PATHS = {
            req: Path(
                next(
                    install.get("path").replace("\\\\?\\", "")
                    for install in local_config
                    if install.get("id") == req
                )
            ).resolve()
            for req in REQUIRED_INSTALLS
        }
        print("\nRequired install paths:")
        for req, path in REQUIRED_INSTALL_PATHS.items():
            print(f"- {req:<20s}  {path.as_posix()}")

        print("\nProcessing CMake files:")
        for cmake_file in cmake_files(CMAKE_DIR):
            print(f"\nProcessing {cmake_file.as_posix()}:")

            with open(cmake_file, "r") as f:
                content = f.read()

            modified = False

            pattern = r"wisec[a-zA-Z0-9]+/p/components"
            new_path = (
                Path(REQUIRED_INSTALL_PATHS["wiseconnect"].parent.stem)
                / "p"
                / "components"
            ).as_posix()

            matches = re.findall(pattern, content)
            for match in matches:
                new_content = content.replace(match, new_path)
                if new_content != content:
                    # Show differences between old and new content (Changed lines)
                    for line in content.splitlines():
                        if match in line:
                            print(f"  - {line}")
                            print(f"  + {line.replace(match, new_path)}")

                    content = new_content
                    modified = True

            pattern = r"\".*/simple[a-zA-Z0-9]+/p"
            new_path = '"' + (Path(REQUIRED_INSTALL_PATHS["simplicity-sdk"])).as_posix()

            matches = re.findall(pattern, content)
            for match in matches:
                new_content = content.replace(match, new_path)
                if new_content != content:
                    # Show differences between old and new content (Changed lines)
                    for line in content.splitlines():
                        if match in line:
                            print(f"- {line}")
                            print(f"+ {line.replace(match, new_path)}")

                    content = new_content
                    modified = True

            pattern = r"PKG_PATH \".*/.silabs/slt/installs\""
            new_path = f'PKG_PATH "{SLT_DIR.as_posix()}/installs"'

            matches = re.findall(pattern, content)
            for match in matches:
                new_content = content.replace(match, new_path)
                if new_content != content:
                    # Show differences between old and new content (Changed lines)
                    for line in content.splitlines():
                        if match in line:
                            print(f"- {line}")
                            print(f"+ {line.replace(match, new_path)}")

                    content = new_content
                    modified = True

            if modified:
                with open(cmake_file, "w") as f:
                    f.write(content)
                print(f"  Updated {cmake_file.as_posix()}")
            else:
                print(f"  No changes needed for {cmake_file.as_posix()}")

else:
    print(f"local.json does not exist in {SLT_DIR.as_posix()}")
