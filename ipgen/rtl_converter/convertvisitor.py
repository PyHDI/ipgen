#-------------------------------------------------------------------------------
# convertvisitor.py
# 
# Verilog AST convert visitor with Pyverilog
#
# Copyright (C) 2013, Shinya Takamaeda-Yamazaki
# License: Apache 2.0
#-------------------------------------------------------------------------------
from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import re
import copy

from pyverilog.vparser.ast import *
from pyverilog.dataflow.visit import *
from pyverilog.dataflow.signalvisitor import SignalVisitor

#-------------------------------------------------------------------------------
# TARGET SETTING BEGIN
#-------------------------------------------------------------------------------
TARGET_PREFIX = 'ipgen_'
TARGET_NAMES = ('NAME', 'ID',) # instance_name if this_value is None else param_dict[this_value]
TARGET_PARAMS = { # param_name : default_value
    'NAME' : "undefined",
    'ID' : 0,
    'ADDR_WIDTH' : 32, 
    'DATA_WIDTH' : 32,
}

TARGET_TABLE = { # module_type : (port_name, port_width)
    "ipgen_master_memory" : (('ext_awvalid', 'output', IntConst('1')),
                             ('ext_awaddr', 'output', Identifier('ADDR_WIDTH')),
                             ('ext_awlen', 'output', IntConst('8')),
                             ('ext_awready', 'input', IntConst('1')),
                               
                             ('ext_wdata', 'output', Identifier('DATA_WIDTH')),
                             ('ext_wstrb', 'output', Divide(Identifier('DATA_WIDTH'), IntConst('8'))),
                             ('ext_wlast', 'output', IntConst('1')),
                             ('ext_wvalid', 'output', IntConst('1')),
                             ('ext_wready', 'input', IntConst('1')),
                               
                             ('ext_arvalid', 'output', IntConst('1')),
                             ('ext_araddr', 'output', Identifier('ADDR_WIDTH')),
                             ('ext_arlen', 'output', IntConst('8')),
                             ('ext_arready', 'input', IntConst('1')),

                             ('ext_rdata', 'input', Identifier('DATA_WIDTH')),
                             ('ext_rlast', 'input', IntConst('1')),
                             ('ext_rvalid', 'input', IntConst('1')),
                             ('ext_rready', 'output', IntConst('1')),),
    
    "ipgen_slave_memory" : (('ext_awvalid', 'input', IntConst('1')),
                            ('ext_awaddr', 'input', Identifier('ADDR_WIDTH')),
                            ('ext_awlen', 'input', IntConst('8')),
                            ('ext_awready', 'output', IntConst('1')),
                              
                            ('ext_wdata', 'input', Identifier('DATA_WIDTH')),
                            ('ext_wstrb', 'input', Divide(Identifier('DATA_WIDTH'), IntConst('8'))),
                            ('ext_wlast', 'input', IntConst('1')),
                            ('ext_wvalid', 'input', IntConst('1')),
                            ('ext_wready', 'output', IntConst('1')),
                              
                            ('ext_arvalid', 'input', IntConst('1')),
                            ('ext_araddr', 'input', Identifier('ADDR_WIDTH')),
                            ('ext_arlen', 'input', IntConst('8')),
                            ('ext_arready', 'output', IntConst('1')),

                            ('ext_rdata', 'output', Identifier('DATA_WIDTH')),
                            ('ext_rlast', 'output', IntConst('1')),
                            ('ext_rvalid', 'output', IntConst('1')),
                            ('ext_rready', 'input', IntConst('1')),),

    "ipgen_master_lite_memory" : (('ext_awvalid', 'output', IntConst('1')),
                                  ('ext_awaddr', 'output', Identifier('ADDR_WIDTH')),
                                  ('ext_awready', 'input', IntConst('1')),
                                  
                                  ('ext_wdata', 'output', Identifier('DATA_WIDTH')),
                                  ('ext_wstrb', 'output', Divide(Identifier('DATA_WIDTH'), IntConst('8'))),
                                  ('ext_wvalid', 'output', IntConst('1')),
                                  ('ext_wready', 'input', IntConst('1')),
                                  
                                  ('ext_arvalid', 'output', IntConst('1')),
                                  ('ext_araddr', 'output', Identifier('ADDR_WIDTH')),
                                  ('ext_arready', 'input', IntConst('1')),
                                  
                                  ('ext_rdata', 'input', Identifier('DATA_WIDTH')),
                                  ('ext_rvalid', 'input', IntConst('1')),
                                  ('ext_rready', 'output', IntConst('1')),),
    
    "ipgen_slave_lite_memory" : (('ext_awvalid', 'input', IntConst('1')),
                                 ('ext_awaddr', 'input', Identifier('ADDR_WIDTH')),
                                 ('ext_awready', 'output', IntConst('1')),
                                 
                                 ('ext_wdata', 'input', Identifier('DATA_WIDTH')),
                                 ('ext_wstrb', 'input', Divide(Identifier('DATA_WIDTH'), IntConst('8'))),
                                 ('ext_wvalid', 'input', IntConst('1')),
                                 ('ext_wready', 'output', IntConst('1')),
                                 
                                 ('ext_arvalid', 'input', IntConst('1')),
                                 ('ext_araddr', 'input', Identifier('ADDR_WIDTH')),
                                 ('ext_arready', 'output', IntConst('1')),
                                 
                                 ('ext_rdata', 'output', Identifier('DATA_WIDTH')),
                                 ('ext_rvalid', 'output', IntConst('1')),
                                 ('ext_rready', 'input', IntConst('1')),),
}

