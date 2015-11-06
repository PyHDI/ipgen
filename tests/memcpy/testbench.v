reg [31:0] readval;
reg [31:0] size, src, dst;

initial begin
  #1000;
  wait(sim_resetn == 1);
  nclk();

  size = 16;
  src = 0;
  dst = 4096;
  
  $display("[testbench] size: %d", size);
  slave_write_ipgen_slave_lite_memory_s_0(size, 0);
  nclk();
  
  $display("[testbench] src: %d", src);
  slave_write_ipgen_slave_lite_memory_s_0(src, 0);
  nclk();
  
  $display("[testbench] dst: %d", dst);
  slave_write_ipgen_slave_lite_memory_s_0(dst, 0);
  nclk();
  
  slave_read_ipgen_slave_lite_memory_s_0(readval, 0);
  nclk();
  $display("[testbench] sum: %d", readval);

  size = 1024;
  src = 0;
  dst = 4096;
  
  $display("[testbench] size: %d", size);
  slave_write_ipgen_slave_lite_memory_s_0(size, 0);
  nclk();
  
  $display("[testbench] src: %d", src);
  slave_write_ipgen_slave_lite_memory_s_0(src, 0);
  nclk();
  
  $display("[testbench] dst: %d", dst);
  slave_write_ipgen_slave_lite_memory_s_0(dst, 0);
  nclk();
  
  slave_read_ipgen_slave_lite_memory_s_0(readval, 0);
  nclk();
  $display("[testbench] sum: %d", readval);
  
  #1000;
  $finish;
end
