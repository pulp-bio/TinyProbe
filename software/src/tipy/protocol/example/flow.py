"""
Copyright (C) 2026 ETH Zurich. All rights reserved.

Authors:
    - Cedric Hirschi, ETH Zurich
    - Federico Villani, ETH Zurich

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

from ...control.methods import TinyprobeMethods
from ...transport.implementations.dummy import TransportDummy
from ...transport.implementations.tcp import TransportTCP
from ...transport.implementations.udp import TransportUDP
from ...transport.transport import TransportEndpoint, TransportProtocol
from ..protocol import ProtocolBase
from .config import LANE_PACKET_BYTES, SAMPLES_PER_LANE_PACKET, ProtocolExampleConfig


class ProtocolExample(ProtocolBase[ProtocolExampleConfig]):
    config_model = ProtocolExampleConfig
    num_packets: int

    def get_transports(self) -> tuple[TransportProtocol, TransportProtocol]:
        if self.config.transport.command_dummy:
            transport_command = TransportDummy(TinyprobeMethods().methods)
        else:
            transport_command = TransportTCP(self.config.transport.command.timeout)

            if self.config.transport.command_resolve:
                devices = TransportTCP.get_available()
                if not devices:
                    raise RuntimeError("TinyProbe device not found on the network.")
                elif len(devices) > 1:
                    self.log.warning(
                        f"Multiple TinyProbe devices found on the network, using the first one: {devices[0].device}"
                    )

                self.config.transport.command.ip = IPv4Address(devices[0].device)
                self.log.info(
                    f"Resolved TinyProbe device at {self.config.transport.command.ip}:{self.config.transport.command.port}"
                )

        device_cmd = TransportEndpoint(
            device=str(self.config.transport.command.ip)
            + ":"
            + str(self.config.transport.command.port),
            description="Command Interface",
        )
        transport_command.set_device(device_cmd)

        transport_bulk = TransportUDP(self.config.transport.bulk.timeout)
        device_bulk = TransportEndpoint(
            device=str(self.config.transport.bulk.ip)
            + ":"
            + str(self.config.transport.bulk.port),
            description="Bulk Interface",
        )
        transport_bulk.set_device(device_bulk)

        return transport_command, transport_bulk

    def check_throughput(self) -> None:
        frame_bytes = LANE_PACKET_BYTES * len(self.config.fpga.lvds_lanes)
        duration_per_frame = frame_bytes * 8 / self.config.transport.bulk_throughput_bps
        frame_period_s = (
            self.config.fpga.shot_period_ms * max(1, self.config.fpga.num_shots) / 1e3
        )
        if duration_per_frame > frame_period_s:
            self.log.warning(
                f"Estimated transfer time is {duration_per_frame * 1e3:.2f} ms per frame "
                f"for an acquisition period of {frame_period_s * 1e3:.2f} ms"
            )

    def setup_fpga(self):
        config = self.config.fpga
        if self.config.transport.bulk_packet_size_bytes != LANE_PACKET_BYTES:
            raise ValueError(
                f"Dual-SPI firmware uses {LANE_PACKET_BYTES} payload bytes per packet"
            )
        if not 1 <= config.fifo_depth <= SAMPLES_PER_LANE_PACKET:
            raise ValueError(
                f"Sample count per lane must be between 1 and {SAMPLES_PER_LANE_PACKET}"
            )
        if not config.lvds_lanes:
            raise ValueError("At least one FPGA acquisition lane must be enabled")

        self.check_throughput()
        self.num_packets = len(set(config.lvds_lanes))

        self.hw.fpga.default_setup(
            lvds_lanes=config.lvds_lanes,
            num_samples=config.fifo_depth,
            meas_period_us=config.shot_period_ms * 1000,
            num_shots=config.num_shots,
            afe_clk_fast=config.afe_clk_hispeed,
            tx_bf_clk_fast=config.txbf_clk_hispeed,
            capture_delay_afe_us=config.afe_startcapt_delay_us,
        )
        self.hw.fpga.trigger_mcu_source = config.mcu_interrupt_src

    def setup(self):
        self.setup_fpga()

    def acquire_power_on(self):
        self.methods.controlpower(self.methods.Powerdomain.POS_HV, True)
        self.methods.controlpower(self.methods.Powerdomain.NEG_HV, True)
        self.methods.controlpower(self.methods.Powerdomain.NEG_5V, True)
        self.methods.controlpower(self.methods.Powerdomain.POS_HV, True)
        self.methods.controlpower(self.methods.Powerdomain.LVDS_2V5, True)

        self.hw.fpga.powerdown_afe_global = False

        self.methods.delayms(4)

    def acquire_power_off(self):
        self.methods.controlpower(self.methods.Powerdomain.LVDS_2V5, False)
        self.hw.fpga.powerdown_afe_global = True
        self.methods.controlpower(self.methods.Powerdomain.POS_HV, False)
        self.methods.controlpower(self.methods.Powerdomain.NEG_HV, False)
        self.methods.controlpower(self.methods.Powerdomain.NEG_5V, False)

    def acquire(self):
        config = self.config.acquisition

        self.acquire_power_on()
        self.methods.setloglevel(self.methods.Loglevel.INFO)

        # Register 11 controls the number of averaged captures inside each returned frame.
        frames_per_request = 256 if config.onboard_looping else 1
        for frame_index in range(0, config.num_frames, frames_per_request):
            self.methods.triggershot(
                num_shots=min(frames_per_request, config.num_frames - frame_index),
                num_packets=self.num_packets,
            )

        self.methods.setloglevel(self.methods.Loglevel.TRACE)

        self.acquire_power_off()

    def teardown(self):
        pass
