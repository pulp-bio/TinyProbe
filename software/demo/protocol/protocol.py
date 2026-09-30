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

from tipy.control.methods import TinyprobeMethods
from tipy.protocol.protocol import ProtocolBase, ProtocolConfig
from tipy.tools.logging import setup_logging
from tipy.transport.implementations.dummy import TransportDummy
from tipy.transport.implementations.udp import TransportUDP
from tipy.transport.transport import TransportEndpoint, TransportProtocol


class DemoProtocolConfig(ProtocolConfig):
    pass


class DemoProtocol(ProtocolBase[DemoProtocolConfig]):
    config_model = DemoProtocolConfig

    def get_transports(self) -> tuple[TransportProtocol, TransportProtocol]:
        cmd_endpoint = TransportEndpoint("0.0.0.0:50008", "Demo Command Endpoint")
        data_endpoint = TransportEndpoint("0.0.0.0:50007", "Demo Data Endpoint")

        cmd_transport = TransportDummy(TinyprobeMethods().methods)
        cmd_transport.set_device(cmd_endpoint)
        data_transport = TransportUDP(timeout=0.1)
        data_transport.set_device(data_endpoint)

        return cmd_transport, data_transport

    def setup(self):
        self.methods.ping()

        self.hw.fpga.num_samples = 5

    def acquire(self):
        self.log.info(
            f"start_capture_delay_global_us={self.hw.fpga.start_capture_delay_global_us}"
        )
        self.hw.fpga.start_capture_delay_afe_us = 5

    def teardown(self):
        self.methods.delayms(100)
        self.methods.setloglevel(self.methods.Loglevel.INFO)


log = setup_logging("DEBUG")

protocol = DemoProtocol(Path(__file__).parent / "config.json")
log.info("Protocol initialized")

protocol.execute_setup()
log.info("Protocol setup complete")

with protocol.session.receive():
    protocol.execute_acquire()
log.info("Protocol acquisition complete")

protocol.execute_teardown()
log.info("Protocol teardown complete")

data = protocol.session.get_received_data()
log.info(f"Received {len(data[0])} shots, {len(data[1])} packets")
