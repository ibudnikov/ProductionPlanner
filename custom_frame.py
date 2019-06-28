from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, Qt, QMimeData, QByteArray
#from PyQt5.QtGui import QDrag
#import os
#import shutil
from functools import partial

import items
from node_frames import *
from util import *

class CustomFrame(QtWidgets.QFrame):
    parent = None
    schema = None
    itemRoot = None
    procRoot = None
    lines = []
    curves = []
    summaryChanged = pyqtSignal()
    def __init__(self, parent, itemRoot, procRoot):
        super().__init__(parent)
        self.parent = parent
        self.itemRoot = itemRoot
        self.procRoot = procRoot
        self.setAcceptDrops(True)
        self.nodeVisual = []
        self.destroyed.connect(partial(CustomFrame.destructor, self.__dict__))
    
    @staticmethod
    def destructor(d):
        schema = d['schema']
        schema.save()

    def displaySchema(self):
        self.lines = []
        self.placeholders = []
        if self.schema is None or len(self.schema.nodes)==0:
            self.clearSchema()
            width = self.parent.width()
            height = self.parent.height()
            self.resize(width, height)
        else:
            self.clearSchema()
            
            minH = 0
            maxH = 0
            minW = 0
            maxW = 0
            
            maxN = 0
            setNodesLevels(self.schema)
            
            levels = []
            for i in range(19):
                levels.append([x for x in self.schema.nodes if x.level==i])
            
            plId = 0
            
            nodeHeight = 120
            placeholderHeight = 40
            nodeWidth = 160
            spaceH = 20
            spaceW = 100

            placeholders = [[] for x in range(19)]
            for x,y in zip(self.schema.connectionsA, self.schema.connectionsB):
                node1lvl = self.schema.getNodeById(x).level
                node2lvl = self.schema.getNodeById(y).level
                sublevel = self.schema.getNodeById(x).sublevel
                for z in range(node1lvl+1, node2lvl):
                    if z==node1lvl+1:
                        p = Placeholder(-1, -1, placeholderHeight, "pl"+str(plId), x, "pl"+str(plId+1), sublevel)
                        plId += 1
                    elif z==node2lvl-1:
                        p = Placeholder(-1, -1, placeholderHeight, "pl"+str(plId), "pl"+str(plId-1), y, sublevel)
                        plId += 1
                    else:
                        p = Placeholder(-1, -1, placeholderHeight, "pl"+str(plId), "pl"+str(plId-1), "pl"+str(plId+1), sublevel)
                        plId += 1
                    item1 = self.schema.getNodeById(x)
                    item2 = self.schema.getNodeById(y)
                    if item1.mouseOver or item2.mouseOver:
                        p.mouseOver = True
                    placeholders[z].append(p)

            for i in range(18):
                curNQ = [x for x in levels[i] if x.type!="question"]
                if len(levels[i])>0 and len(curNQ)==0:
                    j = i+1
                    while j<19 and len([x for x in levels[j] if x.type!="question" and x.type!="process"])==0:
                        j+=1
                    j-=1
                    if j>i:
                        for k in range(i, j):
                            for x in levels[k]:
                                x.level = j
    
            levels = []
            for i in range(19):
                levels.append([x for x in self.schema.nodes if x.level==i])
        
            delNumbers = [i for x,i in zip(levels, range(len(levels))) if len(x) == 0]
            for i in delNumbers:
                for p in placeholders[i]:
                    if i<len(levels)-1 and str(p.nextId).startswith("pl"):
                        next = [x for x in placeholders[i+1] if x.nodeId==p.nextId][0]
                        next.prevId = p.prevId
                    if i>0 and str(p.prevId).startswith("pl"):
                        prev = [x for x in placeholders[i-1] if x.nodeId==p.prevId][0]
                        prev.nextId = p.nextId
            placeholders = [y for x,y in zip(levels, placeholders) if len(x)>0]
            phLen = [len(x) for x in placeholders]
            joint = [(x,i) for x,i in zip(levels, range(len(levels))) if len(x)>0]
            levels = [x[0] for x in joint]
            lvlNumbers = [x[1] for x in joint]

            for node in self.schema.nodes:
                node.start = [-1,-1]
                node.height = -1
        
            levelHeight = [len(x) * nodeHeight + y * placeholderHeight + (len(x)+y)*spaceH for x,y in zip(levels, phLen)]
        
            if len(levelHeight)==0:
                return
            maxLevel = levelHeight.index(max(levelHeight))
            levels = [[[y for y in x if y.sublevel==i] for i in range(6)] for x in levels]
            placeholders = [[[y for y in x if y.sublevel==i] for i in range(6)] for x in placeholders]
            
            maxH = max(levelHeight)+20
            maxW = (spaceW + nodeWidth)*len(levels) + spaceW
            levelStart = [(levelHeight[maxLevel]-x)/2 for x in levelHeight]
            
            itemLevels = []
            procLevels = []
            for lvl, i in zip(levels, range(len(levels))):
                br = False
                for l in lvl:
                    for r in l:
                        if r.type == "item":
                            itemLevels.append(i)
                            br = True
                            break
                        else:
                            procLevels.append(i)
                            br = True
                            break
                    if br:
                        break

            for lvl, plc, st, i in zip(levels, placeholders, levelStart, range(len(levelStart))):
                if i not in itemLevels:
                    continue
                h = st + 20
                for j in range(6):
                    for node in lvl[j]:
                        node.start = [spaceW + (nodeWidth+spaceW)*i, h]
                        node.height = nodeHeight
                        h += nodeHeight + spaceH
                    for place in plc[j]:
                        place.start = [spaceW + (nodeWidth+spaceW)*i, h]
                        h += placeholderHeight + spaceH
    
            for i in range(len(levels)):
                res = []
                for lvl in levels[i]:
                    res.extend(lvl)
                levels[i] = res
            for i in range(len(placeholders)):
                res = []
                for lvl in placeholders[i]:
                    res.extend(lvl)
                placeholders[i] = res

            for i in range(len(lvlNumbers)):
                if i in itemLevels:
                    continue
                subnodes = [x for x in self.schema.nodes if x.level==lvlNumbers[i]]
                res = []
                subnodes.sort(key = lambda x: x.start[1])
                for node in subnodes:
                    if node.type == "question":
                        itemOut = [y for x,y in zip(self.schema.connectionsA, self.schema.connectionsB) if x==node.nodeId]
                        itemIn = [x for x,y in zip(self.schema.connectionsA, self.schema.connectionsB) if y==node.nodeId]
                        if len(itemOut) == 1:
                            item = itemOut[0]
                            itemNode = self.schema.getNodeById(item)
                            width = 1
                            if itemNode.mouseOver:
                                width = 3
                            node.start = [itemNode.start[0]-70, itemNode.start[1]+70]
                            self.lines.append([node.start[0]+50, node.start[1]+25, itemNode.start[0], node.start[1]+25, width])
                            self.lines.append([itemNode.start[0]-5, node.start[1]+22, itemNode.start[0], node.start[1]+25, width])
                            self.lines.append([itemNode.start[0]-5, node.start[1]+28, itemNode.start[0], node.start[1]+25, width])
                            node.height = 50
                        else:
                            item = itemIn[0]
                            itemNode = self.schema.getNodeById(item)
                            width = 1
                            if itemNode.mouseOver:
                                width = 3
                            node.start = [itemNode.start[0]+180, itemNode.start[1]+70]
                            self.lines.append([itemNode.start[0]+nodeWidth, node.start[1]+25, node.start[0], node.start[1]+25, width])
                            self.lines.append([node.start[0]-5, node.start[1]+22, node.start[0], node.start[1]+25, width])
                            self.lines.append([node.start[0]-5, node.start[1]+28, node.start[0], node.start[1]+25, width])
                            node.height = 50

                subnodes = [x for x in subnodes if x.type!="question"]

                for node in subnodes:
                    if node.type == "process" and (node.subtype == "input" or node.subtype == "output"):
                        if node.subtype == "input":
                            itemLink = [y for x,y in zip(self.schema.connectionsA, self.schema.connectionsB) if x==node.nodeId]
                        elif node.subtype == "output":
                            itemLink = [x for x,y in zip(self.schema.connectionsA, self.schema.connectionsB) if y==node.nodeId]
                        
                        item = itemLink[0]
                        itemNode = self.schema.getNodeById(item)
                        node.start = [spaceW + (nodeWidth+spaceW)*i, itemNode.start[1]]
                        node.height = nodeHeight
                        res.append(node)
                        self.findPlace(res, node, maxH, spaceH)

                for node in subnodes:
                    if node.type == "process" and (node.subtype == "construct" or node.subtype == "refine"):
                        if node.subtype == "construct":
                            outItem = [y for x,y in zip(self.schema.connectionsA, self.schema.connectionsB) if x==node.nodeId][0]
                            inItems = [x for x,y in zip(self.schema.connectionsA, self.schema.connectionsB) if y==node.nodeId]
                            outItemNode = self.schema.getNodeById(outItem)
                            inItemNodes = [self.schema.getNodeById(x) for x in inItems]
                            levelOut = outItemNode.start[1]
                            levelsIn = [x.start[1] for x in inItemNodes]
                            level = (sum(levelsIn)/len(levelsIn)+levelOut)/2
                        elif node.subtype == "refine":
                            outItems = [y for x,y in zip(self.schema.connectionsA, self.schema.connectionsB) if x==node.nodeId]
                            inItem = [x for x,y in zip(self.schema.connectionsA, self.schema.connectionsB) if y==node.nodeId][0]
                            outItemNodes = [self.schema.getNodeById(x) for x in outItems]
                            inItemNode = self.schema.getNodeById(inItem)
                            levelsOut = [x.start[1] for x in outItemNodes]
                            levelIn = inItemNode.start[1]
                            level = (sum(levelsOut)/len(levelsOut)+levelIn)/2
                        
                        node.start = [spaceW + (nodeWidth+spaceW)*i, level]
                        node.height = nodeHeight
                        res.append(node)
                        self.findPlace(res, node, maxH, spaceH)

                if i!=len(placeholders)-1:
                    plc = placeholders[i+1]
                    for x in plc:
                        curPlc = [y for y in placeholders[i] if y.nextId==x.nodeId][0]
                        curPlc.start = [spaceW + (nodeWidth+spaceW)*i, x.start[1]]
                        subnodes.append(curPlc)
                        self.findPlace(subnodes, curPlc, maxH, spaceH)
            
            subnodes = [(x+y) for x,y in zip(levels, placeholders)]
            for i in range(len(subnodes)):
                subnodes[i] = [x for x in subnodes[i] if x.type!="question"]
                subnodes[i].sort(key = lambda z: z.start[1])
        
            connA = self.schema.connectionsA
            connB = self.schema.connectionsB
            questions = [x.nodeId for x in self.schema.nodes if x.type=="question"]
            joint = [(x,y) for x,y in zip(connA, connB) if x not in questions and y not in questions]
            connA = [x[0] for x in joint]
            connB = [x[1] for x in joint]

            for sub,i in zip(subnodes[:-1], range(len(subnodes)-1)):
                for node in sub:
                    if node.type != "placeholder":
                        conn = [y for x,y in zip(connA, connB) if x==node.nodeId]
                        for c in conn:
                            destNode = None
                            dest = [x for x in subnodes[i+1] if x.nodeId==c]
                            if len(dest)==1:
                                destNode = dest[0]
                            else:
                                for d,j in zip(subnodes[i+1], range(len(subnodes[i+1]))):
                                    if d.type=="placeholder" and d.prevId==node.nodeId:
                                        destNode = d
                                        subnodes[i+1] = subnodes[i+1][:j] + subnodes[i+1][j+1:]
                                        break
                            self.connect(node, destNode, nodeWidth)
                    else:
                        dest = [x for x in subnodes[i+1] if x.nodeId == node.nextId]
                        destNode = dest[0]
                        self.connect(node, destNode, nodeWidth)
    
            for node in self.schema.nodes:
                if node.start[0]>0:
                    n = self.placeNode(node, node.start[0], node.start[1])
                    if node.type!="question":
                        n.refresh.connect(self.refresh)
                        n.delete.connect(self.deleteNode)
                    if node.type == "process":
                        n.refreshSchema.connect(self.refreshSchema)
                    if node.type == "question":
                        n.clicked.connect(self.openContextMenu)

            self.placeholders = placeholders
    
            width = self.parent.width()
            height = self.parent.height()
            if maxW<width:
                maxW = width
            if maxH<height:
                maxH = height
            self.resize(maxW, maxH)

    def connect(self, node1, node2, nodeWidth):
        if node2 is None:
            return
        width = 1
        if node1.mouseOver or node2.mouseOver:
            width = 3

        add = 0
        if node1.type=="process" and node1.subtype=="input":
            add = 7
        self.lines.append([node1.start[0]+nodeWidth-add, node1.start[1]+node1.height/2, node1.start[0]+nodeWidth+20, node1.start[1]+node1.height/2, width])
        self.lines.append([node1.start[0]+nodeWidth+20, node1.start[1]+node1.height/2, node2.start[0]-20, node2.start[1]+node2.height/2, width])
        add = 0
        if node2.type=="process" and node2.subtype=="output":
            add = 7
        self.lines.append([node2.start[0]-20, node2.start[1]+node2.height/2, node2.start[0]+add, node2.start[1]+node2.height/2, width])
        
        self.lines.append([node2.start[0]-5+add, node2.start[1]+node2.height/2-3, node2.start[0]+add, node2.start[1]+node2.height/2, width])
        self.lines.append([node2.start[0]-5+add, node2.start[1]+node2.height/2+3, node2.start[0]+add, node2.start[1]+node2.height/2, width])
        if node2.type=="placeholder":
            self.lines.append([node2.start[0], node2.start[1]+node2.height/2, node2.start[0]+nodeWidth, node2.start[1]+node2.height/2, width])

    def findPlace(self, nodearr, node, maxH, spaceH):
        pr = False
        nodearr.sort(key = lambda x: x.start[1] + x.height/2)
        idx = [i for x,i in zip(nodearr, range(len(nodearr))) if x.nodeId==node.nodeId][0]
        if idx>0 and nodearr[idx-1].start[0] > 0 and nodearr[idx-1].start[1] + nodearr[idx-1].height + spaceH > node.start[1]:
            low = max(nodearr[idx-1].start[1], node.start[1])
            high = min(nodearr[idx-1].start[1]+nodearr[idx-1].height, node.start[1]+node.height)
            m = (low + high)/2
            nodearr[idx-1].start[1] = m - nodearr[idx-1].height - spaceH/2
            node.start[1] = m + spaceH/2
            self.shift(nodearr, node, maxH, spaceH)
            self.shift(nodearr, nodearr[idx-1], maxH, spaceH)
        elif idx<len(nodearr)-1 and nodearr[idx+1].start[0]>0 and nodearr[idx+1].start[1]<node.start[1]+node.height+spaceH:
            low = max(nodearr[idx-1].start[1], node.start[1])
            high = min(nodearr[idx-1].start[1]+nodearr[idx-1].height, node.start[1]+node.height)
            m = (low + high)/2
            node.start[1] = m - node.height - spaceH/2
            nodearr[idx-1].start[1] = m + spaceH/2
            self.shift(nodearr, node, maxH, spaceH)
            self.shift(nodearr, nodearr[idx-1], maxH, spaceH)
        
        if nodearr[0].start[1]<20:
            self.shift(nodearr, nodearr[0], maxH, spaceH, True)
        if nodearr[-1].start[1]+nodearr[-1].height>maxH-20:
            self.shift(nodearr, nodearr[-1], maxH, spaceH, True)

    def shift(self, nodearr, node, maxH, spaceH, limit = False):
        idx = [i for x,i in zip(nodearr, range(len(nodearr))) if x.nodeId==node.nodeId][0]
        if limit:
            if node.start[1]<spaceH:
                node.start[1] = spaceH
            if node.start[1]+node.height+spaceH>maxH:
                node.start[1] = maxH - node.height - spaceH

        while idx>0 and nodearr[idx-1].start[0]>0 and nodearr[idx-1].start[1] + nodearr[idx-1].height + spaceH > nodearr[idx].start[1]:
            nodearr[idx-1].start[1] = nodearr[idx].start[1] - nodearr[idx-1].height - spaceH
            idx -= 1
        while idx<len(nodearr)-1 and nodearr[idx+1].start[0]>0 and nodearr[idx+1].start[1] < nodearr[idx].start[1]+ nodearr[idx].height + spaceH :
            nodearr[idx+1].start[1] = nodearr[idx].start[1] + nodearr[idx].height + spaceH
            idx += 1

    def placeNode(self, node, startX, startY):
        nodeWidth = 160
        nodeHeight = 120
        node.rect = [startX, startY, startX + nodeWidth, startY + nodeHeight]
        if node.type == "item":
            res = ItemNodeFrame(self, node)
            res.setGeometry(startX, startY, nodeWidth, nodeHeight)
            self.nodeVisual.append(res)
        elif node.type=="planet":
            res = None
            #self.displayPlanet(qp, node, startX, startY)
        elif node.type=="question":
            res = QtWidgets.QPushButton(self)
            res.setText("?")
            
            connA = [x for x,y in zip(self.schema.connectionsA, self.schema.connectionsB) if y==node.nodeId]
            connB = [y for x,y in zip(self.schema.connectionsA, self.schema.connectionsB) if x==node.nodeId]
            if len(connA) == 1:
                res.type = "out"
                res.item = self.schema.getNodeById(connA[0]).item
            else:
                res.type = "in"
                res.item = self.schema.getNodeById(connB[0]).item
            
            res.setGeometry(startX, startY, 50, 50)
            res.setStyleSheet("QPushButton { border: 2px solid #FF4040; background-color: #505050; color: white; border-radius: 25}")
            self.nodeVisual.append(res)
        elif node.subtype=="input" or node.subtype=="output":
            res = IONodeFrame(self, node)
            res.setGeometry(startX, startY, nodeWidth, nodeHeight)
            self.nodeVisual.append(res)
        else:
            res = ProcessNodeFrame(self, node, self.itemRoot)
            res.setGeometry(startX, startY, nodeWidth, nodeHeight)
            self.nodeVisual.append(res)
        res.show()
        return res

    def redrawSchema(self, e=None):
        self.displaySchema()
    
    def refresh(self, e=None):
        self.displaySchema()
        self.repaint()
    
    def refreshSchema(self, e=None):
        self.schema.recalculate()
        self.displaySchema()
        self.repaint()
        self.summaryChanged.emit()
    
    def clearSchema(self):
        for ch in reversed(self.children()):
            ch.setParent(None)
        self.lines = []
    
    def deleteNode(self):
        nodeVisual = self.sender()
        node = nodeVisual.node
        if node.type == "process":
            self.schema.deleteProcess(node.nodeId)
        else: self.schema.deleteItem(node.nodeId)
        self.refresh()
    
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        for l in self.lines:
            pen = QtGui.QPen(QtGui.QColor(112, 112, 112), 1+l[4], Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(l[0], l[1], l[2], l[3])
        qp.end()

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('MimeItemListRow'):
            nameQBA = e.mimeData().data('MimeItemListRow')
            name = str(nameQBA.data(), encoding='utf-8')
            if name.endswith(".json"):
                e.accept()
    
    
    def dropEvent(self, e):
        nameQBA = e.mimeData().data('MimeItemListRow')
        name = str(nameQBA.data(), encoding='utf-8')
        item = items.Item.load(name, [])
        id = item.itemId
        self.schema.addIsolatedItem(self.itemRoot.find(id))
        self.refresh()
        e.accept()

    def openContextMenu(self):
        item = self.sender().item
        direction = self.sender().type
        if direction == "in":
            processes = item.inProcess
        else: processes = item.outProcess
        processes.sort()
        onPlanet = False
        if self.schema.currentPlanet is not None:
            onPlanet = True
        
        self.menu = QMenu(self)
        complexProcesses = []
        for proc in processes:
            name = self.getProcessName(proc, direction, onPlanet)
            if name != "complex" and name != "":
                a = self.menu.addAction(name)
                a.itemId = item.itemId
                a.id = proc
                a.triggered.connect(self.menuTriggered)
            elif name == "complex": complexProcesses.append(proc)

        if len(complexProcesses)>0:
            if ("Minerals" in item.categories or "Ice products" in item.categories) and direction=="in":
                submenu = QMenu(title="Refine")
                if "Ice products" in item.categories:
                    for proc in complexProcesses:
                        procC = self.procRoot.find(proc)
                        itemM = self.itemRoot.find(procC.material)
                        indOut = [i for x,i in zip(procC.items, range(len(procC.items))) if x==item.itemId][0]
                        quant = procC.quantityOut[indOut]
                        a = submenu.addAction(itemM.name + " (" + str(quant) + ")")
                        a.itemId = itemM.itemId
                        a.id = proc
                        a.triggered.connect(self.menuTriggered)
                else:
                    complexProcessesC = [self.procRoot.find(x) for x in complexProcesses]
                    indexes = [[i for y,i in zip(x.items, range(len(x.items))) if y==item.itemId][0] for x in complexProcessesC]
                    quantities = [x.quantityOut[i] for x,i in zip(complexProcessesC, indexes)]
                
                    categories = []
                    items = []
                    pr = []
                    quant = []
                    for proc, qnt in zip(complexProcesses, quantities):
                        procC = self.procRoot.find(proc)
                        itemM = self.itemRoot.find(procC.material)
                        if itemM.categories[-1] not in categories:
                            categories.append(itemM.categories[-1])
                            items.append([])
                            pr.append([])
                            quant.append([])
                        ind = [i for x,i in zip(categories, range(len(categories))) if x==itemM.categories[-1]][0]
                        items[ind].append(itemM)
                        pr[ind].append(proc)
                        quant[ind].append(qnt)
                    for cat, it, proc, q in zip(categories, items, pr, quant):
                        submenu2 = submenu.addMenu(cat)
                        for i,j,k in zip(it, proc, q):
                            a = submenu2.addAction(i.name + " (" + str(k) + ")")
                            a.itemId = i.itemId
                            a.id = j
                            a.triggered.connect(self.menuTriggered)
            elif "Gas Clouds Materials" in item.categories:
                submenu = QMenu(title="React")
                for proc in complexProcesses:
                    procC = self.procRoot.find(proc)
                    item = self.itemRoot.find(procC.item)
                    a = submenu.addAction(item.name)
                    a.itemId = item.itemId
                    a.id = proc
                    a.triggered.connect(self.menuTriggered)
            else:
                submenu = QMenu(title="Construct")
                procs = [self.procRoot.find(x) for x in complexProcesses]
                items = [self.itemRoot.find(x.item) for x in procs]
                self.fillConstructionSubmenus(submenu, items, complexProcesses)
    
            self.menu.addMenu(submenu)

        self.menu.exec_(QtGui.QCursor.pos())

    def fillConstructionSubmenus(self, menu, items, procs):
        categories = [x.categories for x in items]
        self.fillConstructionSubmenusR(menu, items, procs, categories, 0)
    
    def fillConstructionSubmenusR(self, menu, items, procs, categories, ind):
        if len(items)==1:
            a = menu.addAction(items[0].name)
            a.itemId = items[0].itemId
            a.id = procs[0]
            a.triggered.connect(self.menuTriggered)
            return
        if len(items[0].categories)==ind:
            for it, pr in zip(items, procs):
                a = menu.addAction(it.name)
                a.itemId = it.itemId
                a.id = pr
                a.triggered.connect(self.menuTriggered)
            return
        
        curCats = [x[ind] for x in categories]
        curCats = list(set(curCats))
        if len(curCats)==1:
            self.fillConstructionSubmenusR(menu, items, procs, categories, ind+1)
            return
        curCats.sort()
        for c in curCats:
            submenu = menu.addMenu(c)
            joint = [(x,y,z) for x,y,z in zip(items, procs, categories) if x.categories[ind]==c]
            curIt = [x[0] for x in joint]
            curProc = [x[1] for x in joint]
            curCat = [x[2] for x in joint]
            self.fillConstructionSubmenusR(submenu, curIt, curProc, curCat, ind+1)

    def getProcessName(self, procId, direction, onPlanet):
        if not onPlanet:
            if procId == 500000:
                return "Buy"
            elif procId == 500001:
                return "Collect"
            elif procId == 500002:
                if direction=="out":
                    return "Import"
                else: return ""
            elif procId == 500003:
                return "Sell"
            elif procId == 500004:
                return "Store"
            elif procId == 500005:
                if direction=="in":
                    return "Export"
                else: return ""
            elif procId>=500095 and procId<=500169:
                return "Compress"
            elif procId>=500170 and procId<=500178 and direction=="in":
                return "React"
            elif procId>=500235 and procId<=500384 and direction=="out":
                return "Refine"
            elif procId>=500006 and procId<=500026 and direction=="in":
                return "Construct"
            elif procId>=500179 and procId<=500234 and direction=="in":
                return "Construct"
            elif procId>=500027 and procId<=500094:
                return ""
            else: return "complex"
        else:
            if procId == 500002:
                if direction=="in":
                    return "Import"
                else: return ""
            elif procId == 500005:
                if direction=="out":
                    return "Export"
                else: return ""
            elif procId>=5000027 and procId<=500094 and direction=="in":
                return "Construct"
            elif procId>=500006 and procId<=500026:
                return ""
            elif procId>=500179 and procId<=500234:
                return ""
            else: return "complex"

    def menuTriggered(self):
        process = self.procRoot.find(self.sender().id, self.itemRoot.find(self.sender().itemId))
        self.schema.addProcess(process, self.itemRoot)
        self.refreshSchema()
