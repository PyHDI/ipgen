`include "ipgen.v"

module memcpy #
  (
   parameter DATA_WIDTH = 32,
   parameter ADDR_WIDTH = 32,
   parameter S_ADDR_WIDTH = 12
   )
  (
   input CLK,
   input RST,
   output reg [7:0] LED
   );

  localparam BURST_LEN = 128;
  localparam LOG_BURST_LEN = 7; // 2 ** 7 = 128

  // Write Address
  reg                     m_awvalid;
  reg  [ADDR_WIDTH-1:0]   m_awaddr;
  reg  [8-1:0]            m_awlen;
  wire                    m_awready;
  
  // Write Data
  reg  [DATA_WIDTH-1:0]   m_wdata;
  reg  [DATA_WIDTH/8-1:0] m_wstrb;
  reg                     m_wlast;
  reg                     m_wvalid;
  wire                    m_wready;

  // Read Address
  reg                     m_arvalid;
  reg  [ADDR_WIDTH-1:0]   m_araddr;
  reg  [8-1:0]            m_arlen;
  wire                    m_arready;

  // Read Data
  wire [DATA_WIDTH-1:0]   m_rdata;
  wire                    m_rlast;
  wire                    m_rvalid;
  reg                     m_rready;
  
  // Write Address
  wire                    s_awvalid;
  wire [S_ADDR_WIDTH-1:0] s_awaddr;
  reg                     s_awready;
  
  // Write Data
  wire [DATA_WIDTH-1:0]   s_wdata;
  wire [DATA_WIDTH/8-1:0] s_wstrb;
  wire                    s_wvalid;
  reg                     s_wready;

  // Read Address
  wire                    s_arvalid;
  wire [S_ADDR_WIDTH-1:0] s_araddr;
  reg                     s_arready;

  // Read Data
  reg  [DATA_WIDTH-1:0]   s_rdata;
  reg                     s_rvalid;
  wire                    s_rready;
  
  reg [7:0] state;
  
  reg [ADDR_WIDTH-1:0] count;
  reg [DATA_WIDTH-1:0] sum;

  reg  [LOG_BURST_LEN-1:0] ram_addr;
  reg  [DATA_WIDTH-1:0]    ram_data_in;
  reg                      ram_write_enable;
  wire [DATA_WIDTH-1:0]    ram_data_out;

  reg [ADDR_WIDTH-1:0] size;
  reg [ADDR_WIDTH-1:0] src_addr;
  reg [ADDR_WIDTH-1:0] dst_addr;
  
  lutram #
    (
     .ADDR_WIDTH(LOG_BURST_LEN),
     .DATA_WIDTH(DATA_WIDTH)
     )
  inst_lutram
    (
     .CLK(CLK),
     .addr(ram_addr),
     .data_in(ram_data_in),
     .write_enable(ram_write_enable),
     .data_out(ram_data_out)
     );
  
  always @(posedge CLK) begin
    if(RST) begin
      LED <= 0;
      state <= 0;
      m_awaddr <= 0;
      m_awvalid <= 0;
      m_araddr <= 0;
      m_arvalid <= 0;
      m_awlen <= 0;
      m_arlen <= 0;
      m_wvalid <= 0;
      m_wdata <= 0;
      m_wlast <= 0;
      m_wstrb <= {(DATA_WIDTH/8){1'b1}};
      m_rready <= 0;
      s_awready <= 0;
      s_arready <= 0;
      s_wready <= 0;
      s_rdata <= 0;
      s_rvalid <= 0;
      count <= 0;
      sum <= 0;
      ram_addr <= 0;
      ram_data_in <= 0;
      ram_write_enable <= 0;
      size <= 0;
      src_addr <= 0;
      dst_addr <= 0;
    end else begin
      case(state)
        'h00: begin
          m_awaddr <= 0;
          m_awvalid <= 0;
          m_araddr <= 0;
          m_arvalid <= 0;
          m_awlen <= 0;
          m_arlen <= 0;
          m_wvalid <= 0;
          m_wdata <= 0;
          m_wstrb <= {(DATA_WIDTH/8){1'b1}};
          m_wlast <= 0;
          m_rready <= 0;
          
          s_awready <= 1;
          s_arready <= 0;
          s_wready <= 0;
          s_rdata <= 0;
          s_rvalid <= 0;

          sum <= 0;
          size <= 0;
          src_addr <= 0;
          dst_addr <= 0;
          
          if(s_awvalid) begin
            s_wready <= 1;
            s_awready <= 0;
            state <= 'h01;
          end
        end
        'h01: begin
          if(s_wvalid) begin
            size <= s_wdata;
            s_wready <= 0;
            s_awready <= 1;
            state <= 'h02;
          end
        end
        'h02: begin
          if(s_awvalid) begin
            s_wready <= 1;
            s_awready <= 0;
            state <= 'h03;
          end
        end
        'h03: begin
          if(s_wvalid) begin
            src_addr <= s_wdata;
            s_wready <= 0;
            s_awready <= 1;
            state <= 'h04;
          end
        end
        'h04: begin
          if(s_awvalid) begin
            s_wready <= 1;
            s_awready <= 0;
            state <= 'h05;
          end
        end
        'h05: begin
          if(s_wvalid) begin
            dst_addr <= s_wdata;
            s_wready <= 0;
            if(size == 0) begin
              state <= 'h0d;
            end else begin
              state <= 'h06;
            end
          end
        end
        'h06: begin
          m_awaddr <= dst_addr & 'hffff_fffc;
          m_araddr <= src_addr & 'hffff_fffc;
          m_arlen <= (size <= BURST_LEN)? size - 1 : BURST_LEN - 1;
          m_arvalid <= 1;
          state <= 'h07;
        end
        'h07: begin
          if(m_arready) begin
            m_arvalid <= 0;
            m_rready <= 1;
            size <= size - m_arlen - 1;
            count <= 0;
            ram_addr <= -1;
            state <= 'h08;
          end
        end
        'h08: begin
          ram_write_enable <= 0;
          if(m_rready && m_rvalid) begin
            ram_addr <= ram_addr + 1;
            ram_data_in <= m_rdata;
            ram_write_enable <= 1;
            count <= count + 1;
            if(count == m_arlen) begin
              m_rready <= 0;
              state <= 'h09;
            end
          end
        end
        'h09: begin
          ram_write_enable <= 0;
          m_awlen <= m_arlen;
          m_awvalid <= 1;
          state <= 'h0a;
        end
        'h0a: begin
          if(m_awready) begin
            m_awvalid <= 0;
            ram_addr <= 0;
            count <= 0;
            state <= 'hb;
          end
        end
        'h0b: begin
          if(m_wvalid && m_wready) begin
            sum <= sum + m_wdata;
          end
          if(!m_wvalid || (m_wvalid && m_wready)) begin
            m_wdata <= ram_data_out;
            m_wvalid <= 1;
            ram_addr <= ram_addr + 1;
            count <= count + 1;
            if(count == m_awlen) begin
              m_wlast <= 1;
              state <= 'h0c;
            end
          end
        end
        'h0c: begin
          if(m_wvalid && m_wready) begin
            sum <= sum + m_wdata;
          end
          if(m_wvalid && m_wready) begin
            m_wvalid <= 0;
            m_wlast <= 0;
            state <= 'h0d;
          end
        end
        'h0d: begin
          if(size == 0) begin
            LED <= sum;
            s_arready <= 1;
            state <= 'h0e;
          end else begin
            m_araddr <= m_araddr + m_arlen * (DATA_WIDTH/8) + (DATA_WIDTH/8);
            m_awaddr <= m_awaddr + m_awlen * (DATA_WIDTH/8) + (DATA_WIDTH/8);
            m_arlen <= (size <= BURST_LEN)? size - 1 : BURST_LEN - 1;
            m_arvalid <= 1;
            state <= 'h07;
          end
        end
        'h0e: begin
          if(s_arvalid) begin
            s_arready <= 0;
            s_rvalid <= 1;
            s_rdata <= sum;
            state <= 'h0f;
          end
        end
        'h0f: begin
          if(s_rready) begin
            s_rvalid <= 0;
            state <= 'h00;
          end
        end
      endcase
    end
  end
  
  ipgen_master_memory #
    (
     .NAME("m"),
     .ID(0),
     .DATA_WIDTH(DATA_WIDTH),
     .ADDR_WIDTH(ADDR_WIDTH)
     )
  inst_master
    (
     .CLK(CLK),
     .RST(RST),

     .awvalid(m_awvalid),
     .awaddr(m_awaddr),
     .awlen(m_awlen),
     .awready(m_awready),

     .wdata(m_wdata),
     .wstrb(m_wstrb),
     .wlast(m_wlast),
     .wvalid(m_wvalid),
     .wready(m_wready),

     .arvalid(m_arvalid),
     .araddr(m_araddr),
     .arlen(m_arlen),
     .arready(m_arready),

     .rdata(m_rdata),
     .rlast(m_rlast),
     .rvalid(m_rvalid),
     .rready(m_rready)
     );
  
  ipgen_slave_lite_memory #
    (
     .NAME("s"),
     .ID(0),
     .DATA_WIDTH(DATA_WIDTH),
     .ADDR_WIDTH(S_ADDR_WIDTH)
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

module lutram #
  (
   parameter DATA_WIDTH = 32,
   parameter ADDR_WIDTH = 8
   )
  (
   input CLK,
   input [ADDR_WIDTH-1:0] addr,
   input [DATA_WIDTH-1:0] data_in,
   input                  write_enable,
   output [DATA_WIDTH-1:0] data_out
   );
  reg [DATA_WIDTH-1:0] mem [0:2**ADDR_WIDTH-1];
  always @(posedge CLK) begin
    if(write_enable) begin
      mem[addr] <= data_in;
    end
  end
  assign data_out = mem[addr];
endmodule  

