from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, Qt

class Placeholder:
    start = [-1,-1]
    height = -1
    type = ""
    nodeId = ""
    prevId = -1
    nextId = -1
    sublevel = -1
    mouseOver = False
    def __init__(self, startX, startY, height, nodeId, prevId, nextId, sublevel):
        self.start = [startX, startY]
        self.height = height
        self.type = "placeholder"
        self.nodeId = nodeId
        self.prevId = prevId
        self.nextId = nextId
        self.sublevel = sublevel
        self.mouseOver = False

class ItemNodeFrame(QtWidgets.QFrame):
    parent = None
    node = None
    complete = False
    isolated = False
    refresh = pyqtSignal()
    delete = pyqtSignal()
    def __init__(self, parent, node):
        super().__init__(parent)
        self.parent = parent
        self.node = node
        self.isolated = node.isolated
        item = node.item
        background = "#BFA730"  #yellow
        if "Planetary" in item.categories:
            background = "#86B32D"
        elif "Standard ores" in item.categories or "Minerals" in item.categories:
            background = "#BF3030"
        elif "Ice ores" in item.categories or "Ice products" in item.categories:
            background = "#1D7373"
        if node.quantityIn == node.quantityOut and node.quantityIn!=0:
            self.complete = True
        if not self.complete:
            self.setStyleSheet("QFrame{ border: 2px solid #FF4040; background-color: #505050; color: white;}")
        else: self.setStyleSheet("QFrame{ border: 2px solid #707070; background-color: "+"#505050"+"; color: white;}")

        self.frame = QFrame(self)
        self.frame.setStyleSheet("QFrame{ border:0px; background-color: "+background+"}")
        if self.complete:
            self.labelQuantity = QLabel(self)
            self.labelQuantity.setText(str(node.quantityIn))
            self.labelQuantity.setAlignment(Qt.AlignHCenter|Qt.AlignBottom)
            self.labelQuantity.setStyleSheet("QLabel{ border: 0px}")
        else:
            self.labelQuantityIn = QLabel(self)
            self.labelQuantityIn.setText(str(node.quantityIn))
            self.labelQuantityIn.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
            self.labelQuantityIn.setStyleSheet("QLabel{ border: 0px}")
            self.labelQuantityOut = QLabel(self)
            self.labelQuantityOut.setText(str(node.quantityOut))
            self.labelQuantityOut.setAlignment(Qt.AlignRight|Qt.AlignBottom)
            self.labelQuantityOut.setStyleSheet("QLabel{ border: 0px}")
        self.labelName = QLabel(self)
        self.labelName.setWordWrap(True)
        self.labelName.setText(item.name)
        self.labelName.setAlignment(Qt.AlignCenter)
        self.labelName.setStyleSheet("QLabel{ border: 0px}")
        if self.isolated:
            self.close = QPushButton(self)
            self.close.setText("x")
            self.close.clicked.connect(self.deleteSelf)
            #self.close.setStyleSheet("QPushButton{ border: 1px solid white; border-radius: 3px; margin: 2px; background-color:"+background+"} QPushButton:pressed{ background-color:#888888}")

    def resizeEvent(self, e):
        self.frame.setGeometry(2,2,12,self.height()-4)
        if self.complete:
            self.labelQuantity.setGeometry(16, self.height()/2, self.width()-18, self.height()/2-7)
        else:
            self.labelQuantityIn.setGeometry(19, self.height()/2, self.width()/2-17, self.height()/2-7)
            self.labelQuantityOut.setGeometry(self.width()/2+12, self.height()/2, self.width()/2-19, self.height()/2-7)
        self.labelName.setGeometry(16, 2, self.width()-18, 2*self.height()/3-2)
        if self.isolated:
            self.close.setGeometry(self.width()-26, -2, 30, 30)

    def deleteSelf(self):
        self.delete.emit()
    
    def enterEvent(self, event):
        self.node.mouseOver = True
        self.refresh.emit()
    
    def leaveEvent(self, event):
        self.node.mouseOver = False
        self.refresh.emit()

