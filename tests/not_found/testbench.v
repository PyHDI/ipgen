reg [31:0] readval;

initial begin
  #1000;
  wait(sim_resetn == 1);
  nclk();
  
  $display("[testbench] write");
  slave_write_ipgen_slave_lite_memory_s_0(1, 0);
  nclk();
  
  slave_read_ipgen_slave_lite_memory_s_0(readval, 0);
  nclk();
  $display("[testbench] read: %d", readval);
  
  #1000;
  $finish;
end
