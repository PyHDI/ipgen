//------------------------------------------------------------------------------
// IPgen Interface Library
// - ipgen_master_memory:  memory-mapped access interface (master)
// - ipgen_slave_memory:   memory-mapped access interface (slave)
// - ipgen_master_lite_memory:  memory-mapped access lite interface (master)
// - ipgen_slave_lite_memory:   memory-mapped access lite interface (slave)
//------------------------------------------------------------------------------

//------------------------------------------------------------------------------
module ipgen_master_memory #
  (
   parameter NAME = "undefined",
   parameter ID = 0,
   parameter ADDR_WIDTH = 32, // up to 32
   parameter DATA_WIDTH = 32  // 8, 16, 32, 64, 128, 256, and 512 are supported
   )
  (
   input CLK,
   input RST,
   
   // Write Address
   input wire                     awvalid,
   input wire  [ADDR_WIDTH-1:0]   awaddr,
   input wire  [8-1:0]            awlen,
   output wire                    awready,
  
   // Write Data
   input wire  [DATA_WIDTH-1:0]   wdata,
   input wire  [DATA_WIDTH/8-1:0] wstrb,
   input wire                     wlast,
   input wire                     wvalid,
   output wire                    wready,

   // Read Address
   input wire                     arvalid,
   input wire  [ADDR_WIDTH-1:0]   araddr,
   input wire  [8-1:0]            arlen,
   output wire                    arready,

   // Read Data
   output wire [DATA_WIDTH-1:0]   rdata,
   output wire                    rlast,
   output wire                    rvalid,
   input wire                     rready,

   
   // Write Address
   output wire                    ext_awvalid,
   output wire [ADDR_WIDTH-1:0]   ext_awaddr,
   output wire [8-1:0]            ext_awlen,
   input wire                     ext_awready,
  
   // Write Data
   output wire [DATA_WIDTH-1:0]   ext_wdata,
   output wire [DATA_WIDTH/8-1:0] ext_wstrb,
   output wire                    ext_wlast,
   output wire                    ext_wvalid,
   input wire                     ext_wready,
   
   // Read Address
   output wire                    ext_arvalid,
   output wire [ADDR_WIDTH-1:0]   ext_araddr,
   output wire [8-1:0]            ext_arlen,
   input wire                     ext_arready,

   // Read Data
   input wire  [DATA_WIDTH-1:0]   ext_rdata,
   input wire                     ext_rlast,
   input wire                     ext_rvalid,
   output wire                    ext_rready
   );

  assign ext_awvalid = awvalid;
  assign ext_awaddr = awaddr;
  assign ext_awlen = awlen;
  assign awready = ext_awready;

  assign ext_wdata = wdata;
  assign ext_wstrb = wstrb;
  assign ext_wlast = wlast;
  assign ext_wvalid = wvalid;
  assign wready = ext_wready;

  assign ext_arvalid = arvalid;
  assign ext_araddr = araddr;
  assign ext_arlen = arlen;
  assign arready = ext_arready;

  assign rdata = ext_rdata;
  assign rlast = ext_rlast;
  assign rvalid = ext_rvalid;
  assign ext_rready = rready;
endmodule

//------------------------------------------------------------------------------
module ipgen_slave_memory #
  (
   parameter NAME = "undefined",
   parameter ID = 0,
   parameter ADDR_WIDTH = 32, // up to 32
   parameter DATA_WIDTH = 32  // 8, 16, 32, 64, 128, 256, and 512 are supported
   )
  (
   input CLK,
   input RST,
   
   // Write Address
   output wire                    awvalid,
   output wire [ADDR_WIDTH-1:0]   awaddr,
   output wire [8-1:0]            awlen,
   input wire                     awready,
  
   // Write Data
   output wire [DATA_WIDTH-1:0]   wdata,
   output wire [DATA_WIDTH/8-1:0] wstrb,
   output wire                    wlast,
   output wire                    wvalid,
   input wire                     wready,

   // Read Address
   output wire                    arvalid,
   output wire [ADDR_WIDTH-1:0]   araddr,
   output wire [8-1:0]            arlen,
   input wire                     arready,

   // Read Data
   input wire  [DATA_WIDTH-1:0]   rdata,
   input wire                     rlast,
   input wire                     rvalid,
   output wire                    rready,

   
   // Write Address
   input wire                     ext_awvalid,
   input wire  [ADDR_WIDTH-1:0]   ext_awaddr,
   input wire  [8-1:0]            ext_awlen,
   output wire                    ext_awready,
  
   // Write Data
   input wire  [DATA_WIDTH-1:0]   ext_wdata,
   input wire  [DATA_WIDTH/8-1:0] ext_wstrb,
   input wire                     ext_wlast,
   input wire                     ext_wvalid,
   output wire                    ext_wready,

   // Read Address
   input wire                     ext_arvalid,
   input wire  [ADDR_WIDTH-1:0]   ext_araddr,
   input wire  [8-1:0]            ext_arlen,
   output wire                    ext_arready,

   // Read Data
   output wire [DATA_WIDTH-1:0]   ext_rdata,
   output wire                    ext_rlast,
   output wire                    ext_rvalid,
   input wire                     ext_rready
   );
  
  assign awvalid = ext_awvalid;
  assign awaddr = ext_awaddr;
  assign awlen = ext_awlen;
  assign ext_awready = awready;

  assign wdata = ext_wdata;
  assign wstrb = ext_wstrb;
  assign wlast = ext_wlast;
  assign wvalid = ext_wvalid;
  assign ext_wready = wready;

  assign arvalid = ext_arvalid;
  assign araddr = ext_araddr;
  assign arlen = ext_arlen;
  assign ext_arready = arready;

  assign ext_rdata = rdata;
  assign ext_rlast = rlast;
  assign ext_rvalid = rvalid;
  assign rready = ext_rready;
