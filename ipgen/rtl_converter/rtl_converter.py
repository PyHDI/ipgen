#-------------------------------------------------------------------------
# rtl_converter.py
#
# RTL Converter with Pyverilog
#
# Copyright (C) 2013, Shinya Takamaeda-Yamazaki
# License: Apache 2.0
#-------------------------------------------------------------------------
from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import collections

from ipgen.rtl_converter.convertvisitor import InstanceConvertVisitor
from ipgen.rtl_converter.convertvisitor import InstanceReplaceVisitor
from ipgen.rtl_converter.interfaces import *

import pyverilog.vparser.ast as vast
import pyverilog.utils.signaltype as signaltype
from pyverilog.vparser.parser import VerilogCodeParser
from pyverilog.dataflow.modulevisitor import ModuleVisitor
from pyverilog.utils.scope import ScopeLabel, ScopeChain

TEMPLATE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))) + '/template/'
TEMPLATE_FILE = TEMPLATE_DIR + 'ipgen.v'


class RtlConverter(object):

    def __init__(self, filelist, topmodule='userlogic', include=None, define=None):
        self.filelist = filelist
        self.topmodule = topmodule
        self.include = include
        self.define = define
        self.template_file = TEMPLATE_FILE

        self.top_parameters = collections.OrderedDict()
        self.top_ioports = collections.OrderedDict()
        self.target_object = collections.OrderedDict()
        self.not_found_modules = []

    def getTopParameters(self):
        return self.top_parameters

    def getTopIOPorts(self):
        return self.top_ioports

    def getTargetObject(self):
        return self.target_object

    def getNotFoundModules(self):
        return self.not_found_modules

    def getResourceDefinitions(self):
        target_objects = self.getTargetObject()
        master_memory = []
        slave_memory = []

        for mode, target_items in target_objects.items():
            if mode == 'ipgen_master_memory':
                rslt = self.getMasterMemory(target_items)
                master_memory.extend(rslt)
            if mode == 'ipgen_slave_memory':
                rslt = self.getSlaveMemory(target_items)
                slave_memory.extend(rslt)
            if mode == 'ipgen_master_lite_memory':
                rslt = self.getMasterMemory(target_items, lite=True)
                master_memory.extend(rslt)
            if mode == 'ipgen_slave_lite_memory':
                rslt = self.getSlaveMemory(target_items, lite=True)
                slave_memory.extend(rslt)

        return tuple(master_memory), tuple(slave_memory)

    def getMasterMemory(self, target_items, lite=False):
        objs = []

        for name, values in target_items:
            idx = values['ID']
            addrwidth = values['ADDR_WIDTH']
            datawidth = values['DATA_WIDTH']
            objs.append(MasterMemory(name, idx, addrwidth, datawidth, lite))

        return objs

    def getSlaveMemory(self, target_items, lite=False):
        objs = []

        for name, values in target_items:
            idx = values['ID']
            addrwidth = values['ADDR_WIDTH']
            datawidth = values['DATA_WIDTH']
            objs.append(SlaveMemory(name, idx, addrwidth, datawidth, lite))

        return objs

    def dumpTargetObject(self):
        target_object = self.getTargetObject()
        print("[Bus Interfaces]")
        for mode, target_items in target_object.items():
            for name, values in target_items:
                printstr = []
                printstr.append("  ")
                printstr.append(name)
                printstr.append(': ')
                for valname, value in sorted(values.items(), key=lambda x: x[0]):
                    printstr.append('%s:%s ' % (valname, str(value)))
                print(''.join(printstr))

        if self.not_found_modules:
            print("[Not Found Module]")
            for nfound in self.not_found_modules:
                printstr = []
                printstr.append("  ")
                printstr.append(nfound)
                print(''.join(printstr))

    def dumpResourceDefinitions(self):
        master_list, slave_list = self.getResourceDefinitions()

        if master_list:
            print("MasterMemory")
        for value in sorted(master_list, key=lambda x: x.name):
            key = value.name
            print(" %s: %s" % (key, value))

        if slave_list:
            print("SlaveMemory")
        for value in sorted(slave_list, key=lambda x: x.name):
            key = value.name
            print(" %s: %s" % (key, value))

    def generate(self, skip_not_found=False):
        code_parser = VerilogCodeParser(self.filelist,
                                        preprocess_include=self.include,
                                        preprocess_define=self.define)
        ast = code_parser.parse()

        module_visitor = ModuleVisitor()
        module_visitor.visit(ast)
        modulenames = module_visitor.get_modulenames()
        moduleinfotable = module_visitor.get_moduleinfotable()

        template_parser = VerilogCodeParser((self.template_file,))
        template_ast = template_parser.parse()
        template_visitor = ModuleVisitor()
        template_visitor.visit(template_ast)
        templateinfotable = template_visitor.get_moduleinfotable()

        instanceconvert_visitor = InstanceConvertVisitor(
            moduleinfotable, self.topmodule, templateinfotable, skip_not_found=skip_not_found)
        instanceconvert_visitor.start_visit()

        replaced_instance = instanceconvert_visitor.getMergedReplacedInstance()
        replaced_instports = instanceconvert_visitor.getReplacedInstPorts()
        replaced_items = instanceconvert_visitor.getReplacedItems()

        new_moduleinfotable = instanceconvert_visitor.get_new_moduleinfotable()
        instancereplace_visitor = InstanceReplaceVisitor(replaced_instance,
                                                         replaced_instports,
                                                         replaced_items,
                                                         new_moduleinfotable)
        ret = instancereplace_visitor.getAST()

        # gather user-defined io-ports on top-module and parameters to connect
        # external
        frametable = instanceconvert_visitor.getFrameTable()
        top_ioports = []
        for i in moduleinfotable.getIOPorts(self.topmodule):
            if signaltype.isClock(i) or signaltype.isReset(i):
                continue
            top_ioports.append(i)

        top_scope = ScopeChain([ScopeLabel(self.topmodule, 'module')])
        top_sigs = frametable.getSignals(top_scope)
        top_params = frametable.getConsts(top_scope)

        for sk, sv in top_sigs.items():
            if len(sk) > 2:
                continue
            signame = sk[1].scopename
            for svv in sv:
                if (signame in top_ioports and
                    not (signaltype.isClock(signame) or signaltype.isReset(signame)) and
                        isinstance(svv, vast.Input) or isinstance(svv, vast.Output) or isinstance(svv, vast.Inout)):
                    port = svv
                    if port.width is not None:
                        msb_val = instanceconvert_visitor.optimize(
                            instanceconvert_visitor.getTree(port.width.msb, top_scope))
                        lsb_val = instanceconvert_visitor.optimize(
                            instanceconvert_visitor.getTree(port.width.lsb, top_scope))
                        width = int(msb_val.value) - int(lsb_val.value) + 1
                    else:
                        width = None
                    self.top_ioports[signame] = (port, width)
                    break

        for ck, cv in top_params.items():
            if len(ck) > 2:
                continue
            signame = ck[1].scopename
            param = cv[0]
            if isinstance(param, vast.Genvar):
                continue
            self.top_parameters[signame] = param

        self.target_object = instanceconvert_visitor.getTargetObject()
        self.not_found_modules = instanceconvert_visitor.getNotFoundModules()

        return ret
