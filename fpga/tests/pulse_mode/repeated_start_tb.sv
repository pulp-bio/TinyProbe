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
//   Check that capture commands rearm and start subsequent acquisition
//   sequences.
// -----------------------------------------------------------------------------

`timescale 1ns/1ps
module tb;
reg clk=0;integer half=50;always begin #(half);clk=~clk;end
reg rst=0,command=0,oa=0,fast=0; wire start; reg transport_clk=0; always #8 transport_clk=~transport_clk; start_gen starter(.clk_i(transport_clk),.rst_ni(rst),.trig_in(command),.start_o(start),.busy_o());reg[7:0] shots=1;
wire tx,afe,capture;integer pulses=0;time rise_time,afe_time;integer expected_width;
waveform_generator_fsm dut(.clk_i(clk),.rst_ni(rst),.sync_period_i(16'd1000),.start_cap_time_i(16'd0),.capture_delay_i(16'd20),.start_capture_i(start),.n_shots_i(shots),.fifo_rd_busy_i(1'b0),.external_mode_i(1'b0),.external_trigger_i(1'b0),.external_sample_clk_i(clk),.capture_done_i(1'b0),.abort_external_i(1'b0),.oa_pulse_width_cycles_i(16'd0),.oa_mode_i(oa),.core_clk_fast_i(fast),.tx_wake_up_time_i(8'd100),.tx_sleep_time_i(8'd32),.refresh_en_i(1'b0),.tr_en_period_i(16'd50000),.tr_en_on_time_i(8'd100),.afe_wake_up_time_i(8'd30),.afe_clk_on_time_i(16'd500),.afe_data_acq_time_i(16'd50),.tx_bf_sync_o(tx),.afe_tx_trig_o(afe),.fifo_start_capture_o(capture));
always @(posedge tx)if(rst)begin rise_time=$time;pulses=pulses+1;end
always @(negedge tx)if(rst && pulses>0) if($time-rise_time!=expected_width)$fatal(1,"pulse width %0t expected %0d",$time-rise_time,expected_width);
always @(posedge afe)afe_time=$time;
always @(posedge capture)if(rst)if($time-afe_time!=20*2*half)$fatal(1,"capture timing changed");
integer sequences=0;
always @(posedge dut.accumulation_sequence_start_o) sequences=sequences+1;
task command_pulse;
begin @(negedge transport_clk);command=1;@(negedge transport_clk);command=0;end
endtask
integer k;
initial begin
 #1;rst=1;#1;rst=0;repeat(4)@(negedge clk);rst=1;
 shots=10;expected_width=100;
 for(k=1;k<=2;k=k+1)begin
  command_pulse();repeat(11000)@(negedge clk);
  if(pulses!=10*k || sequences!=k || start!==0)
    $fatal(1,"sequence %0d pulses=%0d starts=%0d start=%b",k,pulses,sequences,start);
 end
 $display("PASS: two consecutive ten-accumulation acquisitions without reset, separate starts and 20 captures");$finish;
end
initial begin #3000000;$fatal(1,"timeout");end
endmodule
