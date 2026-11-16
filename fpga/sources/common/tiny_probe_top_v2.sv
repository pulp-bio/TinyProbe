// Copyright 2021-2026 ETH Zurich
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
//   Sergei Vostrikov
//   LisaMaria Odermatt
//   Federico Villani
// -----------------------------------------------------------------------------
// Description:
//   Connect board clocks, AFE capture, waveform control, accumulation,
//   averaging and dual-SPI readout.
//
// Parameters:
//   N_LVDS_LANES - Number of AFE LVDS data lanes.
//   N_BITS_PER_FRAME - Bits per AFE lane frame.
//   CFG_REG_MEM_ADDR_SIZE - Configuration-register address width.
//   CFG_REG_WIDTH - Configuration-register data width.
//   READ_CNT_WIDTH - FIFO read-count width.
//
// Ports:
//   rst_ni - Active-low reset.
//   crystal_clk_i - External 16 MHz oscillator input.
//   spi_io0_io - Bidirectional MCU SPI data pad.
//   spi_io1_io - Bidirectional MCU SPI data pad.
//   spi_clk_i - SPI serial clock.
//   spi_ss_ni - Active-low SPI chip select.
//   mcu_int_o - Acquisition interrupt to the MCU.
//   trigger_o - Acquisition trigger output.
//   ext_trigger_i - External acquisition trigger input.
//   spi_ext_int_sel_i - Select internal FPGA or external peripheral SPI
//     routing.
//   spi_ext_cs_sel_i - Select the external AFE or transmitter chip select.
//   spi_clk_ext_o - Clock to the external configuration interfaces.
//   spi_mosi_ext_o - Serial configuration data to external peripherals.
//   spi_miso_ext_i - Serial response from external peripherals.
//   spi_cs_tx_no - Active-low transmitter configuration chip select.
//   spi_cs_afe_no - Active-low AFE configuration chip select.
//   afe_clk_o - AFE conversion clock.
//   afe_tx_trig_o - AFE transmit-trigger output.
//   afe_rst_o - AFE reset output.
//   afe_data_i - Positive AFE differential data inputs.
//   afe_data_ni - Negative AFE differential data inputs.
//   afe_frame_clk_i - Positive AFE frame-clock input.
//   afe_frame_clk_ni - Negative AFE frame-clock input.
//   afe_bit_clk_i - Positive AFE DDR bit-clock input.
//   afe_bit_clk_ni - Negative AFE DDR bit-clock input.
//   tgc_slope_o - AFE time-gain compensation step signal.
//   tgc_up_dn_o - AFE time-gain compensation direction.
//   afe_fast_pdn_o - AFE fast power-down control.
//   afe_glb_pdn_o - AFE global power-down control.
//   tx_bf_clk_o - Transmitter beamforming clock.
//   tx_bf_sync_o - Transmitter synchronization output.
//   tx_tr_en_o - Transmitter enable output.
//   tx_rst_o - Transmitter reset output.
// -----------------------------------------------------------------------------

  // Top module of Tinyprobe compact design

