import struct
import os

# Command names to IDs mapping
cmd_name_id = {
    "Ping": 0,
    "Activate replies": 1,
    "Switch SPI MUX": 2,
    "Write SPI packet": 3,
    "Write FPGA reg": 4,
    "Write AFE reg": 5,
    "Write TX reg": 6,
    "Delay ns": 7,
    "Sleep ms": 8,
    "Control power": 9,
    "Trigger shot": 10,
    "Set powersave mode": 11,
}

# Packing format for the commands above
arg_pack_fmt = {
    0: "=B",
    1: "=B",
    2: "=B",
    3: "",
    4: "=BI",
    5: "=BBH",
    6: "=HI",
    7: "=Q",
    8: "=I",
    9: "=BB",
    10: "=HHBBHBB",
    11: "BB",
}


# Maximum size of the Command sequence in bytes
MAX_CMD_SEQ_SIZE_BYTES = 1000

# Maximum size of the Command sequence to stores in file
MAX_CMD_SEQ_SIZE_FILE_BYTES = 1000000


# A class to represent a command
class TinyProbeCommand(object):
    def __init__(self, cmd_id):
        self._cmd_id = cmd_id
        self._name = "TinyProbe Command Template"

        self._n_args = 0
        self._args = ()

    def __str__(self):
        return self._name

    def get_cmd_bytearray(self):
        arg_bytes = struct.pack(arg_pack_fmt[self._cmd_id], *self.args)
        header_bytes = struct.pack("=BH", self._cmd_id, len(arg_bytes))

        arr = bytearray(header_bytes)
        arr.extend(arg_bytes)
        return arr

    def _update_args_from_bytearray(self, arr):
        self._args = struct.unpack(arg_pack_fmt[self._cmd_id], arr)
        return

    def init_from_bytearray(self, arr):
        self._update_args_from_bytearray(arr)
        return

    @property
    def cmd_id(self):
        return self._cmd_id

    @property
    def n_args(self):
        return self._n_args

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, new_args):
        self._args = new_args
        self._n_args = len(new_args)


# A class to represent a sequence of commands
class TinyProbeCmdSeq(object):
    def __init__(self, cmd_list=[]):
        # List all available TinyProbe commands
        self._tp_cmds = TinyProbeCommand.__subclasses__()
        self._tp_cmds_ids = [cmd()._cmd_id for cmd in self._tp_cmds]

        self._cmd_list = cmd_list
        self._n_cmds_total = len(cmd_list)
        self._packets = []
        self._n_cmds = []

    def extend(self, cmd_list):
        if isinstance(cmd_list, list):
            for i in range(len(cmd_list)):
                if not isinstance(cmd_list[i], TinyProbeCommand):
                    print("TinyProbeCmdSeq: cmd_list[%d] is not a valid command!" % i)
                    return
            self._cmd_list.extend(cmd_list.copy())

        elif isinstance(cmd_list, TinyProbeCmdSeq):
            for i in range(len(cmd_list._cmd_list)):
                if not isinstance(cmd_list._cmd_list[i], TinyProbeCommand):
                    print("TinyProbeCmdSeq: cmd_list[%d] is not a valid command!" % i)
                    return
            self._cmd_list.extend(cmd_list._cmd_list.copy())

        return

    def get_formatted_packets(self, max_packet_size=MAX_CMD_SEQ_SIZE_BYTES):
        # Temporary packet length in bytes
        pack_len = 0

        self._packets = [bytearray()]
        self._n_cmds = [0]

        # Iterate over the list of commands
        for i in range(len(self._cmd_list)):
            cmd_byte_arr = self._cmd_list[i].get_cmd_bytearray()
            # Check if the size of a single command exceeds the maximum size
            if len(cmd_byte_arr) > max_packet_size:
                print(
                    "TinyProbeCmdSeq: cmd_list[%d] exceeds the size of TX package!" % i
                )
                return None
            # If we add this command will we still fit in packet size?
            if (len(self._packets[-1]) + len(cmd_byte_arr)) > max_packet_size:
                # If no, append a new packet and copy the cmd_byte_arr to it
                self._packets.append(bytearray())
                self._n_cmds.append(0)

            # Extend the package with a new command
            self._packets[-1].extend(cmd_byte_arr)
            self._n_cmds[-1] += 1

        # Iterate over the constructed packets and add headers
        for j in range(len(self._packets)):
            header_bytes = bytearray(struct.pack("=H", self._n_cmds[j]))
            header_bytes.extend(self._packets[j])
            self._packets[j] = header_bytes

        return self._packets, self._n_cmds

    def to_file(self, filename):
        packets = self.get_formatted_packets(
            max_packet_size=MAX_CMD_SEQ_SIZE_FILE_BYTES
        )[0]
        if len(packets) > 1:
            print("TinyProbeCmdSeq: can't save to file. Sequence is too long.")
            return

        # Open the file for writing
        with open(filename, "wb+") as file:
            file.write(packets[0])

        return

    def _init_from_bytearray(self, arr):
        # Extract the number of commands
        seq_header_arr = arr[:2]
        n_cmds_total = struct.unpack("=H", seq_header_arr)[0]

        # Current index point to element 2 of the bytearray
        idx = 2

        self._cmd_list = []
        self._n_cmds_total = len(self._cmd_list)

        # Iterate over the commands
        for i in range(n_cmds_total):
            # Check index (+ 3 bytes for command header)
            if (idx + 3) > len(arr):
                print(
                    "TinyProbeCmdSeq: init_from_bytearray failed. Input array is too short."
                )
                return

            # Extract next command
            cmd_id, cmd_arg_len = struct.unpack("=BH", arr[idx : idx + 3])

            idx += 3
            cmd_args_arr = arr[idx : idx + cmd_arg_len]
            if len(cmd_args_arr) != cmd_arg_len:
                print(
                    "TinyProbeCmdSeq: init_from_bytearray failed. Arg array is too short."
                )
                return

            # Instantiate command object and append to the list
            self._cmd_list.append(self._tp_cmds[self._tp_cmds_ids.index(cmd_id)]())

            # Init command object from bytearray
            self._cmd_list[-1].init_from_bytearray(cmd_args_arr)

            # Update index
            idx += cmd_arg_len

        self._n_cmds_total = len(self._cmd_list)

        return

    def from_file(self, filename):
        # Open in read binary mode
        if os.path.isfile(filename):
            with open(filename, mode="rb") as file:
                bytes_arr = file.read()
        else:
            print("TinyProbeCmdSeq: file %s not found." % filename)
            return

        self._init_from_bytearray(bytes_arr)
        return

    @property
    def cmd_list(self):
        return self._cmd_list


