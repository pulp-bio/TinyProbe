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
//   Read accumulated samples, divide by the acquisition count and write per-
//   lane averaged results.
//
// Parameters:
//   N_LANES - Number of data lanes.
//   SAMPLE_WIDTH - Width of one ADC sample.
//   SUM_WIDTH - Width of one accumulated sample.
//   COUNT_WIDTH - Accumulation-count width.
//   FRAME_COUNT_WIDTH - Per-lane frame-count width.
//
// Ports:
//   clk_i - Module clock.
//   rst_ni - Active-low reset.
//   enable_i - Block enable.
//   accumulation_count_i - Number of accumulated shots for the average.
//   samples_per_lane_i - Frames to process per enabled lane.
//   lanes_enable_i - Enabled lane mask.
//   frame_done_o - All enabled lanes have been averaged.
//   sum_empty_i - Per-lane accumulated-data FIFO empty flags.
//   sum_data_valid_i - Per-lane accumulated-data read-valid flags.
//   sum_data_i - Packed accumulated sample pairs.
//   sum_read_o - Per-lane accumulated-data read requests.
//   average_full_i - Per-lane result FIFO full flags.
//   average_write_o - Per-lane averaged-result write enables.
//   average_data_o - Packed averaged sample pairs.
//   debug_state_o - Averaging controller state diagnostic.
//   debug_lane_o - Lane currently being averaged.
//   debug_lane_write_count_o - Results written for the current lane.
//   debug_enable_o - Averaging enable diagnostic.
//   debug_divider_busy_o - Sample-divider handshake diagnostics.
//   debug_divider_start_o - Sample-divider handshake diagnostics.
//   debug_divider_done_o - Sample-divider handshake diagnostics.
// -----------------------------------------------------------------------------