class ProcessNodeFrame(QtWidgets.QFrame):
    parent = None
    node = None
    background = ""
    refresh = pyqtSignal()
    refreshSchema = pyqtSignal()
    delete = pyqtSignal()
    def __init__(self, parent, node, itemRoot):
        super().__init__(parent)
        self.parent = parent
        self.node = node
        process = node.process
        if node.subtype == "refine":
            item = itemRoot.find(process.items[0])
        else: item = itemRoot.find(process.item)
        self.background = "#BFA730"  #yellow
        if "Planetary" in item.categories:
            self.background = "#86B32D" # green
        elif "Standard ores" in item.categories or "Minerals" in item.categories:
            self.background = "#BF3030" # red
        elif "Ice ores" in item.categories or "Ice products" in item.categories:
            self.background = "#1D7373" # blue
        self.close = QPushButton(self)
        self.close.setText("x")
        self.close.clicked.connect(self.deleteSelf)
        self.sb = QSpinBox(self)
        self.sb.setMinimum(1)
        self.sb.setMaximum(9999999)
        self.sb.setFocusPolicy( Qt.StrongFocus )
        self.sb.setValue(node.quantity)
        self.sb.valueChanged.connect(self.adjustValue)
        self.expLabel = QLabel(self)
        self.expLabel.setText("Exp:")
        self.expLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.expLabel.setStyleSheet("QLabel{ border: 0px;  color: white}")
        self.expenses = QLabel(self)
        expInt = round(node.expense)
        if expInt>=1000000000:
            expStr = str(round(expInt/1000000000, 2))+"B"
        elif expInt>=1000000:
            expStr = str(round(expInt/1000000, 2))+"M"
        elif expInt>=1000:
            expStr = str(round(expInt/1000, 2))+"K"
        else: expStr = str(expInt)
        self.expenses.setText(expStr)
        self.expenses.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.expenses.setStyleSheet("QLabel{ border: 0px;  color: white}")

    def resizeEvent(self, e):
        self.setStyleSheet("QFrame{ border: 2px solid #707070; background-color: "+self.background+"; border-radius: "+str(self.height()/2)+"}")
        self.close.setGeometry(self.width()-40, 20, 30, 30)
        self.sb.setGeometry(22, 20, int(0.54*self.width()), 30)
        self.expLabel.setGeometry(20, self.height()/2, self.width()/4-5, self.height()/2-20)
        self.expenses.setGeometry(self.width()/4+20, self.height()/2, 3*self.width()/4-45, self.height()/2-20)
    
    def deleteSelf(self):
        self.delete.emit()
    
    def enterEvent(self, event):
        self.node.mouseOver = True
        self.refresh.emit()
    
    def leaveEvent(self, event):
        self.node.mouseOver = False
        self.refreshSchema.emit()
    
    def adjustValue(self):
        self.node.quantity = self.sb.value()

