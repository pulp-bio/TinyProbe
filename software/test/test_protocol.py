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

import pytest
from pydantic import Field

from tipy.control.methods import TinyprobeMethods
from tipy.protocol.hardware.fpga import ConfigFPGA
from tipy.protocol.protocol import (
    ProtocolBase,
    ProtocolConfig,
    ProtocolLifecycleState,
    Session,
)
from tipy.transport.implementations.dummy import TransportDummy
from tipy.transport.transport import TransportEndpoint, TransportProtocol

from .common import DATA_DIR


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


class ProtocolAcquisitionConfig(ProtocolConfig):
    num_frames: int = 1


class ProtocolUltrasoundSimpleConfig(ProtocolConfig):
    fpga: ConfigFPGA = Field(default_factory=ConfigFPGA)
    acquisition: ProtocolAcquisitionConfig = Field(
        default_factory=ProtocolAcquisitionConfig
    )
    transport: ProtocolTransportConfig = Field(default_factory=ProtocolTransportConfig)


# Adapted from ultrasound_simple Protocol for Dummy transports
class TestProtocol(ProtocolBase[ProtocolUltrasoundSimpleConfig]):
    __test__ = False
    config_model = ProtocolUltrasoundSimpleConfig
    num_packets: int

    TX_START_DELAY_US = 5
    TR_SW_DELAY_US = 1.1

    def get_transports(self) -> tuple[TransportProtocol, TransportProtocol]:
        return make_dummy_transports(self.config.transport.command.ip.exploded)

    def setup_fpga(self):
        config = self.config.fpga

        self.num_packets = math.ceil(
            config.fifo_depth * 20 * len(config.lvds_lanes) / 8 / 1000
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

    def power_up_acquisition(self):
        self.methods.controlpower(self.methods.Powerdomain.POS_HV, True)
        self.methods.controlpower(self.methods.Powerdomain.NEG_HV, True)
        self.methods.controlpower(self.methods.Powerdomain.NEG_5V, True)
        self.methods.controlpower(self.methods.Powerdomain.POS_HV, True)
        self.methods.controlpower(self.methods.Powerdomain.LVDS_2V5, True)

        self.hw.fpga.powerdown_afe_global = False

        self.methods.delayms(4)

    def acquire(self):
        config = self.config.acquisition

        self.power_up_acquisition()

        dcdc_delay_off_us = self.TX_START_DELAY_US + self.TR_SW_DELAY_US
        read_fifo_delay_us = (
            3
            + self.config.fpga.fifo_depth / self.hw.fpga.freq_afe_hz * 1e6
            - dcdc_delay_off_us
        )

        for _ in range(config.num_frames):
            self.methods.triggershot(
                num_shots=self.config.fpga.num_shots,
                num_packets=self.num_packets,
                delay_dcdc_off_ns=int(dcdc_delay_off_us * 1e3),
                delay_read_fifo_ns=int(read_fifo_delay_us * 1e3),
            )

    def teardown_power(self):
        self.methods.controlpower(self.methods.Powerdomain.LVDS_2V5, False)
        self.hw.fpga.powerdown_afe_global = True
        self.methods.controlpower(self.methods.Powerdomain.POS_HV, False)
        self.methods.controlpower(self.methods.Powerdomain.NEG_HV, False)
        self.methods.controlpower(self.methods.Powerdomain.NEG_5V, False)

    def teardown(self):
        self.teardown_power()


def test_ultrasound_protocol_init():
    config_path = DATA_DIR / "protocol_ultrasound_simple.json"

    TestProtocol(config_path)


def test_protocol_protocol_run():
    config_path = DATA_DIR / "protocol_ultrasound_simple.json"

    protocol = TestProtocol(config_path)

    commands = protocol.run()

    assert isinstance(protocol.config, ProtocolUltrasoundSimpleConfig)
    assert set(commands) == {"setup", "acquire", "teardown"}
    assert sum(len(phase_commands) for phase_commands in commands.values()) > 0
    assert protocol.lifecycle_state == ProtocolLifecycleState.TORN_DOWN


def test_protocol_protocol_uses_shared_session():
    config_path = DATA_DIR / "protocol_ultrasound_simple.json"
    session = Session(*make_dummy_transports("shared-session"))

    protocol_a = TestProtocol(config_path, session=session)
    protocol_b = TestProtocol(config_path, session=session)

    setup_commands = protocol_a.execute_setup()
    acquire_commands = protocol_a.execute_acquire()
    teardown_commands = protocol_b.run(("setup", "acquire", "teardown"))["teardown"]

    assert protocol_a.session is session
    assert protocol_b.session is session
    assert protocol_a.hw is session.hw
    assert protocol_b.hw is session.hw
    assert protocol_a.hw.fpga is session.hw.fpga
    assert protocol_b.session.command_client is session.command_client
    assert len(setup_commands) > 0
    assert len(acquire_commands) > 0
    assert len(teardown_commands) > 0
    assert len(session.command_client.batch_requests) == len(teardown_commands)


def test_ultrasound_protocol_plan_then_execute_setup():
    config_path = DATA_DIR / "protocol_ultrasound_simple.json"
    protocol = TestProtocol(config_path)

    planned_setup = protocol.plan_setup()

    assert protocol.lifecycle_state == ProtocolLifecycleState.INITIAL
    assert len(planned_setup) > 0

    executed_setup = protocol.execute_setup()

    assert executed_setup == planned_setup
    assert protocol.lifecycle_state == ProtocolLifecycleState.SETUP_COMPLETE


def test_ultrasound_protocol_requires_setup_before_acquire():
    config_path = DATA_DIR / "protocol_ultrasound_simple.json"
    protocol = TestProtocol(config_path)

    with pytest.raises(RuntimeError, match="Setup must be executed before acquire"):
        protocol.execute_acquire()


def test_ultrasound_protocol_allows_multiple_acquires_before_teardown():
    config_path = DATA_DIR / "protocol_ultrasound_simple.json"
    protocol = TestProtocol(config_path)

    protocol.execute_setup()
    first = protocol.execute_acquire()
    second = protocol.execute_acquire()
    teardown = protocol.execute_teardown()

    assert len(first) > 0
    assert len(second) > 0
    assert len(teardown) > 0
    assert protocol.lifecycle_state == ProtocolLifecycleState.TORN_DOWN


def test_ultrasound_protocol_allows_teardown_after_setup_without_acquire():
    config_path = DATA_DIR / "protocol_ultrasound_simple.json"
    protocol = TestProtocol(config_path)

    protocol.execute_setup()
    teardown = protocol.execute_teardown()

    assert len(teardown) > 0
    assert protocol.lifecycle_state == ProtocolLifecycleState.TORN_DOWN


def make_dummy_transports(
    command_device: str,
) -> tuple[TransportProtocol, TransportProtocol]:
    transport_command = TransportDummy(TinyprobeMethods().methods)
    device_cmd = TransportEndpoint(
        device=command_device, description="Command Interface"
    )
    transport_command.set_device(device_cmd)

    transport_bulk = TransportDummy()
    device_bulk = TransportEndpoint(device="bulk-session", description="Data Interface")
    transport_bulk.set_device(device_bulk)

    return transport_command, transport_bulk
