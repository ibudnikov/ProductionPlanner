import json as js
import sys

class Node:
    type = ""
    nodeId = -1
    mouseOver = False

class ItemNode(Node):
    item = None
    type = "item"
    quantityIn = 0
    quantityOut = 0
    isolated = True
    def __init__(self, nodeId, it, qIn=0, qOut=0):
        self.nodeId = nodeId
        self.item = it
        self.quantityIn = qIn
        self.quantityOut = qOut

class QuestionNode(Node):
    type = "question"
    def __init__(self, nodeId):
        self.nodeId = nodeId

class ProcessNode(Node):
    process = None
    type = "process"
    subtype = ""
    subtype2 = ""
    quantity = 1
    expense = 0
    def __init__(self, nodeId, proc, quantity):
        self.nodeId = nodeId
        self.process = proc
        self.quantity = quantity
        if proc.processId == 500000:
            self.subtype = "input"
            self.subtype2 = "buy"
            self.method = "sell"
        elif proc.processId == 500001:
            self.subtype = "input"
            self.subtype2 = "aquire"
        elif proc.processId == 500002:
            self.subtype = "output"
            self.subtype2 = "import"
        elif proc.processId == 500003:
            self.subtype = "output"
            self.subtype2 = "sell"
            self.method = "buy"
        elif proc.processId == 500004:
            self.subtype = "output"
            self.subtype2 = "store"
        elif proc.processId == 500005:
            self.subtype = "input"
            self.subtype2 = "export"
        elif proc.type == "construct":
            self.subtype = "construct"
        elif proc.type == "refine":
            self.subtype = "refine"

    def recalculate(self, char, system, facility, itemRoot):
        self.calculateInOutPrice()
        self.calculateInOutVolume()
        self.calculateExpense(char, system, facility, itemRoot)

    def calculateInOutPrice(self):
        if self.subtype=="input" or self.subtype=="output":
            if self.subtype2=="buy" or self.subtype2=="sell":
                if self.method == "buy":
                    self.price = self.process.item.buyPrice * self.quantity
                else: self.price = self.process.item.sellPrice * self.quantity
                if self.price<0 or self.price>0.5*sys.float_info.max:
                    self.price = 0

    def calculateInOutVolume(self):
        if self.subtype=="input" or self.subtype=="output":
            self.volume = self.process.item.volume * self.quantity

    def calculateExpense(self, char, system, facility, itemRoot):
        if self.subtype == "input" and self.subtype2 == "buy":
            if self.method == "buy":
                self.expense = self.price * char.getBrokerCharge()
            else: self.expense = 0
        elif self.subtype == "input" and self.subtype2 == "export":
            it = itemRoot.find(self.process.item)
            self.expense = system.customsTax * it.basePrice * self.quantity
        elif self.subtype == "output" and self.subtype2 == "sell":
            if self.method == "sell":
                self.expense = self.price * (char.getBrokerCharge() + char.getTax())
            else: self.expense = self.price * char.getTax()
        elif self.subtype == "output" and self.subtype2 == "import":
            it = itemRoot.find(self.process.item)
            self.expense = system.customsTax * it.basePrice * self.quantity
        elif self.subtype == "construct":
            it = itemRoot.find(self.process.item)
            if "Polymer materials" in it.categories:
                basePrice = sum([itemRoot.find(x).basePrice for x in self.process.materials])
                self.expense = (1 + facility.tax) * system.manufacturingIndex * basePrice * self.quantity
                if self.expense < 0:
                    self.expense = 0
            elif "Materials" not in it.categories:
                self.expense = (1 + facility.tax) * system.manufacturingIndex * it.basePrice * self.quantity
                if self.expense < 0:
                    self.expense = 0
        elif self.subtype == "refine":
            it = itemRoot.find(self.process.material)
            refTax = 0.05 * (1-facility.standing*1.5)
            if refTax>0 and it.basePrice>0:
                self.expense = refTax * it.basePrice
            else: self.expense = 0

