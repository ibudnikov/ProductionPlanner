import os
import json as js
import sys

#Special processID values:
#500000 -- buy
#500001 -- aquire
#500002 -- import
#500003 -- sell
#500004 -- store
#500005 -- export

class ProcessCategory:
    subcategories = []
    processes = []
    parent = None
    maxItemId = -1
    minItemId = sys.maxsize

    def __getitem__(self, key):
        for it in self.processes:
            if it.name == key:
                return it
        for cat in self.subcategories:
            if cat.name == key:
                return cat
        return None

    def addSubcategories(self, subcs):
        for x in subcs:
            x.parent = self
            if x.maxItemId>self.maxItemId:
                self.maxItemId = x.maxItemId
            if x.minItemId<self.minItemId:
                self.minItemId = x.minItemId
        self.subcategories = subcs
    
    def addProcesses(self, processes):
        for x in processes:
            x.parent = self
            self.processes = processes
            if x.processId>self.maxItemId:
                self.maxItemId = x.processId
            if x.processId<self.minItemId:
                self.minItemId = x.processId

    @staticmethod
    def load(path, itemRoot, type=""):
        if type=="":
            name = path[path.rfind('/')+1:]
            if name=="Construction":
                type = "construct"
            elif name=="Refining":
                type = "refine"
            elif name=="Reverse Engineering":
                type =  "reverse"
        files = os.listdir(path)
        files = [x for x in files if x[0]!='.' and x[-1]!='~']
        dirs = [x for x in files if not os.path.isfile(path+'/'+x)]
        files = [x for x in files if os.path.isfile(path+'/'+x)]
        cat = ProcessCategory()
        subcs = [ProcessCategory.load(path+'/'+x, itemRoot, type) for x in dirs]
        cat.addSubcategories(subcs)
        processes = [Process.load(path+'/'+x, type, itemRoot) for x in files]
        cat.addProcesses(processes)
        return cat

    def find(self, processId, item=None):
        if processId == 500000:
            return Buy(item)
        elif processId == 500001:
            return Aquire(item)
        elif processId == 500002:
            return Import(item)
        elif processId == 500003:
            return Sell(item)
        elif processId == 500004:
            return Store(item)
        elif processId == 500005:
            return Export(item)
        if processId > self.maxItemId or processId < self.minItemId:
            return None
        for it in self.processes:
            if it.processId == processId:
                return it
        for cat in self.subcategories:
            it = cat.find(processId)
            if it is not None:
                return it
        return None

class Process:
    nodeType = "process"
    type = ""
    processId = -1

    @staticmethod
    def load(path, type, itemRoot):
        f = open(path)
        js_str = f.read()
        data = js.loads(js_str)
        if type=="construct":
            c = Construct(data['processId'], data['item'], data['qOut'], data['materials'], data['qIn'], itemRoot)
            return c
        elif type=="refine":
            c = Refine(data['processId'], data['items'], data['qOut'], data['material'], data['qIn'], itemRoot)
            return c
        elif type=="reverse":
            c = Reverse(data['processId'], data['items'], data['qOut'], data['material'], data['qIn'], itemRoot)
            return c
        return None


class Buy(Process):
    type = "buy"
    item = None
    processId = 500000

    def __init__(self, item):
        self.item = item


class Aquire(Process):
    type = "aquire"
    subtype = ""
    item = None
    processId = 500001

    def __init__(self, item):
        if item is not None:
            self.item = item
            if item.parent.name == "Ice ores":
                self.subtype = "miningIce"
            elif item.parent.parent.name == "Standard ores":
                self.subtype = "miningOre"
            elif item.parent.parent.name == "Salvage materials":
                self.subtype = "salvaging"
            elif item.parent.parent.name == "Gas Clouds Materials":
                self.subtype = "miningGas"
            elif item.parent.name == "Ancient Relics":
                self.subtype = "relic"
            elif item.parent.name == "Datacores" or item.parent.name == "Decryptors":
                self.subtype = "data"
            elif item.parent.parent.name == "Planetary":
                self.subtype = "planetary"
            else: self.subtype = "unknown"

class Import(Process):
    type = "import"
    item = None
    processId = 500002
    planetId = -1
    
    def __init__(self, item, planetId):
        self.item = item
        self.planetId = planetId
        if item.parent.parent.name != "Planetary":
            print('SMUGGLER! You are trying to take off-world something wrong.')

class Sell(Process):
    type = "sell"
    item = None
    processId = 500003
    
    def __init__(self, item):
        self.item = item


class Store(Process):
    type = "store"
    item = None
    processId = 500004
    
    def __init__(self, item):
        self.item = item

class Export(Process):
    type = "export"
    item = None
    processId = 500005
    planetId = -1

    def __init__(self, item, planetId):
        self.item = item
        self.planetId = planetId
        if item.parent.parent.name != "Planetary":
            print('SMUGGLER! You are trying to take off-world something wrong.')

class Construct(Process):
    type = "construct"
    subtype = ""
    item = -1
    quantityOut = 0
    materials = []
    quantityIn = []

    def __init__(self, processId, item, quantityOut, materials, quantityIn, itemRoot):
        self.processId = processId
        self.item = item
        self.quantityOut = quantityOut
        self.materials = materials
        self.quantityIn = quantityIn
        objItem = itemRoot.find(item)
        if objItem.parent.parent.name == "Planetary":
            self.subtype = "planetary"
        elif objItem.parent.name == "Polymer materials":
            self.subtype = "polymerReaction"
        elif objItem.name[:10] == "Compressed":
            self.subtype = "compression"
        else: self.subtype = "normal"


class Refine(Process):
    type = "refine"
    subtype = ""
    items = []
    quantityOut = []
    material = None
    quantityIn = 0

    def __init__(self, processId, items, quantityOut, material, quantityIn, itemRoot):
        self.processId = processId
        self.items = items
        self.quantityOut = quantityOut
        self.material = material
        self.quantityIn = quantityIn
        objItem = itemRoot.find(items[0])
        if objItem.parent.name == "Minerals":
            self.subtype = "oreRefining"
        elif objItem.parent.name == "Ice products":
            self.subtype = "iceRefining"
        else: self.subtype = "unknown"


class Reverse(Process):
    type = "reverse"
    subtype = ""
    items = []
    quantityOut = []
    material = None
    quantityIn = 0
    
    def __init__(self, processId, items, quantityOut, material, quantityIn):
        self.processId = processId
        self.items = items
        self.quantityOut = quantityOut
        self.material = material
        self.quantityIn = quantityIn



def init(path, itemRoot):
    procRoot = ProcessCategory.load(path, itemRoot)
    return procRoot
