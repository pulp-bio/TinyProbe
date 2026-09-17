// Copyright 2026 LisaMaria Odermatt
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
//   LisaMaria Odermatt
// -----------------------------------------------------------------------------
// Description:
//   Store the first acquisition and accumulate subsequent shots into per-lane
//   sample sums.
//
// Parameters:
//   N_FIFOS - Number of lane FIFOs.
//   SAMPLE_WIDTH - Width of one ADC sample.
//   SUM_WIDTH - Width of one accumulated sample.
//   WRITE_CNT_WIDTH - Capture write-count width.
//   RAW_QUEUE_DEPTH - Pending raw-frame queue depth.
//
// Ports:
//   rst_state_ni - Active-low accumulation-state reset.
//   rst_fifos_i - Per-lane active-high FIFO resets.
//   write_cnt_i - Frames to accept for the capture.
//   wr_fifo_done_o - Capture accumulation complete.
//   wr_accept_o - Raw capture frame accepted.
//   data_i - Input data word.
//   first_shot_i - First-shot indication for a new accumulation.
//   start_capture_i - Capture-start request.
//   wr_clk_i - FIFO write clock.
//   wr_en_i - Write enable.
//   full_o - FIFO full flag.
//   rd_clk_i - FIFO read clock.
//   rd_en_i - Read enable.
//   data_o - Output data word.
//   data_valid_o - Read-data valid flag.
//   empty_o - FIFO empty flag.
// -----------------------------------------------------------------------------

