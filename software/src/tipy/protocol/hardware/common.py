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


def enum_validator(name: str, prefix: str, v: object, target):
    if isinstance(v, target):
        return v

    if isinstance(v, str):
        value = v.strip()

        if value.isdigit():
            return target(int(value))

        enum_name = value.upper()
        if not enum_name.startswith(prefix):
            enum_name = prefix + enum_name

        try:
            return getattr(target, enum_name)
        except AttributeError:
            pass

    try:
        return target(v)
    except ValueError:
        raise ValueError(
            f"Invalid {name}: {v!r}. Must be one of {[e.name for e in target]} or {[e.value for e in target]}"
        )
