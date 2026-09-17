// FSM-controlled output-register wrapper for waveform_generator.
//
// Internal US/OA timing remains in waveform_generator. External OA uses the
// separate arm/wait/capture sequencer below and shares the accumulation outputs.
module waveform_generator_fsm (
    input  logic        clk_i,
    input  logic        rst_ni,

    // General signals
    input  logic [15:0] sync_period_i,
    input  logic [15:0] start_cap_time_i,
    input  logic [15:0] capture_delay_i,
    input  logic        start_capture_i,
    input  logic [7:0] n_shots_i,
    input  logic        fifo_rd_busy_i,
    input  logic        oa_mode_i,
    input  logic [15:0] oa_pulse_width_cycles_i,
    input  logic        external_mode_i,
    input  logic        external_trigger_i,
    input  logic        external_sample_clk_i,
    input  logic        capture_done_i,
    input  logic        abort_external_i,
    output logic [31:0] external_debug_o,
    output logic [31:0] external_input_debug_o,
    input  logic        core_clk_fast_i,
    // Public terminal-count event from waveform_generator.
    output logic        period_done_o,

    // RX FIFO control signals
    output logic        fifo_start_capture_o,
    output logic        fifo_rst_o,
    output logic        fifo_wr_en_o,
    output logic        accumulation_sequence_start_o, //clear the old accumulation data and start a new sequence
    output logic        accumulation_active_o, //FSM is running
    output logic        accumulation_first_shot_o, //this is the first shot
    output logic        accumulation_final_shot_o, //this is the last

    // TX chip signals
    input  logic [7:0]  tx_wake_up_time_i,
    input  logic [7:0]  tx_sleep_time_i,
    output logic        tx_bf_sync_o,
    output logic        tx_clk_buf_en_o,
    output logic        tx_sync_buf_en_o,
    output logic        tx_tr_en_o,

    // TX chip LDO refreshing options
    input  logic        refresh_en_i,
    input  logic [15:0] tr_en_period_i,
    input  logic [7:0]  tr_en_on_time_i,

    // AFE chip signals
    input  logic [7:0]  afe_wake_up_time_i,
    input  logic [15:0] afe_clk_on_time_i,
    input  logic [15:0] afe_data_acq_time_i,
    output logic        afe_tx_trig_o,
    output logic        afe_tx_trig_buf_en_o,
    output logic        afe_clk_buf_en_o,
    output logic        afe_fast_pdn_o
);

    // waveform_next and waveform_q use this common, explicit bit mapping.
    localparam int unsigned WF_FIFO_START_CAPTURE = 0;
    localparam int unsigned WF_FIFO_RST           = 1;
    localparam int unsigned WF_FIFO_WR_EN         = 2;
    localparam int unsigned WF_TX_BF_SYNC         = 3;
    localparam int unsigned WF_TX_CLK_BUF_EN      = 4;
    localparam int unsigned WF_TX_SYNC_BUF_EN     = 5;
    localparam int unsigned WF_TX_TR_EN           = 6;
    localparam int unsigned WF_AFE_TX_TRIG        = 7;
    localparam int unsigned WF_AFE_TX_TRIG_BUF_EN = 8;
    localparam int unsigned WF_AFE_CLK_BUF_EN     = 9;
    localparam int unsigned WF_AFE_FAST_PDN       = 10;
    localparam int unsigned NUM_OUTPUTS            = 11;
    // Only bit 10 is set: afe_fast_pdn_o is active low, so 1 is inactive.
    localparam logic [NUM_OUTPUTS-1:0] WAVEFORM_RESET_VALUE =
        11'b10000000000;

    typedef enum logic [1:0] {
        HOLD        = 2'b00,
        FORCE_0     = 2'b01,
        FORCE_1     = 2'b10,
        FOLLOW_WAVE = 2'b11
    } waveform_control_t;

    // Public outputs of the unmodified timing generator: these are the next
    // desired values for the wrapper registers, never its internal _d/_q nets.
    logic period_done_next;
    logic fifo_start_capture_next, fifo_rst_next, fifo_wr_en_next;
    logic tx_bf_sync_next, tx_clk_buf_en_next, tx_sync_buf_en_next, tx_tr_en_next;
    logic afe_tx_trig_next, afe_tx_trig_buf_en_next;
    logic afe_clk_buf_en_next, afe_fast_pdn_next;
    logic [NUM_OUTPUTS-1:0] waveform_next;
    logic [NUM_OUTPUTS-1:0] waveform_d;
    logic [NUM_OUTPUTS-1:0] waveform_q;
    // Output i is controlled by control_word[2*i +: 2].
    logic [(2*NUM_OUTPUTS)-1:0] control_word;

    waveform_generator waveform_gen (
    .clk_i                (clk_i),

    .rst_ni               (rst_ni),

    // General signals
    .sync_period_i        (sync_period_i),
    .start_cap_time_i     (start_cap_time_i),
    .capture_delay_i      (capture_delay_i),
    .start_capture_i      (start_capture_i && !external_mode_i),
    .n_shots_i            (n_shots_i),
    .fifo_rd_busy_i       (fifo_rd_busy_i),
    .oa_mode_i            (oa_mode_i),
    .oa_pulse_width_cycles_i(oa_pulse_width_cycles_i),

    // Public terminal-count event
    .period_done_o        (period_done_next),

    // RX FIFO control signals
    .fifo_start_capture_o (fifo_start_capture_next),
    .fifo_rst_o           (fifo_rst_next),
    .fifo_wr_en_o         (fifo_wr_en_next),

    // TX chip signals
    .tx_wake_up_time_i    (tx_wake_up_time_i),
    .tx_sleep_time_i      (tx_sleep_time_i),
    .tx_bf_sync_o         (tx_bf_sync_next),
    .tx_clk_buf_en_o      (tx_clk_buf_en_next),
    .tx_sync_buf_en_o     (tx_sync_buf_en_next),
    .tx_tr_en_o           (tx_tr_en_next),

    // TX chip LDO refreshing options
    .refresh_en_i         (refresh_en_i),
    .tr_en_period_i       (tr_en_period_i),
    .tr_en_on_time_i      (tr_en_on_time_i),

    // AFE chip signals
    .afe_wake_up_time_i   (afe_wake_up_time_i),
    .afe_clk_on_time_i    (afe_clk_on_time_i),
    .afe_data_acq_time_i  (afe_data_acq_time_i),
    .afe_tx_trig_o        (afe_tx_trig_next),
    .afe_tx_trig_buf_en_o (afe_tx_trig_buf_en_next),
    .afe_clk_buf_en_o     (afe_clk_buf_en_next),
    .afe_fast_pdn_o       (afe_fast_pdn_next)
);

    always_comb begin
        waveform_next = '0;
        waveform_next[WF_FIFO_START_CAPTURE] = fifo_start_capture_next;
        waveform_next[WF_FIFO_RST]           = fifo_rst_next;
        waveform_next[WF_FIFO_WR_EN]         = fifo_wr_en_next;
        waveform_next[WF_TX_BF_SYNC]         = tx_bf_sync_next;
        waveform_next[WF_TX_CLK_BUF_EN]      = tx_clk_buf_en_next;
        waveform_next[WF_TX_SYNC_BUF_EN]     = tx_sync_buf_en_next;
        waveform_next[WF_TX_TR_EN]           = tx_tr_en_next;
        waveform_next[WF_AFE_TX_TRIG]        = afe_tx_trig_next;
        waveform_next[WF_AFE_TX_TRIG_BUF_EN] = afe_tx_trig_buf_en_next;
        waveform_next[WF_AFE_CLK_BUF_EN]     = afe_clk_buf_en_next;
        waveform_next[WF_AFE_FAST_PDN]       = afe_fast_pdn_next;
    end

    typedef enum logic [1:0] {
        INITIAL_SETUP,
        SHOT_ACQUISITION,
        RESET
    } state_t;

    state_t state_q, state_d; //current and next state
    logic [7:0] shot_count_q; // number of shots remaining
    logic [7:0] shot_count_d;
    logic        start_capture_q; // detect rising edge of start_capture_i
    logic        start_new_sequence; // one pulse high to load the number of requested shots and move from initial to shot state
    // Remembers a start edge received in RESET while INITIAL_SETUP is applied
    // for one complete clock cycle before the next acquisition begins.
    logic        sequence_pending_q;
    logic        sequence_pending_d;
    logic        shot_done; // means the sync_period is reached 
    logic        sequence_start_accepted;

    // period_done_next is asserted for the terminal-count cycle immediately
    // before waveform_generator reloads its main counter to zero.
    assign shot_done          = external_mode_i ? 1'b0 : period_done_next;
    assign start_new_sequence = start_capture_i && !start_capture_q && !external_mode_i;
    // Match the original generator: ignore new start edges while shots are
    // already active.  Only an edge which the FSM can accept may clear the
    // accumulation/result pipeline.
    assign sequence_start_accepted = start_new_sequence &&
        ((state_q == INITIAL_SETUP) || (state_q == RESET));

    // Two-process FSM. Every output mode is assigned explicitly in every state;
    // the default HOLD assignment also provides safe illegal-state behavior.
    always_comb begin
        state_d            = state_q;
        shot_count_d       = shot_count_q;
        sequence_pending_d = sequence_pending_q;

        for (int i = 0; i < NUM_OUTPUTS; i++)
            control_word[2*i +: 2] = HOLD;

        unique case (state_q)
            INITIAL_SETUP: begin
                control_word[2*WF_FIFO_START_CAPTURE +: 2] = HOLD;
                control_word[2*WF_FIFO_RST           +: 2] = HOLD;
                control_word[2*WF_FIFO_WR_EN         +: 2] = HOLD;
                control_word[2*WF_TX_BF_SYNC         +: 2] = HOLD;
                control_word[2*WF_TX_CLK_BUF_EN      +: 2] = FORCE_1;
                control_word[2*WF_TX_SYNC_BUF_EN     +: 2] = FORCE_1;
                control_word[2*WF_TX_TR_EN           +: 2] = FOLLOW_WAVE;
                control_word[2*WF_AFE_TX_TRIG        +: 2] = HOLD;
                control_word[2*WF_AFE_TX_TRIG_BUF_EN +: 2] = FORCE_1;
                control_word[2*WF_AFE_CLK_BUF_EN     +: 2] = FORCE_1;
                control_word[2*WF_AFE_FAST_PDN       +: 2] = HOLD;

                if (sequence_pending_q) begin
                    sequence_pending_d = 1'b0;
                    state_d            = SHOT_ACQUISITION;
                end else if (start_new_sequence) begin
                    shot_count_d = n_shots_i;
                    state_d      = SHOT_ACQUISITION;
                end
            end

            SHOT_ACQUISITION: begin
                control_word[2*WF_FIFO_START_CAPTURE +: 2] = FOLLOW_WAVE;
                control_word[2*WF_FIFO_RST           +: 2] = FOLLOW_WAVE;
                control_word[2*WF_FIFO_WR_EN         +: 2] = FOLLOW_WAVE;
                control_word[2*WF_TX_BF_SYNC         +: 2] = FOLLOW_WAVE;
                control_word[2*WF_TX_CLK_BUF_EN      +: 2] = HOLD;
                control_word[2*WF_TX_SYNC_BUF_EN     +: 2] = HOLD;
                control_word[2*WF_TX_TR_EN           +: 2] = FOLLOW_WAVE;
                control_word[2*WF_AFE_TX_TRIG        +: 2] = FOLLOW_WAVE;
                control_word[2*WF_AFE_TX_TRIG_BUF_EN +: 2] = HOLD;
                control_word[2*WF_AFE_CLK_BUF_EN     +: 2] = HOLD;
                control_word[2*WF_AFE_FAST_PDN       +: 2] = FOLLOW_WAVE;

                if (shot_done && (shot_count_q > 0)) begin
                    shot_count_d = shot_count_q - 1'b1;

                    // Test the next count so the final completed shot moves
                    // directly into RESET on the same active clock edge.
                    if (shot_count_d == 0)
                        state_d = RESET;
                end
            end

            RESET: begin
                // Restore the same externally inactive values produced by
                // waveform_generator after its shot counter reached zero.
                control_word[2*WF_FIFO_START_CAPTURE +: 2] = FORCE_0;
                control_word[2*WF_FIFO_RST           +: 2] = FORCE_0;
                control_word[2*WF_FIFO_WR_EN         +: 2] = FORCE_0;
                control_word[2*WF_TX_BF_SYNC         +: 2] = FORCE_0;
                control_word[2*WF_TX_CLK_BUF_EN      +: 2] = FORCE_0;
                control_word[2*WF_TX_SYNC_BUF_EN     +: 2] = FORCE_0;
                control_word[2*WF_TX_TR_EN           +: 2] = FOLLOW_WAVE;
                control_word[2*WF_AFE_TX_TRIG        +: 2] = FORCE_0;
                control_word[2*WF_AFE_TX_TRIG_BUF_EN +: 2] = FORCE_0;
                control_word[2*WF_AFE_CLK_BUF_EN     +: 2] = FORCE_0;
                control_word[2*WF_AFE_FAST_PDN       +: 2] = FORCE_1;

                shot_count_d = '0;

                // Remain stopped after the completed sequence.  A new
                // acquisition can begin only after a new rising edge of
                // start_capture_i, at which point the remaining-shot counter
                // is reloaded for the new sequence.
                if (start_new_sequence) begin
                    shot_count_d       = n_shots_i;
                    sequence_pending_d = 1'b1;
                    state_d            = INITIAL_SETUP;
                end
            end

            default: begin
                shot_count_d       = '0;
                sequence_pending_d = 1'b0;
                state_d            = INITIAL_SETUP;
            end
        endcase
    end

    // Calculate the next registered waveform value in the same _d/_q style as
    // waveform_generator. FOLLOW_WAVE is evaluated every clock cycle, so it can
    // track repeated changes without an FSM state transition. it is essentially a mapping from 
    // control word to waveform_d
    always_comb begin
        waveform_d = waveform_q;

        for (int i = 0; i < NUM_OUTPUTS; i++) begin
            case (control_word[2*i +: 2])
                HOLD:        waveform_d[i] = waveform_q[i];
                FORCE_0:     waveform_d[i] = 1'b0;
                FORCE_1:     waveform_d[i] = 1'b1;
                FOLLOW_WAVE: waveform_d[i] = waveform_next[i];
                default:     waveform_d[i] = waveform_q[i];
            endcase
        end
    end

    // FSM state register.
    always_ff @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            state_q         <= INITIAL_SETUP;
            shot_count_q    <= '0;
            start_capture_q <= 1'b0;
            sequence_pending_q <= 1'b0;
        end else begin
            state_q         <= state_d;
            shot_count_q    <= shot_count_d;
            start_capture_q <= start_capture_i;
            sequence_pending_q <= sequence_pending_d;
        end
    end

    // Final waveform output registers. two ff so we can distinguish between the waveform_gen state to outputs
    always_ff @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            // Match the generator's externally inactive values: all outputs
            // low except the active-low AFE fast-power-down signal, which is 1.
            waveform_q <= WAVEFORM_RESET_VALUE;
        end else begin
            waveform_q <= waveform_d;
        end
    end

    // External laser acquisition. The fast-clock edge toggle crosses into
    // the waveform clock; triggers must be separated by at least 6 core clocks.
    // Inputs are sampled at 60 MHz: high and low must each last >= 50 ns.
    logic ext_meta, ext_sync, ext_prev, ext_toggle;
    logic ext_high_seen;
    always_ff @(posedge external_sample_clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            ext_meta<=0; ext_sync<=0; ext_prev<=0; ext_toggle<=0;
            ext_high_seen<=0;
        end else begin
            ext_meta<=external_trigger_i; ext_sync<=ext_meta; ext_prev<=ext_sync;
            if (ext_sync) ext_high_seen<=1;
            if (ext_sync && !ext_prev) ext_toggle<=~ext_toggle;
        end
    end
    logic toggle_meta, toggle_sync, toggle_seen, done_meta, done_sync;
    always_ff @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            toggle_meta<=0; toggle_sync<=0; toggle_seen<=0;
            done_meta<=0; done_sync<=0;
        end else begin
            toggle_meta<=ext_toggle; toggle_sync<=toggle_meta; toggle_seen<=toggle_sync;
            done_meta<=capture_done_i; done_sync<=done_meta;
        end
    end
    wire ext_edge = toggle_sync ^ toggle_seen;
    logic input_level_meta, input_level_core, high_seen_meta, high_seen_core;
    logic [15:0] input_edge_count;
    // Count received edges independently of arming; retain evidence through abort.
    always_ff @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            input_level_meta<=0; input_level_core<=0;
            high_seen_meta<=0; high_seen_core<=0; input_edge_count<=0;
        end else begin
            input_level_meta<=ext_sync; input_level_core<=input_level_meta;
            high_seen_meta<=ext_high_seen; high_seen_core<=high_seen_meta;
            if (ext_edge && input_edge_count!=16'hffff)
                input_edge_count<=input_edge_count+1'b1;
        end
    end
    assign external_input_debug_o = {8'he7, 5'b0, fifo_rd_busy_i,
                                    high_seen_core, input_level_core, input_edge_count};
    typedef enum logic [3:0] {EXT_IDLE, EXT_CLEAR, EXT_WARM, EXT_PREP,
        EXT_WAIT, EXT_DELAY, EXT_CAPTURE, EXT_DRAIN, EXT_FINISHED} ext_state_t;
    ext_state_t ext_state;
    logic [17:0] ext_count;
    logic [15:0] ext_delay, ext_duration;
    logic [7:0] ext_remaining, ext_total;
    logic [15:0] ext_ignored;
    logic ext_done_low, ext_trigger_pulse;
    logic [NUM_OUTPUTS-1:0] external_wave;
    wire external_active = (ext_state != EXT_IDLE && ext_state != EXT_CLEAR);
    always_ff @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            ext_state<=EXT_IDLE; ext_count<=0; ext_remaining<=0; ext_total<=0;
            ext_delay<=0; ext_duration<=0; ext_ignored<=0;
            ext_done_low<=0; ext_trigger_pulse<=0;
        end else begin
            ext_trigger_pulse<=0;
            if (!external_mode_i || abort_external_i) ext_state<=EXT_IDLE;
            else if (start_capture_i && !start_capture_q &&
                     (ext_state==EXT_IDLE || ext_state==EXT_FINISHED)) begin
                ext_state<=EXT_CLEAR;
                ext_remaining <= n_shots_i==0 ? 8'd1 : n_shots_i;
                ext_total <= n_shots_i==0 ? 8'd1 : n_shots_i;
                ext_delay<=capture_delay_i;
                ext_duration<=afe_data_acq_time_i==0 ? 16'd1 : afe_data_acq_time_i;
                // Keep clocks running while receiver powers up, with the same
                // minimum 50 us clock settling and 3 us wake-up as normal setup.
                ext_count <= (afe_clk_on_time_i < (core_clk_fast_i ? 1000 : 500) ?
                    (core_clk_fast_i ? 1000 : 500) : afe_clk_on_time_i) +
                    (afe_wake_up_time_i < (core_clk_fast_i ? 60 : 30) ?
                    (core_clk_fast_i ? 60 : 30) : afe_wake_up_time_i) + 16;
                ext_ignored<=0;
            end else begin
                if (ext_edge && ext_state!=EXT_WAIT && external_active && ext_ignored!=16'hffff)
                    ext_ignored<=ext_ignored+1'b1;
                case(ext_state)
                    EXT_CLEAR: ext_state<=EXT_WARM;
                    EXT_WARM: if(ext_count==0) begin ext_state<=EXT_PREP; ext_count<=8; end
                              else ext_count<=ext_count-1'b1;
                    EXT_PREP: if(ext_count==0) ext_state<=EXT_WAIT;
                              else ext_count<=ext_count-1'b1;
                    EXT_WAIT: if(ext_edge && !fifo_rd_busy_i) begin
                        ext_trigger_pulse<=1;
                        ext_count<=0; ext_done_low<=0;
                        if(ext_delay==0) ext_state<=EXT_CAPTURE;
                        else ext_state<=EXT_DELAY;
                    end
                    EXT_DELAY: if(ext_count+1 >= {2'b0,ext_delay}) begin
                        ext_count<=0; ext_state<=EXT_CAPTURE;
                    end else ext_count<=ext_count+1'b1;
                    EXT_CAPTURE: begin
                        if(!done_sync) ext_done_low<=1;
                        // Keep flags stable while the AFE detects the start.
                        if(ext_count>=5 && ext_done_low && done_sync) ext_state<=EXT_DRAIN;
                        else if(ext_count+1 >= {2'b0,ext_duration} && ext_count>=5) ext_state<=EXT_DRAIN;
                        else ext_count<=ext_count+1'b1;
                    end
                    EXT_DRAIN: begin
                        if(!done_sync) ext_done_low<=1;
                        if(ext_done_low && done_sync) begin
                            if(ext_remaining==1) ext_state<=EXT_FINISHED;
                            else begin ext_remaining<=ext_remaining-1'b1;
                                ext_count<=8; ext_state<=EXT_PREP; end
                        end
                    end
                    default: begin end
                endcase
                if(ext_edge && ext_state==EXT_WAIT && fifo_rd_busy_i && ext_ignored!=16'hffff)
                    ext_ignored<=ext_ignored+1'b1;
            end
        end
    end
    always_comb begin
        external_wave=WAVEFORM_RESET_VALUE;
        external_wave[WF_AFE_CLK_BUF_EN]=external_active;
        external_wave[WF_AFE_TX_TRIG_BUF_EN]=external_active;
        external_wave[WF_AFE_FAST_PDN]=!external_active;
        external_wave[WF_AFE_TX_TRIG]=ext_trigger_pulse;
        external_wave[WF_FIFO_RST]=(ext_state==EXT_PREP);
        external_wave[WF_FIFO_START_CAPTURE]=(ext_state==EXT_CAPTURE && ext_count<5);
        external_wave[WF_FIFO_WR_EN]=(ext_state==EXT_CAPTURE);
    end
    assign external_debug_o={ext_ignored, ext_remaining, 3'b0,
        (ext_state==EXT_WAIT), ext_state};
    wire [NUM_OUTPUTS-1:0] selected_wave = external_mode_i ? external_wave : waveform_q;
    assign fifo_start_capture_o = selected_wave[WF_FIFO_START_CAPTURE];
    // period_done_o is a status/control event, not a waveform output.  It is
    // passed through unregistered so its assertion remains aligned with the
    // original counter's reload-to-zero clock edge.
    assign period_done_o                    = external_mode_i ? 1'b0 : period_done_next;
    assign fifo_rst_o                       = selected_wave[WF_FIFO_RST];
    assign fifo_wr_en_o                     = selected_wave[WF_FIFO_WR_EN];
    assign accumulation_sequence_start_o    = external_mode_i ? (ext_state==EXT_CLEAR) : sequence_start_accepted;
    assign accumulation_active_o            = external_mode_i ? external_active : (state_q == SHOT_ACQUISITION);
    assign accumulation_first_shot_o        = external_mode_i ? (ext_remaining==ext_total) : ((state_q == SHOT_ACQUISITION) && (shot_count_q == n_shots_i));
    assign accumulation_final_shot_o        = external_mode_i ? (ext_remaining==1) : ((state_q == SHOT_ACQUISITION) && (shot_count_q == 1));
    assign tx_bf_sync_o                     = selected_wave[WF_TX_BF_SYNC];
    assign tx_clk_buf_en_o                  = selected_wave[WF_TX_CLK_BUF_EN];
    assign tx_sync_buf_en_o                 = selected_wave[WF_TX_SYNC_BUF_EN];
    assign tx_tr_en_o                       = selected_wave[WF_TX_TR_EN];
    assign afe_tx_trig_o                    = selected_wave[WF_AFE_TX_TRIG];
    assign afe_tx_trig_buf_en_o             = selected_wave[WF_AFE_TX_TRIG_BUF_EN];
    assign afe_clk_buf_en_o                 = selected_wave[WF_AFE_CLK_BUF_EN];
    assign afe_fast_pdn_o                   = selected_wave[WF_AFE_FAST_PDN];

endmodule