# Specify Commands' classes
class Ping(TinyProbeCommand):
    def __init__(self, probe_id=1):
        # Assign an ID to the command
        super().__init__(cmd_name_id["Ping"])

        self._name = "Ping"

        # Put args
        self.args = (probe_id,)


class ActivateReplies(TinyProbeCommand):
    def __init__(self, replies_on=True):
        self._name = "Activate replies"
        # Assign an ID to the command
        super().__init__(cmd_name_id[self._name])

        if replies_on:
            self._replies_on = 1
        else:
            self._replies_on = 0

        self.args = (self._replies_on,)

    def init_from_bytearray(self, arr):
        self._update_args_from_bytearray(arr)
        self._replies_on = self.args[0]
        return

    @property
    def replies_on(self):
        return self._replies_on


class SwitchSpiMux(TinyProbeCommand):
    def __init__(self, code=0):
        self._name = "Switch SPI MUX"

        # Assign an ID to the command
        super().__init__(cmd_name_id[self._name])

        self._mux_code = code

        # Put args
        self.args = (self.mux_code,)

    @property
    def mux_code(self):
        return self._mux_code

    @mux_code.setter
    def mux_code(self, new_code):
        self._mux_code = new_code
        self.args = (self.mux_code,)

    def select_fpga(self):
        self.mux_code = 1

    def select_afe(self):
        self.mux_code = 2

    def select_tx(self):
        self.mux_code = 3

    def init_from_bytearray(self, arr):
        self._update_args_from_bytearray(arr)
        self._mux_code = self.args[0]
        return


class WriteSpiPacket(TinyProbeCommand):
    def __init__(self, bytes_arr=bytearray()):
        self._name = "Write SPI packet"

        # Assign an ID to the command
        super().__init__(cmd_name_id[self._name])

        # Put args
        self._args_bytes = bytearray(bytes_arr)
        self._n_args = len(bytes_arr)

    # Overload the command to generate byte arrays
    def get_cmd_bytearray(self):
        header_bytes = struct.pack("=BH", self._cmd_id, self._n_args)

        arr = bytearray(header_bytes)
        arr.extend(self._args_bytes)
        return arr

    def init_from_bytearray(self, arr):
        self._args_bytes = arr
        self._n_args = len(arr)
        return


class WriteFPGAReg(TinyProbeCommand):
    def __init__(self, addr=0, val=0):
        self._name = "Write FPGA reg"

        # Assign an ID to the command
        super().__init__(cmd_name_id[self._name])

        self._reg_addr = addr
        self._write_val = val

        # Put args
        self.args = (self._reg_addr, self._write_val)

    @property
    def addr(self):
        return self._reg_addr

    @property
    def val(self):
        return self._write_val

    def init_from_bytearray(self, arr):
        self._update_args_from_bytearray(arr)
        self._reg_addr, self._write_val = self.args
        return