class IONodeFrame(QtWidgets.QFrame):
    parent = None
    node = None
    marketConnection = False
    refresh = pyqtSignal()
    refreshSchema = pyqtSignal()
    delete = pyqtSignal()
    def __init__(self, parent, node):
        super().__init__(parent)
        self.parent = parent
        self.node = node
        process = node.process
        titletext = ""
        if node.subtype == "input" and node.subtype2 == "buy":
            titletext = "Buy"
            self.marketConnection = True
        if node.subtype == "input" and node.subtype2 == "aquire":
            if "Salvage materials" in node.process.item.categories:
                titletext = "Salvaging"
            elif "Research Equipment" in node.process.item.categories:
                titletext = "Hacking"
            else: titletext = "Mining"
        if node.subtype == "input" and node.subtype2 == "export":
            titletext = "Export"
        if node.subtype == "output" and node.subtype2 == "sell":
            titletext = "Sell"
            self.marketConnection = True
        if node.subtype == "output" and node.subtype2 == "store":
            titletext = "Store"
        if node.subtype == "output" and node.subtype2 == "import":
            titletext = "Import"
        item = process.item
        self.title = QLabel(self)
        self.title.setText(titletext)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("QLabel{ border: 0px;  color: white}")
        self.close = QPushButton(self)
        self.close.setText("x")
        self.close.clicked.connect(self.deleteSelf)
        self.sb = QSpinBox(self)
        self.sb.setMinimum(1)
        self.sb.setMaximum(9999999)
        self.sb.setFocusPolicy( Qt.StrongFocus )
        self.sb.installEventFilter(self)
        self.sb.setValue(node.quantity)
        self.sb.valueChanged.connect(self.adjustValue)
        self.expLabel = QLabel(self)
        self.expLabel.setText("Exp:")
        self.expLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.expLabel.setStyleSheet("QLabel{ border: 0px;  color: white}")
        self.expenses = QLabel(self)
        expInt = round(node.expense)
        if expInt>=1000000000:
            expStr = str(round(expInt/1000000000, 2))+"B"
        elif expInt>=1000000:
            expStr = str(round(expInt/1000000, 2))+"M"
        elif expInt>=1000:
            expStr = str(round(expInt/1000, 2))+"K"
        else: expStr = str(expInt)
        self.expenses.setText(expStr)
        self.expenses.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.expenses.setStyleSheet("QLabel{ border: 0px;  color: white}")

        if self.marketConnection:
            self.priceLabel = QLabel(self)
            self.priceLabel.setText("ISK:")
            self.priceLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self.priceLabel.setStyleSheet("QLabel{ border: 0px;  color: white}")
            
            self.price = QLabel(self)
            priceInt = round(node.price)
            if priceInt>=1000000000:
                priceStr = str(round(priceInt/1000000000, 2))+"B"
            elif priceInt>=1000000:
                priceStr = str(round(priceInt/1000000, 2))+"M"
            elif priceInt>=1000:
                priceStr = str(round(priceInt/1000, 2))+"K"
            else: priceStr = str(priceInt)
            self.price.setText(priceStr)
            self.price.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.price.setStyleSheet("QLabel{ border: 0px;  color: white}")

            self.methodLabel = QLabel(self)
            self.methodLabel.setText("Orders:")
            self.methodLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self.methodLabel.setStyleSheet("QLabel{ border: 0px;  color: white}")
                
            self.rbBuy = QRadioButton(self)
            self.rbBuy.setText("Buy")
            self.rbSell = QRadioButton(self)
            self.rbSell.setText("Sell")
            font = self.rbBuy.font()
            font.setPixelSize(11)
            self.rbBuy.setFont(font)
            self.rbSell.setFont(font)
            self.rbBuy.setStyleSheet("QRadioButton{ color: white}")
            self.rbSell.setStyleSheet("QRadioButton{ color: white}")
            self.rbBuy.clicked.connect(self.adjustMethod)
            self.rbSell.clicked.connect(self.adjustMethod)
            if node.method == "sell":
                self.rbSell.setChecked(True)
            else: self.rbBuy.setChecked(True)

    def resizeEvent(self, e):
        self.close.setGeometry(self.width()-30, 0, 30, 30)
        self.title.setGeometry(0.115*self.width(), 2, 0.885*self.width(), 15)
        if not self.marketConnection:
            self.sb.setGeometry(22, 20, int(0.54*self.width()), 30) # 70, 30
            self.expLabel.setGeometry(20, self.height()/2, self.width()/4-5, self.height()/2-10)
            self.expenses.setGeometry(self.width()/4+20, self.height()/2, 3*self.width()/4-45, self.height()/2-10)
        else:
            self.sb.setGeometry(22, 20, int(0.54*self.width()), 30) # 70, 30
            self.expLabel.setGeometry(20, 50, self.width()/4-5, (self.height()-40)/4)
            self.expenses.setGeometry(self.width()/4+20, 50, 3*self.width()/4-45, (self.height()-40)/4)
            self.priceLabel.setGeometry(20, 50+(self.height()-40)/4, self.width()/4-5, (self.height()-40)/4)
            self.price.setGeometry(self.width()/4+20, 50+(self.height()-40)/4, 3*self.width()/4-45, (self.height()-40)/4)
            self.methodLabel.setGeometry(10, 40+(self.height()-40)/2, self.width()/2-5, (self.height()-40)/2)
            self.rbBuy.setGeometry(self.width()/2, 42+(self.height()-40)/2, self.width()/2-5, 1.1*(self.height()-40)/4)
            self.rbSell.setGeometry(self.width()/2, 39+3*(self.height()-40)/4, self.width()/2-5, 1.1*(self.height()-40)/4)

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Wheel:
            event.ignore()
            return True
        return False
                                    
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QtGui.QPen(QtGui.QColor(112, 112, 112), 2, Qt.SolidLine))
        qp.setBrush(QtGui.QColor(65, 44, 132))
        polygon = QtGui.QPolygonF()
        frac = round(0.115*self.width())

        polygon.append(QtCore.QPointF(frac, 0))
        polygon.append(QtCore.QPointF(self.width(), 0))
        polygon.append(QtCore.QPointF(self.width()-frac, self.height()))
        polygon.append(QtCore.QPointF(0, self.height()))
                                        
        qp.drawPolygon(polygon)
        qp.end()

    def deleteSelf(self):
        self.delete.emit()

    def enterEvent(self, event):
        self.node.mouseOver = True
        self.refresh.emit()

    def leaveEvent(self, event):
        self.node.mouseOver = False
        self.refreshSchema.emit()

    def adjustValue(self):
        self.node.quantity = self.sb.value()
    
    def adjustMethod(self):
        if self.rbSell.isChecked():
            self.node.method = "sell"
        else: self.node.method = "buy"
