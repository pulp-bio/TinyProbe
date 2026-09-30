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

from zeroconf import ServiceInfo, Zeroconf

from .logging import setup_logging

_log = logging.getLogger().getChild("tools").getChild("mdns")


def get_devices(
    service_type: str = "_wius._udp.local.",
    service_name: str = "tinyprobe",
) -> ServiceInfo | None:
    _log.info("Resolving devices via mDNS...")
    with Zeroconf() as zc:
        result = zc.get_service_info(service_type, f"{service_name}.{service_type}")
    return result


if __name__ == "__main__":
    log = setup_logging("INFO")
    device_info = get_devices()
    if device_info:
        log.info(
            f"Found TinyProbe at {device_info.parsed_addresses()} port {device_info.port}"
        )
    else:
        log.error("TinyProbe not found.")
