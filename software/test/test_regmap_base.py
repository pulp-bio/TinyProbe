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

from tipy.hardware.regmap_base import (
    Access,
    BitField,
    Interface,
    Register,
    RegisterMap,
)


class TestInterface:
    def test_init(self):
        log = logging.getLogger("test")
        intf = Interface(log)
        assert intf.memory == {}
        assert intf.log is log

    def test_read_initializes_register(self):
        log = logging.getLogger("test")
        intf = Interface(log)

        value = intf.read(register_address=0x10, offset=0, width=8, reset_value=0x5)

        assert value == 0x5
        assert 0x10 in intf.memory
        assert intf.memory[0x10][0] == 0x5

    def test_read_existing_value(self):
        log = logging.getLogger("test")
        intf = Interface(log)

        intf.write(register_address=0x10, offset=0, width=8, value=0x7)
        value = intf.read(register_address=0x10, offset=0, width=8, reset_value=0x5)

        assert value == 0x7

    def test_write(self):
        log = logging.getLogger("test")
        intf = Interface(log)

        intf.write(register_address=0x10, offset=4, width=8, value=0x3)

        assert 0x10 in intf.memory
        assert intf.memory[0x10][4] == 0x3

    def test_write_multiple_offsets(self):
        log = logging.getLogger("test")
        intf = Interface(log)

        intf.write(register_address=0x10, offset=0, width=8, value=0x1)
        intf.write(register_address=0x10, offset=4, width=8, value=0x2)

        assert intf.memory[0x10][0] == 0x1
        assert intf.memory[0x10][4] == 0x2

    def test_pull_assembles_registers(self):
        log = logging.getLogger("test")
        intf = Interface(log)

        intf.write(register_address=0x10, offset=0, width=8, value=0x1)
        intf.write(register_address=0x10, offset=4, width=8, value=0x2)
        intf.write(register_address=0x20, offset=0, width=8, value=0x3)

        result = intf.pull()

        # 0x1 << 0 | 0x2 << 4 = 0x21
        assert result[0x10] == 0x21
        assert result[0x20] == 0x3

    def test_pull_returns_sorted_addresses(self):
        log = logging.getLogger("test")
        intf = Interface(log)

        intf.write(register_address=0x30, offset=0, width=8, value=0x1)
        intf.write(register_address=0x10, offset=0, width=8, value=0x2)
        intf.write(register_address=0x20, offset=0, width=8, value=0x3)

        result = intf.pull()
        addresses = list(result.keys())

        assert addresses == [0x10, 0x20, 0x30]

    def test_push(self):
        log = logging.getLogger("test")
        intf = Interface(log)

        memory_state = {
            0x10: {0: 0x1, 4: 0x2},
            0x20: {0: 0x3},
        }

        intf.push(memory_state)

        assert intf.memory == memory_state

    def test_reset(self):
        log = logging.getLogger("test")
        intf = Interface(log)

        intf.write(register_address=0x10, offset=0, width=8, value=0x1)
        intf.reset()

        assert intf.memory == {}


class TestAccess:
    def test_access_values(self):
        assert Access.RO.value == "ro"
        assert Access.RW.value == "rw"
        assert Access.WO.value == "wo"
        assert Access.RWC.value == "rw1c"
        assert Access.WOS.value == "wosc"
        assert Access.ROLH.value == "rolh"

    def test_access_str(self):
        assert str(Access.RO) == "RO"
        assert str(Access.RW) == "RW"

    def test_access_repr(self):
        assert repr(Access.RO) == "Access.RO"
        assert repr(Access.RW) == "Access.RW"


class TestBitField:
    def test_bitfield_defaults(self):
        bf = BitField()
        assert bf._name == "BitField"
        assert bf._description is None
        assert bf._reset == 0
        assert bf._value == 0
        assert bf._width == -1
        assert bf._offset == -1
        assert bf._enums is None
        assert bf._register_address == -1
        assert bf._interface is None

    def test_bitfield_with_interface(self):
        log = logging.getLogger("test")
        intf = Interface(log)

        bf = BitField()
        bf._interface = intf
        bf._register_address = 0x10
        bf._offset = 4
        bf._width = 3
        bf._reset = 0x5

        # Reading should use interface
        intf.write(0x10, 4, width=3, value=0x7)
        assert bf._interface.read(0x10, 4, width=3, reset_value=0x5) == 0x7


class TestRegister:
    def test_register_requires_interface(self):
        log = logging.getLogger("test")
        intf = Interface(log)

        reg = Register(intf)
        assert reg._interface is intf
        assert reg._address == -1
        assert reg._access == Access.RW


class TestRegisterMap:
    def test_registermap_str_requires_annotations(self):
        regmap = RegisterMap()
        # RegisterMap.__str__ uses __annotations__ which won't exist without subclassing
        # This test verifies the base class can be instantiated
        assert isinstance(regmap, RegisterMap)