#-------------------------------------------------------------------------------
# TARGET SETTING END
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Base class of Replace Visitor
#-------------------------------------------------------------------------------
def ischild(node, attr):
    if not isinstance(node, Node): return False
    excludes = ('coord', 'attr_names',)
    if attr.startswith('__'): return False
    if attr in excludes: return False
    attr_names = getattr(node, 'attr_names')
    if attr in attr_names: return False
    attr_test = getattr(node, attr)
    if hasattr(attr_test, '__call__'): return False
    return True

def children_items(node):
    children = [ attr for attr in dir(node) if ischild(node, attr) ]
    ret = []
    for c in children:
        ret.append( (c, getattr(node, c)) )
    return ret

class ReplaceVisitor(NodeVisitor):
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        ret = visitor(node)
        if ret is None: return node
        return ret

    def generic_visit(self, node):
        for name, child in children_items(node):
            ret = None
            if child is None: continue
            if (isinstance(child, list) or isinstance(child, tuple)):
                r = []
                for c in child:
                    r.append( self.visit(c) )
                ret = tuple(r)
            else:
                ret = self.visit(child)
            setattr(node, name, ret)
        return node

#-------------------------------------------------------------------------------
class IdentifierReplaceVisitor(ReplaceVisitor):
    def __init__(self, replace_dict):
        self.replace_dict = replace_dict

    def visit_Identifier(self, node):
        if node.name in TARGET_PARAMS:
            return copy.deepcopy(self.replace_dict[node.name])
        return node

