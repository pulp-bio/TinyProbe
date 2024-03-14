module ti_afe_tgc #(
    parameter integer CNT_WIDTH = 32  // Counter width
)(
    input logic                  clk_afe_i,
    input logic                  clk_i,
    input logic                  rst_ni,

    // Clock divider for slope signal
    input logic [CNT_WIDTH-1:0]  clk_div_i,

    // Input trigger signal
    input logic                  start_i,

    // Time delays aligned with input clock frequency
    input logic [CNT_WIDTH-1:0]  delay_start_i,
    input logic [CNT_WIDTH-1:0]  capt_time_i,
    input logic [CNT_WIDTH-1:0]  delay_finish_i,

    // Control signals for AFE
    output logic                 tgc_slope_o,
    output logic                 tgc_up_dn_o
);
    // Internally stored absolute delays
    logic [CNT_WIDTH-1:0]  delay_start_abs_d, delay_start_abs_q;
    logic [CNT_WIDTH-1:0]  capt_time_abs_d, capt_time_abs_q;
    logic [CNT_WIDTH-1:0]  delay_finish_abs_d, delay_finish_abs_q;

    // Internal counter
    logic [CNT_WIDTH-1:0]  cnt_d, cnt_q;
    logic cnt_en;

    // Rising edge detector signals for start input signal
    logic start_d, start_q, start_q2, start_q3;
    logic start_rising_edge_d, start_rising_edge_q;

    // Start asserted signal (indicates that start was triggered at least once) 
    // and clear signal
    logic start_asserted_d, start_asserted_q;         // Control input for FSM
    logic start_asserted_clr;                         // Control output from FSM

    // Counter related control signals
    logic cnt_exceeds_start_time;                     // Control input for FSM
    logic cnt_exceeds_capt_time;                      // Control input for FSM
    logic cnt_exceeds_finish_time;                    // Control input for FSM

    // Control signal for output waveforms
    logic tgc_slope_en;                               // Control output from FSM
    logic tgc_up_dn_en;                               // Control output from FSM

    // Strobe signal generator
    logic stb_signal;

    integer_divider #(
        .CNT_WIDTH  (32)
    ) int_div_inst (
        .clk_i(clk_i),
        .cnt_en_i(tgc_slope_en),
        .div_i(clk_div_i),
        .stb_o(stb_signal)
    );

    // Internal target signals
    logic tgc_slope_d;             
    logic tgc_up_dn_d;         

    // FSM states type definition
    typedef enum {IDLE, START_DELAY, RISING_AMP, FALLING_AMP} state_e;
    state_e state_q, state_d;

    // Start related signals
    assign start_d = start_i;

    // Rising edge detector
    // The d version is used to load the delay values
    // While q version (delayed by 1 cycled) changes start_asserted_d and thereby triggers FSM
    assign start_rising_edge_d = start_q && !start_q2;
    
    assign start_asserted_d  = start_asserted_clr ? 1'b0:
                               (start_rising_edge_q ? 1'b1 : start_asserted_q);

    // Delay load
    assign delay_start_abs_d  = start_rising_edge_d ? (delay_start_i) : delay_start_abs_q;
    assign capt_time_abs_d    = start_rising_edge_d ? (delay_start_i + capt_time_i) : capt_time_abs_q;
    assign delay_finish_abs_d = start_rising_edge_d ? (delay_start_i + capt_time_i + delay_finish_i) : delay_finish_abs_q;

    // Counter related signals
    assign cnt_exceeds_start_time   = (cnt_q >= delay_start_abs_q)  ? 1'b1 : 1'b0;
    assign cnt_exceeds_capt_time    = (cnt_q >= capt_time_abs_q)    ? 1'b1 : 1'b0;
    assign cnt_exceeds_finish_time  = (cnt_q >= delay_finish_abs_q) ? 1'b1 : 1'b0;

    assign cnt_en = start_asserted_q && (!cnt_exceeds_finish_time);
    assign cnt_d  = cnt_en ? (cnt_q + 1): '0;

    // Target signals multiplexing before syncronization
    assign tgc_slope_d = stb_signal;
    assign tgc_up_dn_d = tgc_up_dn_en;

    // FSM logic
    always_comb begin
        start_asserted_clr   = 1'b0;
        tgc_slope_en         = 1'b0;
        tgc_up_dn_en         = 1'b0;

        state_d = state_q;

        unique case (state_q)
            IDLE: begin
                if(start_asserted_q) begin
                    state_d = START_DELAY;
                end
            end

            START_DELAY: begin
                if(cnt_exceeds_start_time) begin
                    state_d = RISING_AMP;
                end
            end

            RISING_AMP: begin
                if(cnt_exceeds_capt_time) begin
                    state_d = FALLING_AMP;
                end
                tgc_slope_en = 1'b1;
            end

            FALLING_AMP: begin
                if(cnt_exceeds_finish_time) begin
                    state_d = IDLE;
                    start_asserted_clr   = 1'b1;
                end
                tgc_slope_en = 1'b1;
                tgc_up_dn_en = 1'b1;
            end
            default: state_d = IDLE;
        endcase
    end

    // Flip flops for edge detector of start signal
    always_ff  @(posedge clk_i)begin
        start_q              <= start_d;
        start_q2             <= start_q;
        start_q3             <= start_q2;
    end   

    always_ff  @(posedge clk_i, negedge rst_ni)begin
        if(~rst_ni) begin
            start_rising_edge_q  <= 1'b0;
            start_asserted_q     <= 1'b0;
            cnt_q                <= '0;
            state_q              <= IDLE;
            delay_start_abs_q    <= '1;
            capt_time_abs_q      <= '1;
            delay_finish_abs_q   <= '1;
        end
        else begin
            start_rising_edge_q  <= start_rising_edge_d;
            start_asserted_q     <= start_asserted_d;
            cnt_q                <= cnt_d;
            state_q              <= state_d;
            delay_start_abs_q    <= delay_start_abs_d;
            capt_time_abs_q      <= capt_time_abs_d;
            delay_finish_abs_q   <= delay_finish_abs_d;
        end
    end

    // AFE clock domain

    // Internal versions of output signal before syncronized with AFE clock
    logic tgc_slope_q, tgc_slope_q2, tgc_slope_q3;             
    logic tgc_up_dn_q, tgc_up_dn_q2, tgc_up_dn_q3;

    // Rising edge detector signals for tgc_slope
    logic tgc_slope_edge_d, tgc_slope_edge_q;

    // Rising edge detector signals for start input signal
    assign tgc_slope_edge_d =  tgc_slope_q2 && !tgc_slope_q3;

    // Assign outputs
    assign tgc_slope_o = tgc_slope_edge_q;
    assign tgc_up_dn_o = tgc_up_dn_q3;

    // Flip flops to sample the signals from clk_i domain (bruto force synchronizer)
    always_ff  @(posedge clk_afe_i)begin
        tgc_slope_q             <= tgc_slope_d;
        tgc_slope_q2            <= tgc_slope_q;
        tgc_slope_q3            <= tgc_slope_q2;
        tgc_up_dn_q             <= tgc_up_dn_d;
        tgc_up_dn_q2            <= tgc_up_dn_q;
    end

    // Output flip flops
    always_ff  @(negedge clk_afe_i, negedge rst_ni)begin
        if(~rst_ni) begin
            tgc_slope_edge_q        <= 1'b0;
            tgc_up_dn_q3            <= 1'b0;
        end
        else begin
            tgc_slope_edge_q        <= tgc_slope_edge_d;
            tgc_up_dn_q3            <= tgc_up_dn_q2;
        end
    end


endmodule
