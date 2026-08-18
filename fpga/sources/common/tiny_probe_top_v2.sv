// Author: Soumyo Bhattacharjee
  // Top module of Tinyprobe compact design

module tiny_probe_top#(
    parameter N_LVDS_LANES          = 16,
    parameter N_BITS_PER_FRAME      = 20,
    parameter CFG_REG_MEM_ADDR_SIZE = 4,
    parameter CFG_REG_WIDTH         = 32,
    parameter SPI_WORD_WIDTH        = 8,
    parameter READ_CNT_WIDTH        = 12
)(

    // External reset
    input  logic rst_ni,

    // Input of clock oscillator (16 MHz)
    input logic crystal_clk_i,

    // SPI Input Master Interface (FPGA is a Slave) //
    inout  wire  spi_io0_io,
    inout  wire  spi_io1_io,
    input  logic spi_clk_i,
    input  logic spi_ss_ni,

    // Output interrupt for MCU
    output logic mcu_int_o,

    // Trigger out
    output logic trigger_o,
    // Trigger in
    input logic  ext_trigger_i,

    // Control inputs for SPI mux/demux
    input  logic spi_ext_int_sel_i,
    input  logic spi_ext_cs_sel_i,

    // SPI External Slave Interface (for AFE and TX)
    output logic spi_clk_ext_o,
    output logic spi_mosi_ext_o,
    input  logic spi_miso_ext_i,
    output logic spi_cs_tx_no,
    output logic spi_cs_afe_no,

    // AFE 5832 LP signals //
    // Clock signal for AFE
    output logic afe_clk_o,
    // TX trigger signal for AFE
    output logic afe_tx_trig_o,
    // Reset signal for AFE
    output logic afe_rst_o,

    // LVDS signals
    // Data lines
    input logic [N_LVDS_LANES - 1:0] afe_data_i,
    input logic [N_LVDS_LANES - 1:0] afe_data_ni,
    // Frame clock
    input logic afe_frame_clk_i,
    input logic afe_frame_clk_ni,
    // Bit clock
    input logic afe_bit_clk_i,
    input logic afe_bit_clk_ni,

    // TGC signals
    output logic tgc_slope_o,
    output logic tgc_up_dn_o,

    // AFE power down fast
    output logic afe_fast_pdn_o,
    // AFE global power down
    output logic afe_glb_pdn_o,

    // TX chip signals //
    output logic tx_bf_clk_o,
    output logic tx_bf_sync_o,
    output logic tx_tr_en_o,
    // Reset signal for TX chip
    output logic tx_rst_o
);

    ///////////////////////////////// Buffers instantiation /////////////////////////////////
    // Reset
    logic rst_n;
    logic rst;
    // INBUF rst_ibuf (
    //     .PAD   (rst_ni),
    //     .Y   (rst_n)
    // );

    assign rst_n = rst_ni;
    assign rst = ~rst_n;

    ///////////////////////////////// LVDS buffers /////////////////////////////////
    logic [N_LVDS_LANES - 1:0]  afe_bit_input;
    logic [N_LVDS_LANES - 1: 0]  afe_rx_en;
    // Declare a temporary loop variable
    genvar i;
    // Generate for loop to instantiate lvds receiver for each lane
    for (i = 0; i < N_LVDS_LANES; i = i + 1) begin
        ibuf_diff input_diff_data (
            .pad_i      (afe_data_i[i]),
            .pad_ni     (afe_data_ni[i]), 
            // .en_i       (afe_rx_en[i]),
            .d_o        (afe_bit_input[i])
        )/* synthesis syn_keep=1 */;
    end

    logic afe_frame_clock, afe_bit_clock;
    logic afe_frame_clock_temp, afe_bit_clock_temp;

    // Clock signals first enter the fabric through regular IOs
    ibuf_diff input_diff_frame_clock (
        .pad_i      (afe_frame_clk_i),
        .pad_ni     (afe_frame_clk_ni), 
        .d_o        (afe_frame_clock_temp)
    );
    ibuf_diff input_diff_bit_clock (
        .pad_i      (afe_bit_clk_i),
        .pad_ni     (afe_bit_clk_ni), 
        .d_o        (afe_bit_clock_temp)
    );
    // Then the signals are connected to GB clock network
    logic frame_clk_buf_en;
    logic bit_clk_buf_en;

    GCLKINT frame_clock_GBUF (
        .A     (afe_frame_clock_temp),
        .EN    (frame_clk_buf_en),
        .Y     (afe_frame_clock)
    );
    GCLKINT bit_clock_GBUF (
        .A     (afe_bit_clock_temp),
        .EN    (bit_clk_buf_en),
        .Y     (afe_bit_clock)
    );

    ///////////////////////////////// SPI in/out buffers /////////////////////////////////
    logic spi_io0_i, spi_io1_i, spi_io0_o, spi_io1_o;
    logic [1:0] spi_pad_oe;
    logic spi_clk, spi_ss_n;
    logic spi_clk_temp;

    INBUF spi_clk_ibuf (
        .PAD   (spi_clk_i),
        .Y     (spi_clk_temp)
    );

    CLKINT spi_clk_GBUF (
        .A     (spi_clk_temp),
        .Y     (spi_clk)
    );

    BIBUF spi_io0_iobuf (
        .PAD   (spi_io0_io),
        .Y     (spi_io0_i),
        .D     (spi_io0_o),
        .E     (spi_pad_oe[0])
    );
    BIBUF spi_io1_iobuf (
        .PAD   (spi_io1_io),
        .Y     (spi_io1_i),
        .D     (spi_io1_o),
        .E     (spi_pad_oe[1])
    );

    INBUF spi_ss_ibuf (
        .PAD   (spi_ss_ni),
        .Y     (spi_ss_n)
    );

    // PLL Clock generator
    logic tx_bf_clk;
    logic core_clk;
    logic afe_clk;

    ///////////////////////////////// Output clock buffers /////////////////////////////////
    // AFE clock //
    logic afe_clk_buf_en;
    logic tx_clk_buf_en;

    TRIBUFF afe_clk_obuf (
        .D     (afe_clk),
        .E     (afe_clk_buf_en),
        .PAD   (afe_clk_o)
    );

    // TX chip clock //
    TRIBUFF tx_chip_clk_obuf (
        .D     (tx_bf_clk),
        .E     (tx_clk_buf_en),
        .PAD   (tx_bf_clk_o)
    );


    ///////////////////////////////// PLL clock generator /////////////////////////////////

    // Oscillator signal
    logic osc_xtal;
    // HOLD_N signal for NGMUXes
    logic pll_ngmux_hold_n;
    // MUX cintrols for multiple clocks
    logic pll_tx_clk_mux_ctrl;
    logic pll_afe_clk_mux_ctrl;
    logic pll_core_clk_mux_ctrl;
    // Enable signals
    logic pll_tx_bf_clk_en;
    logic pll_afe_clk_en;

    assign pll_ngmux_hold_n = 1;

    // Lock signal
    logic pll_lock;

    // Async Reset and powerdown controls
    logic pll_arst_n, pll_powerdown_n;

    // Driving signal and multiplexer
    logic pll_arst_pwd_mux_ctrl;
    logic pll_arst_pwd_n;

    // Special control signal
    // signalling that PLL signals (arst_n or powerdown_n)
    // are now controlled from MCU (via spi_ss_n line)
    logic pll_mcu_ctrl_active;

    // EXT_OSC
    EXT_OSC ext_osc(
        // Inputs
        .XTL (crystal_clk_i),
        // Outputs
        .XTLOSC_CCC (osc_xtal)
    );


    Clock_gen pll_clk_gen (
        // Inputs
        .XTLOSC          (osc_xtal),
        .GL0_EN          (pll_tx_bf_clk_en),
        .GL1_EN          (pll_afe_clk_en),

        .NGMUX0_ARST_N   (rst_ni),
        .NGMUX0_HOLD_N   (pll_ngmux_hold_n),
        .NGMUX0_SEL      (pll_tx_clk_mux_ctrl),

        .NGMUX1_ARST_N   (rst_ni),
        .NGMUX1_HOLD_N   (pll_ngmux_hold_n),
        .NGMUX1_SEL      (pll_afe_clk_mux_ctrl),

        .NGMUX2_ARST_N   (rst_ni),
        .NGMUX2_HOLD_N   (pll_ngmux_hold_n),
        .NGMUX2_SEL      (pll_core_clk_mux_ctrl),

        .PLL_ARST_N      (pll_arst_n),
        .PLL_POWERDOWN_N (pll_powerdown_n),

        // Outputs
        .GL0        (tx_bf_clk),
        .GL1        (afe_clk),
        .GL2        (core_clk),
        .LOCK       (pll_lock)
    );


    // A multiplexer to control either arst_n or pwd_n signal
    // with pll_arst_pwd_n
    always_comb begin
        // No reset or powerdown 
        // by default
        pll_arst_n = 1;
        pll_powerdown_n = 1;

        // If control signal is active
        // Control arst_n. Otherwise pwd_n
        if (pll_arst_pwd_mux_ctrl) begin
            pll_arst_n = pll_arst_pwd_n;
        end else begin
            pll_powerdown_n = pll_arst_pwd_n;
        end
    end

    ///////////////////////////////// Waveform Generator for TX chip and AFE /////////////////////////////////
    logic fifo_start_capt_wave_gen;
    logic wave_gen_start_capt;
    logic fifo_rst_wave_gen, fifo_wr_en_wave_gen;
    logic tx_clk_buf_en_wave_gen, afe_clk_buf_en_wave_gen;
    logic afe_fast_pdn_wave_gen, afe_glb_pdn_wave_gen;
    logic tx_tr_en_wave_gen;

    logic afe_tx_trig;
    logic tx_bf_sync;

    logic [15:0] sync_period;
    logic [15:0] start_cap_time;
    logic [15:0] capture_delay;
    logic [15:0] n_shots;
    logic fifo_reader_busy;

    logic [7:0]  tx_wake_up_time;
    logic [7:0]  tx_sleep_time;

    // TX chip LDO reshreshing options
    logic refresh_en;
    logic [15:0] tr_en_period;
    logic [7:0]  tr_en_on_time;


    logic [7:0]  afe_wake_up_time;
    logic [15:0] afe_clk_on_time;
    logic [15:0] afe_data_acq_time; 

    waveform_generator waveform_gen (
        .clk_i                (core_clk),

        .rst_ni               (rst_n),

        // General signals
        .sync_period_i        (sync_period),
        .start_cap_time_i     (start_cap_time),
        .capture_delay_i      (capture_delay),
        .start_capture_i      (wave_gen_start_capt),
        .n_shots_i            (n_shots),
        .fifo_rd_busy_i       (fifo_reader_busy),

        // RX FIFO control signals
        .fifo_start_capture_o (fifo_start_capt_wave_gen),
        .fifo_rst_o           (fifo_rst_wave_gen),
        .fifo_wr_en_o         (fifo_wr_en_wave_gen),

        // TX chip signals
        .tx_wake_up_time_i    (tx_wake_up_time),
        .tx_sleep_time_i      (tx_sleep_time),
        .tx_bf_sync_o         (tx_bf_sync),
        .tx_clk_buf_en_o      (tx_clk_buf_en_wave_gen),
        .tx_sync_buf_en_o     (),
        .tx_tr_en_o           (tx_tr_en_wave_gen),

        // TX chip LDO refreshing options
        .refresh_en_i         (refresh_en),
        .tr_en_period_i       (tr_en_period),
        .tr_en_on_time_i      (tr_en_on_time),

        // AFE chip signals
        .afe_wake_up_time_i   (afe_wake_up_time),
        .afe_clk_on_time_i    (afe_clk_on_time),
        .afe_data_acq_time_i  (afe_data_acq_time),
        .afe_tx_trig_o        (afe_tx_trig),
        .afe_tx_trig_buf_en_o (),
        .afe_clk_buf_en_o     (afe_clk_buf_en_wave_gen),
        .afe_fast_pdn_o       (afe_fast_pdn_wave_gen)
    );

    assign afe_tx_trig_o = afe_tx_trig;
    assign tx_bf_sync_o = tx_bf_sync;

    ///////////////////////////////// LVDS receiver /////////////////////////////////
    // Output data
    logic [N_LVDS_LANES * N_BITS_PER_FRAME - 1:0] data_fifo_write;

    afe_rx #(
        .N_LANES          (N_LVDS_LANES),
        .BITS_PER_FRAME   (N_BITS_PER_FRAME)
    ) afe_rx (
        .ser_data_i       (afe_bit_input),
        .bit_clk_i        (afe_bit_clock),
        .frame_clk_i      (afe_frame_clock),

        .en_i             (afe_rx_en),
        .rst_ni           (rst_n),

        .data_o           (data_fifo_write)
    );

    ///////////////////////////////// Time Gain Compensation signal generator /////////////////////////////////
    logic [31:0] tgc_clk_div;
    logic [31:0] tgc_capture_time;
    logic [31:0] tgc_delay_finish;
    logic [31:0] tgc_delay_start;

    ti_afe_tgc #(
        .CNT_WIDTH            (32)
    ) ti_afe_tgc (
        .clk_afe_i            (afe_clk),
        .clk_i                (core_clk),
        .clk_div_i            (tgc_clk_div),
        .rst_ni               (rst_n),
        .start_i              (fifo_start_capt_wave_gen),
        .delay_start_i        (tgc_delay_start),
        .capt_time_i          (tgc_capture_time),
        .delay_finish_i       (tgc_delay_finish),
        .tgc_slope_o          (tgc_slope_o),
        .tgc_up_dn_o          (tgc_up_dn_o)
    );

    ///////////////////////////////// RX FIFO /////////////////////////////////
    logic [N_LVDS_LANES - 1: 0] fifos_empty;
    logic [N_LVDS_LANES - 1: 0] fifos_read_req;
    logic [N_LVDS_LANES * N_BITS_PER_FRAME - 1: 0] fifos_data_read;

    // Temporary variable
    logic wr_fifo_done;

    // Reset signal coming from the SPI slave IP
    logic [N_LVDS_LANES - 1: 0] fifos_rst_spi;

    // Declare a temporary loop variable
    genvar i;
    // Generate for loop to assign the same SW reset sinal to all the FIFOs
    for (i = 0; i < (N_LVDS_LANES); i = i + 1) begin
         assign fifos_rst_spi[i] = fifo_rst_wave_gen;
    end

    // FIFO write enable 
    logic [N_LVDS_LANES - 1: 0] fifos_wr_en;
    // Stage-3A uses the real frame-clock write port of rx_fifo_v3 but
    // replaces the waveform/AFE producer with a deterministic local source.
    // It is selected exclusively by config-register 13 bit 28.
    logic stage3_smoke_enable;
    logic stage3_fifo_reset, stage3_start_capture;
    logic stage3_req_seen, stage3_done;
    logic [2:0] stage3_state;
    logic [7:0] stage3_frame_gray;
    logic stage3_enable_meta, stage3_enable_sync;
    logic [READ_CNT_WIDTH - 1:0] stage3_wr_count_dbg, stage3_wr_count_gray;
    logic stage3_start_asserted_dbg;
    logic [N_LVDS_LANES * N_BITS_PER_FRAME - 1:0] stage3_fifo_data;
    logic [N_LVDS_LANES - 1:0] stage3_fifo_wr_en;
    logic [N_LVDS_LANES - 1:0] fifo_reset_i;
    logic fifo_state_rst_ni, fifo_start_capture_i;
    // Stream-path smoke-test source.  When config register 13 bit 31 is set,
    // lane 0 receives a deterministic 20-bit sample on the *real* AFE frame
    // clock/write-enable path.  This deliberately bypasses only afe_rx; the
    // rx_fifo_v3, multi_fifo_reader, QSPI_STREAM_FIFO and 0x6B path remain
    // exactly the production path.  All other lanes are held inactive.
    logic stream_test_enable;
    logic [N_LVDS_LANES * N_BITS_PER_FRAME - 1:0] fifo_data_i;
    logic [N_LVDS_LANES - 1:0]                    fifo_wr_en_i;

    always_comb begin
        fifo_data_i  = data_fifo_write;
        fifo_wr_en_i = fifos_wr_en;
        if (stream_test_enable) begin
            fifo_data_i  = '0;
            fifo_data_i[0 +: N_BITS_PER_FRAME] = 20'hA5_3C9;
            fifo_wr_en_i = '0;
            fifo_wr_en_i[0] = fifos_wr_en[0];
        end
        if (stage3_smoke_enable) begin
            fifo_data_i  = stage3_fifo_data;
            fifo_wr_en_i = stage3_fifo_wr_en;
        end
    end

    always_comb begin
        fifo_reset_i        = fifos_rst_spi;
        fifo_state_rst_ni   = !fifo_rst_wave_gen;
        fifo_start_capture_i = fifo_start_capt_wave_gen;
        if (stage3_smoke_enable) begin
            fifo_reset_i         = {N_LVDS_LANES{stage3_fifo_reset}};
            fifo_state_rst_ni    = !stage3_fifo_reset;
            fifo_start_capture_i = stage3_start_capture;
        end
    end

    rx_fifo_v3  #(
        .N_FIFOS          (N_LVDS_LANES),
        .DATA_WIDTH       (N_BITS_PER_FRAME),
        .WRITE_CNT_WIDTH  (READ_CNT_WIDTH)
    ) rf_data_fifo (
        .rst_state_ni     (fifo_state_rst_ni), // Resets the rx_fifo_v3 capture state between shots
        .rst_fifos_i      (fifo_reset_i), // Resets all internal FIFO write/read pointers

        .write_cnt_i      (fifos_read_cnt), // Write the same number of samples which we will read
        .wr_fifo_done_o   (wr_fifo_done),

        .wr_clk_i         (afe_frame_clock),
        .wr_en_i          (fifo_wr_en_i),
        .data_i           (fifo_data_i),
        .full_o           (),

        // Keep this read port in the QSPI transport's 60 MHz domain.
        .rd_clk_i         (afe_clk),
        .rd_en_i          (fifos_read_req),
        .data_o           (fifos_data_read),
        .empty_o          (fifos_empty),

        .start_capture_i  (fifo_start_capture_i),
        .start_asserted_dbg_o(stage3_start_asserted_dbg),
        .wr_count_dbg_o   (stage3_wr_count_dbg)
    );

    ///////////////////////////////// SPI slave /////////////////////////////////
    logic [ 2**CFG_REG_MEM_ADDR_SIZE - 1:0] [CFG_REG_WIDTH - 1:0] config_regs;
    // Runtime-only stream smoke-test controls default low after reset.  The
    // Stage-3 mode is supplied as an explicit scalar by the QSPI transport,
    // rather than being reconstructed from this packed register-array port.
    assign stream_test_enable = config_regs[13][31];

    tp_stage3_capture_smoke #(
        .N_LANES      (N_LVDS_LANES),
        .SAMPLE_WIDTH (N_BITS_PER_FRAME)
    ) i_stage3_capture_smoke (
        .frame_clk_i      (afe_frame_clock),
        .rst_ni           (rst_n),
        .enable_i         (stage3_smoke_enable),
        .wr_done_i        (wr_fifo_done),
        .fifo_reset_o     (stage3_fifo_reset),
        .start_capture_o  (stage3_start_capture),
        .fifo_data_o      (stage3_fifo_data),
        .fifo_wr_en_o     (stage3_fifo_wr_en),
        .req_seen_o       (stage3_req_seen),
        .done_o           (stage3_done),
        .state_o          (stage3_state),
        .frame_gray_o     (stage3_frame_gray),
        .enable_meta_o    (stage3_enable_meta),
        .enable_sync_o    (stage3_enable_sync)
    );

    assign stage3_wr_count_gray = stage3_wr_count_dbg ^ (stage3_wr_count_dbg >> 1);

    logic spi_ss_int_n, spi_io0_int, spi_io1_int, spi_io0_qspi, spi_io1_qspi, spi_clk_int;
    logic [1:0] spi_pad_oe_qspi;
    logic [N_LVDS_LANES - 1:0] fifos_en;
    // Indicates how much input samples to acquire from every activ FIFO
    logic [READ_CNT_WIDTH - 1:0] fifos_read_cnt;

    logic start_capture_spi;

    tinyprobe_qspi_transport #(
        .N_FIFOS             (N_LVDS_LANES),
        .IN_DATA_WIDTH       (N_BITS_PER_FRAME),
        .READ_CNT_WIDTH      (READ_CNT_WIDTH)
    ) qspi_transport (
        .spi_sclk_i          (spi_clk_int),
        .spi_cs_ni           (spi_ss_int_n),
        .spi_io0_i           (spi_io0_int),
        .spi_io1_i           (spi_io1_int),
        .spi_io0_o           (spi_io0_qspi),
        .spi_io1_o           (spi_io1_qspi),
        .spi_pad_oe_o        (spi_pad_oe_qspi),
        // GL1 / afe_clk is forced to 60 MHz below during QSPI bring-up.
        .core_clk_i          (afe_clk),
        .rst_ni              (rst_n),
        .fifos_empty_i       (fifos_empty),
        .fifos_data_i        (fifos_data_read),
        .fifos_read_req_o    (fifos_read_req),
        .fifos_en_i          (fifos_en),
        .read_cnt_i          (fifos_read_cnt),
        .stage3_frame_gray_i (stage3_frame_gray),
        .stage3_enable_meta_i(stage3_enable_meta),
        .stage3_enable_sync_i(stage3_enable_sync),
        .stage3_wr_count_gray_i(stage3_wr_count_gray),
        .stage3_req_seen_i   (stage3_req_seen),
        .stage3_start_asserted_i(stage3_start_asserted_dbg),
        .stage3_wr_done_i    (stage3_done),
        .stage3_lane0_nonempty_i(!fifos_empty[0]),
        .stage3_state_i      (stage3_state),
        .fifo_reader_busy_o  (fifo_reader_busy),
        .capture_start_o     (start_capture_spi),
        .stage3_enable_o     (stage3_smoke_enable),
        .config_regs_o       (config_regs)
    );

    ///////////////////////////////// Configuration registers (connections) /////////////////////////////////

    localparam PLL_CONFIG_REG     = 1;
    localparam LVDS_CH_EN_REG     = 2;
    localparam WAVEFORM_GEN_REG_1 = 3;
    localparam WAVEFORM_GEN_REG_2 = 4;
    localparam WAVEFORM_GEN_REG_3 = 5;
    localparam TGC_REG_1          = 6;
    localparam TGC_REG_2          = 7;
    localparam TGC_REG_3          = 8;
    localparam TGC_REG_4          = 9;
    localparam AFE_TX_RST_REG     = 10;
    localparam WAVEFORM_GEN_REG_4 = 11;
    localparam WAVEFORM_GEN_REG_5 = 12;
    localparam EXT_INT_TRIG_REG   = 13;

    // The signals enables LVDS lanes at receive
    logic [N_LVDS_LANES - 1:0] afe_rx_en_reg;
    // Priority signal to enable clock for TX and AFE (required for initialization)
    logic afe_clk_buf_en_mux_ctrl, tx_clk_buf_en_mux_ctrl;

    // Control signal to enable external triggering or software
    logic ext_trigger_en;
    // (De) Multiplexers control for mcu interrupt/ouput triggers
    logic [1:0] mcu_int_mux_ctrl;
    logic [1:0] trig_out_mux_ctrl;

    // REG 1
    // PLL NGMUX controls for different clock domains
    assign pll_tx_clk_mux_ctrl   = config_regs[PLL_CONFIG_REG][0];
    // GL1 is the existing 20/60 MHz PLL output.  Select its 60 MHz input so
    // the QSPI transport/register-bank test domain has a deterministic clock.
    assign pll_afe_clk_mux_ctrl  = 1'b1;
    assign pll_core_clk_mux_ctrl = config_regs[PLL_CONFIG_REG][2];

    assign pll_tx_bf_clk_en      = config_regs[PLL_CONFIG_REG][3] ? tx_clk_buf_en_wave_gen : config_regs[PLL_CONFIG_REG][4];
    // GL1 is now the QSPI transport core clock as well as the AFE clock;
    // keep its global buffer enabled independently of reset register values.
    assign pll_afe_clk_en        = 1'b1;

    assign pll_arst_pwd_mux_ctrl = config_regs[PLL_CONFIG_REG][7];

    // REG 2
    // Enable signals for LVDS receivers (16 lower bits for 16 lanes)
    assign afe_rx_en_reg  = config_regs[LVDS_CH_EN_REG][N_LVDS_LANES - 1:0];
    // Enable signals for clock buffers
    assign afe_clk_buf_en_mux_ctrl = config_regs[LVDS_CH_EN_REG][31];
    assign tx_clk_buf_en_mux_ctrl  = config_regs[LVDS_CH_EN_REG][30];
    // FIFO read count
    assign fifos_read_cnt = config_regs[LVDS_CH_EN_REG][READ_CNT_WIDTH + 15:16];

    // REG 3
    assign sync_period     = config_regs[WAVEFORM_GEN_REG_1][31:16];
    assign tx_wake_up_time = config_regs[WAVEFORM_GEN_REG_1][15:8];
    assign tx_sleep_time   = config_regs[WAVEFORM_GEN_REG_1][7:0];

    // REG 4
    assign afe_wake_up_time  = config_regs[WAVEFORM_GEN_REG_2][15:8];
    assign afe_clk_on_time   = config_regs[WAVEFORM_GEN_REG_2][7:0];

    // REG 5
    assign afe_data_acq_time = config_regs[WAVEFORM_GEN_REG_3][15:0];
    assign capture_delay     = config_regs[WAVEFORM_GEN_REG_3][31:16];
    // REG 6
    assign tgc_clk_div       = config_regs[TGC_REG_1][31:0];

    // REG 7
    assign tgc_capture_time  = config_regs[TGC_REG_2][31:0];

    // REG 8
    assign tgc_delay_finish  = config_regs[TGC_REG_3][31:0];

    // REG 9
    assign tgc_delay_start   = config_regs[TGC_REG_4][31:0];

    // REG 10
    assign afe_rst_o         = config_regs[AFE_TX_RST_REG][0];
    assign tx_rst_o          = config_regs[AFE_TX_RST_REG][1];

    // AFE fast power down mux control
    // If Bit 2 is 1 then Bit 3 controls fast power down. Otherwise - fast_pdn output of the waveform generator.
    assign afe_fast_pdn_o    = config_regs[AFE_TX_RST_REG][2] ? config_regs[AFE_TX_RST_REG][3] : afe_fast_pdn_wave_gen;
    // AFE global power down mux control
    // If Bit 4 is 1 then Bit 5 controls global power down. Otherwise - fast_pdn output of the waveform generator.
    assign afe_glb_pdn_o     = config_regs[AFE_TX_RST_REG][4] ? config_regs[AFE_TX_RST_REG][5] : afe_fast_pdn_wave_gen;
    // TX TR_EN mux control
    // If Bit 6 is 1 then Bit 7 controls TR_EN. Otherwise - tx_tr_en_wave_gen output of the waveform generator.
    assign tx_tr_en_o        = config_regs[AFE_TX_RST_REG][6] ? config_regs[AFE_TX_RST_REG][7] : tx_tr_en_wave_gen;

    // REG 11
    assign start_cap_time    = config_regs[WAVEFORM_GEN_REG_4][31:16];
    assign n_shots           = config_regs[WAVEFORM_GEN_REG_4][15:0];

    // REG 12
    assign tr_en_period      = config_regs[WAVEFORM_GEN_REG_5][15:0];
    assign tr_en_on_time     = config_regs[WAVEFORM_GEN_REG_5][23:16];
    assign refresh_en        = config_regs[WAVEFORM_GEN_REG_5][31];

    // REG 13
    assign ext_trigger_en    = config_regs[EXT_INT_TRIG_REG][0];
    assign mcu_int_mux_ctrl  = config_regs[EXT_INT_TRIG_REG][2:1];
    assign trig_out_mux_ctrl = config_regs[EXT_INT_TRIG_REG][4:3];

    ///////////////////////////////// OUTPUT trigger / MCU interrupt / INPUT trigger multiplexing  /////////////////////////////////

    // MCU interrupt Multiplexer
    localparam MCU_INT_FIFO_WR_DONE = 2'b00,
               MCU_INT_AFE_TX_TRIG  = 2'b01,
               MCU_INT_TX_BF_SYNC   = 2'b10,
               MCU_INT_EXT_TRIG     = 2'b11;

    always_comb begin

        if (pll_mcu_ctrl_active) begin
            mcu_int_o = pll_lock; 
        end else begin
            unique case (mcu_int_mux_ctrl)

                MCU_INT_FIFO_WR_DONE: begin
                    mcu_int_o = wr_fifo_done;
                end

                MCU_INT_AFE_TX_TRIG: begin
                    mcu_int_o = afe_tx_trig;
                end

                MCU_INT_TX_BF_SYNC: begin
                    mcu_int_o = tx_bf_sync;
                end

                MCU_INT_EXT_TRIG: begin
                    mcu_int_o = ext_trigger_i;
                end

                default: mcu_int_o = wr_fifo_done;
            endcase 
        end
    end

    // Output trigger multiplexing

    localparam TRIG_OUT_TX_BF_SYNC   = 2'b00,
               TRIG_OUT_AFE_TX_TRIG  = 2'b01,
               TRIG_OUT_PLL_LOCK     = 2'b10,
               TRIG_OUT_FIFO_WR_DONE = 2'b11;

    always_comb begin
        unique case (trig_out_mux_ctrl)

            TRIG_OUT_TX_BF_SYNC: begin
                trigger_o = tx_bf_sync;
            end

            TRIG_OUT_AFE_TX_TRIG: begin
                trigger_o = afe_tx_trig;
            end

            TRIG_OUT_PLL_LOCK: begin
                trigger_o = pll_lock;
            end

            TRIG_OUT_FIFO_WR_DONE: begin
                trigger_o = wr_fifo_done;
            end

            default: trigger_o = tx_bf_sync;
        endcase
    end

    // Multiplexing the Input trigger signal (Either in SW or via external signal)
    assign wave_gen_start_capt = ext_trigger_en ? ext_trigger_i : start_capture_spi;

    ///////////////////////////////// Buffers enable and other control signals /////////////////////////////////

    // AFE and TX clock buffers are directly controlled by waveform generator 
    // if corresponding register signals are not asserted. Otherwise they are always on.
    assign afe_clk_buf_en = afe_clk_buf_en_mux_ctrl ? 1'b1 : afe_clk_buf_en_wave_gen;
    assign tx_clk_buf_en  = tx_clk_buf_en_mux_ctrl ? 1'b1 : tx_clk_buf_en_wave_gen;

    // Afe frame and bit clock buffers are directly controlled by waveform generator
    // if register signal above is not asserted. Otherwise it is always on.
    assign frame_clk_buf_en = afe_clk_buf_en;
    assign bit_clk_buf_en   = afe_clk_buf_en;

    genvar l;
    // Generate for loop for connecting the control signals 
    for (l = 0; l < N_LVDS_LANES; l = l + 1) begin
        // Enable individual FIFO write if the register value is assigned and waveform generator
        // write enable signal is active
        assign fifos_wr_en[l] = afe_rx_en_reg[l] && fifo_wr_en_wave_gen;
        // If AFE clock is enabled then enable LVDS lanes specified by the register are enabled
        assign afe_rx_en[l] = (afe_clk_buf_en) ? afe_rx_en_reg[l] : '0;
    end

    // A control signal for multi fifo reader
    assign fifos_en = afe_rx_en_reg;

    ///////////////////////////////// SPI master input signals (De)multiplexing /////////////////////////////////


    // Main Demultiplexer (spi_demux) uses only 3 states with 2 control signals (spi_ext_int_sel_i, spi_ext_cs_sel_i)

    // The block below dynamically connects the spi_ss_n either to the
    // spi_demux or to PLL control input signal.
    logic spi_ss_demux_n;

    // If external SPI slaves are not selected (spi_ext_int_sel_i = 0)
    // and spi_ext_cs_sel_i = 0
    // MCU can control PLL inputs via SPI slave select line
    assign pll_mcu_ctrl_active = ~spi_ext_int_sel_i & ~spi_ext_cs_sel_i;

    always_comb begin
        // Default connection
        spi_ss_demux_n = spi_ss_n;
        pll_arst_pwd_n = 1;

        if (pll_mcu_ctrl_active) begin
            // SPI Slave select now drives PLL signals 
            pll_arst_pwd_n = spi_ss_n;
            spi_ss_demux_n = 1;
        end        
    end

    // Main Demultiplexer

    spi_demux spi_demux_inst (
    // SPI Master input signals
        .spi_clk_i          (spi_clk),
        .spi_io0_i          (spi_io0_i),
        .spi_io1_i          (spi_io1_i),
        .spi_cs_i           (spi_ss_demux_n),

    // Control inputs for mux/demux
        .spi_ext_int_sel_i  (spi_ext_int_sel_i),
        .spi_ext_cs_sel_i   (spi_ext_cs_sel_i),

    // SPI internal signals
    // (For internal FPGA SPI module)
        .spi_clk_int_o      (spi_clk_int),
        .spi_io0_int_o      (spi_io0_int),
        .spi_io1_int_o      (spi_io1_int),
        .spi_io0_int_i      (spi_io0_qspi),
        .spi_io1_int_i      (spi_io1_qspi),
        .spi_pad_oe_int_i   (spi_pad_oe_qspi),
        .spi_cs_int_no      (spi_ss_int_n),
        .spi_io0_o          (spi_io0_o),
        .spi_io1_o          (spi_io1_o),
        .spi_pad_oe_o       (spi_pad_oe),

    // SPI external signals
        .spi_clk_ext_o      (spi_clk_ext_o),
        .spi_mosi_ext_o     (spi_mosi_ext_o),
        .spi_miso_ext_i     (spi_miso_ext_i),
        .spi_cs_tx_no       (spi_cs_tx_no),
        .spi_cs_afe_no      (spi_cs_afe_no)
    );

endmodule
