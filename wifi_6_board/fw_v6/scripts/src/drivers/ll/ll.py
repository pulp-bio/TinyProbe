import numpy as np


class TP_LL(object):
    def __init__(self, name: str, default_regs: list[int]):
        self._name = name
        self._n_regs = len(default_regs)
        self._default_regs = default_regs

        # Regs which will be modified
        # Put all the registers to 0
        self._regs = self._default_regs.copy()
        self._regs_reset()

        # Regs encoding the previous state
        self._regs_old = self._regs.copy()

        # List of registers to write to
        self._val_list = []
        self._addr_list = []

        # List of registers written by user
        self._addr_list_hist = []

    def __str__(self):
        return self._name + " LL Driver"

    def _write_bit(self, val, bit):
        mask = 1 << bit
        return val | mask

    def _clear_bit(self, val, bit):
        mask = (~(1 << bit)) & int("".join("1" for x in range(32)), 2)
        return val & mask

    # Set and Reset operations with bits
    def _reg_bit(self, reg_id, bit, set=True):
        if bit > 31 or bit < 0:
            print("Error!")
            return

        if set:
            self._regs[reg_id] = self._write_bit(self._regs[reg_id], bit)
        else:
            self._regs[reg_id] = self._clear_bit(self._regs[reg_id], bit)

        # Add the reg addr to a history
        self._addr_list_hist.append([reg_id])
        return

    # Overwrite operations for register areas
    def _reg_val(self, reg_id, bit_width, bit_shift, val):
        # Make a mask
        mask_str = "".join("1" for x in range(bit_width))
        mask = int(mask_str, 2) << bit_shift

        if int(val) >> bit_width:
            # print("Error! Value is bigger than the provided bit width.")
            raise Exception("Value is bigger than the provided bit width")

        # Clear the reg value in the mask area
        self._regs[reg_id] &= ~mask

        # Set a new value
        self._regs[reg_id] |= int(val) << bit_shift

        # Add the reg addr to a history
        self._addr_list_hist.append([reg_id])
        return

    def _regs_reset(self):
        # Reset all the regs
        self._regs = self._default_regs.copy()

    def _proc_self_clr_bits(self):
        pass

    def get_modified_regs_and_vals(self, from_history=True):
        self._val_list = []
        self._addr_list = []

        if from_history:
            # Get the list of the registers written by the user
            self._addr_list = np.unique(self._addr_list_hist)
            # Get values
            self._val_list = [self._regs[i] for i in self._addr_list]

        else:
            # List only modified registers (compared to the previous state)
            for i in range(len(self._regs)):
                # Check if there are any changes in the register
                if self._regs[i] != self._regs_old[i]:
                    # Add modified register value and address
                    self._val_list.append(self._regs[i])
                    self._addr_list.append(i)

        self._proc_self_clr_bits()

        # Update the "old state" of the registers
        self._regs_old = self._regs.copy()

        # Clear the history of the written register
        self._addr_list_hist = []

        return self._addr_list, self._val_list