// rx_fifo_v3-style per-lane FIFO bank with in-place shot accumulation.
module accumulation #(
    parameter int unsigned N_FIFOS        = 16,
    parameter int unsigned SAMPLE_WIDTH   = 10,
    parameter int unsigned SUM_WIDTH      = 14,
    parameter int unsigned WRITE_CNT_WIDTH = 12,
    parameter int unsigned RAW_QUEUE_DEPTH = 4,
    localparam int unsigned RAW_WIDTH = 2*SAMPLE_WIDTH,
    localparam int unsigned FIFO_WIDTH = 2*SUM_WIDTH,
    localparam int unsigned PTR_WIDTH =
        (RAW_QUEUE_DEPTH > 1) ? $clog2(RAW_QUEUE_DEPTH) : 1,
    localparam int unsigned QUEUE_COUNT_WIDTH = $clog2(RAW_QUEUE_DEPTH + 1)
) (
    input  logic rst_state_ni,
    input  logic [N_FIFOS-1:0] rst_fifos_i,
    input  logic [WRITE_CNT_WIDTH-1:0] write_cnt_i,
    output logic wr_fifo_done_o,
    output logic wr_accept_o,

    input  logic [N_FIFOS*RAW_WIDTH-1:0] data_i,
    input  logic first_shot_i,
    input  logic start_capture_i,
    input  logic wr_clk_i,
    input  logic [N_FIFOS-1:0] wr_en_i,
    output logic [N_FIFOS-1:0] full_o,

    input  logic rd_clk_i,
    input  logic [N_FIFOS-1:0] rd_en_i,
    output logic [N_FIFOS*FIFO_WIDTH-1:0] data_o,
    output logic [N_FIFOS-1:0] data_valid_o,
    output logic [N_FIFOS-1:0] empty_o
);
    logic start_q1, start_q2, start_q3;
    logic start_rising_edge;
    logic start_input_rising_edge;
    logic capture_armed_q;
    assign start_rising_edge = start_q2 && !start_q3;
    // start_capture_i is already synchronous to wr_clk_i at the top level.
    // Detect its input edge as well as the deliberately delayed edge below:
    // the input edge closes acceptance immediately, and the delayed edge
    // performs initialization before acceptance is reopened.
    assign start_input_rising_edge = start_capture_i && !start_q1;

    always_ff @(posedge wr_clk_i or negedge rst_state_ni) begin
        if (!rst_state_ni) begin
            start_q1 <= 1'b0;
            start_q2 <= 1'b0;
            start_q3 <= 1'b0;
        end else begin
            start_q1 <= start_capture_i;
            start_q2 <= start_q1;
            start_q3 <= start_q2;
        end
    end

    always_ff @(posedge wr_clk_i or negedge rst_state_ni) begin
        if (!rst_state_ni)
            capture_armed_q <= 1'b0;
        else if (start_input_rising_edge)
            capture_armed_q <= 1'b0;
        else if (start_rising_edge)
            capture_armed_q <= 1'b1;
    end

    logic [WRITE_CNT_WIDTH-1:0] issue_count_q, commit_count_q;
    logic [N_FIFOS-1:0] fifo_read;
    logic [N_FIFOS-1:0] fifo_write;
    logic [N_FIFOS*FIFO_WIDTH-1:0] fifo_write_data;
    logic [N_FIFOS*FIFO_WIDTH-1:0] fifo_read_data;
    logic [N_FIFOS-1:0] fifo_dvld, fifo_full, fifo_empty;

    logic [N_FIFOS*RAW_WIDTH-1:0]
        raw_queue_q [0:RAW_QUEUE_DEPTH-1]
        /* synthesis syn_ramstyle="registers" */;
    logic [N_FIFOS-1:0] lane_queue_q [0:RAW_QUEUE_DEPTH-1]
        /* synthesis syn_ramstyle="registers" */;
    logic [PTR_WIDTH-1:0] raw_wr_ptr_q, raw_rd_ptr_q;
    logic [QUEUE_COUNT_WIDTH-1:0] raw_count_q;

    logic first_write;
    logic accumulation_read;
    logic accumulation_write;
    logic all_enabled_not_empty;
    logic all_enabled_not_full;
    logic all_enabled_dvld;
    logic [N_FIFOS*RAW_WIDTH-1:0] matched_raw;
    logic [N_FIFOS-1:0] matched_lanes;

    assign all_enabled_not_empty = ((fifo_empty & wr_en_i) == '0);
    assign all_enabled_not_full  = ((fifo_full & wr_en_i) == '0);
    assign all_enabled_dvld =
        ((fifo_dvld & matched_lanes) == matched_lanes);

    assign first_write = capture_armed_q && first_shot_i && (|wr_en_i) &&
        all_enabled_not_full && (issue_count_q < write_cnt_i);
    assign accumulation_read = capture_armed_q && !first_shot_i && (|wr_en_i) &&
        all_enabled_not_empty && (issue_count_q < write_cnt_i) &&
        (raw_count_q < RAW_QUEUE_DEPTH);
    assign accumulation_write = !first_shot_i && all_enabled_dvld &&
        ((raw_count_q != 0) || accumulation_read) &&
        ((fifo_full & matched_lanes) == '0);
    // CoreFIFO may assert DVLD in the request cycle when prefetch is enabled.
    assign matched_raw = (raw_count_q != 0) ?
        raw_queue_q[raw_rd_ptr_q] : data_i;
    assign matched_lanes = (raw_count_q != 0) ?
        lane_queue_q[raw_rd_ptr_q] : wr_en_i;

    // AFE samples are aligned two's-complement words. Bias each sample before
    // unsigned accumulation; the averaging engine removes this bias afterwards.
    function automatic logic [SUM_WIDTH-1:0] offset_sample(
        input logic [SAMPLE_WIDTH-1:0] sample
    );
        offset_sample = {{(SUM_WIDTH-SAMPLE_WIDTH){1'b0}},
                         ~sample[SAMPLE_WIDTH-1], sample[SAMPLE_WIDTH-2:0]};
    endfunction

    always_comb begin
        fifo_read = rd_en_i;
        fifo_write = '0;
        fifo_write_data = '0;

        if (accumulation_read)
            fifo_read = wr_en_i;

        for (int lane = 0; lane < N_FIFOS; lane++) begin
            if (first_write) begin
                fifo_write[lane] = wr_en_i[lane];
                fifo_write_data[lane*FIFO_WIDTH +: SUM_WIDTH] =
                    offset_sample(data_i[lane*RAW_WIDTH +: SAMPLE_WIDTH]);
                fifo_write_data[lane*FIFO_WIDTH + SUM_WIDTH +: SUM_WIDTH] =
                    offset_sample(data_i[lane*RAW_WIDTH + SAMPLE_WIDTH +: SAMPLE_WIDTH]);
            end else if (accumulation_write) begin
                fifo_write[lane] = matched_lanes[lane];
                fifo_write_data[lane*FIFO_WIDTH +: SUM_WIDTH] =
                    fifo_read_data[lane*FIFO_WIDTH +: SUM_WIDTH] +
                    offset_sample(matched_raw[lane*RAW_WIDTH +: SAMPLE_WIDTH]);
                fifo_write_data[lane*FIFO_WIDTH + SUM_WIDTH +: SUM_WIDTH] =
                    fifo_read_data[lane*FIFO_WIDTH + SUM_WIDTH +: SUM_WIDTH] +
                    offset_sample(matched_raw[lane*RAW_WIDTH + SAMPLE_WIDTH +: SAMPLE_WIDTH]);
            end
        end
    end

    always_ff @(posedge wr_clk_i or negedge rst_state_ni) begin
        if (!rst_state_ni) begin
            issue_count_q <= '0;
            commit_count_q <= '0;
            raw_wr_ptr_q <= '0;
            raw_rd_ptr_q <= '0;
            raw_count_q <= '0;
            for (int entry = 0; entry < RAW_QUEUE_DEPTH; entry++) begin
                raw_queue_q[entry] <= '0;
                lane_queue_q[entry] <= '0;
            end
        end else if (start_rising_edge) begin
            issue_count_q <= '0;
            commit_count_q <= '0;
            raw_wr_ptr_q <= '0;
            raw_rd_ptr_q <= '0;
            raw_count_q <= '0;
        end else begin
            if (first_write) begin
                issue_count_q <= issue_count_q + 1'b1;
                commit_count_q <= commit_count_q + 1'b1;
            end else begin
                if (accumulation_read) begin
                    raw_queue_q[raw_wr_ptr_q] <= data_i;
                    lane_queue_q[raw_wr_ptr_q] <= wr_en_i;
                    raw_wr_ptr_q <= raw_wr_ptr_q + 1'b1;
                    issue_count_q <= issue_count_q + 1'b1;
                end
                if (accumulation_write) begin
                    raw_rd_ptr_q <= raw_rd_ptr_q + 1'b1;
                    commit_count_q <= commit_count_q + 1'b1;
                end
                case ({accumulation_read, accumulation_write})
                    2'b10: raw_count_q <= raw_count_q + 1'b1;
                    2'b01: raw_count_q <= raw_count_q - 1'b1;
                    default: raw_count_q <= raw_count_q;
                endcase
            end
        end
    end

    assign wr_fifo_done_o = (commit_count_q == write_cnt_i);
    assign wr_accept_o = first_write || accumulation_read;
    assign full_o = fifo_full;
    assign empty_o = fifo_empty;
    assign data_o = fifo_read_data;
    assign data_valid_o = fifo_dvld;

    genvar lane;
    generate
        for (lane = 0; lane < N_FIFOS; lane++) begin : gen_fifos
            async_sym_fifo #(
                .FIFO_DATA_WIDTH (FIFO_WIDTH)
            ) fifo_inst (
                .wr_clk_i     (wr_clk_i),
                .wr_en_i      (fifo_write[lane]),
                .data_i       (fifo_write_data[lane*FIFO_WIDTH +: FIFO_WIDTH]),
                .full_o       (fifo_full[lane]),
                .rd_clk_i     (rd_clk_i),
                .rd_en_i      (fifo_read[lane]),
                .data_o       (fifo_read_data[lane*FIFO_WIDTH +: FIFO_WIDTH]),
                .data_valid_o (fifo_dvld[lane]),
                .empty_o      (fifo_empty[lane]),
                .rst_i        (rst_fifos_i[lane])
            );
        end
    endgenerate
endmodule
