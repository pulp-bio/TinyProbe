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
    output logic [N_FIFOS - 1:0]                         fifos_rst_o,

    // Ready/Valid output interface
    output logic [OUT_DATA_WIDTH - 1:0]                  data_o,
    output logic                                         valid_o,
    input  logic                                         ready_i
);

    ///////////////////////////////// Input start trigger  /////////////////////////////////
    logic start_q;

    // Internal enable signal
    logic en, en_clr;

    // State transition logic
    always_ff  @(posedge clk_i, negedge rst_ni)begin
        if (~rst_ni) begin
            en <= '0;
            start_q <= start_i;
        end
        else begin
            if (en_clr)
                en <= '0;
            // Edge detector
            else if(~start_q & start_i)
                en <= 1'b1;
            start_q <= start_i;
        end
    end

    ///////////////////////////////// FSM /////////////////////////////////
    // FSM states type definition. This FSM is responsible for start, maintaining and finishing the transfer.
    typedef enum {IDLE, WAIT_TILL_BUSY, WAIT_READ, FINISHED} state_e;

    // State vasriable
    state_e state_q, state_d;

    // Counter variables
    localparam CNT_WIDTH = $clog2(N_FIFOS);
    // Create a counter (counts the states actually)
    logic [(CNT_WIDTH + 1) - 1: 0] cnt_d, cnt_q;
    logic [CNT_WIDTH - 1: 0] mux_ctrl;
    logic cnt_enable;

    // A variable indication the next and current active FIFO
    logic switch_fifo;

    // A signal to start the submodule
    logic start_submod_d, start_submod_q;
    logic submod_busy;

    logic active_fifo_found;
    assign active_fifo_found = |((1 << cnt_q) & fifos_en_i);

    // Next state logic
    always_comb begin

        busy_o = 1;

        en_clr = 0;
        
        state_d = state_q;

        start_submod_d = 0;

        switch_fifo = 0;
        cnt_enable = 0;

        unique case (state_q)
            // default state after the reset
            IDLE: begin
                // Start by finding the first non-zero active FIFO ID
                cnt_enable = 1;

                // Check if start condition is met
                if(en) begin
                    // If the next FIFO is found
                    if (active_fifo_found) begin
                        state_d = WAIT_TILL_BUSY;
                        // Multiplex the FIFO signals to the new one
                        switch_fifo = 1;
                        // Start the submodule
                        start_submod_d = 1;
                        // Keep the counter running to find the next active FIFO
                        cnt_enable = 1;
                    end 

                end else begin

                    // Disable the counter
                    cnt_enable = 0;

                    // The module is not yet busy
                    busy_o = 0;

                end
            end

            WAIT_TILL_BUSY: begin
                // Wait until submodule has started
                if (submod_busy) begin
                    state_d = WAIT_READ;
                end
            end

            WAIT_READ: begin

                // If fifo reshaper is not busy anymore
                // (finished its job)
                if (!submod_busy) begin

                    // Check if the counter saturated
                    if (cnt_q == N_FIFOS) begin
                        // No more active FIFOs found
                        // Finish
                        state_d = FINISHED;
                        en_clr = 1;

                    end else begin

                        // Enable counter
                        cnt_enable = 1;

                        // If the next FIFO is found
                        if(active_fifo_found) begin

                            state_d = WAIT_TILL_BUSY;
                            // Multiplex the FIFO signals to the new one
                            switch_fifo = 1;
                            // Start the submodule
                            start_submod_d = 1;

                            // Keep the counter running to find the next active FIFO
                            cnt_enable = 1;
                        end 
                    end              
                end else

                // If the next active FIFO is found
                // keep its state in the counter (disable the counter) but do not yet switch fifo
                if (active_fifo_found) begin
                    switch_fifo = 0;
                    cnt_enable = 0;
                end else begin
                    // Keep iterating further
                    cnt_enable = 1;                    
                end;


            end

            FINISHED: begin
                // The module is not busy
                busy_o = 0;
                state_d = FINISHED;
            end
            default: state_d = IDLE;
        endcase

        // Counter next state logic
        if (cnt_enable) begin
            // Check saturation
            if (cnt_q == N_FIFOS) begin 
                cnt_d = N_FIFOS;
            end else begin
                cnt_d    =  cnt_q + 1'b1;
            end
        end else begin
            cnt_d = cnt_q;
        end

    end

    // State transition logic
    always_ff  @(posedge clk_i, negedge rst_ni)begin
        if (~rst_ni)
            state_q <= IDLE;
        else
            state_q <= state_d;
    end

    // Counter state transition
    always_ff  @(posedge clk_i, negedge rst_ni)begin
        if(~rst_ni) begin
            cnt_q          <= '0;
            mux_ctrl       <= '0;
            start_submod_q <=  0;
            
        end
        else  begin
            cnt_q          <= cnt_d;

            start_submod_q <= start_submod_d;

            if(switch_fifo) begin
                mux_ctrl   <= cnt_q;
            end
        end
    end

    ///////////////////////////////// FIFOs signals multiplexing /////////////////////////////////


    logic [N_FIFOS - 1:0][IN_DATA_WIDTH - 1:0] fifos_data_temp;

    // Conversion from 1D input to 2D temp array
    always_comb begin
		for (int l = 0; l < N_FIFOS; l++) begin
            fifos_data_temp[l] = fifos_data_i[(l * IN_DATA_WIDTH) +: IN_DATA_WIDTH];
        end
	end

    // Data input mapping
    logic [IN_DATA_WIDTH - 1:0] h2l_data_in;
    assign h2l_data_in = fifos_data_temp[mux_ctrl];

    // FIFO empty signal mapping
    logic h2l_fifo_empty;
    assign h2l_fifo_empty = fifos_empty_i[mux_ctrl];


    logic h2l_fifo_read_req, h2l_fifo_rst;

    // Read request signal and reset
    genvar i;
    generate
        for (i = 0; i < N_FIFOS; i++) begin : gen_block_fifos_read_o
            assign fifos_read_req_o[i] = (mux_ctrl == i) ? h2l_fifo_read_req : 0;
            assign fifos_rst_o[i] = (mux_ctrl == i) ? h2l_fifo_rst : 0;
        end
    endgenerate


    ///////////////////////////////// FIFO h2l Reshaper instance /////////////////////////////////

    fifo_h2l_reshaper #(
        .INPUT_DATA_WIDTH     (IN_DATA_WIDTH),
        .OUTPUT_DATA_WIDTH    (OUT_DATA_WIDTH),
        .READ_CNT_WIDTH       (READ_CNT_WIDTH)
    ) fifo_h2l_reshaper_inst (
        .clk_i                (clk_i),
        .rst_ni               (rst_ni),
        .read_cnt_i           (read_cnt_i),
        .fifo_empty_i         (h2l_fifo_empty),
        .fifo_data_i          (h2l_data_in),
        .fifo_read_req_o      (h2l_fifo_read_req),
        .fifo_rst_o           (h2l_fifo_rst),
        .data_o               (data_o),
        .valid_o              (valid_o),
        .ready_i              (ready_i),
        .start_i              (start_submod_q),
        .busy_o               (submod_busy)
    );

endmodule