endmodule

//------------------------------------------------------------------------------
module ipgen_master_lite_memory #
  (
   parameter NAME = "undefined",
   parameter ID = 0,
   parameter ADDR_WIDTH = 32, // up to 32
   parameter DATA_WIDTH = 32  // 8, 16, 32, 64, 128, 256, and 512 are supported
   )
  (
   input CLK,
   input RST,
   
   // Write Address
   input wire                     awvalid,
   input wire  [ADDR_WIDTH-1:0]   awaddr,
   output wire                    awready,
  
   // Write Data
   input wire  [DATA_WIDTH-1:0]   wdata,
   input wire  [DATA_WIDTH/8-1:0] wstrb,
   input wire                     wvalid,
   output wire                    wready,

   // Read Address
   input wire                     arvalid,
   input wire  [ADDR_WIDTH-1:0]   araddr,
   output wire                    arready,

   // Read Data
   output wire [DATA_WIDTH-1:0]   rdata,
   output wire                    rvalid,
   input wire                     rready,

   
   // Write Address
   output wire                    ext_awvalid,
   output wire [ADDR_WIDTH-1:0]   ext_awaddr,
   input wire                     ext_awready,
  
   // Write Data
   output wire [DATA_WIDTH-1:0]   ext_wdata,
   output wire [DATA_WIDTH/8-1:0] ext_wstrb,
   output wire                    ext_wvalid,
   input wire                     ext_wready,

   // Read Address
   output wire                    ext_arvalid,
   output wire [ADDR_WIDTH-1:0]   ext_araddr,
   input wire                     ext_arready,

   // Read Data
   input wire  [DATA_WIDTH-1:0]   ext_rdata,
   input wire                     ext_rvalid,
   output wire                    ext_rready
   );

  assign ext_awvalid = awvalid;
  assign ext_awaddr = awaddr;
  assign awready = ext_awready;

  assign ext_wdata = wdata;
  assign ext_wstrb = wstrb;
  assign ext_wvalid = wvalid;
  assign wready = ext_wready;

  assign ext_arvalid = arvalid;
  assign ext_araddr = araddr;
  assign arready = ext_arready;

  assign rdata = ext_rdata;
  assign rvalid = ext_rvalid;
  assign ext_rready = rready;
endmodule

//------------------------------------------------------------------------------
module ipgen_slave_lite_memory #
  (
   parameter NAME = "undefined",
   parameter ID = 0,
   parameter ADDR_WIDTH = 32, // up to 32
   parameter DATA_WIDTH = 32  // 8, 16, 32, 64, 128, 256, and 512 are supported
   )
  (
   input CLK,
   input RST,
   
   // Write Address
   output wire                    awvalid,
   output wire [ADDR_WIDTH-1:0]   awaddr,
   input wire                     awready,
  
   // Write Data
   output wire [DATA_WIDTH-1:0]   wdata,
   output wire [DATA_WIDTH/8-1:0] wstrb,
   output wire                    wvalid,
   input wire                     wready,

   // Read Address
   output wire                    arvalid,
   output wire [ADDR_WIDTH-1:0]   araddr,
   input wire                     arready,

   // Read Data
   input wire  [DATA_WIDTH-1:0]   rdata,
   input wire                     rvalid,
   output wire                    rready,

   
   // Write Address
   input wire                     ext_awvalid,
   input wire  [ADDR_WIDTH-1:0]   ext_awaddr,
   output wire                    ext_awready,
  
   // Write Data
   input wire  [DATA_WIDTH-1:0]   ext_wdata,
   input wire  [DATA_WIDTH/8-1:0] ext_wstrb,
   input wire                     ext_wvalid,
   output wire                    ext_wready,

   // Read Address
   input wire                     ext_arvalid,
   input wire  [ADDR_WIDTH-1:0]   ext_araddr,
   output wire                    ext_arready,

   // Read Data
   output wire [DATA_WIDTH-1:0]   ext_rdata,
   output wire                    ext_rvalid,
   input wire                     ext_rready
   );
  
  assign awvalid = ext_awvalid;
  assign awaddr = ext_awaddr;
  assign ext_awready = awready;

  assign wdata = ext_wdata;
  assign wstrb = ext_wstrb;
  assign wvalid = ext_wvalid;
  assign ext_wready = wready;

  assign arvalid = ext_arvalid;
  assign araddr = ext_araddr;
  assign ext_arready = arready;

  assign ext_rdata = rdata;
  assign ext_rvalid = rvalid;
  assign rready = ext_rready;
endmodule