module tiny_probe_top#(
    parameter N_LVDS_LANES          = 16,
    parameter N_BITS_PER_FRAME      = 20,
    parameter CFG_REG_MEM_ADDR_SIZE = 4,
    parameter CFG_REG_WIDTH         = 32,
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

    localparam int ACCUM_SAMPLE_WIDTH = 10;
    localparam int ACCUM_SUM_WIDTH    = 13;
    localparam int ACCUM_FRAME_WIDTH  = 2 * ACCUM_SUM_WIDTH;

    ///////////////////////////////// Buffers instantiation /////////////////////////////////
    // Reset
    logic rst_n;

    assign rst_n = rst_ni;

    ///////////////////////////////// LVDS buffers /////////////////////////////////
    logic [N_LVDS_LANES - 1:0]  afe_bit_input;
    logic [N_LVDS_LANES - 1: 0]  afe_rx_en;
    // Declare a temporary loop variable
    genvar i;
    // Generate for loop to instantiate lvds receiver for each lane
    for (i = 0; i < N_LVDS_LANES; i = i + 1) begin
        // Preserve the physical data pads during fixed-result substitution.
        // Apply noprune to the primitive itself, not the shared clock wrapper.
        INBUF_DIFF input_diff_data (
            .PADP       (afe_data_i[i]),
            .PADN       (afe_data_ni[i]),
            .Y          (afe_bit_input[i])
        ) /* synthesis syn_noprune=1 */;
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
        .NGMUX2_SEL      (1'b0), // Fixed 10 MHz waveform/control clock.

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
    logic fifo_wr_en_wave_gen;
    logic tx_clk_buf_en_wave_gen, afe_clk_buf_en_wave_gen;
    logic afe_fast_pdn_wave_gen;
    logic tx_tr_en_wave_gen;

    logic afe_tx_trig;
    logic tx_bf_sync;

    logic [15:0] sync_period;
    logic [15:0] start_cap_time;
    logic [15:0] capture_delay;
    logic [7:0] n_shots;
    logic fifo_reader_busy;
    logic accumulation_sequence_start;
    logic accumulation_active;
    logic accumulation_first_shot;
    logic accumulation_final_shot;
    logic [7:0] accumulation_count_q;

    logic [7:0]  tx_wake_up_time;
    logic [7:0]  tx_sleep_time;

    // TX chip LDO reshreshing options
    logic refresh_en;
    logic [15:0] tr_en_period;
    logic [7:0]  tr_en_on_time;


    logic [7:0]  afe_wake_up_time;
    logic [15:0] afe_clk_on_time;
    logic [15:0] afe_data_acq_time; 

    // The FSM wrapper is a port-compatible replacement for waveform_generator.
    // It contains the original timing generator and applies the FSM-controlled
    // output-register layer before driving the board-level waveform signals.
    logic [ 2**CFG_REG_MEM_ADDR_SIZE - 1:0] [CFG_REG_WIDTH - 1:0] config_regs;
    logic accumulation_done_afe;
    logic [31:0] external_debug;
    logic [31:0] external_input_debug;
    waveform_generator_fsm waveform_gen (
        .clk_i                (core_clk),
        .rst_ni               (rst_n),

        // General signals
        .sync_period_i        (sync_period),
        .start_cap_time_i     (start_cap_time),
        .capture_delay_i      (capture_delay),
        .start_capture_i      (wave_gen_start_capt),
        .oa_mode_i            (config_regs[12][24]),
        .oa_pulse_width_cycles_i(config_regs[1][23:8]),
        .external_mode_i      (config_regs[12][25]),
        .external_trigger_i   (ext_trigger_i),
        .external_sample_clk_i(afe_clk),
        .capture_done_i       (accumulation_done_afe),
        .abort_external_i     (config_regs[10][4] && config_regs[10][5]),
        .external_debug_o     (external_debug),
        .external_input_debug_o(external_input_debug),
        .n_shots_i            (n_shots),
        .fifo_rd_busy_i       (fifo_reader_busy),
        .period_done_o        (),

        // RX FIFO control signals
        .fifo_start_capture_o (fifo_start_capt_wave_gen),
        .fifo_rst_o           (),
        .fifo_wr_en_o         (fifo_wr_en_wave_gen),
        .accumulation_sequence_start_o (accumulation_sequence_start),
        .accumulation_active_o         (accumulation_active),
        .accumulation_first_shot_o     (accumulation_first_shot),
        .accumulation_final_shot_o     (accumulation_final_shot),

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

    ////////////////////// Circular accumulation and result FIFOs //////////////////////
    logic [N_LVDS_LANES-1:0] afe_rx_en_reg;

    // FSM controls are synchronized into the AFE frame-clock domain. They are
    // stable for a complete shot; only rising edges are converted into pulses.
    logic accumulation_active_meta, accumulation_active_afe;
    logic accumulation_active_afe_q;
    logic accumulation_first_meta, accumulation_first_afe;
    logic accumulation_final_meta, accumulation_final_afe;
    logic fifo_start_meta, fifo_start_afe, fifo_start_afe_q;
    logic fifo_wr_en_meta, fifo_wr_en_afe;
    logic accumulation_sequence_start_afe;
    logic accumulation_shot_start_afe;
    logic normal_debug_enable_meta, normal_debug_enable_afe;
    logic pipeline_trace_enable_meta, pipeline_trace_enable_afe;

    always_ff @(posedge afe_frame_clock or negedge rst_n) begin
        if (!rst_n) begin
            accumulation_active_meta  <= 1'b0;
            accumulation_active_afe   <= 1'b0;
            accumulation_active_afe_q <= 1'b0;
            accumulation_first_meta   <= 1'b0;
            accumulation_first_afe    <= 1'b0;
            accumulation_final_meta   <= 1'b0;
            accumulation_final_afe    <= 1'b0;
            fifo_start_meta           <= 1'b0;
            fifo_start_afe            <= 1'b0;
            fifo_start_afe_q          <= 1'b0;
            fifo_wr_en_meta           <= 1'b0;
            fifo_wr_en_afe            <= 1'b0;
            normal_debug_enable_meta  <= 1'b0;
            normal_debug_enable_afe   <= 1'b0;
            pipeline_trace_enable_meta <= 1'b0;
            pipeline_trace_enable_afe  <= 1'b0;
        end else begin
            accumulation_active_meta  <= accumulation_active;
            accumulation_active_afe   <= accumulation_active_meta;
            accumulation_active_afe_q <= accumulation_active_afe;
            accumulation_first_meta   <= accumulation_first_shot;
            accumulation_first_afe    <= accumulation_first_meta;
            accumulation_final_meta   <= accumulation_final_shot;
            accumulation_final_afe    <= accumulation_final_meta;
            fifo_start_meta           <= fifo_start_capt_wave_gen;
            fifo_start_afe            <= fifo_start_meta;
            fifo_start_afe_q          <= fifo_start_afe;
            fifo_wr_en_meta           <= fifo_wr_en_wave_gen;
            fifo_wr_en_afe            <= fifo_wr_en_meta;
            normal_debug_enable_meta  <= config_regs[13][27];
            normal_debug_enable_afe   <= normal_debug_enable_meta;
            pipeline_trace_enable_meta <= config_regs[13][23];
            pipeline_trace_enable_afe  <= pipeline_trace_enable_meta;
        end
    end

    assign accumulation_sequence_start_afe =
        accumulation_active_afe && !accumulation_active_afe_q;
    assign accumulation_shot_start_afe =
        fifo_start_afe && !fifo_start_afe_q;

    logic [N_LVDS_LANES-1:0] deep_fifo_empty;
    logic [N_LVDS_LANES-1:0] deep_fifo_rd_en;
    logic [N_LVDS_LANES-1:0] deep_fifo_data_valid;
    logic [N_LVDS_LANES*ACCUM_FRAME_WIDTH-1:0] deep_fifo_rd_data;


    logic accumulation_accept_afe;

    // Stage-3A uses the real returned AFE frame clock and the production
    // accumulation FIFO, but supplies deterministic lane-0 data. It is
    // enabled only by register 13 bit 28, so normal acquisition is unchanged.
    logic stage3_enable;
    logic accumulation_test_enable;
    logic stage3_fifo_reset;
    logic stage3_start_capture;
    logic stage3_first_shot;
    logic [N_LVDS_LANES*N_BITS_PER_FRAME-1:0] stage3_fifo_data;
    logic [N_LVDS_LANES-1:0] stage3_fifo_wr_en;
    logic stage3_req_seen;
    logic stage3_done;
    logic [2:0] stage3_state;
    logic [7:0] stage3_frame_gray;
    logic stage3_enable_meta;
    logic stage3_enable_sync;
    logic stage3_start_seen_afe;
    logic [READ_CNT_WIDTH-1:0] stage3_wr_count_q;
    logic [READ_CNT_WIDTH-1:0] stage3_wr_count_gray;

    logic [N_LVDS_LANES*N_BITS_PER_FRAME-1:0] accumulation_data;
    logic [N_LVDS_LANES-1:0] accumulation_wr_en;
    logic accumulation_first_shot_mux;
    logic accumulation_start_capture_mux;
    logic [N_LVDS_LANES-1:0] accumulation_fifo_reset;

    tp_stage3_capture_smoke #(
        .N_LANES      (N_LVDS_LANES),
        .SAMPLE_WIDTH (N_BITS_PER_FRAME)
    ) stage3_capture_smoke (
        .frame_clk_i       (afe_frame_clock),
        .rst_ni            (rst_n),
        .enable_i          (stage3_enable | accumulation_test_enable),
        .wr_done_i         (accumulation_done_afe),
        .sample_accepted_i (accumulation_accept_afe),
        .fifo_reset_o      (stage3_fifo_reset),
        .start_capture_o   (stage3_start_capture),
        .first_shot_o      (stage3_first_shot),
        .fifo_data_o       (stage3_fifo_data),
        .fifo_wr_en_o      (stage3_fifo_wr_en),
        .req_seen_o        (stage3_req_seen),
        .done_o            (stage3_done),
        .state_o           (stage3_state),
        .frame_gray_o      (stage3_frame_gray),
        .enable_meta_o     (stage3_enable_meta),
        .enable_sync_o     (stage3_enable_sync)
    );

    always_ff @(posedge afe_frame_clock or negedge rst_n) begin
        if (!rst_n) begin
            stage3_start_seen_afe <= 1'b0;
            stage3_wr_count_q     <= '0;
        end else if (!stage3_enable_sync || stage3_fifo_reset) begin
            stage3_start_seen_afe <= 1'b0;
            stage3_wr_count_q     <= '0;
        end else begin
            if (stage3_start_capture)
                stage3_start_seen_afe <= 1'b1;
            if (stage3_fifo_wr_en[0] && !accumulation_done_afe)
                stage3_wr_count_q <= stage3_wr_count_q + 1'b1;
        end
    end

    assign stage3_wr_count_gray =
        stage3_wr_count_q ^ (stage3_wr_count_q >> 1);

    assign accumulation_data = stage3_enable_sync ?
        stage3_fifo_data : data_fifo_write;
    assign accumulation_wr_en = stage3_enable_sync ?
        stage3_fifo_wr_en :
        (afe_rx_en_reg & {N_LVDS_LANES{fifo_wr_en_afe}});
    assign accumulation_first_shot_mux = stage3_enable_sync ?
        stage3_first_shot : accumulation_first_afe;
    assign accumulation_start_capture_mux = stage3_enable_sync ?
        stage3_start_capture : fifo_start_afe;
    assign accumulation_fifo_reset =
        {N_LVDS_LANES{accumulation_sequence_start_afe | stage3_fifo_reset}};

    logic [N_LVDS_LANES-1:0] average_fifo_full;
    logic [N_LVDS_LANES-1:0] average_fifo_empty;
    logic [N_LVDS_LANES-1:0] average_fifo_write;
    logic [N_LVDS_LANES-1:0] average_fifo_read_req;
    logic [N_LVDS_LANES*N_BITS_PER_FRAME-1:0] result_fifo_average_data;
    logic [N_LVDS_LANES*N_BITS_PER_FRAME-1:0] averaged_frame_data;
    logic result_processing_rst_n;
    logic [2:0] result_reset_count_q;
    logic averaging_frame_done_afe;

    // CoreFIFO contains reset synchronizers for both clock domains. Stretch
    // the sequence reset in the AFE domain so it cannot be missed as the old
    // single-core-clock pulse could be.
    always_ff @(posedge afe_frame_clock or negedge rst_n) begin
        if (!rst_n)
            result_reset_count_q <= 3'd7;
        else if (accumulation_sequence_start_afe || stage3_fifo_reset)
            result_reset_count_q <= 3'd7;
        else if (result_reset_count_q != 0)
            result_reset_count_q <= result_reset_count_q - 1'b1;
    end

    assign result_processing_rst_n =
        rst_n && (result_reset_count_q == 0);

    // The waveform generator supplies exactly the same controls used by
    // rx_fifo_v3. accumulation owns the Libero FIFO bank and only changes the
    // later-shot operation from a direct write to read/add/write.
    accumulation #(
        .N_FIFOS          (N_LVDS_LANES),
        .SAMPLE_WIDTH     (ACCUM_SAMPLE_WIDTH),
        .SUM_WIDTH        (ACCUM_SUM_WIDTH),
        .WRITE_CNT_WIDTH  (READ_CNT_WIDTH),
        .RAW_QUEUE_DEPTH  (4)
    ) accumulation_fifo (
        .rst_state_ni     (rst_n),
        .rst_fifos_i      (accumulation_fifo_reset),
        // Preserve the original rx_fifo_v3 contract: capture exactly the
        // number of frames that the MCU later requests from the SPI reader.
        .write_cnt_i      (fifos_read_cnt),
        .wr_fifo_done_o   (accumulation_done_afe),
        .wr_accept_o      (accumulation_accept_afe),
        .data_i           (accumulation_data),
        .first_shot_i     (accumulation_first_shot_mux),
        .start_capture_i  (accumulation_start_capture_mux),
        .wr_clk_i         (afe_frame_clock),
        .wr_en_i          (accumulation_wr_en),
        .full_o           (),
        .rd_clk_i         (afe_frame_clock),
        .rd_en_i          (deep_fifo_rd_en),
        .data_o           (deep_fifo_rd_data),
        .data_valid_o     (deep_fifo_data_valid),
        .empty_o          (deep_fifo_empty)
    );

    // Arm only after the final shot has cleared the previous shot's sticky
    // done level. This prevents the previous completion from starting a drain
    // during the few AFE clocks needed to detect the final start pulse.
    logic final_shot_seen_afe;
    logic final_done_armed_afe;

    always_ff @(posedge afe_frame_clock or negedge rst_n) begin
        if (!rst_n) begin
            final_shot_seen_afe <= 1'b0;
            final_done_armed_afe <= 1'b0;
        end else if (accumulation_sequence_start_afe) begin
            final_shot_seen_afe <= 1'b0;
            final_done_armed_afe <= 1'b0;
        end else begin
            if (accumulation_shot_start_afe && accumulation_final_afe) begin
                final_shot_seen_afe <= 1'b1;
                final_done_armed_afe <= 1'b0;
            end
            if (final_shot_seen_afe && !accumulation_done_afe)
                final_done_armed_afe <= 1'b1;
        end
    end

    genvar accum_lane;
    generate
        for (accum_lane = 0; accum_lane < N_LVDS_LANES;
             accum_lane = accum_lane + 1) begin : gen_accumulation_fifos
            // Store the complete averaged frame before allowing the MCU to
            // start SPI readout. The former two-entry CDC buffer forced the
            // reader and shared divider to run concurrently and starved SPI.
            async_sym_fifo #(
                .FIFO_DATA_WIDTH (N_BITS_PER_FRAME)
            ) average_buffer (
                .rst_i     (!result_processing_rst_n),
                .wr_clk_i  (afe_frame_clock),
                .wr_en_i   (average_fifo_write[accum_lane]),
                .data_i    (averaged_frame_data[
                     accum_lane*N_BITS_PER_FRAME +: N_BITS_PER_FRAME]),
                .full_o    (average_fifo_full[accum_lane]),
                // The stream reader generates rd_en and consumes empty/data
                // on afe_clk. Keep the FIFO read port in that same domain so
                // no unsynchronised request or response crosses core_clk.
                .rd_clk_i  (afe_clk),
                .rd_en_i   (average_fifo_read_req[accum_lane]),
                .data_o    (result_fifo_average_data[
                     accum_lane*N_BITS_PER_FRAME +: N_BITS_PER_FRAME]),
                .data_valid_o (),
                .empty_o   (average_fifo_empty[accum_lane])
            );
        end
    endgenerate

    logic [2:0] average_debug_state;
    logic [3:0] average_debug_lane;
    logic [READ_CNT_WIDTH-1:0] average_debug_lane_count;
    logic average_debug_enable;
    logic average_debug_divider_busy;
    logic average_debug_divider_start;
    logic average_debug_divider_done;
    logic [7:0] average_debug_event_sticky_afe_q;
    logic [31:0] average_engine_debug_status;
    logic [31:0] average_fifo_debug_status;
    logic [N_BITS_PER_FRAME-1:0] pipeline_trace_shot1_q [0:15];
    logic [N_BITS_PER_FRAME-1:0] pipeline_trace_shot2_q [0:15];
    logic [ACCUM_FRAME_WIDTH-1:0] pipeline_trace_sum_q [0:15];
    logic [N_BITS_PER_FRAME-1:0] pipeline_trace_average_q [0:15];
    logic [4:0] pipeline_trace_shot1_count_q;
    logic [4:0] pipeline_trace_shot2_count_q;
    logic [4:0] pipeline_trace_sum_count_q;
    logic [4:0] pipeline_trace_average_count_q;
    logic [31:0] pipeline_trace_data;

    result_average_engine #(
        .N_LANES      (N_LVDS_LANES),
        .SAMPLE_WIDTH (ACCUM_SAMPLE_WIDTH),
        .SUM_WIDTH    (ACCUM_SUM_WIDTH),
        .COUNT_WIDTH  (8)
    ) average_engine (
        .clk_i                (afe_frame_clock),
        // Abort any unfinished drain/divide operation when a new acquisition
        // clears the associated accumulation and result buffers.
        .rst_ni               (result_processing_rst_n),
        .enable_i             (stage3_enable_sync ? stage3_done :
                               (final_done_armed_afe && accumulation_done_afe)),
        .accumulation_count_i (stage3_enable_sync ? 8'd2 : accumulation_count_q),
        .samples_per_lane_i   (fifos_read_cnt),
        .lanes_enable_i       (stage3_enable_sync ? {{(N_LVDS_LANES-1){1'b0}}, 1'b1} :
                               result_lane_enable_q),
        .frame_done_o         (averaging_frame_done_afe),
        .sum_empty_i          (deep_fifo_empty),
        .sum_data_valid_i     (deep_fifo_data_valid),
        .sum_data_i           (deep_fifo_rd_data),
        .sum_read_o           (deep_fifo_rd_en),
        .average_full_i       (average_fifo_full),
        .average_write_o      (average_fifo_write),
        .average_data_o       (averaged_frame_data),
        .debug_state_o        (average_debug_state),
        .debug_lane_o         (average_debug_lane),
        .debug_lane_write_count_o(average_debug_lane_count),
        .debug_enable_o       (average_debug_enable),
        .debug_divider_busy_o (average_debug_divider_busy),
        .debug_divider_start_o(average_debug_divider_start),
        .debug_divider_done_o (average_debug_divider_done)
    );


    always_ff @(posedge afe_frame_clock or negedge rst_n) begin
        if (!rst_n) begin
            pipeline_trace_shot1_count_q <= '0;
            pipeline_trace_shot2_count_q <= '0;
            pipeline_trace_sum_count_q <= '0;
            pipeline_trace_average_count_q <= '0;
        end else if (accumulation_sequence_start_afe) begin
            pipeline_trace_shot1_count_q <= '0;
            pipeline_trace_shot2_count_q <= '0;
            pipeline_trace_sum_count_q <= '0;
            pipeline_trace_average_count_q <= '0;
        end else if (pipeline_trace_enable_afe) begin
            if (accumulation_accept_afe && accumulation_wr_en[0]) begin
                if (accumulation_first_shot_mux &&
                    pipeline_trace_shot1_count_q < 5'd16) begin
                    pipeline_trace_shot1_q[pipeline_trace_shot1_count_q[3:0]] <=
                        accumulation_data[0 +: N_BITS_PER_FRAME];
                    pipeline_trace_shot1_count_q <= pipeline_trace_shot1_count_q + 1'b1;
                end else if (!accumulation_first_shot_mux &&
                             pipeline_trace_shot2_count_q < 5'd16) begin
                    pipeline_trace_shot2_q[pipeline_trace_shot2_count_q[3:0]] <=
                        accumulation_data[0 +: N_BITS_PER_FRAME];
                    pipeline_trace_shot2_count_q <= pipeline_trace_shot2_count_q + 1'b1;
                end
            end
            if (average_debug_enable && deep_fifo_data_valid[0] &&
                pipeline_trace_sum_count_q < 5'd16) begin
                pipeline_trace_sum_q[pipeline_trace_sum_count_q[3:0]] <=
                    deep_fifo_rd_data[0 +: ACCUM_FRAME_WIDTH];
                pipeline_trace_sum_count_q <= pipeline_trace_sum_count_q + 1'b1;
            end
            if (average_fifo_write[0] &&
                pipeline_trace_average_count_q < 5'd16) begin
                pipeline_trace_average_q[pipeline_trace_average_count_q[3:0]] <=
                    averaged_frame_data[0 +: N_BITS_PER_FRAME];
                pipeline_trace_average_count_q <= pipeline_trace_average_count_q + 1'b1;
            end
        end
    end

    always_comb begin
        pipeline_trace_data = '0;
        unique case (config_regs[13][5:4])
            2'd0: pipeline_trace_data[N_BITS_PER_FRAME-1:0] =
                      pipeline_trace_shot1_q[config_regs[13][3:0]];
            2'd1: pipeline_trace_data[N_BITS_PER_FRAME-1:0] =
                      pipeline_trace_shot2_q[config_regs[13][3:0]];
            2'd2: pipeline_trace_data[ACCUM_FRAME_WIDTH-1:0] =
                      pipeline_trace_sum_q[config_regs[13][3:0]];
            2'd3: pipeline_trace_data[N_BITS_PER_FRAME-1:0] =
                      pipeline_trace_average_q[config_regs[13][3:0]];
            default: pipeline_trace_data = 32'hffff_ffff;
        endcase
    end

    // Latch the divisor and enabled lanes for the complete sequence. The
    // sticky result-ready indication crosses into the core-clock domain only
    // after every requested sample for every enabled lane has been averaged.
    logic results_ready;
    logic [N_LVDS_LANES-1:0] result_lane_enable_q;
    logic averaging_done_meta;
    logic averaging_done_core;
    logic accumulation_test_enable_q;
    logic accumulation_test_armed_q;
    logic normal_result_pending_q;
    logic normal_result_armed_q;
    logic [6:0] normal_debug_sticky_afe_q;
    logic [7:0] normal_debug_status;

    // Register 13 bit 27 enables normal-acquisition observability. Short
    // frame-domain events are made sticky before crossing to the transport
    // clock, so a slow register read cannot miss them. Bit layout at status F:
    // [7] sequence start, [6] FIFO start, [5] FIFO write enable,
    // [4] accumulation done, [3] final shot seen, [2] final done armed,
    // [1] averaging done, [0] results ready.
    always_ff @(posedge afe_frame_clock or negedge rst_n) begin
        if (!rst_n) begin
            normal_debug_sticky_afe_q <= '0;
            average_debug_event_sticky_afe_q <= '0;
        end else if (!normal_debug_enable_afe) begin
            normal_debug_sticky_afe_q <= '0;
            average_debug_event_sticky_afe_q <= '0;
        end else begin
            normal_debug_sticky_afe_q[6] <= normal_debug_sticky_afe_q[6] |
                                             accumulation_sequence_start_afe;
            normal_debug_sticky_afe_q[5] <= normal_debug_sticky_afe_q[5] |
                                             accumulation_shot_start_afe;
            normal_debug_sticky_afe_q[4] <= normal_debug_sticky_afe_q[4] |
                                             fifo_wr_en_afe;
            normal_debug_sticky_afe_q[3] <= normal_debug_sticky_afe_q[3] |
                                             accumulation_done_afe;
            normal_debug_sticky_afe_q[2] <= normal_debug_sticky_afe_q[2] |
                                             final_shot_seen_afe;
            normal_debug_sticky_afe_q[1] <= normal_debug_sticky_afe_q[1] |
                                             final_done_armed_afe;
            normal_debug_sticky_afe_q[0] <= normal_debug_sticky_afe_q[0] |
                                             averaging_frame_done_afe;
            average_debug_event_sticky_afe_q[0] <=
                average_debug_event_sticky_afe_q[0] | average_debug_enable;
            average_debug_event_sticky_afe_q[1] <=
                average_debug_event_sticky_afe_q[1] | (|deep_fifo_rd_en);
            average_debug_event_sticky_afe_q[2] <=
                average_debug_event_sticky_afe_q[2] | (|deep_fifo_data_valid);
            average_debug_event_sticky_afe_q[3] <=
                average_debug_event_sticky_afe_q[3] | average_debug_divider_start;
            average_debug_event_sticky_afe_q[4] <=
                average_debug_event_sticky_afe_q[4] | average_debug_divider_done;
            average_debug_event_sticky_afe_q[5] <=
                average_debug_event_sticky_afe_q[5] | (|average_fifo_write);
            average_debug_event_sticky_afe_q[6] <=
                average_debug_event_sticky_afe_q[6] | (|average_fifo_full);
            average_debug_event_sticky_afe_q[7] <=
                average_debug_event_sticky_afe_q[7] | averaging_frame_done_afe;
        end
    end

    assign normal_debug_status = {normal_debug_sticky_afe_q, results_ready};
    assign average_engine_debug_status = {
        8'hd5, average_debug_enable, average_debug_divider_busy,
        average_debug_state, average_debug_lane,
        // Page 1 bits 14:12 expose the core-domain completion handshake.
        normal_result_pending_q, normal_result_armed_q, averaging_done_core,
        average_debug_lane_count
    };
    assign average_fifo_debug_status = {average_fifo_full, deep_fifo_empty};

    always_ff @(posedge core_clk or negedge rst_n) begin
        if (!rst_n) begin
            accumulation_count_q     <= '0;
            result_lane_enable_q     <= '0;
            results_ready            <= 1'b0;
            averaging_done_meta       <= 1'b0;
            averaging_done_core       <= 1'b0;
            accumulation_test_enable_q <= 1'b0;
            accumulation_test_armed_q <= 1'b0;
            normal_result_pending_q <= 1'b0;
            normal_result_armed_q <= 1'b0;
        end else begin
            averaging_done_meta <= averaging_frame_done_afe;
            averaging_done_core <= averaging_done_meta;
            accumulation_test_enable_q <= accumulation_test_enable;
            if (accumulation_test_enable) begin
                normal_result_pending_q <= 1'b0;
                normal_result_armed_q <= 1'b0;
            end
            if (accumulation_test_enable && !accumulation_test_enable_q) begin
                accumulation_count_q <= 8'd2;
                result_lane_enable_q <= {{(N_LVDS_LANES-1){1'b0}}, 1'b1};
                // Do not accept a stale frame_done level from the preceding
                // acquisition. Arm only after this diagnostic's reset has
                // propagated a low level through the synchronizer.
                accumulation_test_armed_q <= 1'b0;
                results_ready <= 1'b0;
            end else if (accumulation_test_enable) begin
                if (!averaging_done_core) begin
                    accumulation_test_armed_q <= 1'b1;
                    results_ready <= 1'b0;
                end else if (accumulation_test_armed_q) begin
                    results_ready <= 1'b1;
                end
            end else if (accumulation_sequence_start) begin
                accumulation_count_q <= n_shots;
                result_lane_enable_q <= afe_rx_en_reg;
                accumulation_test_armed_q <= 1'b0;
                results_ready        <= 1'b0;
                normal_result_pending_q <= 1'b1;
                normal_result_armed_q <= 1'b0;
            end else if (normal_result_pending_q) begin
                // The previous completion may remain high until the AFE-domain
                // reset has crossed back through the two-flop synchronizer.
                // Require a low level after start before accepting completion.
                if (!averaging_done_core)
                    normal_result_armed_q <= 1'b1;
                else if (normal_result_armed_q) begin
                    results_ready <= 1'b1;
                    normal_result_pending_q <= 1'b0;
                    normal_result_armed_q <= 1'b0;
                end
            end
        end
    end

    ///////////////////////////////// SPI slave /////////////////////////////////


    logic spi_ss_int_n, spi_io0_int, spi_io1_int;
    logic spi_io0_qspi, spi_io1_qspi, spi_clk_int;
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
        .fifos_empty_i       (average_fifo_empty),
        .fifos_data_i        (result_fifo_average_data),
        .fifos_read_req_o    (average_fifo_read_req),
        .fifos_en_i          (fifos_en),
        .read_cnt_i          (fifos_read_cnt),
        .stage3_frame_gray_i (stage3_frame_gray),
        .stage3_enable_meta_i(stage3_enable_meta),
        .stage3_enable_sync_i(stage3_enable_sync),
        .stage3_wr_count_gray_i(stage3_wr_count_gray),
        .stage3_req_seen_i   (stage3_req_seen),
        .stage3_start_asserted_i(stage3_start_seen_afe),
        .stage3_wr_done_i    (stage3_done),
        .stage3_lane0_nonempty_i(!deep_fifo_empty[0]),
        .stage3_state_i      (stage3_state),
        .normal_debug_i      (normal_debug_status),
        .average_engine_debug_i(average_engine_debug_status),
        .average_fifo_debug_i(config_regs[12][25] ?
            (config_regs[13][22] ? external_input_debug : external_debug) : average_fifo_debug_status),
        .average_event_debug_i(average_debug_event_sticky_afe_q),
        .pipeline_trace_data_i(pipeline_trace_data),
        .fifo_reader_busy_o  (fifo_reader_busy),
        .capture_start_o     (start_capture_spi),
        .stage3_enable_o     (stage3_enable),
        .accumulation_test_enable_o(accumulation_test_enable),
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
    
    // The signals enabling the LVDS receivers are declared with the
    // accumulation datapath above because they also gate accumulator lanes.
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

    // Keep GL0 / tx_bf_clk continuously enabled during QSPI bring-up.  Driving
    // the FCCC clock-gate enable from the 60 MHz register domain creates a
    // timing-critical clock-control crossing into the 100 MHz TX clock.
    assign pll_tx_bf_clk_en      = 1'b1;
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
    // OA (register 12 bit 24) holds the physical pin low, including refresh
    // pulses and the manual override. Configure the mode before acquisition.
    // In US, Bit 6 selects Bit 7 or the waveform generator as before.
    assign tx_tr_en_o        = (config_regs[12][24] || config_regs[12][25]) ? 1'b0 :
                              (config_regs[AFE_TX_RST_REG][6] ? config_regs[AFE_TX_RST_REG][7] : tx_tr_en_wave_gen);

    // REG 11
    assign start_cap_time    = config_regs[WAVEFORM_GEN_REG_4][31:16];
    // Old-MCU compatibility mode: register 11 remains accessible, but its
    // low byte cannot change acquisition behavior in this bitstream.
    // to get the new number of accumulations from the user
    // if zero no division by zero is allowed, so we will use 1 instead
    // US and OA use the same accumulation count; pulse mode changes width only.
    assign n_shots =
        ((config_regs[WAVEFORM_GEN_REG_4][7:0] == 8'd0) ? 8'd1 : config_regs[WAVEFORM_GEN_REG_4][7:0]);

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
    localparam MCU_INT_RESULTS_READY = 2'b00,
               MCU_INT_AFE_TX_TRIG  = 2'b01,
               MCU_INT_TX_BF_SYNC   = 2'b10,
               MCU_INT_EXT_TRIG     = 2'b11;

    always_comb begin

        if (pll_mcu_ctrl_active) begin
            mcu_int_o = pll_lock; 
        end else if (config_regs[12][25] && config_regs[13][27] && config_regs[13][21]) begin
            // External diagnostic only: validate the physical MCU interrupt path.
            mcu_int_o = config_regs[13][20];
        end else begin
            unique case (mcu_int_mux_ctrl)

                MCU_INT_RESULTS_READY: begin
                    mcu_int_o = results_ready;
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

                default: mcu_int_o = results_ready;
            endcase 
        end
    end

    // Output trigger multiplexing
    localparam TRIG_OUT_TX_BF_SYNC = 2'b00,
               TRIG_OUT_AFE_TX_TRIG = 2'b01,
               TRIG_OUT_PLL_LOCK = 2'b10,
               TRIG_OUT_RESULTS_READY = 2'b11;

    always_comb begin
        unique case (trig_out_mux_ctrl)
            TRIG_OUT_TX_BF_SYNC: trigger_o = tx_bf_sync;
            TRIG_OUT_AFE_TX_TRIG: trigger_o = afe_tx_trig;
            TRIG_OUT_PLL_LOCK: trigger_o = pll_lock;
            TRIG_OUT_RESULTS_READY: trigger_o = results_ready;
            default: trigger_o = tx_bf_sync;
        endcase
    end

    // Multiplexing the Input trigger signal (Either in SW or via external signal)
    assign wave_gen_start_capt = config_regs[12][25] ? start_capture_spi :
        (ext_trigger_en ? ext_trigger_i : start_capture_spi);

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
