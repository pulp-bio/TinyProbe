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

from pathlib import Path

from tipy.protocol.example.flow import ProtocolExample
from tipy.tools.logging import setup_logging

log = setup_logging("DEBUG")

protocol = ProtocolExample(Path(__file__).parent / "demo_acquisition.json")
log.info("Protocol initialized")

protocol.execute_setup()
log.info("Protocol setup complete")

with protocol.session.receive():
    protocol.execute_acquire()
log.info("Protocol acquisition complete")

data = protocol.session.get_received_data()
log.info(f"Received {len(data[0])} shots, {len(data[1])} packets")
