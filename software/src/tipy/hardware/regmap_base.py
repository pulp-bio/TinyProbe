"""
Register map base definitions.

This file is part of embgen. Do not edit manually.
"""

from enum import Enum as BaseEnum
from logging import Logger
from typing import Optional, Any, Protocol


class RegisterMapInterface(Protocol):
    """Interface for register map hardware access.

    Implement this protocol to provide custom hardware access behavior.
    The default implementation `Interface` provides an in-memory simulation.
    """

    def read(
        self, register_address: int, offset: int, width: int, reset_value: int
    ) -> int:
        """Read a bitfield value from a register.

        Args:
            register_address: The address of the register.
            offset: The bit offset within the register.
            width: The width of the bitfield.
            reset_value: The reset value to use if not previously written.

        Returns:
            The value read from the register at the given offset.
        """
        ...

    def write(self, register_address: int, offset: int, width: int, value: int) -> None:
        """Write a bitfield value to a register.

        Args:
            register_address: The address of the register.
            offset: The bit offset within the register.
            width: The width of the bitfield.
            value: The value to write.
        """
        ...


class Interface(RegisterMapInterface):
    """Default hardware interface implementation (in-memory simulation)."""

    def __init__(self, log: Logger):
        self.memory: dict[int, dict[int, int]] = {}
        self.log: Logger = log

    def read(
        self, register_address: int, offset: int, width: int, reset_value: int
    ) -> int:
        if register_address not in self.memory:
            self.log.debug(f"init  {register_address=}")
            self.memory[register_address] = {}
        if offset not in self.memory[register_address]:
            self.log.debug(f"init  {register_address=}, {offset=}")
            self.memory[register_address][offset] = reset_value
        self.log.debug(
            f"read  {register_address=}, {offset=}, {width=}, {reset_value=}"
        )
        return self.memory[register_address][offset]

    def write(self, register_address: int, offset: int, width: int, value: int) -> None:
        if register_address not in self.memory:
            self.log.debug(f"init  {register_address=}")
            self.memory[register_address] = {}

        # Validate value against width
        max_value = (1 << width) - 1
        if value < 0:
            raise ValueError(f"Value {value} cannot be negative")
        if value > max_value:
            raise ValueError(
                f"Value {value} exceeds maximum {max_value} for width {width}"
            )

        self.memory[register_address][offset] = value
        self.log.debug(f"write {register_address=}, {offset=}, {width=}, {value=}")

    def pull(self) -> dict[int, int]:
        result = {a: sum(v << o for o, v in r.items()) for a, r in self.memory.items()}
        return dict(sorted(result.items()))

    def push(self, memory: dict[int, dict[int, int]]) -> None:
        self.memory = memory

    def reset(self) -> None:
        self.memory = {}


class Access(BaseEnum):
    """Register access types."""

    RO = "ro"
    RW = "rw"
    WO = "wo"
    RWC = "rw1c"
    WOS = "wosc"
    ROLH = "rolh"

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return "Access." + str(self)