#-------------------------------------------------------------------------------
class InstanceConvertVisitor(SignalVisitor):
    def __init__(self, moduleinfotable, top, templateinfotable,
                 skip_not_found=False):
        SignalVisitor.__init__(self, moduleinfotable, top)
        self.new_moduleinfotable = ModuleInfoTable()
        self.templateinfotable = templateinfotable
        self.target_object = {} # key:kind, value:list of object
        self.used_name_count = {}

        self.rename_prefix = '_r'
        self.rename_prefix_count = 0
        self.used = set([])

        self.replaced_instance = {}
        self.replaced_instports = {}
        self.replaced_items = {}
        self.merged_replaced_instance = {} # replaced target used in next stage

        self.additionalport = [] # temporal variable

        self.skip_not_found = skip_not_found
        self.not_found_modules = []

    #----------------------------------------------------------------------------
    def get_new_moduleinfotable(self):
        return self.new_moduleinfotable

    def getModuleDefinition(self, name):
        return self.new_moduleinfotable.dict[name].definition

    #----------------------------------------------------------------------------
    def getMergedReplacedInstance(self):
        self.mergeInstancelist()
        return self.merged_replaced_instance

    def getReplacedInstPorts(self):
        return self.replaced_instports

    def getReplacedItems(self):
        return self.replaced_items

    #----------------------------------------------------------------------------
    def getTargetObject(self):
        return self.target_object

    #----------------------------------------------------------------------------
    def getNotFoundModules(self):
        return self.not_found_modules

    #----------------------------------------------------------------------------
    def getRenamedTargetName(self, name):
        if name not in self.used_name_count:
            self.used_name_count[name] = 1
            return name
        ret = name + '_' + str(self.used_name_count[name])
        while ret in self.used_name_count:
            self.used_name_count[name] += 1
            ret = name + '_' + str(self.used_name_count[name])
        self.used_name_count[ret] = 1
        return ret

    #----------------------------------------------------------------------------
    def copyModuleInfo(self, src, dst):
        if src not in self.moduleinfotable.dict:
            if self.skip_not_found: return
            raise ValueError("No such module '%s'" % src)
        
        if dst not in self.new_moduleinfotable.dict:
            if src == dst:
                self.new_moduleinfotable.dict[dst] = self.moduleinfotable.dict[src]
            else:
                self.new_moduleinfotable.dict[dst] = copy.deepcopy(self.moduleinfotable.dict[src])
                self.new_moduleinfotable.dict[dst].definition.name = dst
        if (src != dst) and (dst not in self.moduleinfotable.dict):
            self.moduleinfotable.dict[dst] = self.moduleinfotable.dict[src]
            self.moduleinfotable.dict[dst].definition.name = dst

    #----------------------------------------------------------------------------
    def changeModuleName(self, dst, name):
        self.moduleinfotable.dict[dst].definition.name = name

    #----------------------------------------------------------------------------
    def isUsed(self, name):
        return (name in self.used)

    def setUsed(self, name):
        if name not in self.used: self.used.add(name)

    def rename(self, name):
        ret = name + self.rename_prefix + str(self.rename_prefix_count)
        self.rename_prefix_count += 1
        return ret

    #----------------------------------------------------------------------------
    def appendInstance(self, key, value):
        actualkey = id(key)
        if actualkey not in self.replaced_instance:
            self.replaced_instance[actualkey] = []
        self.replaced_instance[actualkey].append(value)

    def mergeInstancelist(self):
        for key, insts in self.replaced_instance.items():
            head = self.mergeInstances(key, insts)
            self.merged_replaced_instance[key] = head

    def mergeInstances(self, key, insts):
        head = None
        tail = None
        for inst in insts:
            if head is None: 
                head = inst
                tail = inst
            else:
                tail.false_statement = inst
                tail = tail.false_statement
        return head

    #----------------------------------------------------------------------------    
    def extendInstPorts(self, key, value):
        actualkey = id(key)
        if actualkey not in self.replaced_instports:
            self.replaced_instports[actualkey] = []
        self.replaced_instports[actualkey].extend(value)

    #----------------------------------------------------------------------------
    def extendItems(self, key, value):
        actualkey = id(key)
        if actualkey not in self.replaced_items:
            self.replaced_items[actualkey] = []
        self.replaced_items[actualkey].extend(value)

    #----------------------------------------------------------------------------
    def updateInstancePort(self, node, generate=False):
        new_node = copy.deepcopy(node)
        instance = new_node.instances[0]
        
        ioport = not (len(instance.portlist) == 0 or 
                      instance.portlist[0].portname is None)
        new_portlist = list(instance.portlist)
        if ioport:
            for i, a in enumerate(self.additionalport):
                new_portlist.append(PortArg(copy.deepcopy(a.name),
                                            Identifier(copy.deepcopy(a.name))))
        else:
            for a in self.additionalport:
                new_portlist.append(PortArg(None, Identifier(copy.deepcopy(a.name))))
        instance.portlist = tuple(new_portlist)

        if generate:
            blockstatement = []
            blockstatement.append(new_node)
            block = Block( tuple(blockstatement) )

            genconds = self.frames.getGenerateConditions()
            condlist = []
            for iter, val in genconds:
                if iter is None: # generate if
                    #condlist.append( val )
                    pass
                else: # generate for
                    name = iter[-1].scopename
                    condlist.append( Eq(Identifier(name), IntConst(str(val))) )

            cond = None
            for c in condlist:
                if cond is None:
                    cond = c
                else:
                    cond = Land(cond, c)

            if cond is None:
                cond = IntConst('1')

            ret = IfStatement(cond, block, None)
            self.appendInstance(node, ret)
        else:
            ret = new_node
            self.appendInstance(node, ret)

        module = self.getModuleDefinition(node.module)
        self.updateModulePort(module)

    #---------------------------------------------------------------------------- 
    def updateModulePort(self, node):
        new_portlist = list(node.portlist.ports)
        ioport = not (len(node.portlist.ports) == 0 or 
                      isinstance(node.portlist.ports[0], Port))
        if ioport:
            for a in self.additionalport:
                new_portlist.append(Ioport(copy.deepcopy(a)))
        else:
            for a in self.additionalport:
                new_portlist.append(Port(a.name, width=a.width, type=None))
        self.extendInstPorts(node, new_portlist)
        if not ioport:
            new_items = copy.deepcopy(self.additionalport)
            new_items.extend(list(node.items))
            self.extendItems(node, new_items)

    #----------------------------------------------------------------------------
    def convertTargetInstance(self, node, mode, generate=False, opt=None):
        current = self.frames.getCurrent()
        paramnames = self.moduleinfotable.getParamNames(node.module)
        param_dict = {}
        param_opt_dict = {}

        for param_i, param in enumerate(node.parameterlist):
            paramname = paramnames[param_i] if param.paramname is None else param.paramname 
            if paramname in TARGET_PARAMS:
                param_dict[paramname] = copy.deepcopy(param.argname)
                param_opt_dict[paramname] = self.optimize(self.getTree(param.argname, current)).value

        for name, defvalue in TARGET_PARAMS.items():
            if name not in param_dict:
                param_dict[name] = StringConst(defvalue) if isinstance(defvalue, str) else IntConst(str(defvalue))
            if name not in param_opt_dict:
                param_opt_dict[name] = defvalue

        nameprefix = None
        if TARGET_NAMES:
            modeprefix = 'none'
            m = re.match( '^(.*)([0-9]+P)$', mode)
            if m:
                modeprefix = m.group(1)
            else:
                modeprefix = mode
                
            nameprefix = ''.join([ modeprefix.lower(), '_' ] + [ str(param_opt_dict[i]) + '_' for i in TARGET_NAMES ])[:-1]
        else:
            nameprefix = self.getRenamedTargetName(node.name)

        self.addTargetObject(mode, nameprefix, param_opt_dict)

        new_node = copy.deepcopy(node)
        instance = new_node.instances[0]
        
        noportname = (len(instance.portlist) == 0 or
                      instance.portlist[0].portname is None)
        new_portlist = list(instance.portlist)
        idreplace = IdentifierReplaceVisitor(param_dict)

        for (name, direction, msb) in TARGET_TABLE[mode]:
            width_tree = Minus(idreplace.visit(msb), IntConst('1'))
            width_value = self.optimize(self.getTree(width_tree, current)).value
            width = Width(IntConst(str(width_value)), IntConst('0'))
            dirtype = Input if direction == 'input' else Output if direction == 'output' else Inout
            portarg_name = None if noportname else name
            new_portlist.append( PortArg(portarg_name, Identifier(nameprefix+'_'+name)) )
            self.additionalport.append( dirtype(name=nameprefix+'_'+name, width=width) )

        instance.portlist = tuple(new_portlist)

        if generate:
            blockstatement = []
            blockstatement.append(new_node)
            block = Block( tuple(blockstatement) )

            genconds = self.frames.getGenerateConditions()
            condlist = []
            for iter, val in genconds:
                if iter is None: # generate if
                    #condlist.append( val )
                    pass
                else: # generate for
                    name = iter[-1].scopename
                    condlist.append( Eq(Identifier(name), IntConst(str(val))) )

            cond = None
            for c in condlist:
                if cond is None:
                    cond = c
                else:
                    cond = Land(cond, c)

            if cond is None:
                cond = IntConst('1')

            ret = IfStatement(cond, block, None)
            self.appendInstance(node, ret)
        else:
            ret = new_node
            self.appendInstance(node, ret)

    #----------------------------------------------------------------------------
    def addTargetObject(self, mode, name, params):
        if mode not in self.target_object:
            self.target_object[mode] = []
        self.target_object[mode].append( (name, params) )

    #----------------------------------------------------------------------------
    def start_visit(self):
        for k, d in self.templateinfotable.getDefinitions().items():
            self.moduleinfotable.overwriteDefinition(k, d)
            self.copyModuleInfo(k, k)
        self.copyModuleInfo(self.top, self.top)
        node = self.getModuleDefinition(self.top)
        self.visit(node)
        self.updateModulePort(node)

    #----------------------------------------------------------------------------
    def visit_ModuleDef(self, node):
        new_node = self.getModuleDefinition(node.name)
        self.generic_visit(new_node)

    #----------------------------------------------------------------------------
    def visit_InstanceList(self, node):
        if len(node.instances) > 1: return
        if self.skip_not_found and node.module not in self.moduleinfotable.dict:
            self.not_found_modules.append(node.module)
            return 
        
        m = re.match('('+TARGET_PREFIX+'.*)', node.module)
        if not m: # normal instance
            return self._visit_InstanceList_normal(node)

        mode = m.group(0)

        if self.frames.isGenerate():
            tmp = self.additionalport
            self.additionalport = []
            self.convertTargetInstance(node, mode, generate=True)
            tmp.extend(self.additionalport)
            self.additionalport = tmp
            return

        self.convertTargetInstance(node, mode, generate=False)

    #----------------------------------------------------------------------------
    def _visit_InstanceList_normal(self, node):
        if self.isUsed(node.module):
            tmp = self.additionalport
            self.additionalport = []
            new_module = self.rename(node.module)
            self.copyModuleInfo(node.module, new_module)
            
            prev_module_name = node.module
            node.module = new_module
            # Not only InstanceList, module of Instance must be changed
            for instance in node.instances:
                instance.module = new_module
                
            self.changeModuleName(node.module, node.module)
            
            SignalVisitor.visit_InstanceList(self, node)
            
            if self.additionalport:
                self.setUsed(node.module)
                self.updateInstancePort(node, generate=self.frames.isGenerate())
                tmp.extend(self.additionalport)
            self.additionalport = tmp
            
            node.module = prev_module_name
            # Not only InstanceList, module of Instance must be restored
            for instance in node.instances:
                instance.module = prev_module_name
                
            self.changeModuleName(node.module, prev_module_name)

        else:
            tmp = self.additionalport
            self.additionalport = []
            self.copyModuleInfo(node.module, node.module)
            SignalVisitor.visit_InstanceList(self, node)
            if self.additionalport:
                self.setUsed(node.module)
                self.updateInstancePort(node, generate=self.frames.isGenerate())
                tmp.extend(self.additionalport)
            self.additionalport = tmp

