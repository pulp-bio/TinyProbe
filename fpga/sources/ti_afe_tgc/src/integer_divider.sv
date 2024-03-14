// Creates strobe signal from the root clock and divider
// Based on https://forum.digilentinc.com/topic/18256-frequency-divider-in-systemverilog/
module integer_divider #(
    parameter integer CNT_WIDTH = 16  // Counter width
)(
	input	logic	                 clk_i,
    input	logic	                 cnt_en_i,
	input	logic [CNT_WIDTH-1:0]	 div_i,
	output	logic	                 stb_o
);

	logic	[CNT_WIDTH-1:0]  cnt_d, cnt_q;

    always_comb begin
        cnt_d = cnt_q - 1;
        if(cnt_q == 0) begin
            cnt_d = div_i - 1;
        end
    end

	always_ff @(posedge clk_i) begin
        if (~cnt_en_i) begin
            cnt_q <= 0;
        end
        else begin
            cnt_q <= cnt_d;
        end
    end

	// Assign output
   	assign	stb_o = (cnt_d == 0);
        
endmodule