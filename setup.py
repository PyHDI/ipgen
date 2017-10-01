from setuptools import setup, find_packages

import ipgen.utils.version
import re
import os

m = re.search(r'(\d+\.\d+\.\d+(-.+)?)', ipgen.utils.version.VERSION)
version = m.group(1) if m is not None else '0.0.0'

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

import sys
script_name = 'ipgen'

setup(name='ipgen',
      version=version,
      description='IP-core package generator for AXI4/Avalon',
      long_description=read('README.rst'),
      keywords = 'FPGA, Verilog HDL, IP-core, AMBA AXI4, Avalon',
      author='Shinya Takamaeda-Yamazaki',
      license="Apache License 2.0",
      url='https://github.com/PyHDI/ipgen',
      packages=find_packages(),
      package_data={ 'ipgen.template' : ['*.*'], },
      install_requires=[ 'pyverilog>=1.1.0', 'Jinja2>=2.8' ],
      extras_require={
          'test' : [ 'pytest>=2.8.2', 'pytest-pythonpath>=0.7' ],
      },
      entry_points="""
      [console_scripts]
      %s = ipgen.run_ipgen:main
      """ % script_name,
)
