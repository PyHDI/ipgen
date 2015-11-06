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
   input wire                     rready
   );
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
   output wire                    rready
   );
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
   output wire                    rlast,
   output wire                    rvalid,
   input wire                     rready
   );
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
   output wire                    rready
   );
endmodule