class PlanetNode(Node):
    type = "planet"
    pranetId = -1
    name = ""
    schema = None
    baseSchema = None
    imports = []
    exports = []
    def __init__(self, nodeId, planetId, name, baseSchema):
        self.nodeId = nodeId
        self.planetId = planetId
        self.schema = Schema()
        self.name = name
        self.baseSchema = baseSchema

    def getPlanetDict(self):
        res = {'nodeId': self.nodeId, 'planetId':self.planetId, 'name':self.name, 'schema':self.getSchemaDict(), 'imports':[{'id':x.nodeId, 'item':x.process.item.itemId, 'quantity':x.quantity} for x in self.imports], 'exports':[{'id':x.nodeId, 'item':x.process.item.itemId, 'quantity':x.quantity} for x in self.exports]}
        return res

    @staticmethod
    def getPlanetFromDict(data, itemRoot, procRoot):
        p = PlanetNode()
        p.nodeId = data['nodeId']
        p.planetId = data['planetId']
        p.name = data['name']
        p.schema = Schema.getSchemaFromDict(data['schema'], itemRoot, procRoot)
        p.imports = [ProcessNode(x['id'], Import(x['item'], p.planetId), x['quantity']) for x in data['imports']]
        p.exports = [ProcessNode(x['id'], Export(x['item'], p.planetId), x['quantity']) for x in data['exports']]
        return p


class SchemaSummary:
    buys = []
    sells = []
    aquires = []
    stores = []
    imports = []
    exports = []
    
    totalBuy = 0
    totalBuyVolume = 0
    totalAquireEst = 0
    totalAquireVolume = 0
    
    totalCustomsTax = 0
    totalProductionTax = 0
    totalRefiningTax = 0
    totalMarketTax = 0
    totalInterplanetaryShipment = 0
    
    totalSell = 0
    totalSellVolume = 0
    totalStoreEst = 0
    totalStoreVolume = 0
    
    
    def __init__(self, nodes, char, system, facility, itemRoot):
        [x.calculateInOutPrice() for x in nodes if x.type=="process"]
        [x.calculateInOutVolume() for x in nodes if x.type=="process"]
        self.buys = [x for x in nodes if x.type=="process" and x.subtype=="input" and x.subtype2=="buy"]
        self.aquires = [x for x in nodes if x.type=="process" and x.subtype=="input" and x.subtype2=="aquire"]
        self.sells = [x for x in nodes if x.type=="process" and x.subtype=="output" and x.subtype2=="sell"]
        self.stores = [x for x in nodes if x.type=="process" and x.subtype=="output" and x.subtype2=="store"]
        self.imports = [x for x in nodes if x.type=="process" and x.subtype=="output" and x.subtype2=="import"]
        self.exports = [x for x in nodes if x.type=="process" and x.subtype=="output" and x.subtype2=="export"]

        [x.calculateExpense(char, system, facility, itemRoot) for x in nodes if x.type=="process"]
        
        self.totalBuy = sum([x.price for x in self.buys])
        self.totalBuyVolume = sum([x.volume for x in self.buys])
        aquireItems = [x.process.item for x in self.aquires]
        self.totalAquireEst = sum([x.buyPrice * y.quantity for x,y in zip(aquireItems, self.aquires)])
        self.totalAquireVolume = sum([x.volume for x in self.aquires])
        
        self.totalCustomsTax = sum([x.expense for x in self.imports+self.exports])
        self.totalProductionTax = sum([x.expense for x in nodes if x.type=="process" and x.subtype=="construct"])
        self.totalRefiningTax = sum([x.expense for x in nodes if x.type=="process" and x.subtype=="refine"])
        self.totalMarketTax = sum([x.expense for x in self.buys+self.sells])
        self.totalInterplanetaryShipment = 0  #TODO
        
        self.totalSell = sum([x.price for x in self.sells])
        self.totalSellVolume = sum([x.volume for x in self.sells])
        storeItems = [x.process.item for x in self.stores]
        self.totalStoreEst = sum([x.buyPrice * y.quantity for x,y in zip(storeItems, self.stores)])
        self.totalStoreVolume = sum([x.volume for x in self.stores])


