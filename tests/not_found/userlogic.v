`include "ipgen.v"

module userlogic #
  (
   parameter LED_WIDTH = 8,
   parameter DATA_WIDTH = 32,
   parameter ADDR_WIDTH = 32
   )
  (
   input CLK,
   input RST,
   output reg [LED_WIDTH-1:0] LED
   );

  wire OCLK;
  tmp #( .A(100) )
  inst_tmp(.CLK(CLK), .RST(RST), .OCLK(OCLK));
  
  localparam BURST_LEN = 16;
  localparam REPEAT_NUM = 4;

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
  
  reg [3:0] state;
  reg [ADDR_WIDTH-1:0] count;

  reg [DATA_WIDTH-1:0] latest_read_data;
  reg [ADDR_WIDTH-1:0] repeat_count;

  reg [DATA_WIDTH-1:0] sum;
  
  always @(posedge CLK) begin
    if(RST) begin
      state <= 0;
      LED <= 0;
      m_awaddr <= 0;
      m_awvalid <= 0;
      m_araddr <= 0;
      m_arvalid <= 0;
      m_awlen <= 0;
      m_arlen <= 0;
      m_wvalid <= 0;
      m_wdata <= 0;
      m_wstrb <= {(DATA_WIDTH/8){1'b1}};
      m_rready <= 0;
      s_awready <= 0;
      s_arready <= 0;
      s_wready <= 0;
      s_rdata <= 0;
      s_rvalid <= 0;
      count <= 0;
      latest_read_data <= 0;
      repeat_count <= 0;
      sum <= 0;
    end else begin
      case(state)
        'h00: begin
          m_awaddr <= 0;
          m_awvalid <= 0;
          m_araddr <= 0;
          m_arvalid <= 0;
          m_awlen <= BURST_LEN - 1;
          m_arlen <= BURST_LEN - 1;
          m_wvalid <= 0;
          m_wdata <= 0;
          m_wstrb <= {(DATA_WIDTH/8){1'b1}};
          m_rready <= 0;
          
          s_awready <= 1;
          s_arready <= 0;
          s_wready <= 0;
          s_rdata <= 0;
          s_rvalid <= 0;
          
          repeat_count <= 0;
          
          if(s_awvalid) begin
            s_wready <= 1;
            s_awready <= 0;
            state <= 'h01;
          end
        end
        'h01: begin
          if(s_wvalid) begin
            // read s_wdata
            s_wready <= 0;
            state <= 'h02;
          end
        end
        'h02: begin
          m_arvalid <= 1;
          state <= 'h03;
        end
        'h03: begin
          if(m_arready) begin
            m_arvalid <= 0;
            m_rready <= 1;
            count <= 0;
            state <= 'h04;
          end
        end
        'h04: begin
          if(m_rvalid) begin
            count <= count + 1;
            latest_read_data <= m_rdata;
            sum <= sum + m_rdata;
            $display("rdata:%x", m_rdata);
            if(count == BURST_LEN-1) begin
              state <= 'h05;
            end
          end
        end
        'h05: begin
          if(repeat_count == REPEAT_NUM-1) begin
            repeat_count <= 0;
            state <= 'h06;
          end else begin
            m_araddr <= m_araddr + (DATA_WIDTH/8) * BURST_LEN;
            repeat_count <= repeat_count + 1;
            state <= 'h02;
          end
        end
        'h06: begin
          s_arready <= 1;
          state <= 'h07;
        end
        'h07: begin
          if(s_arvalid) begin
            s_arready <= 0;
            s_rvalid <= 1;
            s_rdata <= sum;
            state <= 'h08;
          end
        end
        'h08: begin
          if(s_rready) begin
            s_rvalid <= 0;
            state <= 'h09;
          end
        end
        'h09: begin
          // $finish;
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
