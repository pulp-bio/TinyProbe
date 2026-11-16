// Copyright 2021-2026 ETH Zurich
// Copyright and related rights are licensed under the Solderpad Hardware
// License, Version 0.51 (the "License"); you may not use this file except in
// compliance with the License. You may obtain a copy of the License at
// http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law
// or agreed to in writing, software, hardware and materials distributed under
// this License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.
//
// Authors:
//   Sergei Vostrikov
//   LisaMaria Odermatt
//   Federico Villani
// -----------------------------------------------------------------------------
// Description:
//   Expose the waveform generator and its configuration signals to cocotb.
// -----------------------------------------------------------------------------

module waveform_gen_tb ();

    logic         clk;
    logic         rst_n;

    // General signals
    logic  [15:0] sync_period;
    logic  [15:0] capture_delay;
    logic         start_capture;
    logic  [7:0]  n_shots;
    logic  [15:0] start_cap_time;
    logic         fifo_rd_busy;

    // RX FIFO control signals
    logic         fifo_start_capture;
    logic         fifo_rst;
    logic         fifo_wr_en;

    // TX chip signals
    logic  [7:0]  tx_wake_up_time;
    logic  [7:0]  tx_sleep_time;
    logic         tx_bf_sync;
    logic         tx_clk_buf_en;
    logic         tx_sync_buf_en;
    logic         tx_tr_en;

    // TX chip LDO reshreshing options
    logic  [15:0] tr_en_period;
    logic  [7:0]  tr_en_on_time;
    logic         refresh_en;

    // AFE chip signals
    logic  [7:0]  afe_wake_up_time;
    logic  [15:0] afe_clk_on_time;
    logic  [15:0] afe_data_acq_time;
    logic         afe_tx_trig_o;
    logic         afe_tx_trig_buf_en;
    logic         afe_clk_buf_en;
    logic         afe_fast_pdn;

    waveform_generator dut (
        .clk_i                (clk),
        .rst_ni               (rst_n),

        // General signals
        .sync_period_i        (sync_period),
        .capture_delay_i      (capture_delay),
        .start_capture_i      (start_capture),
        .n_shots_i            (n_shots),
        .start_cap_time_i     (start_cap_time),
        .fifo_rd_busy_i       (fifo_rd_busy),

        // RX FIFO control signals
        .fifo_start_capture_o (fifo_start_capture),
        .fifo_rst_o           (fifo_rst),
        .fifo_wr_en_o         (fifo_wr_en),

        // TX chip signals
        .tx_wake_up_time_i    (tx_wake_up_time),
        .tx_sleep_time_i      (tx_sleep_time),
        .tx_bf_sync_o         (tx_bf_sync),
        .tx_clk_buf_en_o      (tx_clk_buf_en),
        .tx_sync_buf_en_o     (tx_sync_buf_en),
        .tx_tr_en_o           (tx_tr_en),

        .tr_en_period_i       (tr_en_period),
        .tr_en_on_time_i      (tr_en_on_time),
        .refresh_en_i         (refresh_en),

        // AFE chip signals
        .afe_wake_up_time_i   (afe_wake_up_time),
        .afe_clk_on_time_i    (afe_clk_on_time),
        .afe_data_acq_time_i  (afe_data_acq_time),
        .afe_tx_trig_o        (afe_tx_trig_o),
        .afe_tx_trig_buf_en_o (afe_tx_trig_buf_en),
        .afe_clk_buf_en_o     (afe_clk_buf_en),
        .afe_fast_pdn_o       (afe_fast_pdn)
    );

    // Dump waves
    initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, waveform_gen_tb);
    end

endmodule