class BitField:
    """Base class for register bitfields."""

    # Class-level metadata (for documentation/introspection)
    _name: str = "BitField"
    _description: Optional[str] = None
    _reset: int = 0
    _width: int = -1
    _offset: int = -1
    _enums: Any = None

    def __init__(self) -> None:
        # Instance-level state (each instance has its own copy)
        self._value: int = self._reset
        self._register_address: int = -1
        self._interface: Optional[RegisterMapInterface] = None
        self._access: Access = Access.RW

    def reset(self) -> None:
        """Reset the bitfield to its initial state."""
        # Skip read-only bitfields - they can't be reset by writing
        if self._access in [Access.RO]:
            return

        # Convert reset value to enum if this bitfield has enums
        reset_value = (
            self._enums(self._reset) if self._enums is not None else self._reset
        )
        self.value = reset_value

    def is_valid(self, value: int | BaseEnum) -> bool:
        """Check if a value is valid for this bitfield.

        Args:
            value: The value to validate.

        Returns:
            True if the value is valid, False otherwise.
        """
        if self._enums is not None:
            return isinstance(value, self._enums)
        if not isinstance(value, int):
            return False
        return 0 <= value < (1 << self._width)

    @property
    def maximum(self) -> int:
        """Get the maximum integer value for this bitfield.

        Returns:
            The maximum valid integer value.
        """
        return (1 << self._width) - 1

    def __str__(self) -> str:
        """Return a human-readable representation of the bitfield."""
        try:
            if self._interface:
                val = self.value
                if isinstance(val, BaseEnum):
                    return f"{self._name}: {val.name} [bits {self._offset}:{self._offset + self._width - 1}, access={self._access}]"
                return f"{self._name}: {val} [bits {self._offset}:{self._offset + self._width - 1}, access={self._access}]"
        except RuntimeError:
            pass
        return f"{self._name} [bits {self._offset}:{self._offset + self._width - 1}, reset={self._reset}, access=unbound]"

    def __repr__(self) -> str:
        return f"{self._name}(value={self.value}, reset={self._reset}, width={self._width}, offset={self._offset}, access={self._access})"

    def _set_interface(
        self, register_address: int, interface: RegisterMapInterface, access: Access
    ) -> None:
        self._register_address = register_address
        self._interface = interface
        self._access = access

    @property
    def value(self) -> int | BaseEnum:
        if not self._interface:
            raise RuntimeError(f"Interface not set for bitfield {self._name}")

        if self._access not in [Access.RO, Access.RW, Access.ROLH]:
            raise RuntimeError(
                f"BitField {self._name} is not readable (access={self._access})"
            )

        raw_value = self._interface.read(
            self._register_address, self._offset, self._width, self._reset
        )
        if self._enums is not None:
            return self._enums(raw_value)
        return raw_value

    @value.setter
    def value(self, value: int | BaseEnum) -> None:
        if not self._interface:
            raise RuntimeError(f"Interface not set for bitfield {self._name}")

        if self._access not in [
            Access.WO,
            Access.RW,
            Access.RWC,
            Access.WOS,
            Access.ROLH,
        ]:
            raise RuntimeError(
                f"BitField {self._name} is not writable (access={self._access})"
            )

        if self._enums is not None:
            if not isinstance(value, BaseEnum):
                raise TypeError(
                    f"{value=} of BitField {self._name} must be of type {type(BaseEnum).__name__}, not {type(value).__name__}"
                )
            int_value = value.value
        else:
            if not isinstance(value, int):
                raise TypeError(
                    f"{value=} of BitField {self._name} must be an int when no enums are defined"
                )
            if value >= 2**self._width:
                raise ValueError(
                    f"{value=} exceeds width={self._width} of BitField {self._name} (max_value={2**self._width - 1})"
                )
            elif value < 0:
                raise ValueError(
                    f"{value=} of BitField {self._name} cannot be negative"
                )
            int_value = value

        self._interface.write(
            self._register_address, self._offset, self._width, int(int_value)
        )

    @property
    def raw(self) -> int:
        """Read the raw bitfield value."""
        return (
            (self.value if isinstance(self.value, int) else self.value.value)
            & ((1 << self._width) - 1)
        ) << self._offset


