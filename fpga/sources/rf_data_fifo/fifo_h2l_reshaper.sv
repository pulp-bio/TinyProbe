module fifo_h2l_reshaper #(
    parameter integer INPUT_DATA_WIDTH  = 20,
    parameter integer OUTPUT_DATA_WIDTH = 8,
    parameter integer READ_CNT_WIDTH = 12
) (
    input logic                             clk_i,
    input logic                             rst_ni,
    input logic  [READ_CNT_WIDTH - 1:0]     read_cnt_i,

    // FIFO related signals
    input logic                             fifo_empty_i,
    input  logic [INPUT_DATA_WIDTH - 1:0]   fifo_data_i,
    output logic                            fifo_read_req_o,
    output logic                            fifo_rst_o,

    // Ready/Valid output interface
    output logic [OUTPUT_DATA_WIDTH - 1:0]  data_o,
    output logic                            valid_o,
    input  logic                            ready_i,

    // Start module signal
    input logic                             start_i,
    // Module busy signal
    output logic                            busy_o
);

    localparam WIDTH_DIFF = INPUT_DATA_WIDTH - OUTPUT_DATA_WIDTH;
    localparam QUOTIENT = (INPUT_DATA_WIDTH)/OUTPUT_DATA_WIDTH;
    localparam REMAINDER = INPUT_DATA_WIDTH - OUTPUT_DATA_WIDTH * QUOTIENT;
    
    // Divide OUTPUT_DATA_WIDTH by REMAINDER and then ceil
    // This will define the cycles required by accumulate the bits difference into a new output word
    localparam I_MAX = (REMAINDER == 0) ? 1 :(OUTPUT_DATA_WIDTH + REMAINDER - 1)/REMAINDER;

    // Integer number of output words in a single input word
    localparam J_MAX = (INPUT_DATA_WIDTH/OUTPUT_DATA_WIDTH);

    ///////////////////////////////// Generate parameter arrays /////////////////////////////////
    // If the input is integer divisible by the output than J_MAX, otherwise J_MAX * I_MAX
    // In the second case, +1 stands for the state when we collected enough data for two consequtive
    // write operations to the rececive FIFO
    localparam N_MUX_STATES = (REMAINDER == 0) ? J_MAX : J_MAX * I_MAX + 1;

    // Large enough to fit the data when input MUX in any possible state
    localparam BUFF_WIDTH = INPUT_DATA_WIDTH + OUTPUT_DATA_WIDTH;
    // Create a internal buffer
    logic [BUFF_WIDTH - 1: 0] buffer;
    // Create a signal to shift a buffer and load a new value
    // Next state and delayed state
    logic shift_buffer_d, shift_buffer_q;
    // Real signal
    logic shift_buffer;


    // Arrays of the main parameters of the internal FSM
    localparam TEMP_WIDTH = $clog2(INPUT_DATA_WIDTH);

    // Array of bit shifs. Guides output MUX from where in the buffer to read the data
    logic [N_MUX_STATES - 1:0][TEMP_WIDTH - 1:0] bit_shifts;
    // Defines if we need to request the FIFO at a certain state or not.
    // The first array is easier to calculate 
    // The second will be actually used in the FSM
    logic [N_MUX_STATES - 1:0] req_word_raw;
    logic [N_MUX_STATES - 1:0] req_word;

    genvar i, j;
    generate
        for (i = 0; i < I_MAX; i++) begin : gen_block_i
            for (j = 0; j < J_MAX; j++) begin : gen_block_j

                assign bit_shifts[i*J_MAX + j] = WIDTH_DIFF + i*REMAINDER - j*OUTPUT_DATA_WIDTH;
            
                if((j == J_MAX - 1)) begin
                    // If we are at max i and j
                    if ((i == I_MAX - 1) & (REMAINDER != 0)) begin
                        assign req_word_raw[i*J_MAX + j] = 0;
                    end else begin
                        assign req_word_raw[i*J_MAX + j] = 1;
                    end
                end else begin
                    assign req_word_raw[i*J_MAX + j] = 0;
                end
            end
        end

        if((REMAINDER != 0)) begin
           assign bit_shifts[N_MUX_STATES-1] = '0;
           assign req_word_raw[N_MUX_STATES-1] = 1;
        end

    endgenerate

    assign req_word = (req_word_raw >> 1) | (req_word_raw << (N_MUX_STATES - 1));
    
    localparam MUX_CTL_WIDTH = $clog2(N_MUX_STATES);
    // Create a counter (counts the states actually)
    logic [MUX_CTL_WIDTH - 1: 0] cnt_q, cnt_d;
    logic cnt_enable;
    logic cnt_clr;

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

    ///////////////////////////////// Read counter  /////////////////////////////////

    logic [READ_CNT_WIDTH - 1:0] rd_cnt_d;
    logic [READ_CNT_WIDTH - 1:0] rd_cnt_q;

    logic rd_cnt_done;

    always_comb begin
        rd_cnt_d = rd_cnt_q;
        rd_cnt_done = 0;

        if(fifo_read_req_o) begin
            rd_cnt_d = rd_cnt_q + 1;
        end

        // If read counter reaches the threshold
        // raise the flag
        if (rd_cnt_q == read_cnt_i) begin
            rd_cnt_done = 1;
        end

        // Use the dedicated signal to reset the read counter
        if (cnt_clr) begin
            rd_cnt_d = 0;
        end
    end

    // State transition logic
    always_ff  @(posedge clk_i, negedge rst_ni)begin
    if (~rst_ni) begin
            rd_cnt_q <= '0;
        end
        else begin
            rd_cnt_q <= rd_cnt_d;
        end
    end

    ///////////////////////////////// Output multiplexer /////////////////////////////////
    // (control input comes from FSM)

    logic [N_MUX_STATES - 1:0][OUTPUT_DATA_WIDTH - 1:0] temp_arr;

    // Conversion from 1D input to 2D temp array
    always_comb begin
		for (int l = 0; l < N_MUX_STATES; l++) begin
            temp_arr[l] = buffer[bit_shifts[l] +: OUTPUT_DATA_WIDTH];
        end
	end

    // Data mapping
    assign data_o = temp_arr[cnt_q];

    ///////////////////////////////// FSM /////////////////////////////////
    // FSM states type definition. This FSM is responsible for start, maintaining and finishing the transfer.
    typedef enum {IDLE, REQ_FIRST_WORD, CONT_TRANSFER, SEND_LEFTOVERS} state_e;

    // State vasriable
    state_e state_q, state_d;

    // Next state logic
    always_comb begin

        en_clr = 0;
        busy_o = 1;

        state_d = state_q;
        fifo_read_req_o = 0;

        cnt_d = cnt_q;
        cnt_enable = 0;
        cnt_clr = 0;

        valid_o = 0;

        shift_buffer_d = 0;
        shift_buffer = 0;

        unique case (state_q)
            // default state after the reset
            IDLE: begin

                // If FIFO is not empty, the module is enabled
                // and the read counter threshold is not reached
                // request the input word
                if (!fifo_empty_i && en && !rd_cnt_done) begin
                    fifo_read_req_o = 1;
                    state_d = REQ_FIRST_WORD;
                end else begin
                    // The module is not yet busy
                    // Either the FIFO is empty or the start is not triggered
                    busy_o = 1'b0;
                end
            end

            REQ_FIRST_WORD: begin
                // This state is needed for a delay
                // to wait for the input data to be available
                // and the output FIFO to be ready

                // Preload the shift buffer value
                shift_buffer_d = req_word[cnt_q];

                if (ready_i) begin
                    // Shift the first word into the internal buffer
                    shift_buffer = 1;

                    // Corner case for the sutuations
                    // When only one output word contains in the input word.
                    if (J_MAX == 1) begin
                        // Request the new word in the next cycle
                        fifo_read_req_o = 1;
                    end
                    
                    // Go to the Next state
                    state_d = CONT_TRANSFER; 
                end
            end

            CONT_TRANSFER: begin

                // Counter is always enabled in this state
                cnt_enable = 1;

                // Keep the next shifting state equal to the last precomputed value
                shift_buffer_d = req_word[cnt_q];

                // The output data is also always valid
                valid_o = 1;

                // If ouput FIFO is ready to receive do all the other checks
                if (ready_i) begin

                    // Request the input word depending on the counter state
                    // and precomputed values
                    fifo_read_req_o = req_word[cnt_q];

                    // Shift buffer value depends on the previous states
                    shift_buffer = shift_buffer_q;

                end else begin
                    // Otherwise halt the timer and wait till the output FIFO is ready
                    cnt_enable = 0;
                    // Don't shift the buffer
                    shift_buffer = 0;
                end


                // If FIFO becomes empty or the read counter almost reached the threshold 
                // check the following conditions
                if (fifo_empty_i || rd_cnt_done) begin
                    // if we need to request the input word in the next round
                    // Jump into the next state
                    if (fifo_read_req_o) begin
                        state_d = SEND_LEFTOVERS;
                        fifo_read_req_o = 0;
                    end
                end
            end

            SEND_LEFTOVERS: begin
                // Counter enabled in this state until all the output 
                // words stored in the buffer are not transmitted.
                cnt_enable = 1;

                // Of course we do not request new input words
                fifo_read_req_o = 0;

                // But the output data stays valid
                valid_o = 1;

                // Keep the next shifting state equal to the last precomputed value
                shift_buffer_d = req_word[cnt_q];

                // The same as above: proceed only if the output FIFO is ready
                if (ready_i) begin

                    // Shift buffer value depends on the previous state
                    shift_buffer = shift_buffer_q;

                    if (shift_buffer) begin
                        state_d = IDLE;
                        valid_o = 1;
                        en_clr = 1;
                        cnt_clr = 1;
                    end

                end else begin
                    // Halt the timer and wait till the output FIFO is ready
                    cnt_enable = 0;

                    // The output data stays valid
                    valid_o = 1;

                    // Don't shift the buffer
                    shift_buffer = 0;

                end


            end

            default: state_d = IDLE;
        endcase

        // Counter next state logic
        if (cnt_enable) begin
            // Check saturation and counter clear flag
            if ((cnt_q == N_MUX_STATES - 1) || (cnt_clr == 1)) begin 
                cnt_d = '0;
            end else begin
                cnt_d    =  cnt_q + 1'b1;
            end
        end

    end

    // Never reset FIFO
    assign fifo_rst_o = 0;

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
            cnt_q    <= 0;
            shift_buffer_q <= 0;
        end
        else  begin
            cnt_q    <=  cnt_d;
            // The buffer is usually shifted (written into the internal FIFO)
            // one cycle after the FIFO read request (if reasy signal is asserted)
            if (ready_i) begin
                shift_buffer_q <= shift_buffer_d; 
            end
        end
    end

    // Data buffer shifting
    always_ff  @(posedge clk_i, negedge rst_ni)begin
        if(~rst_ni) begin
            buffer  <= '0;
        end
        else  begin
            // Shift the buffer
            if (shift_buffer) begin
                buffer <= {buffer[BUFF_WIDTH - INPUT_DATA_WIDTH - 1:0], fifo_data_i};
            end
        end
    end

endmodule
