class Interface(object):
    def __init__(self, name, idx, addrwidth, datawidth, lite=False):
        self.name = name
        self.idx = idx
        self.datawidth = datawidth
        self.addrwidth = addrwidth
        self.lite = lite

    def __repr__(self):
        ret = []
        ret.append('(')
        ret.append(self.__class__.__name__)
        ret.append(' ')
        ret.append('NAME:')
        ret.append(str(self.name))
        ret.append(' ')
        ret.append('ID:')
        ret.append(str(self.idx))
        ret.append(' ')
        ret.append('ADDR_WIDTH:')
        ret.append(str(self.addrwidth))
        ret.append(' ')
        ret.append('DATA_WIDTH:')
        ret.append(str(self.datawidth))
        ret.append(' ')
        ret.append('LITE:')
        ret.append(str(self.lite))
        ret.append(')')
        return ''.join(ret)

class MasterMemory(Interface): pass
class SlaveMemory(Interface): pass