class WriteAfeReg(TinyProbeCommand):
    def __init__(self, addr=0, val=0, dtgc_die=True):
        self._name = "Write AFE reg"

        # Assign an ID to the command
        super().__init__(cmd_name_id[self._name])

        self._reg_addr = addr
        self._write_val = val
        self._dtgc_die = 0 if dtgc_die == 0 else 1

        # Put args
        self.args = (self._dtgc_die, self._reg_addr, self._write_val)

    @property
    def addr(self):
        return self._reg_addr

    @property
    def val(self):
        return self._write_val

    @property
    def dtgc_die(self):
        return self._dtgc_die

    def init_from_bytearray(self, arr):
        self._update_args_from_bytearray(arr)
        self._dtgc_die, self._reg_addr, self._write_val = self.args
        return


class WriteTxReg(TinyProbeCommand):
    def __init__(self, addr=0, val=0):
        self._name = "Write TX reg"

        # Assign an ID to the command
        super().__init__(cmd_name_id[self._name])

        self._reg_addr = addr
        self._write_val = val

        # Put args
        self.args = (self._reg_addr, self._write_val)

    @property
    def addr(self):
        return self._reg_addr

    @property
    def val(self):
        return self._write_val

    def init_from_bytearray(self, arr):
        self._update_args_from_bytearray(arr)
        self._reg_addr, self._write_val = self.args
        return


class DelayNs(TinyProbeCommand):
    def __init__(self, delay=0):
        self._name = "Delay ns"

        # Assign an ID to the command
        super().__init__(cmd_name_id[self._name])

        self._delay = delay

        # Put args
        self.args = (delay,)

    @property
    def delay(self):
        return self._delay

    def init_from_bytearray(self, arr):
        self._update_args_from_bytearray(arr)
        self._delay = self.args[0]
        return


class SleepMs(TinyProbeCommand):
    def __init__(self, delay=0):
        self._name = "Sleep ms"

        # Assign an ID to the command
        super().__init__(cmd_name_id[self._name])

        self._delay = delay

        # Put args
        self.args = (self._delay,)

    @property
    def delay(self):
        return self._delay

    def init_from_bytearray(self, arr):
        self._update_args_from_bytearray(arr)
        self._delay = self.args[0]
        return


class ControlPower(TinyProbeCommand):
    def __init__(self, domain_id=0, enable=False):
        self._name = "Control power"

        # Assign an ID to the command
        super().__init__(cmd_name_id[self._name])

        self._domain_id = domain_id
        self._enable = 0 if enable == 0 else 1

        # Put args
        self.args = (self._domain_id, self._enable)

    @property
    def domain_id(self):
        return self._domain_id

    @property
    def enable(self):
        return self._enable

    def init_from_bytearray(self, arr):
        self._update_args_from_bytearray(arr)
        self._domain_id, self._enable = self.args
        return


class TriggerShot(TinyProbeCommand):
    def __init__(
        self,
        n_shots=1,
        n_packets=82,
        dc_dc_off_delay_us=6.1,
        read_fifo_delay_us=200,
        trig_pack_id=65535,
        sw_trigger=True,
        dc_dc_pwd_at_rx=True,
    ):
        self._name = "Trigger shot"

        # Assign an ID to the command
        super().__init__(cmd_name_id[self._name])

        self._n_shots = n_shots
        self._n_packets = n_packets
        self.read_fifo_delay_us = read_fifo_delay_us
        self.dc_dc_off_delay_us = dc_dc_off_delay_us
        self.trig_pack_id = trig_pack_id
        self.sw_trigger = 1 if sw_trigger else 0
        self.dc_dc_pwd_at_rx = 1 if dc_dc_pwd_at_rx else 0

        # Put args
        self.args = (
            self._n_shots,
            self._n_packets,
            int(self.dc_dc_off_delay_us * 10),
            int(self.read_fifo_delay_us),
            self.trig_pack_id,
            self.sw_trigger,
            self.dc_dc_pwd_at_rx,
        )

    @property
    def n_shots(self):
        return self._n_shots

    def init_from_bytearray(self, arr):
        self._update_args_from_bytearray(arr)
        (
            self._n_shots,
            self._n_packets,
            self.dc_dc_off_delay_us,
            self.read_fifo_delay_us,
            self.trig_pack_id,
            self.sw_trigger,
            self.dc_dc_pwd_at_rx,
        ) = self.args

        self.dc_dc_off_delay_us = self.dc_dc_off_delay_us / 10
        return


class SetPowersaveMode(TinyProbeCommand):
    def __init__(self, enable=False, domain="mcu"):
        self._name = "Set powersave mode"

        # Assign an ID to the command
        super().__init__(cmd_name_id[self._name])

        self._enable = enable

        if domain == "mcu":
            self._domain = 1
        else:
            self._domain = 0  # WiFi

        # Put args
        self.args = (self._domain, self._enable)

    @property
    def domain(self):
        return self._domain

    @property
    def enable(self):
        return self._enable

    def init_from_bytearray(self, arr):
        self._update_args_from_bytearray(arr)
        self._domain, self._enable = self.args
        return
