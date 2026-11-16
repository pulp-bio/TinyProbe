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
//   Check ultrasound and optoacoustic waveform-control modes.
// -----------------------------------------------------------------------------

`timescale 1ns/1ps
module tb;
reg clk=0;integer half=50;always begin #(half);clk=~clk;end
reg rst=0,start=0,oa=0,fast=0;reg[7:0] shots=1;
reg [15:0] width=0;
wire tx,afe,capture;integer pulses=0;time rise_time,afe_time;integer expected_width;
waveform_generator_fsm dut(.clk_i(clk),.rst_ni(rst),.sync_period_i(16'd1000),.start_cap_time_i(16'd0),.capture_delay_i(16'd20),.start_capture_i(start),.n_shots_i(shots),.fifo_rd_busy_i(1'b0),.external_mode_i(1'b0),.external_trigger_i(1'b0),.external_sample_clk_i(clk),.capture_done_i(1'b0),.abort_external_i(1'b0),.oa_pulse_width_cycles_i(width),.oa_mode_i(oa),.core_clk_fast_i(fast),.tx_wake_up_time_i(8'd100),.tx_sleep_time_i(8'd32),.refresh_en_i(1'b0),.tr_en_period_i(16'd50000),.tr_en_on_time_i(8'd100),.afe_wake_up_time_i(8'd30),.afe_clk_on_time_i(16'd500),.afe_data_acq_time_i(16'd50),.tx_bf_sync_o(tx),.afe_tx_trig_o(afe),.fifo_start_capture_o(capture));
always @(posedge tx)if(rst)begin rise_time=$time;pulses=pulses+1;end
always @(negedge tx)if(rst && pulses>0) if($time-rise_time!=expected_width)$fatal(1,"pulse width %0t expected %0d",$time-rise_time,expected_width);
always @(posedge afe)afe_time=$time;
always @(posedge capture)if(rst)if($time-afe_time!=20*2*half)$fatal(1,"capture timing changed");
task run(input reg mode,input reg speed,input integer n,input integer cycles);
begin
 @(negedge clk);rst=0;start=0;oa=mode;fast=speed;half=speed?25:50;shots=n;width=cycles;pulses=0;expected_width=mode?(cycles==0?2:cycles)*2*half:2*half;
 repeat(3)@(negedge clk);rst=1;
 repeat(3)@(negedge clk);start=1;
 repeat(5)@(negedge clk);start=0;
 // Writes during acquisition must not change this sequence's pulse width.
 width=7;
 repeat(3500)@(negedge clk);
 if(pulses!=n)$fatal(1,"pulse count %0d expected %0d",pulses,n);
end
endtask
initial begin #1;rst=1;#1;rst=0;run(0,0,2,100);run(1,0,3,0);run(0,1,2,100);run(1,1,3,2);run(1,0,3,100);run(1,1,3,100);run(1,0,1,1);$display("PASS: US unchanged, OA legacy/1/2/100 cycles at 10/20 MHz, latched width and unchanged capture delay");$finish;end
initial begin #5000000;$fatal(1,"timeout");end
endmodule

