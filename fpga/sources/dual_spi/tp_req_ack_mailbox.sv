// Author: Soumyo Bhattacharjee
// One-entry bundled-data mailbox between unrelated clock domains.
//
// The source captures src_data_i while src_ready_o is high, then toggles a
// request bit.  The data remains unchanged until the destination observes the
// request and returns an acknowledgement.  dst_valid_o is a one-dst_clk_i
// pulse for each accepted source request.
//
// This is intended for infrequent single-word control transfers.  Use an
// asynchronous FIFO for burst or continuously streamed data.
module tp_req_ack_mailbox #(
    parameter int WIDTH = 32,
    // SPI writes complete on a falling capture edge.  Selecting this option
    // lets that source domain commit without requiring a following SCLK edge.
    parameter bit SRC_ON_NEGEDGE = 1'b0
) (
    input  logic             src_clk_i,
    input  logic             src_rst_ni,
    input  logic [WIDTH-1:0] src_data_i,
    input  logic             src_valid_i,
    output logic             src_ready_o,
    output logic [WIDTH-1:0] src_captured_data_o,

    input  logic             dst_clk_i,
    input  logic             dst_rst_ni,
    output logic [WIDTH-1:0] dst_data_o,
    output logic             dst_valid_o
);
    logic [WIDTH-1:0] data_q;
    logic req_toggle_q, ack_toggle_q;
    (* ASYNC_REG = "TRUE" *) logic ack_meta_q, ack_sync_q;
    (* ASYNC_REG = "TRUE" *) logic req_meta_q, req_sync_q;
    logic req_seen_q;

    // The source may overwrite data_q only after the acknowledged request.
    assign src_ready_o = (req_toggle_q == ack_sync_q);
    assign src_captured_data_o = data_q;
    assign dst_data_o  = data_q;

    generate
        if (SRC_ON_NEGEDGE) begin : g_src_negedge
            always_ff @(negedge src_clk_i or negedge src_rst_ni) begin
                if (!src_rst_ni) begin
                    data_q       <= '0;
                    req_toggle_q <= 1'b0;
                    ack_meta_q   <= 1'b0;
                    ack_sync_q   <= 1'b0;
                end else begin
                    ack_meta_q <= ack_toggle_q;
                    ack_sync_q <= ack_meta_q;
                    if (src_valid_i && src_ready_o) begin
                        data_q       <= src_data_i;
                        req_toggle_q <= ~req_toggle_q;
                    end
                end
            end
        end else begin : g_src_posedge
            always_ff @(posedge src_clk_i or negedge src_rst_ni) begin
                if (!src_rst_ni) begin
                    data_q       <= '0;
                    req_toggle_q <= 1'b0;
                    ack_meta_q   <= 1'b0;
                    ack_sync_q   <= 1'b0;
                end else begin
                    ack_meta_q <= ack_toggle_q;
                    ack_sync_q <= ack_meta_q;
                    if (src_valid_i && src_ready_o) begin
                        data_q       <= src_data_i;
                        req_toggle_q <= ~req_toggle_q;
                    end
                end
            end
        end
    endgenerate

    always_ff @(posedge dst_clk_i or negedge dst_rst_ni) begin
        if (!dst_rst_ni) begin
            req_meta_q  <= 1'b0;
            req_sync_q  <= 1'b0;
            req_seen_q  <= 1'b0;
            ack_toggle_q <= 1'b0;
            dst_valid_o <= 1'b0;
        end else begin
            req_meta_q  <= req_toggle_q;
            req_sync_q  <= req_meta_q;
            dst_valid_o <= 1'b0;
            if (req_sync_q != req_seen_q) begin
                req_seen_q   <= req_sync_q;
                ack_toggle_q <= req_sync_q;
                dst_valid_o  <= 1'b1;
            end
        end
    end
endmodule
