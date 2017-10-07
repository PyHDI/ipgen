IPgen
=====

IP-core package generator for AXI4/Avalon

Copyright (C) 2015, Shinya Takamaeda-Yamazaki

E-mail: takamaeda\_at\_ist.hokudai.ac.jp

License
=======

Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)

Publication
===========

If you use IPgen in your research, please cite my paper about Pyverilog.
(IPgen is constructed on Pyverilog.)

-  Shinya Takamaeda-Yamazaki: Pyverilog: A Python-based Hardware Design
   Processing Toolkit for Verilog HDL, 11th International Symposium on
   Applied Reconfigurable Computing (ARC 2015) (Poster), Lecture Notes
   in Computer Science, Vol.9040/2015, pp.451-460, April 2015.
   `Paper <http://link.springer.com/chapter/10.1007/978-3-319-16214-0_42>`__

::

    @inproceedings{Takamaeda:2015:ARC:Pyverilog,
    title={Pyverilog: A Python-Based Hardware Design Processing Toolkit for Verilog HDL},
    author={Takamaeda-Yamazaki, Shinya},
    booktitle={Applied Reconfigurable Computing},
    month={Apr},
    year={2015},
    pages={451-460},
    volume={9040},
    series={Lecture Notes in Computer Science},
    publisher={Springer International Publishing},
    doi={10.1007/978-3-319-16214-0_42},
    url={http://dx.doi.org/10.1007/978-3-319-16214-0_42},
    }

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

-  Pyverilog: 1.1.1 or later

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

-  memcpy.v : User-defined Verilog code using IPgen abstract memory
   interfaces

Then type 'make' and 'make run' to simulate sample system.

::

    make build
    make sim

Or type commands as below directly.

::

    ipgen default.config -t memcpy -I include tests/memcpy/memcpy.v
    iverilog -I memcpy_ip_v1_00_a/hdl/verilog/ memcpy_ip_v1_00_a/test/test_memcpy_ip.v 
    ./a.out

IPgen compiler generates a directory for IP-core (memcpy\_ip\_v1\_00\_a,
in this example).

'memcpy\_ip\_v1\_00\_a.v' includes - IP-core RTL design
(hdl/verilog/memcpy\_ip.v) - Test bench (test/test\_memcpy\_ip.v) - XPS
setting files (memcpy\_ip\_v2\_1\_0.{mpd,pao,tcl}) - IP-XACT file
(component.xml)

A bit-stream can be synthesized by using Xilinx Platform Studio, Xilinx
Vivado, and Altera Qsys. In case of XPS, please copy the generated
IP-core into 'pcores' directory of XPS project.

IPgen Command Options
=====================

Command
-------

::

    ipgen [config] [-t topmodule] [--ipname=ipname] [--memimg=memimg_name] [--usertest=usertest_name] [-I include]+ [-D define]+ [file]+

Description
-----------

-  config

   -  System configuration file which includes memory and device
      specifications

-  -t

   -  Top-module name of user logic, default: 'top'

-  --ipname

   -  IP-core package name, default: '(topmodule)*ip*\ (version)'

-  --memimg

   -  Memory image file in HEX (option). The file is copied into test
      directory. If no file is assigned, the array is initialized with
      incremental values.

-  --usertest

   -  User-defined test code file (option). The code is copied into
      testbench script.

-  -I

   -  Include path

-  -D

   -  Macro definition

-  file

   -  User-logic Verilog file (.v)

Related Project
===============

`Pyverilog <https://github.com/PyHDI/Pyverilog>`__ - Python-based
Hardware Design Processing Toolkit for Verilog HDL

`Veriloggen <https://github.com/PyHDI/veriloggen>`__ - A library for
constructing a Verilog HDL source code in Python
