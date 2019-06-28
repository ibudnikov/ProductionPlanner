#!/usr/bin/env python3
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, Qt, QMimeData, QByteArray
from PyQt5.QtGui import QDrag
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QBrush
import os
import shutil
import darkdetect

import design
import newFileDialog
import items
import chars
import processes
import schema
import systems
import facilities

from new_file_dialog import *
from schema_list_row import *
from items_list_row import *
from tab_plus_widget import *
from custom_frame import *

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

version = "0.0.0"

#backend:
# Reverse engineering
# Planetary

#frontend:
# Tab close buttons disappearing problem (wait till PyQt upgrade)
# Style supporting -- switching icons for themes
# Redraw of widget with schema without direct method call
# Items close buttons style
# ? buttons style

class App(QtWidgets.QMainWindow, design.Ui_MainWindow):
    itemRoot = None
    procRoot = None
    char = None
    system = None
    facility = None
    
    openSchemas = [""]
    currentSchemaPath = "Schemas"
    currentItemsPath = "Items"
    procPath = "Processes"
    iconsPath = "Icons"
    
    schemasRoot = "Schemas"
    itemsRoot = "Items"
    
    newName = ""
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        if getattr(sys, 'frozen', False):
            self.currentItemsPath = sys._MEIPASS + "/" + self.currentItemsPath
            self.currentSchemaPath = sys._MEIPASS + "/" + self.currentSchemaPath
            self.itemsRoot = self.currentItemsPath
            self.schemasRoot = self.currentSchemaPath
            self.procPath = sys._MEIPASS + "/Processes"
            self.iconsPath = sys._MEIPASS + "/Icons"
        self.itemRoot=items.init(self.currentItemsPath)
        self.procRoot=processes.init(self.procPath, self.itemRoot)
        self.char = chars.init()
        self.system = systems.init()
        self.facility = facilities.init()
        self.setWindowTitle("Production planner  v"+version)
        self.buttonBack.clicked.connect(self.buttonBackClick)
        self.buttonAdd.clicked.connect(self.buttonAddClick)
        self.buttonAddDir.clicked.connect(self.buttonAddDirClick)
    
        self.mainFieldWidget = TabPlusWidget(parent=self)
        self.mainFieldWidget.setDocumentMode(True)
        self.mainFieldWidget.setObjectName("mainFieldWidget")
        self.horizontalLayout.addWidget(self.mainFieldWidget)
        
        self.buttonBack.setText("")
        self.buttonAdd.setText("")
        self.buttonAddDir.setText("")
        self.buttonBack.setIcon(QtGui.QIcon(QtGui.QPixmap(self.iconsPath+'/back.png')))
        self.buttonAdd.setIcon(QtGui.QIcon(QtGui.QPixmap(self.iconsPath+'/newFile.png')))
        self.buttonAddDir.setIcon(QtGui.QIcon(QtGui.QPixmap(self.iconsPath+'/newFolder.png')))
    
        tab = self.fillTabEmpty()
        self.mainFieldWidget.addTab(tab, "Empty")
    
        self.mainFieldWidget.plusClicked.connect(self.addTab)
    
    def closeEvent(self, event):
        widget = self.mainFieldWidget.currentWidget()
        if hasattr(widget, 'frame'):
            schema = widget.frame.schema
            schema.save()
    
    def schemaCopy(self):
        currentSchemaPath = self.currentSchemaPath
        oldFilename = currentSchemaPath + "/" + self.sender().name + ".json"
        newFileDialog = NewFileDialog(self)
        newFileDialog.exec_()
        if self.newName != "":
            names = [x for x in os.listdir(currentSchemaPath) if os.path.isfile(currentSchemaPath+"/"+x)]
            if self.newName+".json" in names:
                return
            newFilename = currentSchemaPath + "/"+self.newName + ".json"
            s = schema.Schema.load(oldFilename, self.char, self.system, self.facility, self.itemRoot, self.procRoot)
            s.filename = newFilename
            s.save()
            self.choseFile(newFilename)
            self.fillSchemasList(currentSchemaPath)
    
    def schemaRename(self):
        currentSchemaPath = self.currentSchemaPath
        if not self.sender().isDir:
            oldFilename = currentSchemaPath + "/" + self.sender().name + ".json"
            newFileDialog = NewFileDialog(self, self.sender().name)
            newFileDialog.exec_()
            index = -1
            for fn,i in zip(self.openSchemas, range(len(self.openSchemas))):
                if fn == oldFilename:
                    index = i
                    break
            if self.newName != "":
                names = [x for x in os.listdir(currentSchemaPath) if os.path.isfile(currentSchemaPath+"/"+x)]
                if self.newName+".json" in names:
                    return
                newFilename = currentSchemaPath + "/"+self.newName + ".json"
                os.rename(oldFilename, newFilename)
                if index!=-1:
                    self.mainFieldWidget.setTabText(index, self.newName)
                    self.mainFieldWidget.widget(index).label.setText(newFilename)
                    self.openSchemas[index] = newFilename
                self.fillSchemasList(currentSchemaPath)
        else:
            oldFilename = currentSchemaPath + "/" + self.sender().name
            newFileDialog = NewFileDialog(self)
            newFileDialog.exec_()
            indexes = []
            for fn,i in zip(self.openSchemas, range(len(self.openSchemas))):
                if fn.startswith(oldFilename):
                    indexes.append(i)
            if self.newName != "":
                names = [x for x in os.listdir(currentSchemaPath) if os.path.isfile(currentSchemaPath+"/"+x)]
                if self.newName in names:
                    return
                newFilename = currentSchemaPath + "/"+self.newName
                os.rename(oldFilename, newFilename)
                for i in indexes:
                    oldFile = self.openSchemas[i]
                    newFile = newFilename + oldFile[len(oldFilename):]
                    self.mainFieldWidget.widget(i).label.setText(newFile)
                    self.openSchemas[i] = newFile
                self.fillSchemasList(currentSchemaPath)
    
    def schemaDelete(self):
        currentSchemaPath = self.currentSchemaPath
        qm = QtWidgets.QMessageBox()
        message = "Do you really want to delete this schema?"
        if self.sender().isDir:
            message = "Do you really want to delete this directory and all it's schemas?"
        ret = qm.question(self,'', message, qm.Yes | qm.No)
        if ret == qm.Yes:
            if not self.sender().isDir:
                index = -1
                filename = currentSchemaPath + "/" + self.sender().name + ".json"
                for fn,i in zip(self.openSchemas, range(len(self.openSchemas))):
                    if fn == filename:
                        index = i
                        break
                if index!=-1:
                    self.mainFieldWidget.removeTab(index)
                os.remove(filename)
                self.fillSchemasList(currentSchemaPath)
            else:
                index = []
                filename = currentSchemaPath + "/" + self.sender().name
                for fn,i in zip(self.openSchemas, range(len(self.openSchemas))):
                    if fn.startswith(filename):
                        index.append(i)
                for i in index:
                    self.mainFieldWidget.removeTab(i)
                shutil.rmtree(filename)
                self.fillSchemasList(currentSchemaPath)
        return
    
    def addTab(self):
        tab = self.fillTabEmpty()
        self.mainFieldWidget.addTab(tab, "Empty")
        self.openSchemas.append("")
    
    def fillTabEmpty(self):
        tab = QtWidgets.QWidget()
        tab.setObjectName("tab")
        verticalLayout = QtWidgets.QVBoxLayout(tab)
        verticalLayout.setContentsMargins(0, 0, 0, 0)
        verticalLayout.setSpacing(0)
        verticalLayout.setObjectName("verticalLayout")
        return tab
    
    def fillTabContent(self, filename):
        tab = QtWidgets.QWidget()
        tab.setObjectName("tab")
        verticalLayout = QtWidgets.QVBoxLayout(tab)
        verticalLayout.setContentsMargins(0, 0, 0, 0)
        verticalLayout.setSpacing(0)
        verticalLayout.setObjectName("verticalLayout")
        
        tab.frame = CustomFrame(tab, self.itemRoot, self.procRoot)
        tab.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        tab.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        tab.frame.setObjectName("frame")
        tab.frame.summaryChanged.connect(self.refreshSummary)
        
        tab.scrollArea = QtWidgets.QScrollArea()
        tab.scrollArea.setBackgroundRole(QtGui.QPalette.Light)
        tab.scrollArea.setWidget(tab.frame)
        verticalLayout.addWidget(tab.scrollArea)
        
        tab.tableView = QtWidgets.QTableView(tab)
        tab.tableView.setMaximumSize(QtCore.QSize(16777215, 182))
        tab.tableView.setObjectName("tableView")
        verticalLayout.addWidget(tab.tableView)
        tab.label = QtWidgets.QLabel(filename, tab)
        tab.label.setMaximumSize(QtCore.QSize(16777215, 12))
        tab.label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        verticalLayout.addWidget(tab.label)
        
        s = schema.Schema.load(filename, self.char, self.system, self.facility, self.itemRoot, self.procRoot)
        summary = s.calculateSummary(self.char, self.system, self.facility, self.itemRoot)
        
        self.visualizeSchema(tab, s)
        self.visualizeSummary(tab.tableView, summary)
        return tab

    def visualizeSchema(self, tab, schema):
        tab.frame.schema = schema
        tab.frame.displaySchema()
        return

    def refreshSummary(self):
        summary = self.sender().schema.calculateSummary(self.char, self.system, self.facility, self.itemRoot)
        tableView = self.sender().parent.tableView
        self.visualizeSummary(tableView, summary)
    
    def visualizeSummary(self, table, summary):
        NpTableModel = QtGui.QStandardItemModel(parent=table)

        NpTableModel.setRowCount(6)
        NpTableModel.setColumnCount(8)
        
        item1 = QtGui.QStandardItem("In")
        item2 = QtGui.QStandardItem("Misc")
        item3 = QtGui.QStandardItem("Out")
        item4 = QtGui.QStandardItem("Summary")
        item1.setTextAlignment(Qt.AlignCenter)
        item2.setTextAlignment(Qt.AlignCenter)
        item3.setTextAlignment(Qt.AlignCenter)
        item4.setTextAlignment(Qt.AlignCenter)
        font = item1.font()
        font.setBold(True)
        item1.setFont(font)
        item2.setFont(font)
        item3.setFont(font)
        item4.setFont(font)
        NpTableModel.setItem(0,0,item1)
        NpTableModel.setItem(0,2,item2)
        NpTableModel.setItem(0,4,item3)
        NpTableModel.setItem(0,6,item4)
        
        item5 = QtGui.QStandardItem("Buy")
        item6 = QtGui.QStandardItem("Buy volume")
        item7 = QtGui.QStandardItem("Mining, estimate")
        item8 = QtGui.QStandardItem("Mining volume")
        NpTableModel.setItem(1,0,item5)
        NpTableModel.setItem(2,0,item6)
        NpTableModel.setItem(3,0,item7)
        NpTableModel.setItem(4,0,item8)
        
        buy = summary.totalBuy
        buyV = summary.totalBuyVolume
        aquire = summary.totalAquireEst
        aquireV = summary.totalAquireVolume
        itemV5 = QtGui.QStandardItem(self.getStrFromNumber(buy)+" ISK")
        itemV6 = QtGui.QStandardItem(self.getStrFromNumber(buyV)+" m3")
        itemV7 = QtGui.QStandardItem(self.getStrFromNumber(aquire)+" ISK")
        itemV8 = QtGui.QStandardItem(self.getStrFromNumber(aquireV)+" m3")
        itemV5.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV6.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV7.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV8.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        NpTableModel.setItem(1,1,itemV5)
        NpTableModel.setItem(2,1,itemV6)
        NpTableModel.setItem(3,1,itemV7)
        NpTableModel.setItem(4,1,itemV8)
        
        
        item9 = QtGui.QStandardItem("Customs tax")
        item10 = QtGui.QStandardItem("Production tax")
        item11 = QtGui.QStandardItem("Refining tax")
        item12 = QtGui.QStandardItem("Market tax")
        item13 = QtGui.QStandardItem("Interplanetary")
        NpTableModel.setItem(1,2,item9)
        NpTableModel.setItem(2,2,item10)
        NpTableModel.setItem(3,2,item11)
        NpTableModel.setItem(4,2,item12)
        NpTableModel.setItem(5,2,item13)
        
        customTax = summary.totalCustomsTax
        productionTax = summary.totalProductionTax
        refiningTax = summary.totalRefiningTax
        marketTax = summary.totalMarketTax
        interplanetary = summary.totalInterplanetaryShipment
        itemV9 = QtGui.QStandardItem(self.getStrFromNumber(customTax)+" ISK")
        itemV10 = QtGui.QStandardItem(self.getStrFromNumber(productionTax)+" ISK")
        itemV11 = QtGui.QStandardItem(self.getStrFromNumber(refiningTax)+" ISK")
        itemV12 = QtGui.QStandardItem(self.getStrFromNumber(marketTax)+" ISK")
        itemV13 = QtGui.QStandardItem(self.getStrFromNumber(interplanetary)+" m3")
        itemV9.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV10.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV11.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV12.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV13.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        NpTableModel.setItem(1,3,itemV9)
        NpTableModel.setItem(2,3,itemV10)
        NpTableModel.setItem(3,3,itemV11)
        NpTableModel.setItem(4,3,itemV12)
        NpTableModel.setItem(5,3,itemV13)
        
        item14 = QtGui.QStandardItem("Sell")
        item15 = QtGui.QStandardItem("Sell volume")
        item16 = QtGui.QStandardItem("Store, estimate")
        item17 = QtGui.QStandardItem("Store volume")
        NpTableModel.setItem(1,4,item14)
        NpTableModel.setItem(2,4,item15)
        NpTableModel.setItem(3,4,item16)
        NpTableModel.setItem(4,4,item17)
        
        sell = summary.totalSell
        sellV = summary.totalSellVolume
        store = summary.totalStoreEst
        storeV = summary.totalStoreVolume
        itemV14 = QtGui.QStandardItem(self.getStrFromNumber(sell)+" ISK")
        itemV15 = QtGui.QStandardItem(self.getStrFromNumber(sellV)+" m3")
        itemV16 = QtGui.QStandardItem(self.getStrFromNumber(store)+" ISK")
        itemV17 = QtGui.QStandardItem(self.getStrFromNumber(storeV)+" m3")
        itemV14.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV15.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV16.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV17.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        NpTableModel.setItem(1,5,itemV14)
        NpTableModel.setItem(2,5,itemV15)
        NpTableModel.setItem(3,5,itemV16)
        NpTableModel.setItem(4,5,itemV17)
        
        item18 = QtGui.QStandardItem("Income")
        item19 = QtGui.QStandardItem("Expenses")
        item20 = QtGui.QStandardItem("Profit")
        item21 = QtGui.QStandardItem("Profit w/o mining")
        item22 = QtGui.QStandardItem("Profit, %")
        item18.setFont(font)
        item19.setFont(font)
        item20.setFont(font)
        item21.setFont(font)
        item22.setFont(font)
        NpTableModel.setItem(1,6,item18)
        NpTableModel.setItem(2,6,item19)
        NpTableModel.setItem(3,6,item20)
        NpTableModel.setItem(4,6,item21)
        NpTableModel.setItem(5,6,item22)
        
        exp = buy + customTax + productionTax + refiningTax + marketTax
        profit = sell - exp
        profitWOMining = profit - aquire
        if exp + aquire > 0:
            profitPer = profitWOMining * 100/ (exp + aquire)
            profitPerStr = str(round(profitPer,2)) + "%"
            if profitPer>0:
                profitPerStr = "+"+profitPerStr
        itemV18 = QtGui.QStandardItem(self.getStrFromNumber(sell)+" ISK")
        itemV19 = QtGui.QStandardItem(self.getStrFromNumber(exp)+" ISK")
        itemV20 = QtGui.QStandardItem(self.getStrFromNumber(profit)+" ISK")
        itemV21 = QtGui.QStandardItem(self.getStrFromNumber(profitWOMining)+" ISK")
        itemV18.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV19.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV20.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV21.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
        itemV18.setFont(font)
        itemV19.setFont(font)
        itemV20.setFont(font)
        itemV21.setFont(font)
        NpTableModel.setItem(1,7,itemV18)
        NpTableModel.setItem(2,7,itemV19)
        NpTableModel.setItem(3,7,itemV20)
        NpTableModel.setItem(4,7,itemV21)
        if exp>0:
            itemV22 = QtGui.QStandardItem(profitPerStr)
            itemV22.setTextAlignment(Qt.AlignVCenter|Qt.AlignRight)
            itemV22.setFont(font)
            NpTableModel.setItem(5,7,itemV22)
        
        table.setModel(NpTableModel)
        table.setSpan(0,0,1,2)
        table.setSpan(0,2,1,2)
        table.setSpan(0,4,1,2)
        table.setSpan(0,6,1,2)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


    def getStrFromNumber(self, number):
        number = round(number, 2)
        if number<1000:
            return str(number)
        elif number<1000000:
            number = number/1000
            number = round(number, 2)
            return str(number)+"K"
        elif number<1000000000:
            number = number/1000000
            number = round(number, 2)
            return str(number)+"M"
        else:
            number = number/1000000000
            number = round(number, 2)
            return str(number)+"B"
    
    def buttonBackClick(self):
        if self.currentSchemaPath=="Schemas":
            return
        self.currentSchemaPath = self.currentSchemaPath[:self.currentSchemaPath.rfind('/')]
        self.fillSchemasList(self.currentSchemaPath)

    def buttonAddClick(self):
        currentSchemaPath = self.currentSchemaPath
        newFileDialog = NewFileDialog(self)
        newFileDialog.exec_()
        if self.newName != "":
            names = [x for x in os.listdir(currentSchemaPath) if os.path.isfile(currentSchemaPath+"/"+x)]
            if self.newName+".json" in names:
                return
            filename = currentSchemaPath + "/"+self.newName + ".json"
            s = schema.Schema(self.char, self.system, self.facility, self.itemRoot)
            s.filename = filename
            s.save()
            self.choseFile(filename)
            self.fillSchemasList(currentSchemaPath)

    def buttonAddDirClick(self):
        currentSchemaPath = self.currentSchemaPath
        newFileDialog = NewFileDialog(self)
        newFileDialog.exec_()
        if self.newName != "":
            names = [x for x in os.listdir(currentSchemaPath) if os.path.isdir(currentSchemaPath+"/"+x)]
            if self.newName in names:
                return
            filename = currentSchemaPath + "/"+self.newName
            os.mkdir(filename)
            self.fillSchemasList(currentSchemaPath)

            
    def choseFile(self, filename):
        for fn,i in zip(self.openSchemas, range(len(self.openSchemas))):
            if fn == filename:
                self.mainFieldWidget.setCurrentIndex(i)
                return
        index = self.mainFieldWidget.currentIndex()
        newtab = self.fillTabContent(filename)
        name = filename[filename.rfind("/")+1:-5]
        self.mainFieldWidget.insertTab(index, newtab, name)
        self.mainFieldWidget.removeTab(index+1)
        self.mainFieldWidget.setCurrentIndex(index)
        self.openSchemas[index] = filename
        
            
    def dirClick(self):
        name = self.sender().name
        if name=='..':
            self.currentSchemaPath = self.currentSchemaPath[:self.currentSchemaPath.rfind('/')]
        else: self.currentSchemaPath = self.currentSchemaPath+'/'+name
        self.fillSchemasList(self.currentSchemaPath)

    def itemsDirClick(self):
        name = self.sender().name
        if name=='..':
            self.currentItemsPath = self.currentItemsPath[:self.currentItemsPath.rfind('/')]
        else: self.currentItemsPath = self.currentItemsPath+'/'+name
        self.fillItemsView()

    def fileClick(self):
        currentSchemaPath = self.currentSchemaPath
        name = currentSchemaPath+'/'+self.sender().name + '.json'
        self.choseFile(name)
    
    def redrawSchemas(self):
        self.fillSchemasList(self.currentSchemaPath)

    def redrawItems(self):
        self.fillItemsView()
    
    def fillSchemasList(self, path="Schemas"):
        root = False
        if path == self.schemasRoot:
            root = True
            self.buttonBack.setEnabled(False)
        else: self.buttonBack.setEnabled(True)
        count = self.schemasList.count()
        for i in range(count):
            if self.schemasList.item(count-i-1).isHidden():
                self.schemasList.removeItemWidget(self.schemasList.item(count-i-1))
        for i in range(self.schemasList.count()):
            self.schemasList.item(i).setHidden(True)
        directory = path
        files = [x for x in os.listdir(directory) if x[0]!='.' and x[-1]!='~']
        dirs = [x for x in files if os.path.isdir(path + "/"+x)]
        files = [x for x in files if os.path.isfile(path + "/"+x)]
        dirs.sort()
        if not root:
            dirs = ['..']+dirs
        files.sort()
        
        for file_name in dirs:
            item = QListWidgetItem(self.schemasList)
            self.schemasList.addItem(item)
            row = SchemaListRow(file_name, True, self.iconsPath, self)
            item.setSizeHint(row.minimumSizeHint())
            self.schemasList.setItemWidget(item, row)
            row.clicked.connect(self.dirClick)
            row.redraw.connect(self.redrawSchemas)
            row.rename.connect(self.schemaRename)
            row.delete.connect(self.schemaDelete)
        for file_name in files:
            item = QListWidgetItem(self.schemasList)
            self.schemasList.addItem(item)
            row = SchemaListRow(file_name[:-5], False, self.iconsPath, self)
            item.setSizeHint(row.minimumSizeHint())
            self.schemasList.setItemWidget(item, row)
            row.clicked.connect(self.fileClick)
            row.copy.connect(self.schemaCopy)
            row.rename.connect(self.schemaRename)
            row.delete.connect(self.schemaDelete)

    def fillItemsView(self):
        root = False
        path = self.currentItemsPath
        if path == self.itemsRoot:
            root = True
        count = self.itemsView.count()
        for i in range(count):
            if self.itemsView.item(count-i-1).isHidden():
                self.itemsView.removeItemWidget(self.itemsView.item(count-i-1))
        for i in range(self.itemsView.count()):
            self.itemsView.item(i).setHidden(True)
        files = [x for x in os.listdir(path) if x[0]!='.' and x[-1]!='~']
        dirs = [x for x in files if os.path.isdir(path + "/" + x)]
        dirs = [x for x in dirs if x!="BPO"]
        files = [x for x in files if os.path.isfile(path + "/" + x)]
        dirs.sort()
        if not root:
            dirs = ['..']+dirs
        files.sort()
        
        for file_name in dirs:
            item = QListWidgetItem(self.itemsView)
            self.itemsView.addItem(item)
            row = ItemListRow(file_name, True, self.iconsPath, self)
            item.setSizeHint(row.minimumSizeHint())
            self.itemsView.setItemWidget(item, row)
            row.clicked.connect(self.itemsDirClick)
            row.redraw.connect(self.redrawItems)
        for file_name in files:
            item = QListWidgetItem(self.itemsView)
            self.itemsView.addItem(item)
            row = ItemListRow(file_name[:-5], False, self.iconsPath, self)
            item.setSizeHint(row.minimumSizeHint())
            self.itemsView.setItemWidget(item, row)

def main():
    if getattr(sys, 'frozen', False):
        path = sys._MEIPASS
    
    app = QtWidgets.QApplication(sys.argv)
    theme = darkdetect.theme()
    if theme=="Dark":
        dark_palette = QPalette()

        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.AlternateBase, QColor(253, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.gray)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(12, 90, 198))
        dark_palette.setColor(QPalette.HighlightedText, Qt.white)
        dark_palette.setColor(QPalette.Light, QColor(53, 53, 53))

        app.setPalette(dark_palette)


    window = App()
    
    window.fillSchemasList(window.currentSchemaPath)
    window.fillItemsView()

    window.showMaximized()
    app.exec_()  

if __name__ == '__main__':
    main()
