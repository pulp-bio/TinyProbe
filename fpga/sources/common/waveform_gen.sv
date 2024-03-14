
module waveform_generator (
    input logic         clk_i,
    input logic         rst_ni,

    // General signals
    input logic  [15:0] sync_period_i,
    input logic  [15:0] start_cap_time_i,
    input logic  [15:0] capture_delay_i,
    input logic         start_capture_i,
    input logic  [15:0] n_shots_i,
    input logic         fifo_rd_busy_i,

    // RX FIFO control signals
    output logic        fifo_start_capture_o,
    output logic        fifo_rst_o,
    output logic        fifo_wr_en_o,

    // TX chip signals
    input logic  [7:0]  tx_wake_up_time_i,
    input logic  [7:0]  tx_sleep_time_i,
    output logic        tx_bf_sync_o,
    output logic        tx_clk_buf_en_o,
    output logic        tx_sync_buf_en_o,
    output logic        tx_tr_en_o,

    // TX chip LDO reshreshing options
    input logic         refresh_en_i,
    input logic  [15:0] tr_en_period_i,
    input logic  [7:0]  tr_en_on_time_i,

    // AFE chip signals
    input logic  [7:0]  afe_wake_up_time_i,
    input logic  [15:0] afe_clk_on_time_i,
    input logic  [15:0] afe_data_acq_time_i,
    output logic        afe_tx_trig_o,
    output logic        afe_tx_trig_buf_en_o,
    output logic        afe_clk_buf_en_o,
    output logic        afe_fast_pdn_o
);

  // Capture request.
  logic start_capt_q1, start_capt_q2;
  logic start_capt_rising_edge;

  assign start_capt_rising_edge = start_capt_q1 && !start_capt_q2;

  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      start_capt_q1 <= 1'b0;
      start_capt_q2 <= 1'b0;
    end else begin
      start_capt_q1 <= start_capture_i;
      start_capt_q2 <= start_capt_q1;
    end
  end

    ///////////////////////////////// Shot counter + shot enable /////////////////////////////////

    logic [15:0] shot_cnt_d, shot_cnt_q;
    logic shot_en_d, shot_en_q;

    logic afe_trig_done, sync_per_finish, sync_per_almost_finish;

    // Shot enabled if shot counter is nonzero
    assign shot_en_d = (shot_cnt_q != 0) ? 1'b1 : 1'b0;

    always_comb begin

        // Preserve the counter by default
        shot_cnt_d = shot_cnt_q;

        // If the start condition is met, and the previous shots are finished, load n_shots_i
        if (start_capt_rising_edge && (shot_cnt_q == 0)) begin
            shot_cnt_d = n_shots_i;
        // If number of shots is non-zero and AFE was triggered in this cycle
        end else if (shot_cnt_q != 0 && afe_trig_done && sync_per_almost_finish) begin
            // Decrement the shot counter
            shot_cnt_d = shot_cnt_q - 1'b1;
        end

    end

    always_ff  @(posedge clk_i, negedge rst_ni) begin
        if(~rst_ni) begin
            shot_cnt_q  <= '0;
            shot_en_q   <= 1'b0;
        end
        else begin
            shot_cnt_q  <= shot_cnt_d;
            shot_en_q  <= shot_en_d;
        end
    end

    ///////////////////////////////// Main counter /////////////////////////////////

    logic [15:0] main_cnt_d, main_cnt_q;
    logic [15:0] sync_period;

    always_comb begin

        // Preserve the counter by default
        main_cnt_d = main_cnt_q;

        sync_per_finish = (main_cnt_q == sync_period);
        sync_per_almost_finish = (main_cnt_q == sync_period - 1);

        // If start capture is detected
        // Preload the counter
        if (start_capt_rising_edge) begin
            main_cnt_d = start_cap_time_i;
        end

        if (shot_en_q) begin
            if (sync_per_finish) begin
                main_cnt_d = '0;
            end else begin
                main_cnt_d = (main_cnt_q + 1'b1);
            end
        end
    end

    always_ff  @(posedge clk_i, negedge rst_ni) begin
        if(~rst_ni) begin
            main_cnt_q  <= start_cap_time_i;
        end
        else begin 
            main_cnt_q  <= main_cnt_d;
        end
    end

    ///////////////////////////////// AFE trigger Done signal /////////////////////////////////
    logic afe_trig_done_d, afe_trig_done_q;

    always_comb begin
        // By default the var preserves the state
        afe_trig_done_d = afe_trig_done_q;

        if (afe_tx_trig_o) begin
            afe_trig_done_d = 1;
        // Reset at the end of the period
        end else if (sync_per_almost_finish) begin
            afe_trig_done_d = 0;
        end
    end

    always_ff  @(posedge clk_i, negedge rst_ni) begin
        if(~rst_ni) begin
            afe_trig_done_q  <= 0;
        end
        else begin 
            afe_trig_done_q  <= afe_trig_done_d;
        end
    end

    assign afe_trig_done = afe_trig_done_q;

    ///////////////////////////////// TR EN counter (for LDO refreshing) /////////////////////////////////

    localparam REFRESH_PERIOD_MIN = 50000; // 200 Hz
    localparam RESFRESH_ON_TIME_MIN = 500; // 10 us

    logic [15:0] refresh_cnt_d, refresh_cnt_q;
    logic [15:0] refresh_period_d, refresh_period_q, refresh_half_period;
    logic refresh_on_time_d, refresh_on_time_q, refresh_half_on_time;

    logic tr_en_int;


    // Refresh parameters check up
    assign refresh_period_d = (tr_en_period_i > REFRESH_PERIOD_MIN) ? tr_en_period_i : REFRESH_PERIOD_MIN;
    assign refresh_on_time_d = (tr_en_on_time_i > RESFRESH_ON_TIME_MIN) ? tr_en_on_time_i : RESFRESH_ON_TIME_MIN;

    // Next state of the refresh counter
    always_comb begin
        refresh_cnt_d = refresh_cnt_q + 1'b1;

        // If we reached the period or if refresh is disabled
        if ((refresh_cnt_q == tr_en_period_i) || (!refresh_en_i)) begin
            refresh_cnt_d = '0;
        end
    end

    // TR_EN logic
    assign refresh_half_period = (refresh_period_q >> 1);
    assign refresh_half_on_time = (refresh_on_time_q >> 1);

    assign tr_en_int = (!refresh_en_i) ? 1'b0:
                       ((refresh_cnt_q >= refresh_half_period - refresh_half_on_time ) && 
                        (refresh_cnt_q <= refresh_half_period + refresh_half_on_time)) ? 1'b1 : 1'b0;  

    always_ff  @(posedge clk_i, negedge rst_ni) begin
        if(~rst_ni) begin
            refresh_cnt_q  <= '0;
        end
        else begin
            refresh_cnt_q  <= refresh_cnt_d;
        end
    end

    always_ff  @(posedge clk_i, negedge rst_ni) begin
        if(~rst_ni) begin
            refresh_on_time_q  <= RESFRESH_ON_TIME_MIN;
            refresh_period_q   <= REFRESH_PERIOD_MIN;
        end
        else if (refresh_cnt_q == '0) begin
            refresh_on_time_q  <= refresh_on_time_d;
            refresh_period_q   <= refresh_period_d;
        end
    end

    ///////////////////////////////// Sampling of the input parameters /////////////////////////////////

    logic [15:0] sync_period_d, sync_period_q;
    logic [15:0] sync_half_period, sync_period_d_half;
    logic [15:0] capt_delay_d, capt_delay_q;
    logic [7:0]  tx_wake_up_time_d, tx_wake_up_time_q;
    logic [7:0]  tx_sleep_time_d, tx_sleep_time_q;
    logic [15:0] afe_clk_on_time_d, afe_clk_on_time_q;
    logic [7:0]  afe_wake_up_time_d, afe_wake_up_time_q;
    logic [15:0] afe_data_acq_time_d, afe_data_acq_time_q;

    localparam SYNC_PERIOD_DEFAULT      = 16'h07CF;
    localparam CAPT_DELAY_DEFAULT       = 8'h00;
    localparam TX_WAKE_UP_TIME_DEFAULT  = 8'h64;
    localparam TX_SLEEP_TIME_DEFAULT    = 8'h20;
    localparam AFE_WAKE_UP_TIME_DEFAULT = 8'h1E; // ~3 uS 
    // The time afe clock should be active before wakeup (~50 uS)
    localparam AFE_CLK_ON_TIME_DEFAULT  = 16'h01F4;
    localparam DATA_ACQ_TIME_MINIMAL    = 8'h64; // ~10 uS

    assign sync_period_d       = (sync_period_i == '0) ? SYNC_PERIOD_DEFAULT : sync_period_i;
    assign sync_period_d_half  = sync_period_d >> 1;
    assign sync_half_period    = sync_period_q >> 1;

    assign capt_delay_d        = (capture_delay_i > sync_period_d_half) ? '0 : capture_delay_i;
    assign tx_wake_up_time_d   = (tx_wake_up_time_i < TX_WAKE_UP_TIME_DEFAULT) ? TX_WAKE_UP_TIME_DEFAULT : tx_wake_up_time_i;
    assign tx_sleep_time_d     = (tx_sleep_time_i < TX_SLEEP_TIME_DEFAULT) ? TX_SLEEP_TIME_DEFAULT : tx_sleep_time_i;

    // The time afe clock is active before sync should not exceed a half of sync period - wake up time
    assign afe_clk_on_time_d   = (afe_clk_on_time_i > (sync_period_d_half - afe_wake_up_time_d)) ? 
                                 (sync_period_d_half) : afe_clk_on_time_i;

    assign afe_wake_up_time_d  = (afe_wake_up_time_i < AFE_WAKE_UP_TIME_DEFAULT) ? 
                                 AFE_WAKE_UP_TIME_DEFAULT : afe_wake_up_time_i;

    assign afe_data_acq_time_d = (afe_data_acq_time_i < DATA_ACQ_TIME_MINIMAL) ? 
                                  DATA_ACQ_TIME_MINIMAL : (afe_data_acq_time_i > sync_period_d_half - afe_wake_up_time_d) ?
                                  DATA_ACQ_TIME_MINIMAL : afe_data_acq_time_i;


    always_ff  @(posedge clk_i, negedge rst_ni) begin
        if(~rst_ni) begin
            sync_period_q       <= SYNC_PERIOD_DEFAULT;
            capt_delay_q        <= CAPT_DELAY_DEFAULT;
            tx_wake_up_time_q   <= TX_WAKE_UP_TIME_DEFAULT;
            tx_sleep_time_q     <= TX_SLEEP_TIME_DEFAULT;
            afe_clk_on_time_q   <= AFE_CLK_ON_TIME_DEFAULT;
            afe_wake_up_time_q  <= AFE_WAKE_UP_TIME_DEFAULT;
            afe_data_acq_time_q <= DATA_ACQ_TIME_MINIMAL;

        end
        else if (start_capt_rising_edge) begin
            sync_period_q       <= sync_period_d;
            capt_delay_q        <= capt_delay_d;
            tx_wake_up_time_q   <= tx_wake_up_time_d;
            tx_sleep_time_q     <= tx_sleep_time_d;
            afe_clk_on_time_q   <= afe_clk_on_time_d;
            afe_wake_up_time_q  <= afe_wake_up_time_d;
            afe_data_acq_time_q <= afe_data_acq_time_d;
        end
    end

    assign sync_period = sync_period_q;

    ///////////////////////////////// AFE TX trig anf TX BF SYNC signals /////////////////////////////////

    logic trigger_d, trigger_q;

    assign trigger_d = (main_cnt_q == sync_half_period) ? 1'b1 : 1'b0;

    always_ff  @(posedge clk_i, negedge rst_ni) begin
        if(~rst_ni) begin
            trigger_q <= 1'b0;
        end
        else begin
            trigger_q <= trigger_d;
        end
    end

    // Enable the sync and tx signals only is shot_en signal is active
    // And if the FIFO read signal is not busy
    assign tx_bf_sync_o  = (shot_en_q & !fifo_rd_busy_i) ? trigger_q : 1'b0;
    assign afe_tx_trig_o = (shot_en_q & !fifo_rd_busy_i) ? trigger_q : 1'b0;

    ///////////////////////////////// Output buffers enable signals + AFE FAST PWDN + TR_EN signal for TX chip /////////////////////////////////

    logic tx_clk_buf_en_q, tx_clk_buf_en_d;
    logic tx_tr_en_q, tx_tr_en_d, tx_tr_en_shot;
    logic tx_sync_buf_en_q, tx_sync_buf_en_d;
    logic afe_clk_buf_en_q, afe_clk_buf_en_d;
    logic afe_trig_buf_en_q, afe_trig_buf_en_d;
    logic afe_fast_pdn_q, afe_fast_pdn_d;

    // TX clock signal is active tx_wake_up_time_q clock cycles before sync signal 
    // and tx_sleep_time_q clock cycles after sync
    assign tx_clk_buf_en_d  = ((main_cnt_q >= sync_half_period - tx_wake_up_time_q) && 
                               (main_cnt_q <= sync_half_period + tx_sleep_time_q)) ? 1'b1 : 1'b0;

    // TX SYNC signal power down scheme is identical to clock signal
    assign tx_sync_buf_en_d = tx_clk_buf_en_d;

    // AFE clock signal is active afe_clk_on_time_q clock cycles before sync signal 
    // and tx_sleep_time_q clock cycles after sync
    assign afe_clk_buf_en_d = ((main_cnt_q >= sync_half_period - afe_clk_on_time_q - afe_wake_up_time_q) && 
                               (main_cnt_q <= sync_half_period + capt_delay_q + afe_data_acq_time_q + afe_wake_up_time_q)) ? 1'b1 : 1'b0;

    // AFE TX TRIG signal power down scheme is identical to clock signal
    assign afe_trig_buf_en_d = afe_clk_buf_en_d;

    // AFE fast power down
    assign afe_fast_pdn_d = ((main_cnt_q >= sync_half_period - afe_wake_up_time_q) && 
                             (main_cnt_q <= sync_half_period + capt_delay_q + afe_data_acq_time_q)) ? 1'b0 : 1'b1;

    // TR_EN signal is active tx_wake_up_time_q before sync signal untill the assertion of sync_signal.
    assign tx_tr_en_d = ((main_cnt_q >= sync_half_period - tx_wake_up_time_q) &&
                         (main_cnt_q <= sync_half_period)) ? 1'b1 : 1'b0;

    always_ff  @(posedge clk_i, negedge rst_ni) begin
        if(~rst_ni) begin
            tx_clk_buf_en_q   <= 1'b0;
            tx_sync_buf_en_q  <= 1'b0;
            afe_clk_buf_en_q  <= 1'b0;
            afe_trig_buf_en_q <= 1'b0;
            afe_fast_pdn_q    <= 1'b0;
            tx_tr_en_q        <= 1'b0;
        end
        else begin
            tx_clk_buf_en_q   <= tx_clk_buf_en_d;
            tx_sync_buf_en_q  <= tx_sync_buf_en_d;
            afe_clk_buf_en_q  <= afe_clk_buf_en_d;
            afe_trig_buf_en_q <= afe_trig_buf_en_d;
            afe_fast_pdn_q    <= afe_fast_pdn_d;
            tx_tr_en_q        <= tx_tr_en_d;
        end
    end

    // Buffer enable signals are only active if shot_en signal is active
    assign tx_clk_buf_en_o      = (shot_en_q) ? tx_clk_buf_en_q : 1'b0;
    assign tx_sync_buf_en_o     = (shot_en_q) ? tx_sync_buf_en_q : 1'b0;
    assign afe_clk_buf_en_o     = (shot_en_q) ? afe_clk_buf_en_q : 1'b0;
    assign afe_tx_trig_buf_en_o = (shot_en_q) ? afe_trig_buf_en_q : 1'b0;
    assign afe_fast_pdn_o       = (shot_en_q) ? afe_fast_pdn_q : 1'b1;

    // TX tr_en is enabled when both the shot is enabled and
    // the FIFO read IP is not busy
    assign tx_tr_en_shot        = (shot_en_q & !fifo_rd_busy_i) ? tx_tr_en_q : 1'b0;

    // TR_EN signal should periodically be active to recharge power capacitors 
    // regardless of shot_en signal.
    assign tx_tr_en_o    = tx_tr_en_shot | tr_en_int;

    ///////////////////////////////// FIFO start capture, write_enable and reset /////////////////////////////////

    logic fifo_start_capture_d, fifo_start_capture_q;
    logic fifo_rst_d, fifo_rst_q;
    logic fifo_wr_en_d, fifo_wr_en_q;

    assign fifo_start_capture_d = ((main_cnt_q >= sync_half_period + capt_delay_q) && 
                                   (main_cnt_q <= sync_half_period + capt_delay_q + 4)) ? 1'b1 : 1'b0;

    assign fifo_rst_d   = (main_cnt_q == sync_half_period + capt_delay_q - 5) ? 1'b1 : 1'b0;

    assign fifo_wr_en_d = ((main_cnt_q >= sync_half_period + capt_delay_q) && 
                           (main_cnt_q <= sync_half_period + capt_delay_q + afe_data_acq_time_q)) ? 1'b1 : 1'b0;

    always_ff  @(posedge clk_i, negedge rst_ni) begin
        if(~rst_ni) begin
            fifo_start_capture_q <= 1'b0;
            fifo_rst_q           <= 1'b0;
            fifo_wr_en_q         <= 1'b0;
        end
        else begin
            fifo_start_capture_q <= fifo_start_capture_d;
            fifo_rst_q           <= fifo_rst_d;
            fifo_wr_en_q         <= fifo_wr_en_d;
        end
    end


    // FIFO control signals are only active if shot_en signal is active
    // and FIFO read IP is not busy
    assign fifo_start_capture_o = (shot_en_q & !fifo_rd_busy_i) ? fifo_start_capture_q : 1'b0;
    assign fifo_rst_o           = (shot_en_q & !fifo_rd_busy_i) ? fifo_rst_q : 1'b0;
    assign fifo_wr_en_o         = (shot_en_q & !fifo_rd_busy_i) ? fifo_wr_en_q : 1'b0;

endmodule