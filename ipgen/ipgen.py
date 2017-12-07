#-------------------------------------------------------------------------
# ipgen.py
#
# IPgen: IP-core package generator for AXI4/Avalon
#
# Copyright (C) 2013, Shinya Takamaeda-Yamazaki
# License: Apache 2.0
#-------------------------------------------------------------------------

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import math
import shutil
import copy
from jinja2 import Environment, FileSystemLoader

import ipgen.utils.componentgen
from ipgen.rtl_converter.rtl_converter import RtlConverter

import pyverilog.vparser.ast as vast
import pyverilog.utils.identifiervisitor as iv
import pyverilog.utils.identifierreplace as ir
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator

TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/template/'

# default value
default_ext_burstlength = 256


def log2(v):
    return int(math.ceil(math.log(v, 2)))


class SystemBuilder(object):

    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        self.env.globals['int'] = int
        self.env.globals['log'] = math.log
        self.env.globals['log2'] = log2
        self.env.globals['len'] = len

    def render(self, template_file,
               userlogic_name, ipname,
               masterlist, slavelist,
               def_top_parameters, def_top_localparams,
               def_top_ioports, name_top_ioports,

               ext_addrwidth=32, ext_burstlength=256,
               single_clock=False,
               use_acp=False,
               hdlname=None, common_hdlname=None,
               testname=None,
               ipcore_version=None,
               memimg=None, binfile=False,
               usertestcode=None, simaddrwidth=None,

               mpd_parameters=None, mpd_ports=None,
               tcl_parameters=None, tcl_ports=None,
               clock_hperiod_userlogic=None,
               clock_hperiod_bus=None,

               ignore_protocol_error=False):

        ext_burstlen_width = log2(ext_burstlength)
        template_dict = {
            'userlogic_name': userlogic_name,
            'ipname': ipname,

            'masterlist': masterlist,
            'slavelist': slavelist,

            'def_top_parameters': def_top_parameters,
            'def_top_localparams': def_top_localparams,
            'def_top_ioports': def_top_ioports,
            'name_top_ioports': name_top_ioports,

            'ext_addrwidth': ext_addrwidth,
            'ext_burstlength': ext_burstlength,
            'ext_burstlen_width': ext_burstlen_width,

            'hdlname': hdlname,
            'common_hdlname': common_hdlname,
            'testname': testname,
            'ipcore_version': ipcore_version,
            'memimg': memimg if memimg is not None else 'None',
            'binfile': binfile,
            'usertestcode': '' if usertestcode is None else usertestcode,
            'simaddrwidth': simaddrwidth,

            'mpd_parameters': () if mpd_parameters is None else mpd_parameters,
            'mpd_ports': () if mpd_ports is None else mpd_ports,
            'tcl_parameters': () if tcl_parameters is None else tcl_parameters,
            'tcl_ports': () if tcl_ports is None else tcl_ports,

            'clock_hperiod_userlogic': clock_hperiod_userlogic,
            'clock_hperiod_bus': clock_hperiod_bus,
            'single_clock': single_clock,
            'use_acp': use_acp,

            'ignore_protocol_error': ignore_protocol_error,
        }

        template = self.env.get_template(template_file)
        rslt = template.render(template_dict)
        return rslt

    def build(self, configs, topmodule, ipname, filelist,
              include=None, define=None, memimg=None, usertest=None,
              ignore_protocol_error=False,
              skip_not_found=False, silent=False):

        if (configs['single_clock'] and
                (configs['hperiod_ulogic'] != configs['hperiod_bus'])):
            raise ValueError(
                "All clock periods should be same in single clock mode.")

        # RTL conversion
        converter = RtlConverter(filelist, topmodule,
                                 include=include, define=define)
        userlogic_ast = converter.generate(skip_not_found)

        (masterlist, slavelist) = converter.getResourceDefinitions()
        top_parameters = converter.getTopParameters()
        top_ioports = converter.getTopIOPorts()

        not_found_modules = converter.getNotFoundModules()

        # print target object
        if not silent:
            converter.dumpTargetObject()

        # code generator
        asttocode = ASTCodeGenerator()
        userlogic_code = asttocode.visit(userlogic_ast)

        asttocode = ASTCodeGenerator()

        def_top_parameters = []
        def_top_localparams = []
        def_top_ioports = []
        name_top_ioports = []

        for p in top_parameters.values():
            r = asttocode.visit(p)
            if r.count('localparam'):
                def_top_localparams.append(r)
            else:
                def_top_parameters.append(r.replace(';', ','))

        for pk, (pv, pwidth) in top_ioports.items():
            if configs['if_type'] == 'avalon':
                new_pv = copy.deepcopy(pv)
                new_pv.name = 'coe_' + new_pv.name
                new_pv = vast.Ioport(new_pv, vast.Wire(
                    new_pv.name, new_pv.width, new_pv.signed))
                def_top_ioports.append(asttocode.visit(new_pv))
            else:
                new_pv = vast.Ioport(pv, vast.Wire(
                    pv.name, pv.width, pv.signed))
                def_top_ioports.append(asttocode.visit(new_pv))
            name_top_ioports.append(pk)

        node_template_file = ('node_axi.txt' if configs['if_type'] == 'axi' else
                              'node_avalon.txt' if configs['if_type'] == 'avalon' else
                              'node_general.txt')

        node_code = self.render(node_template_file,
                                topmodule, ipname,
                                masterlist, slavelist,
                                def_top_parameters, def_top_localparams,
                                def_top_ioports, name_top_ioports,
                                ext_addrwidth=configs['ext_addrwidth'],
                                ext_burstlength=default_ext_burstlength,
                                single_clock=configs['single_clock'],
                                use_acp=configs['use_acp'])

        # finalize of code generation
        synthesized_code_list = []
        synthesized_code_list.append(node_code)
        synthesized_code_list.append(userlogic_code)

        common_code_list = []

        if configs['if_type'] == 'axi':
            common_code_list.append(
                open(TEMPLATE_DIR + 'axi_master_interface.v', 'r').read())
            common_code_list.append(
                open(TEMPLATE_DIR + 'axi_lite_master_interface.v', 'r').read())
            common_code_list.append(
                open(TEMPLATE_DIR + 'axi_slave_interface.v', 'r').read())
            common_code_list.append(
                open(TEMPLATE_DIR + 'axi_lite_slave_interface.v', 'r').read())

        if configs['if_type'] == 'avalon':
            common_code_list.append(
                open(TEMPLATE_DIR + 'avalon_master_interface.v', 'r').read())
            common_code_list.append(
                open(TEMPLATE_DIR + 'avalon_lite_master_interface.v', 'r').read())
            common_code_list.append(
                open(TEMPLATE_DIR + 'avalon_slave_interface.v', 'r').read())
            common_code_list.append(
                open(TEMPLATE_DIR + 'avalon_lite_slave_interface.v', 'r').read())

        synthesized_code = '\n'.join(synthesized_code_list)
        common_code = '\n'.join(common_code_list)

        # print settings
        if not silent:
            print("[IP-core Information]")
            print("  IP-core name: %s" % ipname)
            print("  Top-module name: %s" % topmodule)

            print("[Synthesis Option]")
            for k, v in sorted(configs.items(), key=lambda x: x[0]):
                print("  %s: %s" % (str(k), str(v)))

        # write to file
        if configs['if_type'] == 'general':
            self.build_package_general(configs, synthesized_code, common_code,
                                       masterlist, slavelist,
                                       top_parameters, top_ioports,
                                       topmodule, ipname,
                                       memimg, usertest, ignore_protocol_error)

            return

        if configs['if_type'] == 'axi':
            self.build_package_axi(configs, synthesized_code, common_code,
                                   masterlist, slavelist,
                                   top_parameters, top_ioports,
                                   topmodule, ipname,
                                   memimg, usertest, ignore_protocol_error)
            return

        if configs['if_type'] == 'avalon':
            self.build_package_avalon(configs, synthesized_code, common_code,
                                      masterlist, slavelist,
                                      top_parameters, top_ioports,
                                      topmodule, ipname,
                                      memimg, usertest, ignore_protocol_error)
            return

        raise ValueError("Interface type '%s' is not supported." %
                         configs['if_type'])

    def build_package_general(self, configs, synthesized_code, common_code,
                              masterlist, slavelist,
                              top_parameters, top_ioports,
                              topmodule, ipname,
                              memimg, usertest, ignore_protocol_error):

        code = '\n'.join([synthesized_code, common_code])

        f = open(configs['output'], 'w')
        f.write(code)
        f.close()

    def build_package_axi(self, configs, synthesized_code, common_code,
                          masterlist, slavelist,
                          top_parameters, top_ioports,
                          topmodule, ipname,
                          memimg, usertest, ignore_protocol_error):

        code = '\n'.join([synthesized_code, common_code])

        # write to files
        def_top_parameters = []
        def_top_localparams = []
        def_top_ioports = []
        name_top_ioports = []

        mpd_parameters = []
        mpd_ports = []
        ext_params = []
        ext_ports = []

        asttocode = ASTCodeGenerator()

        for pk, pv in top_parameters.items():
            r = asttocode.visit(pv)
            def_top_parameters.append(r)
            if r.count('localparam'):
                def_top_localparams.append(r)
                continue
            _name = pv.name
            _value = asttocode.visit(pv.value)
            _dt = 'string' if r.count('"') else 'integer'
            mpd_parameters.append((_name, _value, _dt))

        for pk, (pv, pwidth) in top_ioports.items():
            name_top_ioports.append(pk)
            new_pv = vast.Wire(pv.name, pv.width, pv.signed)
            def_top_ioports.append(asttocode.visit(new_pv))
            _name = pv.name
            _dir = ('I' if isinstance(pv, vast.Input) else
                    'O' if isinstance(pv, vast.Output) else
                    'IO')
            _vec = '' if pv.width is None else asttocode.visit(pv.width)
            mpd_ports.append((_name, _dir, _vec))

        for pk, (pv, pwidth) in top_ioports.items():
            new_pv = vast.Wire(pv.name, pv.width, pv.signed)
            _name = pv.name
            _dir = ('in' if isinstance(pv, vast.Input) else
                    'out' if isinstance(pv, vast.Output) else
                    'inout')
            _vec = None if pv.width is None else pwidth - 1
            _ids = None if pv.width is None else iv.getIdentifiers(
                pv.width.msb)
            _d = {}
            if _ids is not None:
                for i in _ids:
                    _d[i] = "(spirit:decode(id('MODELPARAM_VALUE." + i + "')))"
            _msb = (None if _ids is None else
                    asttocode.visit(ir.replaceIdentifiers(pv.width.msb, _d)))
            ext_ports.append((_name, _dir, _vec, _msb))

        for pk, pv in top_parameters.items():
            r = asttocode.visit(pv)
            if r.count('localparam'):
                def_top_localparams.append(r)
                continue
            _name = pv.name
            _value = asttocode.visit(pv.value)
            _dt = 'string' if r.count('"') else 'integer'
            ext_params.append((_name, _value, _dt))

        # names
        ipcore_version = '_v1_00_a'
        mpd_version = '_v2_1_0'

        dirname = ipname + ipcore_version + '/'

        # pcore
        mpdname = ipname + mpd_version + '.mpd'
        #muiname = ipname + mpd_version + '.mui'
        paoname = ipname + mpd_version + '.pao'
        tclname = ipname + mpd_version + '.tcl'

        # IP-XACT
        xmlname = 'component.xml'
        xdcname = ipname + '.xdc'
        bdname = 'bd.tcl'
        xguiname = 'xgui.tcl'

        # source
        hdlname = ipname + '.v'
        testname = 'test_' + ipname + '.v'
        memname = 'mem.img'
        makefilename = 'Makefile'
        copied_memimg = memname if memimg is not None else None
        binfile = (True if memimg is not None and memimg.endswith('.bin')
                   else False)

        # pcore
        mpdpath = dirname + 'data/'
        #muipath = dirname + 'data/'
        paopath = dirname + 'data/'
        tclpath = dirname + 'data/'

        # IP-XACT
        xmlpath = dirname
        xdcpath = dirname + 'data/'
        bdpath = dirname + 'bd/'
        xguipath = dirname + 'xgui/'

        # source
        hdlpath = dirname + 'hdl/'
        verilogpath = dirname + 'hdl/verilog/'
        testpath = dirname + 'test/'
        makefilepath = dirname + 'test/'

        if not os.path.exists(dirname):
            os.mkdir(dirname)
        if not os.path.exists(dirname + '/' + 'data'):
            os.mkdir(dirname + '/' + 'data')
        if not os.path.exists(dirname + '/' + 'doc'):
            os.mkdir(dirname + '/' + 'doc')
        if not os.path.exists(dirname + '/' + 'bd'):
            os.mkdir(dirname + '/' + 'bd')
        if not os.path.exists(dirname + '/' + 'xgui'):
            os.mkdir(dirname + '/' + 'xgui')
        if not os.path.exists(dirname + '/' + 'hdl'):
            os.mkdir(dirname + '/' + 'hdl')
        if not os.path.exists(dirname + '/' + 'hdl/verilog'):
            os.mkdir(dirname + '/' + 'hdl/verilog')
        if not os.path.exists(dirname + '/' + 'test'):
            os.mkdir(dirname + '/' + 'test')

        # mpd file
        mpd_template_file = 'mpd.txt'
        mpd_code = self.render(mpd_template_file,
                               topmodule, ipname,
                               masterlist, slavelist,
                               def_top_parameters, def_top_localparams,
                               def_top_ioports, name_top_ioports,

                               ext_addrwidth=configs['ext_addrwidth'],
                               ext_burstlength=default_ext_burstlength,
                               single_clock=configs['single_clock'],
                               hdlname=hdlname,
                               ipcore_version=ipcore_version,
                               mpd_ports=mpd_ports,
                               mpd_parameters=mpd_parameters)

        f = open(mpdpath + mpdname, 'w')
        f.write(mpd_code)
        f.close()

        # mui file
        #mui_template_file = 'mui.txt'
        # mui_code = self.render(mui_template_file,
        #                       topmodule, ipname,
        #                       masterlist, slavelist,
        #                       def_top_parameters, def_top_localparams,
        #                       def_top_ioports, name_top_ioports,
        #
        #                       ext_addrwidth=configs['ext_addrwidth'],
        #                       ext_burstlength=default_ext_burstlength,
        #                       single_clock=configs['single_clock'],
        #                       hdlname=hdlname,
        #                       ipcore_version=ipcore_version,
        #                       mpd_ports=mpd_ports,
        #                       mpd_parameters=mpd_parameters)
        #
        #f = open(muipath+muiname, 'w')
        # f.write(mui_code)
        # f.close()

        # pao file
        pao_template_file = 'pao.txt'
        pao_code = self.render(pao_template_file,
                               topmodule, ipname,
                               masterlist, slavelist,
                               def_top_parameters, def_top_localparams,
                               def_top_ioports, name_top_ioports,

                               ext_addrwidth=configs['ext_addrwidth'],
                               ext_burstlength=default_ext_burstlength,
                               single_clock=configs['single_clock'],
                               hdlname=hdlname,
                               ipcore_version=ipcore_version,
                               mpd_ports=mpd_ports,
                               mpd_parameters=mpd_parameters)

        f = open(paopath + paoname, 'w')
        f.write(pao_code)
        f.close()

        # tcl file
        tcl_code = ''
        if not configs['single_clock']:
            tcl_code = open(TEMPLATE_DIR + 'pcore_tcl.tcl', 'r').read()

        f = open(tclpath + tclname, 'w')
        f.write(tcl_code)
        f.close()

        memorylist = []
        for m in masterlist:
            memorylist.append(
                ipgen.utils.componentgen.AxiDefinition(
                    m.name + '_AXI', m.datawidth, True, m.lite))

        for s in slavelist:
            memorylist.append(
                ipgen.utils.componentgen.AxiDefinition(
                    s.name + '_AXI', s.datawidth, False, s.lite))

        # component.xml
        gen = ipgen.utils.componentgen.ComponentGen()
        xml_code = gen.generate(ipname,
                                memorylist,
                                ext_addrwidth=configs['ext_addrwidth'],
                                ext_burstlength=default_ext_burstlength,
                                ext_ports=ext_ports,
                                ext_params=ext_params)

        f = open(xmlpath + xmlname, 'w')
        f.write(xml_code)
        f.close()

        # xdc
        xdc_code = ''
        if not configs['single_clock']:
            xdc_code = open(TEMPLATE_DIR + 'ipxact.xdc', 'r').read()

        f = open(xdcpath + xdcname, 'w')
        f.write(xdc_code)
        f.close()

        # bd
        bd_code = ''
        bd_code = open(TEMPLATE_DIR + 'bd.tcl', 'r').read()

        f = open(bdpath + bdname, 'w')
        f.write(bd_code)
        f.close()

        # xgui file
        xgui_template_file = 'xgui_tcl.txt'
        xgui_code = self.render(xgui_template_file,
                                topmodule, ipname,
                                masterlist, slavelist,
                                def_top_parameters, def_top_localparams,
                                def_top_ioports, name_top_ioports,

                                ext_addrwidth=configs['ext_addrwidth'],
                                ext_burstlength=default_ext_burstlength,
                                single_clock=configs['single_clock'],
                                hdlname=hdlname,
                                ipcore_version=ipcore_version,
                                mpd_ports=mpd_ports,
                                mpd_parameters=mpd_parameters)

        f = open(xguipath + xguiname, 'w')
        f.write(xgui_code)
        f.close()

        # hdl file
        f = open(verilogpath + hdlname, 'w')
        f.write(code)
        f.close()

        # user test code
        usertestcode = None
        if usertest is not None:
            usertestcode = open(usertest, 'r').read()

        # test file
        test_template_file = 'test_ipgen_axi.txt'
        test_code = self.render(test_template_file,
                                topmodule, ipname,
                                masterlist, slavelist,
                                def_top_parameters, def_top_localparams,
                                def_top_ioports, name_top_ioports,

                                ext_addrwidth=configs['ext_addrwidth'],
                                ext_burstlength=default_ext_burstlength,
                                single_clock=configs['single_clock'],
                                use_acp=configs['use_acp'],

                                hdlname=hdlname,
                                memimg=copied_memimg,
                                binfile=binfile,
                                usertestcode=usertestcode,
                                simaddrwidth=configs['sim_addrwidth'],
                                clock_hperiod_userlogic=configs['hperiod_ulogic'],
                                clock_hperiod_bus=configs['hperiod_bus'],
                                ignore_protocol_error=ignore_protocol_error)

        f = open(testpath + testname, 'w')
        f.write(test_code)
        f.write(open(TEMPLATE_DIR + 'axi_master_fifo.v', 'r').read())
        f.close()

        # memory image for test
        if memimg is not None:
            shutil.copyfile(os.path.expanduser(memimg), testpath + memname)

        # makefile file
        makefile_template_file = 'Makefile.txt'
        makefile_code = self.render(makefile_template_file,
                                    topmodule, ipname,
                                    masterlist, slavelist,
                                    def_top_parameters, def_top_localparams,
                                    def_top_ioports, name_top_ioports,
                                    ext_addrwidth=configs['ext_addrwidth'],
                                    ext_burstlength=default_ext_burstlength,
                                    single_clock=configs['single_clock'],
                                    testname=testname)

        f = open(makefilepath + makefilename, 'w')
        f.write(makefile_code)
        f.close()

    def build_package_avalon(self, configs, synthesized_code, common_code,
                             masterlist, slavelist,
                             top_parameters, top_ioports,
                             topmodule, ipname,
                             memimg, usertest, ignore_protocol_error):

        # write to files, with AXI interface
        def_top_parameters = []
        def_top_localparams = []
        def_top_ioports = []
        name_top_ioports = []
        tcl_parameters = []
        tcl_ports = []

        asttocode = ASTCodeGenerator()

        for pk, pv in top_parameters.items():
            r = asttocode.visit(pv)
            def_top_parameters.append(r)
            if r.count('localparam'):
                def_top_localparams.append(r)
                continue
            _name = pv.name
            _value = asttocode.visit(pv.value)
            _dt = ('STRING' if r.count('"') else
                   'INTEGER' if r.count('integer') else
                   'STD_LOGIC_VECTOR')
            tcl_parameters.append((_name, _value, _dt))

        for pk, (pv, pwidth) in top_ioports.items():
            name_top_ioports.append(pk)
            new_pv = vast.Wire(pv.name, pv.width, pv.signed)
            def_top_ioports.append(asttocode.visit(new_pv))
            _name = pv.name
            _dir = ('Input' if isinstance(pv, vast.Input) else
                    'Output' if isinstance(pv, vast.Output) else
                    'Inout')
            _vec = str(pwidth)
            tcl_ports.append((_name, _dir, _vec))

        # names
        ipcore_version = '_v1_00_a'

        dirname = ipname + ipcore_version + '/'

        tclname = ipname + '.tcl'

        hdlname = ipname + '.v'
        common_hdlname = 'ipgen_common.v'
        testname = 'test_' + ipname + '.v'
        memname = 'mem.img'
        makefilename = 'Makefile'
        copied_memimg = memname if memimg is not None else None
        binfile = (True if memimg is not None and memimg.endswith('.bin')
                   else False)

        hdlpath = dirname + 'hdl/'
        verilogpath = dirname + 'hdl/verilog/'
        tclpath = dirname + 'hdl/verilog/'
        testpath = dirname + 'test/'
        makefilepath = dirname + 'test/'

        if not os.path.exists(dirname):
            os.mkdir(dirname)
        if not os.path.exists(dirname + '/' + 'hdl'):
            os.mkdir(dirname + '/' + 'hdl')
        if not os.path.exists(dirname + '/' + 'hdl/verilog'):
            os.mkdir(dirname + '/' + 'hdl/verilog')
        if not os.path.exists(dirname + '/' + 'test'):
            os.mkdir(dirname + '/' + 'test')

        # tcl file
        tcl_template_file = 'qsys_tcl.txt'
        tcl_code = self.render(tcl_template_file,
                               topmodule, ipname,
                               masterlist, slavelist,
                               def_top_parameters, def_top_localparams,
                               def_top_ioports, name_top_ioports,
                               ext_addrwidth=configs['ext_addrwidth'],
                               ext_burstlength=default_ext_burstlength,
                               single_clock=configs['single_clock'],
                               hdlname=hdlname,
                               common_hdlname=common_hdlname,
                               tcl_ports=tcl_ports,
                               tcl_parameters=tcl_parameters)

        f = open(tclpath + tclname, 'w')
        f.write(tcl_code)
        f.close()

        # hdl file
        f = open(verilogpath + hdlname, 'w')
        f.write(synthesized_code)
        f.close()

        # common hdl file
        f = open(verilogpath + common_hdlname, 'w')
        f.write(common_code)
        f.close()

        # user test code
        usertestcode = None
        if usertest is not None:
            usertestcode = open(usertest, 'r').read()

        # test file
        test_template_file = 'test_ipgen_avalon.txt'
        test_code = self.render(test_template_file,
                                topmodule, ipname,
                                masterlist, slavelist,
                                def_top_parameters, def_top_localparams,
                                def_top_ioports, name_top_ioports,
                                ext_addrwidth=configs['ext_addrwidth'],
                                ext_burstlength=default_ext_burstlength,
                                single_clock=configs['single_clock'],
                                hdlname=hdlname,
                                common_hdlname=common_hdlname,
                                memimg=copied_memimg,
                                binfile=binfile,
                                usertestcode=usertestcode,
                                simaddrwidth=configs['sim_addrwidth'],
                                clock_hperiod_userlogic=configs['hperiod_ulogic'],
                                clock_hperiod_bus=configs['hperiod_bus'],
                                ignore_protocol_error=ignore_protocol_error)

        f = open(testpath + testname, 'w')
        f.write(test_code)
        f.write(open(TEMPLATE_DIR + 'avalon_master_fifo.v', 'r').read())
        f.close()

        # memory image for test
        if memimg is not None:
            shutil.copy(memimg, testpath + memname)

        # makefile file
        makefile_template_file = 'Makefile.txt'
        makefile_code = self.render(makefile_template_file,
                                    topmodule, ipname,
                                    masterlist, slavelist,
                                    def_top_parameters, def_top_localparams,
                                    def_top_ioports, name_top_ioports,
                                    ext_addrwidth=configs['ext_addrwidth'],
                                    ext_burstlength=default_ext_burstlength,
                                    single_clock=configs['single_clock'],
                                    testname=testname)

        f = open(makefilepath + makefilename, 'w')
        f.write(makefile_code)
        f.close()