#-------------------------------------------------------------------------------
class InstanceReplaceVisitor(ReplaceVisitor):
    """ replace instances in new_moduleinfotable by using object address """
    def __init__(self, replaced_instance, replaced_instports, replaced_items,
                 new_moduleinfotable):
        self.replaced_instance = replaced_instance
        self.replaced_instports = replaced_instports
        self.replaced_items = replaced_items
        self.new_moduleinfotable = new_moduleinfotable

    def getAST(self):
        modulelist = sorted([ m.definition for m in self.new_moduleinfotable.dict.values() ],
                            key=lambda x:x.name)
        new_modulelist = []
        for m in modulelist:
            new_modulelist.append( self.visit(m) )
        description = Description( tuple(new_modulelist) )
        source = Source('converted', description)
        return source

    def getReplacedNode(self, key):
        actualkey = id(key)
        return self.replaced_instance[actualkey]

    def hasReplacedNode(self, key):
        actualkey = id(key)
        return (actualkey in self.replaced_instance)

    def getReplacedInstPorts(self, key):
        actualkey = id(key)
        return self.replaced_instports[actualkey]

    def hasReplacedInstPorts(self, key):
        actualkey = id(key)
        return (actualkey in self.replaced_instports)

    def getReplacedItems(self, key):
        actualkey = id(key)
        return self.replaced_items[actualkey]

    def hasReplacedItems(self, key):
        actualkey = id(key)
        return (actualkey in self.replaced_items)

    def visit_InstanceList(self, node):
        if not self.hasReplacedNode(node):
            return self.generic_visit(node)
        return self.getReplacedNode(node)

    def visit_ModuleDef(self, node):
        if self.hasReplacedInstPorts(node):
            node.portlist.ports = tuple(self.getReplacedInstPorts(node))
        if self.hasReplacedItems(node):
            node.items = tuple(self.getReplacedItems(node))
        return self.generic_visit(node)
