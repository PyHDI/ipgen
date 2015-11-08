IPgen
=====

IP-core package generator for AXI4/Avalon

Copyright (C) 2015, Shinya Takamaeda-Yamazaki

E-mail: shinya\_at\_is.naist.jp

License
=======

Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)

What's IPgen?
=============

IPgen is a lightweight IP-core package synthesizer from abstract RTL
sources. You can implement both AXI4 and Avalon IP-core by using the
provided abstract interfaces.

-  ipgen\_master\_memory: memory-mapped access interface (master)
-  ipgen\_slave\_memory: memory-mapped access interface (slave)
-  ipgen\_master\_lite\_memory: memory-mapped access lite interface
   (master)
-  ipgen\_slave\_lite\_memory: memory-mapped access lite interface
   (slave)

Installation
============

Requirements
------------

-  Python: 2.7, 3.4 or later

Python3 is recommended.

-  Icarus Verilog: 0.9.7 or later

Install on your platform. For exmple, on Ubuntu:

::

    sudo apt-get install iverilog

-  Jinja2: 2.8 or later
-  pytest: 2.8.2 or later
-  pytest-pythonpath: 0.7 or later

Install on your python environment by using pip.

::

    pip install jinja2 pytest pytest-pythonpath

-  Pyverilog: 1.0.0 or later

Install from pip:

::

    pip install pyverilog

Install
-------

Install IPgen.

::

    python setup.py install

Getting Started
===============

You can use the ipgen command from your console.

::

    ipgen

You can find the sample projects in 'tests'. Now let's see
'tests/memcpy'. There is an input source code.

-  userlogic.v : User-defined Verilog code using IPgen abstract memory
   interfaces

Then type 'make' and 'make run' to simulate sample system.

::

    make build
    make sim

Or type commands as below directly.

::

    ipgen default.config -t userlogic -I include tests/memcpyuserlogic.v
    iverilog -I ipen_userlogic_v1_00_a/hdl/verilog/ ipgen_userlogic_v1_00_a/test/test_ipgen_userlogic.v 
    ./a.out

IPgen compiler generates a directory for IP-core
(ipgen\_userlogic\_v1\_00\_a, in this example).

'ipgen\_userlogic\_v1\_00\_a.v' includes - IP-core RTL design
(hdl/verilog/ipgen\_userlogic.v) - Test bench
(test/test\_ipgen\_userlogic.v) - XPS setting files
(ipgen\_userlogic\_v2\_1\_0.{mpd,pao,tcl}) - IP-XACT file
(component.xml)

A bit-stream can be synthesized by using Xilinx Platform Studio, Xilinx
Vivado, and Altera Qsys. In case of XPS, please copy the generated
IP-core into 'pcores' directory of XPS project.

IPgen Command Options
=====================

Command
-------

::

    ipgen [config] [-t topmodule] [-I includepath]+ [--memimg=filename] [--usertest=filename] [file]+

Description
-----------

-  file

   -  User-logic Verilog file (.v) and FPGA system memory specification
      (.config). Automatically, .v file is recognized as a user-logic
      Verilog file, and .config file recongnized as a memory
      specification of used FPGA system, respectively.

-  config

   -  Configuration file which includes memory and device specification

-  -t

   -  Name of user-defined top module, default is "userlogic".

-  -I

   -  Include path for input Verilog HDL files.

-  --memimg

   -  DRAM image file in HEX DRAM (option, if you need). The file is
      copied into test directory. If no file is assigned, the array is
      initialized with incremental values.

-  --usertest

   -  User-defined test code file (option, if you need). The code is
      copied into testbench script.

Related Project
===============

`Pyverilog <http://shtaxxx.github.io/Pyverilog/>`__ - Python-based
Hardware Design Processing Toolkit for Verilog HDL - Used as basic code
analyser and generator