// Reads final accumulated sums directly from the accumulation FIFO, divides
// them with one shared divider, and presents 20-bit frames to the SPI buffers.
module result_average_engine #(
    parameter int unsigned N_LANES      = 16,
    parameter int unsigned SAMPLE_WIDTH = 10,
    parameter int unsigned SUM_WIDTH    = 14,
    parameter int unsigned COUNT_WIDTH  = 8,
    parameter int unsigned FRAME_COUNT_WIDTH = 12,
    localparam int unsigned SUM_FRAME_WIDTH = 2*SUM_WIDTH,
    localparam int unsigned RAW_FRAME_WIDTH = 2*SAMPLE_WIDTH,
    localparam int unsigned LANE_WIDTH =
        (N_LANES > 1) ? $clog2(N_LANES) : 1
) (
    input  logic                                  clk_i,
    input  logic                                  rst_ni,
    input  logic                                  enable_i,
    input  logic [COUNT_WIDTH-1:0]                accumulation_count_i,
    input  logic [FRAME_COUNT_WIDTH-1:0]          samples_per_lane_i,
    input  logic [N_LANES-1:0]                    lanes_enable_i,
    output logic                                  frame_done_o,

    input  logic [N_LANES-1:0]                    sum_empty_i,
    input  logic [N_LANES-1:0]                    sum_data_valid_i,
    input  logic [N_LANES*SUM_FRAME_WIDTH-1:0]    sum_data_i,
    output logic [N_LANES-1:0]                    sum_read_o,

    input  logic [N_LANES-1:0]                    average_full_i,
    output logic [N_LANES-1:0]                    average_write_o,
    output logic [N_LANES*RAW_FRAME_WIDTH-1:0]    average_data_o,

    // Live diagnostic state. These outputs do not affect datapath control.
    output logic [2:0]                            debug_state_o,
    output logic [LANE_WIDTH-1:0]                 debug_lane_o,
    output logic [FRAME_COUNT_WIDTH-1:0]          debug_lane_write_count_o,
    output logic                                  debug_enable_o,
    output logic                                  debug_divider_busy_o,
    output logic                                  debug_divider_start_o,
    output logic                                  debug_divider_done_o
);

    typedef enum logic [2:0] {
        AVG_IDLE,
        AVG_WAIT_READ,
        AVG_START_A,
        AVG_WAIT_A,
        AVG_START_B,
        AVG_WAIT_B,
        AVG_WRITE
    } average_state_t;

    average_state_t state_q;
    logic [LANE_WIDTH-1:0] lane_q;
    logic [SUM_FRAME_WIDTH-1:0] sum_frame_q;
    logic [SAMPLE_WIDTH-1:0] average_a_q;
    logic [SAMPLE_WIDTH-1:0] average_b_q;
    logic [FRAME_COUNT_WIDTH-1:0] lane_write_count_q [N_LANES];
    logic all_lanes_complete_after_write;
    logic lane_found;
    logic [LANE_WIDTH-1:0] selected_lane;

    logic divider_start;
    logic divider_busy;
    logic divider_done;
    logic [SUM_WIDTH-1:0] divider_numerator;
    logic [SAMPLE_WIDTH-1:0] divider_quotient;

    assign debug_state_o            = state_q;
    assign debug_lane_o             = lane_q;
    assign debug_lane_write_count_o = lane_write_count_q[lane_q];
    assign debug_enable_o           = enable_i;
    assign debug_divider_busy_o     = divider_busy;
    assign debug_divider_start_o    = divider_start;
    assign debug_divider_done_o     = divider_done;

    sample_average_divider #(
        .NUMERATOR_WIDTH (SUM_WIDTH),
        .DIVISOR_WIDTH   (COUNT_WIDTH),
        .QUOTIENT_WIDTH  (SAMPLE_WIDTH)
    ) shared_divider (
        .clk_i       (clk_i),
        .rst_ni      (rst_ni),
        .start_i     (divider_start),
        .numerator_i (divider_numerator),
        .divisor_i   (accumulation_count_i),
        .busy_o      (divider_busy),
        .done_o      (divider_done),
        .quotient_o  (divider_quotient)
    );

    always_comb begin
        sum_read_o       = '0;
        average_write_o  = '0;
        average_data_o   = '0;
        divider_start    = 1'b0;
        divider_numerator = '0;
        lane_found       = 1'b0;
        selected_lane    = '0;
        all_lanes_complete_after_write = 1'b1;

        for (int lane = 0; lane < N_LANES; lane++) begin
            if (lanes_enable_i[lane]) begin
                if (state_q == AVG_WRITE && lane == lane_q) begin
                    if ((lane_write_count_q[lane] + 1'b1) < samples_per_lane_i)
                        all_lanes_complete_after_write = 1'b0;
                end else if (lane_write_count_q[lane] < samples_per_lane_i) begin
                    all_lanes_complete_after_write = 1'b0;
                end
            end
        end

        for (int lane = 0; lane < N_LANES; lane++) begin
            // Do not issue speculative reads beyond the configured result
            // count. An asynchronous FIFO's EMPTY indication can lag the
            // final accepted read by several synchronizer clocks; without
            // this count guard, a lane can overshoot the target and exact
            // completion can never be observed.
            if (enable_i && !lane_found &&
                (lane_write_count_q[lane] < samples_per_lane_i) &&
                !sum_empty_i[lane] &&
                !average_full_i[lane]) begin
                lane_found    = 1'b1;
                selected_lane = lane[LANE_WIDTH-1:0];
            end
        end

        if (state_q == AVG_IDLE && lane_found)
            sum_read_o[selected_lane] = 1'b1;

        if (state_q == AVG_START_A) begin
            divider_start = 1'b1;
            divider_numerator = sum_frame_q[0 +: SUM_WIDTH];
        end

        if (state_q == AVG_START_B) begin
            divider_start = 1'b1;
            divider_numerator = sum_frame_q[SUM_WIDTH +: SUM_WIDTH];
        end

        if (state_q == AVG_WRITE) begin
            average_write_o[lane_q] = 1'b1;
            average_data_o[lane_q*RAW_FRAME_WIDTH +: RAW_FRAME_WIDTH] =
                {average_b_q, average_a_q};
        end
    end

    always_ff @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            state_q     <= AVG_IDLE;
            lane_q      <= '0;
            sum_frame_q <= '0;
            average_a_q <= '0;
            average_b_q <= '0;
            frame_done_o <= 1'b0;
            for (int lane = 0; lane < N_LANES; lane++)
                lane_write_count_q[lane] <= '0;
        end else begin
            if (state_q == AVG_WRITE) begin
                lane_write_count_q[lane_q] <= lane_write_count_q[lane_q] + 1'b1;
                if (all_lanes_complete_after_write)
                    frame_done_o <= 1'b1;
            end
            case (state_q)
                AVG_IDLE: begin
                    if (lane_found) begin
                        lane_q  <= selected_lane;
                        // With CoreFIFO prefetch enabled, DVLD can qualify the
                        // requested output in the same cycle as RE. Other FIFO
                        // implementations may return it in a later cycle.
                        if (sum_data_valid_i[selected_lane]) begin
                            sum_frame_q <= sum_data_i[
                                selected_lane*SUM_FRAME_WIDTH +:
                                SUM_FRAME_WIDTH];
                            state_q <= AVG_START_A;
                        end else begin
                            state_q <= AVG_WAIT_READ;
                        end
                    end
                end

                // The Libero FIFO asserts DVLD when its registered output is
                // valid; its exact read latency is therefore not assumed.
                AVG_WAIT_READ: begin
                    if (sum_data_valid_i[lane_q]) begin
                        sum_frame_q <= sum_data_i[
                            lane_q*SUM_FRAME_WIDTH +: SUM_FRAME_WIDTH];
                        state_q <= AVG_START_A;
                    end
                end

                AVG_START_A: begin
                    if (!divider_busy)
                        state_q <= AVG_WAIT_A;
                end

                AVG_WAIT_A: begin
                    if (divider_done) begin
                        // Restore two's complement for the existing host parser.
                        average_a_q <= {~divider_quotient[SAMPLE_WIDTH-1],
                                         divider_quotient[SAMPLE_WIDTH-2:0]};
                        state_q <= AVG_START_B;
                    end
                end

                AVG_START_B: begin
                    if (!divider_busy)
                        state_q <= AVG_WAIT_B;
                end

                AVG_WAIT_B: begin
                    if (divider_done) begin
                        average_b_q <= {~divider_quotient[SAMPLE_WIDTH-1],
                                         divider_quotient[SAMPLE_WIDTH-2:0]};
                        state_q <= AVG_WRITE;
                    end
                end

                AVG_WRITE: state_q <= AVG_IDLE;

                default: state_q <= AVG_IDLE;
            endcase
        end
    end

endmodule