class Register:
    """Base class for hardware registers."""

    # Class-level metadata
    _name: str = "Register"
    _description: Optional[str] = None
    _address: int = -1

    def __init__(self, interface: RegisterMapInterface) -> None:
        """Initialize register with interface.

        Note: Subclasses should override this to create BitField instances.
        """
        # Instance-level state
        self._interface: RegisterMapInterface = interface
        self._access: Access = Access.RW

    def reset(self) -> None:
        """Reset the register to its initial state."""
        # Reset instance-level BitFields
        for attr_name, attr_value in self.__dict__.items():
            if not attr_name.startswith("_") and isinstance(attr_value, BitField):
                if hasattr(attr_value, "reset") and callable(attr_value.reset):
                    attr_value.reset()

    def get_bitfield(self, name: str) -> BitField:
        """Retrieve a bitfield by name.

        Args:
            name: The name of the bitfield.

        Returns:
            The BitField instance.

        Raises:
            KeyError: If the bitfield is not found.
        """
        for attr_value in self.__dict__.values():
            if isinstance(attr_value, BitField) and attr_value._name == name:
                return attr_value
        raise KeyError(
            f"BitField '{name}' not found in register at address 0x{self._address:04x}"
        )

    @property
    def bitfields(self) -> dict[str, BitField]:
        """Get all bitfields in this register.

        Returns:
            Dictionary mapping bitfield names to BitField instances.
        """
        return {
            attr_value._name: attr_value
            for attr_value in self.__dict__.values()
            if isinstance(attr_value, BitField)
        }

    def __str__(self) -> str:
        """Return a human-readable representation of the register."""
        if self.bitfields and self._interface:
            bf_strs = []
            for bf in self.bitfields.values():
                try:
                    val = bf.value
                    if isinstance(val, BaseEnum):
                        bf_strs.append(f"{bf._name}={val.name}")
                    else:
                        bf_strs.append(f"{bf._name}={val}")
                except RuntimeError:
                    bf_strs.append(f"{bf._name}=<unbound>")
            return f"{self._name} at 0x{self._address:04x} [{self._access}]: {', '.join(bf_strs)}"
        return f"{self._name} at 0x{self._address:04x} [{self._access}]"

    def __repr__(self) -> str:
        return f"{self._name}(address={self._address}, access={self._access})"

    @property
    def raw(self) -> int:
        """Read the raw register value."""
        if not self._interface:
            raise RuntimeError(
                f"Interface not set for register at address {self._address}"
            )

        result = 0
        # Check instance-level BitFields
        for attr_value in self.__dict__.values():
            if isinstance(attr_value, BitField):
                result |= attr_value.raw

        return result


