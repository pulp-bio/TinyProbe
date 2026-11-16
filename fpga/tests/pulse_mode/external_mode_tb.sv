// Copyright 2026 ETH Zurich
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
//   LisaMaria Odermatt
//   Federico Villani
// -----------------------------------------------------------------------------
// Description:
//   Check external-trigger acquisition timing and completion behavior.
// -----------------------------------------------------------------------------

`timescale 1ns/1ps
module external_mode_tb;
reg clk=0, fastclk=0, rst=0, arm=0, ext=0, done=1, abort_rx=0;
always #50 clk=~clk;
always #8 fastclk=~fastclk;
wire capture, wr, tx, tr, afe, pdn, active, first_shot, final_shot;
wire [31:0] debug;
integer captures=0;
waveform_generator_fsm dut(
 .clk_i(clk),.rst_ni(rst),
 .sync_period_i(16'd1000),.start_cap_time_i(16'd0),.capture_delay_i(16'd10),
 .start_capture_i(arm),.n_shots_i(8'd3),.fifo_rd_busy_i(1'b0),
 .oa_pulse_width_cycles_i(16'd0),.oa_mode_i(1'b1),.core_clk_fast_i(1'b0),.external_mode_i(1'b1),
 .external_trigger_i(ext),.external_sample_clk_i(fastclk),.capture_done_i(done),
 .abort_external_i(abort_rx),.external_debug_o(debug),
 .tx_wake_up_time_i(8'd100),.tx_sleep_time_i(8'd32),.refresh_en_i(1'b1),
 .tr_en_period_i(16'd500),.tr_en_on_time_i(8'd100),
 .afe_wake_up_time_i(8'd30),.afe_clk_on_time_i(16'd500),.afe_data_acq_time_i(16'd40),
 .fifo_start_capture_o(capture),.fifo_wr_en_o(wr),.tx_bf_sync_o(tx),
 .tx_tr_en_o(tr),.afe_tx_trig_o(afe),.afe_fast_pdn_o(pdn),
 .accumulation_active_o(active),.accumulation_first_shot_o(first_shot),
 .accumulation_final_shot_o(final_shot));
time trigger_time;
always @(posedge afe) trigger_time=$time;
always @(posedge capture) begin
 captures=captures+1;
 if($time-trigger_time!=1000) $fatal(1,"capture delay not measured from trigger");
 if(first_shot !== (captures==1) || final_shot !== (captures==3)) $fatal(1,"shot flags");
 // Delayed acknowledgement clears stale done, then finishes this capture.
 #250 done=0;
 #1750 done=1;
end
always @(posedge clk) if(rst) begin
 if(tx || tr) $fatal(1,"external mode emitted TX");
 if(active && pdn) $fatal(1,"receiver powered down while armed");
end
task pulse; begin #13 ext=1; #50 ext=0; end endtask
task start; begin @(negedge clk);arm=1;repeat(3)@(negedge clk);arm=0;end endtask
initial begin
 #1 rst=1; #1 rst=0; #110 rst=1;
 pulse(); repeat(20)@(negedge clk);
 if(captures!=0) $fatal(1,"unarmed capture");
 start(); pulse(); // warmup edge ignored
 wait(debug[4]); repeat(2000)@(negedge clk);
 if(captures!=0) $fatal(1,"free running capture");
 pulse(); wait(capture); pulse(); // busy edge ignored
 wait(debug[4]); pulse(); wait(capture); wait(debug[4]); pulse();
 wait(debug[3:0]==8); repeat(100)@(negedge clk); pulse();
 repeat(20)@(negedge clk);
 if(captures!=3 || debug[31:16]<2) $fatal(1,"counts captures=%0d debug=%h",captures,debug);
 abort_rx=1; repeat(5)@(negedge clk);
 if(active || wr || !pdn) $fatal(1,"abort failed");
 abort_rx=0; captures=0; start(); wait(debug[4]);
 pulse(); wait(capture); wait(debug[4]); pulse(); wait(capture);
 wait(debug[4]); pulse(); wait(debug[3:0]==8);
 if(captures!=3) $fatal(1,"rearm failed");
 $display("PASS: external arm, short edges, no autonomous captures, N=3, busy/warmup rejection, stale done, timing, TX suppression, abort");
 $finish;
end
initial begin #1000000;$fatal(1,"timeout debug=%h captures=%0d",debug,captures);end
endmodule
