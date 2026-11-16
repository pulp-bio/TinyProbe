// Copyright 2025-2026 ETH Zurich
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
//   Soumyo Bhattacharjee
//   LisaMaria Odermatt
//   Federico Villani
// -----------------------------------------------------------------------------
// Description:
//   Shift received and transmitted SPI words, with optional dual-lane payload
//   transfers.
//
// Parameters:
//   ENABLE_DUAL - Enable dual-lane payload transfers.
//
// Ports:
//   sclk - SPI serial clock.
//   sys_rst_n - Active-low reset.
//   cs_n - Active-low SPI chip select.
//   rx_mode - Select serial receive mode.
//   data_phase - Payload phase indication.
//   shift_en - Enable serial-word shifting.
//   rx_frame_clks - Clock count for the receive frame.
//   sdi0 - SPI lane input data.
//   sdi1 - SPI lane input data.
//   sdi2 - SPI lane input data.
//   sdi3 - SPI lane input data.
//   sdo0 - SPI lane output data.
//   sdo1 - SPI lane output data.
//   sdo2 - SPI lane output data.
//   sdo3 - SPI lane output data.
//   shift_data_next - Received word including the current input bits.
//   shift_done - Receive word complete indication.
//   load_data - Transmit word to load.
//   load_en - Load the transmit shift register.
//   tx_done - Transmit word complete indication.
// -----------------------------------------------------------------------------

/**
 * Mode-1 SPI symbol engine (CPOL=0, CPHA=1).
 *
 * The slave captures incoming symbols on falling SCLK edges and launches
 * outgoing symbols on rising SCLK edges.
 */
module spi_quad_shift_reg #(
    parameter bit ENABLE_DUAL = 1'b0
) (
    input  logic        sclk,
    input  logic        sys_rst_n,
    input  logic        cs_n,
    input  logic        rx_mode,
    input  logic        data_phase,
    input  logic        shift_en,
    input  logic [5:0]  rx_frame_clks,
    input  logic        sdi0, sdi1, sdi2, sdi3,
    output logic        sdo0, sdo1, sdo2, sdo3,
    output logic [31:0] shift_data_next,
    output logic        shift_done,
    input  logic [31:0] load_data,
    input  logic        load_en,
    output logic        tx_done
);

    localparam logic [5:0] ACTIVE_FRAME_CLKS = ENABLE_DUAL ? 6'd16 : 6'd8;

    logic [31:0] rx_shift_reg;
    logic [31:0] tx_shift_reg;
    logic [5:0]  rx_clock_cnt;
    logic [5:0]  tx_clock_cnt;
    logic [5:0]  frame_cycles;

    // Command/address are eight serial symbols.  The controller selects the
    // common read-dummy count while its transaction state is DUMMY.
    assign frame_cycles = data_phase ? ACTIVE_FRAME_CLKS : rx_frame_clks;

    always_comb begin
        shift_data_next = rx_shift_reg;
        if (shift_en && rx_mode) begin
            if (data_phase) begin
                if (ENABLE_DUAL) begin
                    shift_data_next = {rx_shift_reg[29:0], sdi1, sdi0};
                end else begin
                    shift_data_next = {rx_shift_reg[27:0], sdi3, sdi2, sdi1, sdi0};
                end
            end else begin
                shift_data_next = {rx_shift_reg[30:0], sdi0};
            end
        end
    end

    // RX symbols are sampled on the falling edge for CPOL=0, CPHA=1.
    // shift_done is predictive: it is true before the final capture edge, so
    // the controller can consume shift_data_next on that same edge.
    always_ff @(negedge sclk or negedge sys_rst_n or posedge cs_n) begin
        if (!sys_rst_n || cs_n) begin
            rx_shift_reg <= 32'h0;
            rx_clock_cnt <= 6'd0;
        end else if (shift_en && rx_mode) begin
            rx_shift_reg <= shift_data_next;
            if (shift_done) begin
                rx_clock_cnt <= 6'd0;
            end else begin
                rx_clock_cnt <= rx_clock_cnt + 1'b1;
            end
        end
    end

    assign shift_done = shift_en && rx_mode && (rx_clock_cnt == (frame_cycles - 6'd1));

    // TX symbols are launched on the leading edge
    always_ff @(posedge sclk or negedge sys_rst_n or posedge cs_n) begin
        if (!sys_rst_n || cs_n) begin
            tx_shift_reg <= 32'h0;
            tx_clock_cnt <= 6'd0;
            tx_done      <= 1'b0;
        end else begin
            tx_done <= 1'b0;
            if (load_en) begin
                tx_shift_reg <= load_data;
                tx_clock_cnt <= 6'd0;
            end else if (shift_en && !rx_mode && data_phase) begin
                if (ENABLE_DUAL) begin
                    tx_shift_reg <= {tx_shift_reg[29:0], 2'b00};
                end else begin
                    tx_shift_reg <= {tx_shift_reg[27:0], 4'b0000};
                end

                if (tx_clock_cnt == (ACTIVE_FRAME_CLKS - 2)) begin
                    tx_clock_cnt <= 6'd0;
                    tx_done      <= 1'b1;
                end else begin
                    tx_clock_cnt <= tx_clock_cnt + 1'b1;
                end
            end
        end
    end

    assign sdo0 = data_phase ? (ENABLE_DUAL ? tx_shift_reg[30] : tx_shift_reg[28]) : 1'b0;
    assign sdo1 = data_phase ? (ENABLE_DUAL ? tx_shift_reg[31] : tx_shift_reg[29]) : 1'b0;
    assign sdo2 = (data_phase && !ENABLE_DUAL) ? tx_shift_reg[30] : 1'b0;
    assign sdo3 = (data_phase && !ENABLE_DUAL) ? tx_shift_reg[31] : 1'b0;

endmodule