class Schema:
    nodes = []
    connectionsA = []
    connectionsB = []
    filename = ""
    freeId = 0
    summary = None
    
    currentPlanet = None
    planetFreeIdx = 0
    
    char = None
    system = None
    facility = None
    itemRoot = None
    
    def __init__(self, char, system, facility, itemRoot):
        self.nodes = []
        self.connectionsA = []
        self.connectionsB = []
        self.filename = ""
        self.freeId = 0
        self.summary = None
        self.currentPlanet = None
        self.planetFreeIdx = 0
        
        self.char = char
        self.system = system
        self.facility = facility
        self.itemRoot = itemRoot

    @staticmethod
    def createSchema(item):
        s = Schema()
        itNode = ItemNode(0, item)
        s.freeId = 1
        s.nodes = [itNode]
        s.connectionsA = []
        s.connectionsB = []
        s.filename = ""
        return s
    
    def getSchemaDict(self):
        qNodes = [x.nodeId for x in self.nodes if x.type=="question"]
        joint = [(x,y) for x,y in zip(self.connectionsA, self.connectionsB) if x not in qNodes and y not in qNodes]
        connA = [x[0] for x in joint]
        connB = [x[1] for x in joint]
        
        d = {'items':[{'id':x.nodeId, 'item':x.item.itemId, 'quantityIn':x.quantityIn, 'quantityOut':x.quantityOut} for x in self.nodes if x.type == "item"],
            'processes':[{'id':x.nodeId, 'process':x.process.processId, 'quantity':x.quantity} for x in self.nodes if x.type == "process"],
            'planets':[x.getPlanetDict() for x in self.nodes if x.type=="planet"],
            'connectionsA':connA, 'connectionsB':connB}
        return d
    
    def save(self):
        if self.filename == "":
            return
        d = self.getSchemaDict()
        js_data = js.loads(js.dumps(d))
        with open(self.filename, 'w') as f:
            js.dump(js_data, f)

    @staticmethod
    def getSchemaFromDict(data, char, system, facility, itemRoot, procRoot):
        s = Schema(char, system, facility, itemRoot)
        s.nodes = [ItemNode(x['id'], itemRoot.find(x['item']), x['quantityIn'], x['quantityOut']) for x in data['items']]
        s.nodes.extend([ProcessNode(x['id'], procRoot.find(x['process']), x['quantity']) for x in data['processes']])
        s.nodes.extend([PlanetNode.getPlanetFromDict(x, itemRoot, procRoot) for x in data['planets']])
        s.nodes.sort(key=lambda x: x.nodeId)
        s.connectionsA = data['connectionsA']
        s.connectionsB = data['connectionsB']
        if len(s.nodes)>0:
            s.freeId = s.nodes[-1].nodeId+1
        else: s.freeId = 0
        for x in [x for x in s.nodes if x.type=="process" and x.subtype=="input"]:
            conn = [z for y,z in zip(s.connectionsA, s.connectionsB) if y==x.nodeId][0]
            x.process.item = s.getNodeById(conn).item
        for x in [x for x in s.nodes if x.type=="process" and x.subtype=="output"]:
            conn = [y for y,z in zip(s.connectionsA, s.connectionsB) if z==x.nodeId][0]
            x.process.item = s.getNodeById(conn).item
        return s

    @staticmethod
    def load(path, char, system, facility, itemRoot, procRoot):
        f = open(path)
        js_str = f.read()
        data = js.loads(js_str)
        s = Schema.getSchemaFromDict(data, char, system, facility, itemRoot, procRoot)
        s.filename = path
        
        s.recalculateIsolation()
        s.recalculate()
        return s

    def recalculateIsolation(self):
        itemNodes = [x for x in self.nodes if x.type=="item"]
        for iN in itemNodes:
            iN.isolated = True
            nodesA = [self.getNodeById(x) for x,y in zip(self.connectionsA, self.connectionsB) if y==iN.nodeId]
            nodesB = [self.getNodeById(y) for x,y in zip(self.connectionsA, self.connectionsB) if x==iN.nodeId]
            nodesA = [x for x in nodesA if x.type!="question"]
            nodesB = [x for x in nodesB if x.type!="question"]
            if len(nodesA)>0 or len(nodesB)>0:
                iN.isolated = False
        if self.currentPlanet is not None:
            for iN in itemNodes:
                itemId = it.item.itemId
                for imp in self.imports:
                    if itemId == imp.item.itemId:
                        iN.isolated = False
                for exp in self.exports:
                    if itemId == exp.item.itemId:
                        iN.isolated = False

    def recalculate(self):
        qNodes = [x.nodeId for x in self.nodes if x.type=="question"]
        joint = [(x,y) for x,y in zip(self.connectionsA, self.connectionsB) if x not in qNodes and y not in qNodes]
        self.connectionsA = [x[0] for x in joint]
        self.connectionsB = [x[1] for x in joint]
        self.nodes = [x for x in self.nodes if x.nodeId not in qNodes]
        
        items = [x for x in self.nodes if x.type=="item"]
        for it in items:
            procIn = [self.getNodeById(x) for x,y in zip(self.connectionsA, self.connectionsB) if y==it.nodeId]
            procInTerm = [x for x in procIn if x.subtype=="input"]
            procInConstruct = [x for x in procIn if x.subtype=="construct"]
            procInRefine = [x for x in procIn if x.subtype=="refine"]
            
            procOut = [self.getNodeById(y) for x,y in zip(self.connectionsA, self.connectionsB) if x==it.nodeId]
            procOutTerm = [x for x in procOut if x.subtype=="output"]
            procOutConstruct = [x for x in procOut if x.subtype=="construct"]
            procOutRefine = [x for x in procOut if x.subtype=="refine"]
            
            indexIn = [[i for y,i in zip(x.process.items, range(len(x.process.items))) if y==it.item.itemId][0] for x in procInRefine]
            it.quantityIn = sum([x.quantity*x.process.quantityOut for x in procInConstruct])
            it.quantityIn += sum([x.quantity for x in procInTerm])
            it.quantityIn += sum([x.quantity*x.process.quantityOut[y] for x,y in zip(procInRefine, indexIn)])
            
            indexOut = [[i for y,i in zip(x.process.materials, range(len(x.process.materials))) if y==it.item.itemId][0] for x in procOutConstruct]
            it.quantityOut = sum([x.quantity*x.process.quantityIn[y] for x,y in zip(procOutConstruct, indexOut)])
            it.quantityOut += sum([x.quantity for x in procOutTerm])
            it.quantityOut += sum([x.quantity*x.process.quantityIn for x in procOutRefine])
        
            if it.quantityIn<it.quantityOut or (it.quantityIn==0 and it.quantityOut==0):
                qNode = QuestionNode(self.freeId)
                self.connectionsA.append(self.freeId)
                self.connectionsB.append(it.nodeId)
                self.nodes.append(qNode)
                self.freeId += 1
            if it.quantityIn>it.quantityOut or (it.quantityIn==0 and it.quantityOut==0):
                qNode = QuestionNode(self.freeId)
                self.connectionsB.append(self.freeId)
                self.connectionsA.append(it.nodeId)
                self.nodes.append(qNode)
                self.freeId += 1
        
        if self.currentPlanet is not None:
            for it in items:
                for imp in self.imports:
                    if it.itemId == imp.item.itemId:
                        it.quantityIn += imp.quantity
                        break
                for exp in self.exports:
                    if it.itemId == exp.item.itemId:
                        it.quantityOut += exp.quantity
                        break
        else:
            pls = [self.getNodeById(x) for x in self.nodes if x.type=="planet"]
            [pls.schema.recalculate() for x in pls]
        for n in self.nodes:
            if n.type=="process":
                n.recalculate(self.char, self.system, self.facility, self.itemRoot)

    def calculateSummary(self, char, system, facility, itemRoot):
        self.summary = SchemaSummary(self.nodes, char, system, facility, itemRoot)
        return self.summary


    def adjustProcessNumber(self, processNodeId):
        procNode = self.getNodeById(processNodeId)
        if procNode is None or procNode.type != "process":
            return -1

        inConnections = [x for x,y in zip(self.connectionsA, self.connectionsB) if y==processNodeId]
        outConnections = [y for x,y in zip(self.connectionsA, self.connectionsB) if x==processNodeId]
        if procNode.subtype == "input":
            outItem = self.getNodeById(outConnections[0])
            quantity = outItem.quantityOut - outItem.quantityIn + procNode.quantity
            if quantity<1:
                quantity = 1
            procNode.quantity = quantity
        elif procNode.subtype == "output":
            inItem = self.getNodeById(inConnections[0])
            quantity = inItem.quantityIn - inItem.quantityOut + procNode.quantity
            if quantity<1:
                quantity = 1
            procNode.quantity = quantity
            

    def deepTopSort(self, index):
        dirs = [y for x,y in zip(self.connectionsA, self.connectionsB) if x==index]
        cols = [self.getNodeById(x).color for x in dirs]
        wgCols = [x for x in cols if x!=2]
        if len(wgCols)==0:
            self.getNodeById(index).color = 2
            return [index]
        else:
            stack = []
            for d in dirs:
                stack.extend(self.deepTopSort(d))
            self.getNodeById(index).color = 2
            stack.append(index)
            return stack

    def getNodeById(self, nodeId):
        for node in self.nodes:
            if node.nodeId == nodeId:
                return node
        return None

    def getNodeIdByContent(self, id):
        for node in self.nodes:
            if node.type == "item":
                if node.item.itemId == id:
                    return node.nodeId
            elif node.type == "process":
                if node.process.processId == id:
                    return node.nodeId
        return -1
    
    def addIsolatedItem(self, item):
        if self.currentPlanet is not None and "Planetary" not in item.categories:
            return
        oldItems = [x.item.itemId for x in self.nodes if x.type == "item"]
        if item.itemId in oldItems:
            return
        itemNode = ItemNode(self.freeId, item)
        self.nodes.append(itemNode)
        self.freeId = self.freeId+1
        self.recalculate()

    def addPlanet(self, name):
        if self.currentPlanet is not None:
            return
        p = PlanetNode(self.freeId, self.planetFreeIdx, name, self)
        self.freeId = self.freeId + 1
        self.planetFreeIdx = self.planetFreeIdx + 1

    
    def addProcess(self, process, itemRoot, item=None):
        if self.currentPlanet is None:
            if process.type == "buy" or process.type == "aquire":
                return self.addInProcess(process)
            elif process.type == "export":
                return None
            elif process.type == "sell" or process.type == "store":
                return self.addOutProcess(process)
            elif process.type == "import":
                return None
            elif process.type == "construct":
                return self.addConstruction(process, itemRoot)
            elif process.type == "refine":
                return self.addRefining(process, itemRoot)
            else: return None
        elif "Planetary" in process.item.categories:
            if process.type == "aquire":
                return self.addInProcess(process)
            elif process.type == "export":
                return None
            elif process.type == "import":
                return None
            elif process.type == "construct":
                return self.addConstruction(process, itemRoot)
            else: return None

    def addExport(self, process, planetNodeId):
        if self.currentPlanet is not None:
            item = process.item
            itemNodeId = self.currentPlanet.baseSchema.getNodeIdByContent(item.itemId)
            if itemNodeId==-1:
                self.currentPlanet.baseSchema.addIsolatedItem(item)
            return self.currentPlanet.baseSchema.addExport(process, self.currentPlanet.planetIdx)

        planetNode = self.getNodeById(planetNodeId)
        if planetNode is None:
            return -1

        item = process.item
        itemNodeId = self.getNodeIdByContent(item.itemId)
        exports = [self.getNodeById(x) for x,y in zip(self.connectionsA, connectionsB) if y==itemNodeId]
        exports = [x for x in exports if x.subtype=="export" and x.planetId==planetNode.planetId]
        if len(exports)>0:
            return -2

        p = ProcessNode(self.freeId, process, 1)
        self.connectionsA.append(self.freeId)
        self.connectionsB.append(itemNodeId)
        planetNode.exports.append(p)
        self.connectionsA.append(planetNodeId)
        self.connectionsB.append(self.freeId)
        self.freeId = self.freeId+1
        
        planetItemId = planetNode.schema.getNodeIdByContent(item.itemId)
        if planetItemId == -1:
            planetNode.schema.addIsolatedItem(item)
        self.recalculate()
            
    def addImport(self, process, planetNodeId):
        if self.currentPlanet is not None:
            item = process.item
            itemNodeId = self.currentPlanet.baseSchema.getNodeIdByContent(item.itemId)
            if itemNodeId==-1:
                self.currentPlanet.baseSchema.addIsolatedItem(item)
            return self.currentPlanet.baseSchema.addImport(process, self.currentPlanet.planetIdx)
        
        planetNode = self.getNodeById(planetNodeId)
        if planetNode is None:
            return -1
        
        item = process.item
        itemNodeId = self.getNodeIdByContent(item.itemId)
        imports = [self.getNodeById(y) for x,y in zip(self.connectionsA, connectionsB) if x==itemNodeId]
        imports = [x for x in imports if x.subtype=="import" and x.planetId==planetNode.planetId]
        if len(imports)>0:
            return -2
        
        p = ProcessNode(self.freeId, process, 1)
        self.connectionsA.append(itemNodeId)
        self.connectionsB.append(self.freeId)
        planetNode.imports.append(p)
        self.connectionsA.append(self.freeId)
        self.connectionsB.append(planetNodeId)
        self.freeId = self.freeId+1
        
        planetItemId = planetNode.schema.getNodeIdByContent(item.itemId)
        if planetItemId == -1:
            planetNode.schema.addIsolatedItem(item)
        self.recalculate()
        

    def addInProcess(self, process):
        item = process.item
        nodeId = self.getNodeIdByContent(item.itemId)
        node = self.getNodeById(nodeId)
        if node is None:
            return -1
        if node.type != "item":
            return -2
        if process.processId>500001:
            return -3
        if process.processId not in node.item.inProcess:
            return -4
        p = ProcessNode(self.freeId, process, 1)
        self.nodes.append(p)
        self.connectionsA.append(self.freeId)
        self.connectionsB.append(nodeId)
        self.freeId = self.freeId + 1
        self.recalculate()
        self.adjustProcessNumber(p.nodeId)
        return p.nodeId

    def addOutProcess(self, process):
        item = process.item
        nodeId = self.getNodeIdByContent(item.itemId)
        node = self.getNodeById(nodeId)
        if node is None:
            return -1
        if node.type != "item":
            return -2
        if process.processId>500004 or process.processId<500003:
            return -3
        p = ProcessNode(self.freeId, process, 1)
        self.nodes.append(p)
        self.connectionsA.append(nodeId)
        self.connectionsB.append(self.freeId)
        self.freeId = self.freeId + 1
        self.recalculate()
        self.adjustProcessNumber(p.nodeId)
        return p.nodeId

    def addConstruction(self, process, itemRoot):
        if process.type != "construct":
            return -1
        for n in self.nodes:
            if n.type == "process" and n.process.processId == process.processId:
                return -2

        usedOut = False
        usedIn = []
        processNodeId = self.freeId

        connected = False
        for n in self.nodes:
            if n.type == "item":
                if process.processId in n.item.inProcess:
                    connected = True
                    usedOut = True
                    n.isolated = False
                    self.connectionsA.append(processNodeId)
                    self.connectionsB.append(n.nodeId)
                if process.processId in n.item.outProcess:
                    connected = True
                    n.isolated = False
                    usedIn.append(n.item.itemId)
                    self.connectionsA.append(n.nodeId)
                    self.connectionsB.append(processNodeId)

        if connected:
            p = ProcessNode(self.freeId, process, 1)
            self.nodes.append(p)
            self.freeId = self.freeId + 1
            if not usedOut:
                it = ItemNode(self.freeId, itemRoot.find(process.item))
                it.isolated = False
                self.nodes.append(it)
                self.connectionsA.append(processNodeId)
                self.connectionsB.append(self.freeId)
                self.freeId = self.freeId + 1
            for itemId in process.materials:
                if itemId not in usedIn:
                    it = ItemNode(self.freeId, itemRoot.find(itemId))
                    it.offworld = True
                    it.isolated = False
                    self.nodes.append(it)
                    self.connectionsA.append(self.freeId)
                    self.connectionsB.append(processNodeId)
                    self.freeId = self.freeId + 1
            self.recalculate()
            return processNodeId
        return -3
    
    def addRefining(self, process, itemRoot):
        if process.type != "refine":
            return -1
        for n in self.nodes:
            if n.type == "process" and n.process.processId == process.processId:
                return -2
        
        usedIn = False
        usedOut = []
        processNodeId = self.freeId
        
        connected = False
        for n in self.nodes:
            if n.type == "item":
                if process.processId in n.item.inProcess:
                    connected = True
                    usedOut.append(n.item.itemId)
                    n.isolated = False
                    self.connectionsA.append(processNodeId)
                    self.connectionsB.append(n.nodeId)
                if process.processId in n.item.outProcess:
                    connected = True
                    n.isolated = False
                    usedIn = True
                    self.connectionsA.append(n.nodeId)
                    self.connectionsB.append(processNodeId)
                
        if connected:
            p = ProcessNode(self.freeId, process, 1)
            self.nodes.append(p)
            self.freeId = self.freeId + 1
            if not usedIn:
                it = ItemNode(self.freeId, itemRoot.find(process.material))
                it.isolated = False
                self.nodes.append(it)
                self.connectionsA.append(self.freeId)
                self.connectionsB.append(processNodeId)
                self.freeId = self.freeId + 1
            for itemId in process.items:
                if itemId not in usedOut:
                    it = ItemNode(self.freeId, itemRoot.find(itemId))
                    it.isolated = False
                    self.nodes.append(it)
                    self.connectionsA.append(processNodeId)
                    self.connectionsB.append(self.freeId)
                    self.freeId = self.freeId + 1
            self.recalculate()
            return processNodeId
        return -3
    
    def deleteProcess(self, processNodeId):
        processNode = self.getNodeById(processNodeId)
        if processNode is None or processNode.type != "process":
            return
        if processNode.subtype == "input" and processNode.subtype2 == "export":
            planetNode = self.getNodeById(processNode.process.planetId)
            planetNode.exports = [x for x in planetNode.exports if x.item.itemId != processNode.process.item.itemId]
        if processNode.subtype == "output" and processNode.subtype2 == "import":
            planetNode = self.getNodeById(processNode.process.planetId)
            planetNode.imports = [x for x in planetNode.imports if x.item.itemId != processNode.process.item.itemId]
        joined = [(x,y) for x,y in zip(self.connectionsA, self.connectionsB) if x!=processNodeId and y!=processNodeId]
        self.connectionsA = [x[0] for x in joined]
        self.connectionsB = [x[1] for x in joined]
        self.nodes = [x for x in self.nodes if x.nodeId!=processNodeId]
        self.recalculateIsolation()
        self.recalculate()

    def deleteItem(self, itemNodeId):
        itemNode = self.getNodeById(itemNodeId)
        if itemNode.type != "item" or not itemNode.isolated:
            return
        processesToDeleteIds = [x for x,y in zip(self.connectionsA, self.connectionsB) if y==itemNodeId]
        processesToDeleteIds.extend([y for x,y in zip(self.connectionsA, self.connectionsB) if x==itemNodeId])
        joined = [(x,y) for x,y in zip(self.connectionsA, self.connectionsB) if x!=itemNodeId and y!=itemNodeId]
        self.connectionsA = [x[0] for x in joined]
        self.connectionsB = [x[1] for x in joined]
        self.nodes = [x for x in self.nodes if x.nodeId!=itemNodeId and x.nodeId not in processesToDeleteIds]

    def deletePlanet(self, planetNodeId):
        planetNode = self.getNodeById(planetNodeId)
        if planetNode is None or planetNode.type != "planet":
            return
        if len(planetNode.schema.nodes)>0:
            return
        processesToDeleteIds = [x for x,y in zip(self.connectionsA, self.connectionsB) if y==planetNodeId]
        processesToDeleteIds.extend([y for x,y in zip(self.connectionsA, self.connectionsB) if x==planetNodeId])
        joined = [(x,y) for x,y in zip(self.connectionsA, self.connectionsB) if x!=planetNodeId and y!=planetNodeId]
        self.connectionsA = [x[0] for x in joined]
        self.connectionsB = [x[1] for x in joined]
        self.nodes = [x for x in self.nodes if x.nodeId!=planetNodeId and x.nodeId not in processesToDeleteIds]


def lcm(a, b):
    m = a*b
    return m // lcd(a,b)

def lcd(a, b):
    while a!=0 and b!=0:
        if a>b:
            a%=b
        else: b%=a
    return a+b
