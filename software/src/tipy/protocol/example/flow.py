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

import math
from ipaddress import IPv4Address

from ...control.methods import TinyprobeMethods
from ...transport.implementations.dummy import TransportDummy
from ...transport.implementations.tcp import TransportTCP
from ...transport.implementations.udp import TransportUDP
from ...transport.transport import TransportEndpoint, TransportProtocol
from ..protocol import ProtocolBase
from .config import ProtocolExampleConfig


class ProtocolExample(ProtocolBase[ProtocolExampleConfig]):
    config_model = ProtocolExampleConfig
    num_packets: int

    TX_START_DELAY_US = 5
    TR_SW_DELAY_US = 1.1

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
        bytes_per_shot = (
            self.config.fpga.fifo_depth * len(self.config.fpga.lvds_lanes) * 20 / 8
        )
        packets_per_shot = math.ceil(
            bytes_per_shot / self.config.transport.bulk_packet_size_bytes
        )
        bytes_per_shot = packets_per_shot * self.config.transport.bulk_packet_size_bytes
        duration_per_shot = (
            bytes_per_shot * 8 / self.config.transport.bulk_throughput_bps
        )

        if duration_per_shot > self.config.fpga.shot_period_ms / 1e3:
            self.log.warning(
                "Configured bulk transport may not be able to keep up with the acquisition"
            )
            self.log.warning(
                f"Estimated time to transfer each shot is {duration_per_shot * 1e3:.2f} ms, but shot period is only {self.config.fpga.shot_period_ms} ms"
            )

            budget_bytes = (
                self.config.fpga.shot_period_ms
                / 1e3
                * self.config.transport.bulk_throughput_bps
                / 8
            )
            max_packets = int(
                budget_bytes // self.config.transport.bulk_packet_size_bytes
            )
            max_raw_bytes = max_packets * self.config.transport.bulk_packet_size_bytes

            self.log.warning("Consider reducing:")
            ok_num_samples = (
                max_raw_bytes * 8 // (20 * len(self.config.fpga.lvds_lanes))
            )
            self.log.warning(
                f"- Number of samples (currently {self.config.fpga.fifo_depth}, max {ok_num_samples})"
            )
            ok_num_lanes = max_raw_bytes * 8 // (20 * self.config.fpga.fifo_depth)
            self.log.warning(
                f"- Number of LVDS lanes (currently {len(self.config.fpga.lvds_lanes)}, max {ok_num_lanes})"
            )

            self.log.warning("Consider increasing:")
            self.log.warning(
                f"- Shot period (currently {self.config.fpga.shot_period_ms} ms, min {duration_per_shot * 1e3:.2f} ms)"
            )
        else:
            self.log.debug(
                f"Estimated link congestion: {duration_per_shot / (self.config.fpga.shot_period_ms / 1e3):.1%}"
            )

    def setup_fpga(self):
        config = self.config.fpga

        self.check_throughput()

        self.num_packets = math.ceil(
            config.fifo_depth
            * 20
            * len(config.lvds_lanes)
            / 8
            / 1000  # Firmware will convert from 1000 byte packets to the packet size specified in the firmware
        )

        self.hw.fpga.default_setup(
            lvds_lanes=config.lvds_lanes,
            num_samples=config.fifo_depth,
            meas_period_us=config.shot_period_ms * 1000,
            num_shots=config.num_shots,
            afe_clk_fast=config.afe_clk_hispeed,
            tx_bf_clk_fast=config.txbf_clk_hispeed,
            fpga_core_clk_fast=config.fpga_clk_hispeed,
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

        # dcdc_delay_off_us = self.TX_START_DELAY_US + self.TR_SW_DELAY_US
        # read_fifo_delay_us = (
        #     3
        #     + self.config.fpga.fifo_depth / self.hw.fpga.freq_afe_hz * 1e6
        #     - dcdc_delay_off_us
        # )

        self.acquire_power_on()  # Methods 0 - 6

        self.methods.setloglevel(self.methods.Loglevel.INFO)  # Method 7

        if config.onboard_looping:
            self.methods.delayms(1)  # Method 8
            self.methods.ping()  # Method 9

            self.methods.loop(
                config.num_frames, 8
            )  # Loop back to method 8 for num_frames times
        else:
            for _ in range(config.num_frames):
                # Trigger shot does not work when the AFE and TX are not initialized
                # self.methods.triggershot(
                #     num_shots=self.config.fpga.num_shots,
                #     num_packets=self.num_packets,
                #     delay_dcdc_off_ns=int(dcdc_delay_off_us * 1e3),
                #     delay_read_fifo_ns=int(read_fifo_delay_us * 1e3),
                # )
                self.methods.delayms(
                    1
                )  # Simulate the time it would take to acquire a shot
                self.methods.ping()  # Simulate some communication

        self.methods.setloglevel(self.methods.Loglevel.TRACE)

        self.acquire_power_off()

    def teardown(self):
        pass
