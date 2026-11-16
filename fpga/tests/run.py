# Copyright 2026 ETH Zurich
# Copyright and related rights are licensed under the Solderpad Hardware
# License, Version 0.51 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law
# or agreed to in writing, software, hardware and materials distributed under
# this License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# Authors:
#   Sergei Vostrikov
#   LisaMaria Odermatt
#   Federico Villani
# -----------------------------------------------------------------------------
# Description:
#   Compile and run cocotb and native SystemVerilog regressions with Questa.
# -----------------------------------------------------------------------------

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys

from cocotb_tools.runner import get_results, get_runner


TESTS = Path(__file__).resolve().parent
FPGA = TESTS.parent
RTL = FPGA / "sources"
COCOTB = {
    "waveform_gen": ("waveform_gen_tb", ["common/waveform_gen.sv"]),
    "waveform_gen_fsm": ("waveform_gen_fsm_tb", [
        "common/waveform_gen.sv", "common/waveform_generator_fsm.sv",
    ]),
    "fifo_accumulator": ("accumulation_tb", [
        "rf_data_fifo/sync_circular_fifo.sv", "rf_data_fifo/accumulation.sv",
    ]),
    "cdc_reshaper_pipeline": ("cdc_reshaper_pipeline_tb", [
        "rf_data_fifo/async_two_entry_buffer.sv", "rf_data_fifo/fifo_h2l_reshaper.sv",
    ]),
    "accumulation_pipeline": ("accumulation_pipeline_tb", [
        "rf_data_fifo/accumulation.sv", "rf_data_fifo/sample_average_divider.sv",
        "rf_data_fifo/result_average_engine.sv", "rf_data_fifo/multi_fifo_reader.sv",
    ]),
}
NATIVE = {
    "pulse_mode": (["common/waveform_gen.sv", "common/waveform_generator_fsm.sv",
                    "common/start_gen.sv"],
                   [("pulse_mode_tb", "tb"), ("repeated_start_tb", "tb"),
                    ("external_mode_tb", "external_mode_tb")]),
    "signed_average": (["rf_data_fifo/accumulation.sv",
                        "rf_data_fifo/sample_average_divider.sv",
                        "rf_data_fifo/result_average_engine.sv"],
                       [("signed_average_tb", "signed_average_tb")]),
}


def run_cocotb(suite, fifo):
    top, sources = COCOTB[suite]
    directory = TESTS / suite
    sources = [directory / f"{suite}_tb.sv"] + [RTL / path for path in sources]
    defines = {}
    if fifo == "libero" and suite in ("fifo_accumulator", "accumulation_pipeline"):
        libero = Path(os.environ["LIBERO_ROOT"])
        project = Path(os.environ.get("LIBERO_PROJECT", FPGA / "Projects/tiny_probe"))
        core = project / "component/work/RF_DATA_FIFO"
        sources += [libero / "Designer/lib/questasim/precompiled/vlog/src/smartfusion2.v",
                    RTL / "rf_data_fifo/async_sym_fifo_sf2.sv", core / "RF_DATA_FIFO.v"]
        sources += sorted((core / "RF_DATA_FIFO_0/rtl/vlog/core").glob("*.v"))
        defines["USE_LIBERO_FIFO"] = 1
    runner = get_runner("questa")
    runner.build(sources=sources, defines=defines, hdl_toplevel=top,
                 build_dir=directory / "sim_build" / fifo, always=True)
    sys.path.insert(0, str(directory))
    results = runner.test(test_module=suite, hdl_toplevel=top,
                          test_args=["-voptargs=+acc"])
    count, failed = get_results(results)
    if not count or failed:
        raise RuntimeError(f"{suite}: {failed} failures in {count} tests")


def run_native(suite):
    sources, benches = NATIVE[suite]
    sources = [RTL / path for path in sources]
    directory = TESTS / ("accumulation_pipeline" if suite == "signed_average" else suite)
    if suite == "signed_average":
        sources += [directory / "accumulation_pipeline_tb.sv"]
    for bench, top in benches:
        build = TESTS / suite / "sim_build" / bench
        build.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["vlib", build.as_posix()], check=True)
        subprocess.run(["vlog", "-sv", "-work", build.as_posix(),
                        *[path.as_posix() for path in sources],
                        (directory / f"{bench}.sv").as_posix()], check=True)
        transcript = build / "transcript"
        subprocess.run(["vsim", "-c", "-lib", build.as_posix(), top, "-l", transcript.as_posix(),
                        "-onfinish", "exit", "-do", "run -all"], check=True)
        text = transcript.read_text()
        if not re.search(r"^# PASS:", text, re.M) or re.search(r"^# \*\* (Fatal|Error):", text, re.M):
            raise RuntimeError(f"{bench} failed; see {transcript}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("suites", nargs="*")
    parser.add_argument("--fifo", choices=("behavioral", "libero"), default="behavioral")
    args = parser.parse_args()
    for suite in args.suites or [*COCOTB, *NATIVE]:
        if suite in COCOTB:
            run_cocotb(suite, args.fifo)
        else:
            run_native(suite)
