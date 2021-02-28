import textwrap

def toFixedLns(text:str,TEXT_WIDTH=18):
    if len(text) <= TEXT_WIDTH:
        return "<b>"+ text +"</b>"
    _L = []
    for _line in textwrap.wrap(text.replace("\n", ""), width=TEXT_WIDTH):
        _L.append(_line)
        _L.append( "<br /> \n")
    if len(_L) > 0:
        _L[0] = "<html><b>"+ _L[0] +"</b></html>"
        del _L[-1]
    return "".join(_L)

def popLns(text:str,prefix:str="【",suffix:str="】"):
    trim = text.replace("\n", "")
    if len(trim) <=0: return "",""
    _L = []
    for _line in textwrap.wrap(trim, width=(20 - len(prefix) - len(suffix))):
        _L.append(_line)
        _L.append("\n")
    return prefix + _L[0] + suffix ,"".join(_L[2:])
class Rangedlist:
    def __init__(self,l:list):
        self._l = l
        self._len = len(self._l)
        self._i = 0

    def next(self):
        self._i = (self._i + 1 ) % self._len

    def last(self):
        self._i = (self._i - 1) % self._len

    def __getitem__(self, item):
        return self._l[item]

    def get(self):
        return self._l[self._i]

if __name__ =="__main__":
    L = []
    for line in textwrap.wrap("a".replace("\n",""), width=18):
        L.append(line)
        L.append("\n")
    print(L)