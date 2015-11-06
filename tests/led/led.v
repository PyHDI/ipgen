`include "ipgen.v"

module led #
  (
   parameter LED_WIDTH = 8,
   parameter DATA_WIDTH = 32,
   parameter ADDR_WIDTH = 12
   )
  (
   input CLK,
   input RST,
   output reg [LED_WIDTH-1:0] LED
   );

  // Write Address
  wire                    s_awvalid;
  wire [ADDR_WIDTH-1:0]   s_awaddr;
  reg                     s_awready;
  
  // Write Data
  wire [DATA_WIDTH-1:0]   s_wdata;
  wire [DATA_WIDTH/8-1:0] s_wstrb;
  wire                    s_wvalid;
  reg                     s_wready;

  // Read Address
  wire                    s_arvalid;
  wire [ADDR_WIDTH-1:0]   s_araddr;
  reg                     s_arready;

  // Read Data
  reg  [DATA_WIDTH-1:0]   s_rdata;
  reg                     s_rvalid;
  wire                    s_rready;
  
  reg read_busy;
  reg write_busy;
  
  always @(posedge CLK) begin
    if(RST) begin
      LED <= 0;
      read_busy <= 0;
      write_busy <= 0;
      s_awready <= 0;
      s_arready <= 0;
      s_wready <= 0;
      s_rdata <= 0;
      s_rvalid <= 0;
    end else begin
      if(write_busy) begin
        s_awready <= 0;
        if(s_wvalid && s_wready) begin
          LED <= s_wdata;
          s_wready <= 0;
          write_busy <= 0;
        end
      end else if(read_busy) begin
        s_arready <= 0;
        if(s_rvalid && s_rready) begin
          s_rvalid <= 0;
          read_busy <= 0;
        end
      end else begin
        //default value
        s_awready <= 0;
        s_arready <= 0;
        s_wready <= 0;
        s_rvalid <= 0;
        if(s_awvalid) begin // new write request
          s_awready <= 1;
          s_wready <= 1;
          write_busy <= 1;
        end else if(s_arvalid) begin // new read request
          s_arready <= 1;
          s_rvalid <= 1;
          s_rdata <= LED; // 1st data 
          read_busy <= 1;
        end
      end
    end
  end

  ipgen_slave_lite_memory #
    (
     .NAME("s"),
     .ID(0),
     .DATA_WIDTH(DATA_WIDTH),
     .ADDR_WIDTH(ADDR_WIDTH)
     )
  inst_slave
    (
     .CLK(CLK),
     .RST(RST),

     .awvalid(s_awvalid),
     .awaddr(s_awaddr),
     .awready(s_awready),

     .wdata(s_wdata),
     .wstrb(s_wstrb),
     .wvalid(s_wvalid),
     .wready(s_wready),

     .arvalid(s_arvalid),
     .araddr(s_araddr),
     .arready(s_arready),

     .rdata(s_rdata),
     .rvalid(s_rvalid),
     .rready(s_rready)
     );
  
endmodule