class RegisterMap:
    """Base class for register maps."""

    def reset(self) -> None:
        """Reset the register map to its initial state."""
        for attr_value in self.__dict__.values():
            if isinstance(attr_value, Register):
                # Call reset method from Register class to avoid conflicts with
                # bitfields named 'reset' that shadow the method
                Register.reset(attr_value)
            elif isinstance(attr_value, dict):
                # Handle register groups (dicts of Register instances)
                for item in attr_value.values():
                    if isinstance(item, Register):
                        Register.reset(item)

    def get_register(self, address_or_name: int | str) -> Register:
        """Retrieve a register by address or name.

        Args:
            address_or_name: The register address or name.

        Returns:
            The Register instance.

        Raises:
            KeyError: If the register is not found.
        """

        if isinstance(address_or_name, int):
            for attr_value in self.__dict__.values():
                if isinstance(attr_value, Register):
                    if attr_value._address == address_or_name:
                        return attr_value
                elif isinstance(attr_value, dict):
                    for item in attr_value.values():
                        if (
                            isinstance(item, Register)
                            and item._address == address_or_name
                        ):
                            return item

            raise KeyError(f"Register at address 0x{address_or_name:04x} not found")
        elif isinstance(address_or_name, str):
            for attr_value in self.__dict__.values():
                if isinstance(attr_value, Register):
                    if attr_value._name == address_or_name:
                        return attr_value
                elif isinstance(attr_value, dict):
                    for item in attr_value.values():
                        if isinstance(item, Register) and item._name == address_or_name:
                            return item

            raise KeyError(f"Register with name '{address_or_name}' not found")
        else:
            raise TypeError("address_or_name must be an int (address) or str (name)")

    def get_bitfield(
        self, register_address_or_name: int | str, bitfield_name: str
    ) -> BitField:
        """Find a specific bitfield by register and bitfield names.

        Args:
            register_address_or_name: The address or name of the register.
            bitfield_name: The name of the bitfield within the register.

        Returns:
            The BitField instance.

        Raises:
            KeyError: If the register or bitfield is not found.
        """
        register = self.get_register(register_address_or_name)
        return register.get_bitfield(bitfield_name)

    @property
    def dump(self) -> str:
        """Return a pretty-printed representation of all registers and their bitfield values.

        Returns:
            Multi-line string showing all registers and their bitfield values.
        """
        lines = [f"{self.__class__.__name__}:"]
        for address, register in self.registers.items():
            bitfields = register.bitfields
            if bitfields:
                lines.append(
                    f"  0x{address:04x} {register.__class__.__name__} [{register._access}]:"
                )
                for bf in bitfields.values():
                    lines.append(f"    {bf}")
            else:
                lines.append(
                    f"  0x{address:04x} {register.__class__.__name__} [{register._access}]"
                )
        return "\n".join(lines)

    def restore(self, state: dict[int | str, int]) -> None:
        """Restore register map state from a dict of raw values.

        Args:
            state: Dictionary of {address|name: raw_register_value}.
        """
        for address, raw_value in state.items():
            register = self.get_register(address)
            for bf in register.bitfields.values():
                bf_value = (raw_value >> bf._offset) & ((1 << bf._width) - 1)
                if bf._enums is not None:
                    bf.value = bf._enums(bf_value)
                else:
                    bf.value = bf_value

    def compare(self, other: "RegisterMap") -> dict[int | str, tuple[int, int]]:
        """Compare this register map with another.

        Args:
            other: Another RegisterMap instance to compare with.

        Returns:
            Dictionary of {address|name: (self_raw_value, other_raw_value)} for addresses that differ.
        """
        self_raw = self.raw
        other_raw = other.raw
        diffs = {}
        for addr in self_raw.keys() | other_raw.keys():
            sv = self_raw.get(addr)
            ov = other_raw.get(addr)
            if sv != ov:
                diffs[addr] = (sv, ov)
        return dict(sorted(diffs.items()))

    def write_raw(self, address_or_name: int | str, value: int) -> None:
        """Write a raw value to a register by decomposing into bitfields.

        Args:
            address_or_name: The register address or name.
            value: The raw register value.
        """
        register = self.get_register(address_or_name)
        for bf in register.bitfields.values():
            bf_value = (value >> bf._offset) & ((1 << bf._width) - 1)
            if bf._enums is not None:
                bf.value = bf._enums(bf_value)
            else:
                bf.value = bf_value

    def read_raw(self, address_or_name: int | str) -> int:
        """Read a raw value from a register.

        Args:
            address_or_name: The register address or name.

        Returns:
            The raw register value.
        """
        return self.get_register(address_or_name).raw

    def __str__(self) -> str:
        """Return a human-readable representation of the register map."""
        if self.registers:
            addr_list = [f"0x{addr:04x}" for addr in self.registers.keys()]
            return f"{self.__class__.__name__}(registers=[{', '.join(addr_list)}])"
        return f"{self.__class__.__name__}(registers=[])"

    def __repr__(self) -> str:
        return str(self)

    @property
    def raw(self) -> dict[int | str, int]:
        """Read the raw register map values."""
        result = {}
        for attr_value in self.__dict__.values():
            if isinstance(attr_value, Register):
                result[attr_value._address] = attr_value.raw
            elif isinstance(attr_value, dict):
                # Handle register groups (dicts of Register instances)
                for item in attr_value.values():
                    if isinstance(item, Register):
                        result[item._address] = item.raw
        return dict(sorted(result.items()))

    @property
    def addresses(self) -> set[int | str]:
        """Get a list of register addresses in the map."""
        addresses = set()
        for attr_value in self.__dict__.values():
            if isinstance(attr_value, Register):
                addresses.add(attr_value._address)
            elif isinstance(attr_value, dict):
                # Handle register groups (dicts of Register instances)
                for item in attr_value.values():
                    if isinstance(item, Register):
                        addresses.add(item._address)
        return addresses

    @property
    def registers(self) -> dict[int | str, Register]:
        """Get a mapping of register addresses to register instances."""
        registers = {}
        for attr_value in self.__dict__.values():
            if isinstance(attr_value, Register):
                registers[attr_value._address] = attr_value
            elif isinstance(attr_value, dict):
                # Handle register groups (dicts of Register instances)
                for item in attr_value.values():
                    if isinstance(item, Register):
                        registers[item._address] = item
        return dict(sorted(registers.items()))
