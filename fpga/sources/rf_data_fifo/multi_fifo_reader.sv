// Copyright 2024-2026 ETH Zurich
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
//   Read enabled lane FIFOs sequentially and pack their data into a
//   ready/valid output stream.
//
// Parameters:
//   N_FIFOS - Number of lane FIFOs.
//   IN_DATA_WIDTH - Input word width per FIFO.
//   OUT_DATA_WIDTH - Output stream word width.
//   READ_CNT_WIDTH - FIFO read-count width.
//
// Ports:
//   clk_i - Module clock.
//   rst_ni - Active-low reset.
//   start_i - Start request.
//   read_cnt_i - FIFO words to read per enabled lane.
//   busy_o - Operation in progress.
//   fifos_en_i - Enabled lane mask.
//   fifos_empty_i - Per-lane FIFO empty flags.
//   fifos_data_i - Packed data from the lane FIFOs.
//   fifos_read_req_o - Per-lane FIFO read requests.
//   data_o - Output data word.
//   valid_o - Output data valid.
//   ready_i - Output consumer ready.
//   debug_word_load_o - Diagnostic pulse when an input FIFO word is loaded.
//   debug_word_data_o - Input FIFO word observed by the diagnostic.
// -----------------------------------------------------------------------------

module multi_fifo_reader #(
    parameter integer N_FIFOS  = 16,
    parameter integer IN_DATA_WIDTH = 20,
    parameter integer OUT_DATA_WIDTH = 8,
    parameter integer READ_CNT_WIDTH = 12
)(
    input logic                                          clk_i,
    input logic                                          rst_ni,
    input logic                                          start_i,
    input logic  [READ_CNT_WIDTH - 1:0]                  read_cnt_i,
    output logic                                         busy_o,

    // Enable signals for the FIFOs
    input logic  [N_FIFOS - 1:0]                         fifos_en_i,

    // FIFO related signals
    input logic  [N_FIFOS - 1:0]                         fifos_empty_i,
    input logic  [(IN_DATA_WIDTH *N_FIFOS)  - 1:0]       fifos_data_i,
    output logic [N_FIFOS - 1:0]                         fifos_read_req_o,

    // Ready/Valid output interface
    output logic [OUT_DATA_WIDTH - 1:0]                  data_o,
    output logic                                         valid_o,
    input  logic                                         ready_i,

    output logic                                         debug_word_load_o,
    output logic [IN_DATA_WIDTH-1:0]                     debug_word_data_o
);

    // Each enabled lane produces exactly 1000 output bytes. EMPTY ends a
    // lane immediately: retain any partial byte, then pad with zero bytes.
    // Reaching the byte limit stops reads, leaving surplus FIFO words unread.
    // The normal acquisition reset owns clearing those surplus words.
    localparam integer FRAME_BYTES = 1000;
    localparam integer RESERVOIR_WIDTH = IN_DATA_WIDTH + OUT_DATA_WIDTH;
    localparam integer LANE_WIDTH = (N_FIFOS > 1) ? $clog2(N_FIFOS) : 1;
    typedef enum logic [2:0] {IDLE, SELECT_LANE, EMIT, READ_RETURN,
                              PAD, NEXT_LANE} state_t;
    state_t state_q;
    logic start_q;
    logic [LANE_WIDTH:0] lane_q;
    logic [READ_CNT_WIDTH-1:0] word_count_q;
    logic [9:0] byte_count_q;
    logic [RESERVOIR_WIDTH-1:0] reservoir_q;
    integer bits_q;
    wire [IN_DATA_WIDTH-1:0] lane_data =
        fifos_data_i[lane_q*IN_DATA_WIDTH +: IN_DATA_WIDTH];

    always_comb begin
        busy_o = (state_q != IDLE);
        fifos_read_req_o = '0;
        valid_o = 1'b0;
        data_o = '0;
        debug_word_load_o = (state_q == READ_RETURN);
        debug_word_data_o = lane_data;
        if (state_q == EMIT) begin
            if (bits_q >= OUT_DATA_WIDTH) begin
                valid_o = 1'b1;
                data_o = reservoir_q >> (bits_q - OUT_DATA_WIDTH);
            end else if ((word_count_q < read_cnt_i) && !fifos_empty_i[lane_q]) begin
                fifos_read_req_o[lane_q] = 1'b1;
            end
        end else if (state_q == PAD) begin
            valid_o = 1'b1;
            // At most one partial byte remains. Put its bits first and
            // zero-fill the low bits; subsequent padding bytes are all zero.
            if (bits_q != 0)
                data_o = reservoir_q << (OUT_DATA_WIDTH - bits_q);
        end
    end

    always_ff @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            state_q <= IDLE;
            start_q <= 1'b0;
            lane_q <= '0;
            word_count_q <= '0;
            byte_count_q <= '0;
            reservoir_q <= '0;
            bits_q <= 0;
        end else begin
            start_q <= start_i;
            case (state_q)
                IDLE: if (start_i && !start_q) begin
                    lane_q <= '0;
                    state_q <= SELECT_LANE;
                end
                SELECT_LANE: begin
                    if (lane_q == N_FIFOS)
                        state_q <= IDLE;
                    else if (fifos_en_i[lane_q]) begin
                        word_count_q <= '0;
                        byte_count_q <= '0;
                        reservoir_q <= '0;
                        bits_q <= 0;
                        state_q <= EMIT;
                    end else
                        lane_q <= lane_q + 1'b1;
                end
                EMIT: begin
                    if (bits_q >= OUT_DATA_WIDTH) begin
                        if (ready_i) begin
                            bits_q <= bits_q - OUT_DATA_WIDTH;
                            byte_count_q <= byte_count_q + 1'b1;
                            if (byte_count_q == FRAME_BYTES-1)
                                state_q <= NEXT_LANE;
                        end
                    end else if ((word_count_q < read_cnt_i) && !fifos_empty_i[lane_q]) begin
                        word_count_q <= word_count_q + 1'b1;
                        state_q <= READ_RETURN;
                    end else
                        state_q <= PAD;
                end
                READ_RETURN: begin
                    // Same registered FIFO latency as the previous reshaper.
                    reservoir_q <= (reservoir_q << IN_DATA_WIDTH) | lane_data;
                    bits_q <= bits_q + IN_DATA_WIDTH;
                    state_q <= EMIT;
                end
                PAD: if (ready_i) begin
                    bits_q <= 0;
                    reservoir_q <= '0;
                    byte_count_q <= byte_count_q + 1'b1;
                    if (byte_count_q == FRAME_BYTES-1)
                        state_q <= NEXT_LANE;
                end
                NEXT_LANE: begin
                    lane_q <= lane_q + 1'b1;
                    state_q <= SELECT_LANE;
                end
                default: state_q <= IDLE;
            endcase
        end
    end
endmodule
