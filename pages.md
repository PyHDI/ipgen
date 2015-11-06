What's IPgen?
==============================

IPgen is a lightweight IP-core package synthesizer from abstract RTL sources.
You can implement both AXI4 and Avalon IP-core by using the provided abstract interfaces.

- ipgen_master_memory:  memory-mapped access interface (master)
- ipgen_slave_memory:   memory-mapped access interface (slave)
- ipgen_master_lite_memory:  memory-mapped access lite interface (master)
- ipgen_slave_lite_memory:   memory-mapped access lite interface (slave)


Requirements
==============================

Software
--------------------------------------------------------------------------------

* Python (2.7 or later, 3.3 or later)
* Icarus Verilog (0.9.6 or later)
    - 'iverilog -E' command is used for preprocessing Verilog source code.
* Jinja2 (2.7 or later)
    - The code generator uses Jinja2 template engine.
    - 'pip install jinja2' (for Python 2.x) or 'pip3 install jinja2' (for Python 3.x)
* Pyverilog (Python-based Verilog HDL Design Processing Toolkit)
    - Install from pip: 'pip install pyverilog' for Python2.7 or 'pip3 install pyverilog' for Python3
    - Install from github into this package: 'cd ipgen; git clone https://github.com/shtaxxx/Pyverilog.git; cd ipgen; ln -s ../Pyverilog/pyverilog'

### for RTL simulation

* Icarus Verilog
    - Icarus Verilog is an open-sourced Verilog simulator
* Synopsys VCS (option, if you have) 
    - VCS is a very fast commercial Verilog simulator

### for bitstream synthesis

* Xilinx: Vivado (2014.4 or later) and Xilinx Platform Studio (14.6 or later)
* Altera: Qsys (14.0 or later)


Installation
==============================

If you want to use flipSyrup as a general library, you can install on your environment by using setup.py.

If Python 2.7 is used,

    python setup.py install

If Python 3.x is used,

    python3 setup.py install

Then you can use the flipSyrup command from your console (the version number depends on your environment).

    ipgen-0.1.0-py3.4.1


Getting Started
==============================

First, please make sure TARGET in 'base.mk' in 'sample' is correctly defined. If you use the installed IPgen command on your environment, please modify 'TARGET' in base.mk as below (the version number depends on your environment)

    TARGET=ipgen-0.1.0-py3.4.1

You can find the sample projects in 'sample/test/single\_master\_memory'.

* userlogic.v  : User-defined Verilog code using IPgen abstract memory interfaces

Then type 'make' and 'make run' to simulate sample system.

    make build
    make sim

Or type commands as below directly.

    python ipgen/ipegn.py sample/default.config -t userlogic -I include/ sample/test/single_master_memory/userlogic.v
    iverilog -I ipen_userlogic_v1_00_a/hdl/verilog/ ipgen_userlogic_v1_00_a/test/test_ipgen_userlogic.v 
    ./a.out

IPgen compiler generates a directory for IP-core (ipgen\_userlogic\_v1\_00\_a, in this example).

'ipgen\_userlogic\_v1\_00\_a.v' includes 
* IP-core RTL design (hdl/verilog/ipgen\_userlogic.v)
* Test bench (test/test\_ipgen\_userlogic.v) 
* XPS setting files (ipgen\_userlogic\_v2\_1\_0.{mpd,pao,tcl})
* IP-XACT file (component.xml)

A bit-stream can be synthesized by using Xilinx Platform Studio, Xilinx Vivado, and Altera Qsys.
In case of XPS, please copy the generated IP-core into 'pcores' directory of XPS project.


IPgen Command Options
==============================

Command
------------------------------

    python ipgen.py [config] [-t topmodule] [-I includepath]+ [--memimg=filename] [--usertest=filename] [file]+

Description
------------------------------

* file
    - User-logic Verilog file (.v) and FPGA system memory specification (.config).
      Automatically, .v file is recognized as a user-logic Verilog file, and 
      .config file recongnized as a memory specification of used FPGA system, respectively.
* config
    - Configuration file which includes memory and device specification 
* -t
    - Name of user-defined top module, default is "userlogic".
* -I
    - Include path for input Verilog HDL files.
* --memimg
    - DRAM image file in HEX DRAM (option, if you need).
      The file is copied into test directory.
      If no file is assigned, the array is initialized with incremental values.
* --usertest
    - User-defined test code file (option, if you need).
      The code is copied into testbench script.


Related Project
==============================

[Pyverilog](http://shtaxxx.github.io/Pyverilog/)
- Python-based Hardware Design Processing Toolkit for Verilog HDL
- Used as basic code analyser and generator


License
==============================

Apache License 2.0
(http://www.apache.org/licenses/LICENSE-2.0)


Copyright and Contact
==============================

Copyright (C) 2015, Shinya Takamaeda-Yamazaki

E-mail: shinya\_at\_is.naist.jp

