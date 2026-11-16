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
//   Check signed sample accumulation and averaging through the pipeline.
// -----------------------------------------------------------------------------

`timescale 1ns/1ps
// Uses the FIFO model in accumulation_pipeline_tb.sv and production arithmetic.
module signed_average_tb;
reg clk=0,rst=0,reset_fifo=1,start=0,first=1,enable=0;
always #5 clk=~clk;
reg [19:0] raw;
reg wr=0;
reg [7:0] count=1;
wire done,accept,empty,dv,read_sum,write_average,finished;
wire [27:0] sum;
wire [19:0] average;
integer sums_a[0:3],sums_b[0:3];
integer received=0,tests=0;
accumulation #(.N_FIFOS(1),.SUM_WIDTH(14),.WRITE_CNT_WIDTH(8)) acc(
 .rst_state_ni(rst),.rst_fifos_i(reset_fifo),.write_cnt_i(8'd4),
 .wr_fifo_done_o(done),.wr_accept_o(accept),.data_i(raw),.first_shot_i(first),
 .start_capture_i(start),.wr_clk_i(clk),.wr_en_i(wr),.rd_clk_i(clk),
 .rd_en_i(read_sum),.data_o(sum),.data_valid_o(dv),.empty_o(empty));
result_average_engine #(.N_LANES(1),.SUM_WIDTH(14),.FRAME_COUNT_WIDTH(8)) avg(
 .clk_i(clk),.rst_ni(rst),.enable_i(enable),.accumulation_count_i(count),
 .samples_per_lane_i(8'd4),.lanes_enable_i(1'b1),.frame_done_o(finished),
 .sum_empty_i(empty),.sum_data_valid_i(dv),.sum_data_i(sum),.sum_read_o(read_sum),
 .average_full_i(1'b0),.average_write_o(write_average),.average_data_o(average));
function integer value(input integer shot,input integer sample,input integer side,input integer base);
 case(sample)
  0:value=(shot%2==0)?1:-1;
  1:value=(shot%2==0)?-512:511;
  2:value=side?-37:100;
  3:value=base+side;
 endcase
endfunction
integer ea,eb;
always @(posedge clk) if(rst && write_average) begin
 ea=((sums_a[received]+512*count)/count)-512;
 eb=((sums_b[received]+512*count)/count)-512;
 if(average[9:0] !== (ea & 1023) || average[19:10] !== (eb & 1023))
  $fatal(1,"N=%0d index=%0d got=%h expected A=%0d B=%0d",count,received,average,ea,eb);
 received=received+1;
end
task run(input integer n,input integer base);
 integer shot,k,a,b;
 begin
 @(negedge clk);rst=0;reset_fifo=1;enable=0;wr=0;start=0;count=n;received=0;
 for(k=0;k<4;k=k+1)begin sums_a[k]=0;sums_b[k]=0;end
 repeat(4)@(negedge clk);rst=1;reset_fifo=0;
 for(shot=0;shot<n;shot=shot+1)begin
  first=(shot==0);start=1;repeat(5)@(negedge clk);start=0;
  for(k=0;k<4;k=k+1)begin
   a=value(shot,k,0,base);b=value(shot,k,1,base);
   sums_a[k]=sums_a[k]+a;sums_b[k]=sums_b[k]+b;
   raw={10'(b),10'(a)};wr=1;
   @(posedge clk);while(!accept)@(posedge clk);
   @(negedge clk);
  end
  wr=0;wait(done);repeat(5)@(negedge clk);
 end
 enable=1;wait(finished);@(negedge clk);
 if(received!=4)$fatal(1,"missing output");
 tests=tests+1;
 end
endtask
integer v,n;
initial begin
 // Verify one-accumulation identity for every possible 10-bit input code.
 for(v=-512;v<511;v=v+2)run(1,v);
 for(n=2;n<=12;n=n+1)run(n,-123);
 $display("PASS: %0d sequences, all 1024 input codes at N=1, signed mixed/extreme/constant samples at N=2..12",tests);
 $finish;
end
initial begin #10000000;$fatal(1,"timeout");end
endmodule
