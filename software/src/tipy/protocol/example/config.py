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

from ipaddress import IPv4Address

from pydantic import Field

from ..hardware.fpga import ConfigFPGA
from ..protocol import ProtocolConfig


class ProtocolAcquisitionConfig(ProtocolConfig):
    num_frames: int = 1
    onboard_looping: bool = True


class ProtocolSingleTransportConfig(ProtocolConfig):
    ip: IPv4Address = IPv4Address("0.0.0.0")
    port: int
    timeout: float = 5.0


class ProtocolTransportConfig(ProtocolConfig):
    command: ProtocolSingleTransportConfig = ProtocolSingleTransportConfig(port=50008)
    command_dummy: bool = False  # Whether to use a dummy command transport
    command_resolve: bool = True  # Whether to resolve mDNS addresses

    bulk: ProtocolSingleTransportConfig = ProtocolSingleTransportConfig(
        port=50007, timeout=0.5
    )
    bulk_packet_size_bytes: int = 3000  # Size of each packet sent by the bulk transport
    bulk_throughput_bps: float = (
        32e6  # Approximate throughput of the bulk transport in bits per second
    )


class ProtocolExampleConfig(ProtocolConfig):
    fpga: ConfigFPGA = Field(default_factory=ConfigFPGA)
    acquisition: ProtocolAcquisitionConfig = Field(
        default_factory=ProtocolAcquisitionConfig
    )
    transport: ProtocolTransportConfig = Field(default_factory=ProtocolTransportConfig)
