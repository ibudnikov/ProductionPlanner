from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, Qt, QMimeData, QByteArray
from PyQt5.QtGui import QDrag
import os

class SchemaListRow(QWidget):
    isDir = False
    name = ""
    clicked = pyqtSignal()
    redraw = pyqtSignal()
    copy = pyqtSignal()
    rename = pyqtSignal()
    delete = pyqtSignal()
    iconPath = ""
    parent = None
    def __init__(self, name, isDir, iconPath, parent=None):
        self.name = name
        self.parent = parent
        self.iconPath = iconPath
        super(SchemaListRow, self).__init__(parent)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(0)
        self.row = layout
        if isDir:
            gv = QLabel("")
            gv.setScaledContents(True)
            gv.setPixmap(QtGui.QPixmap(iconPath+'/folder.png'))
            self.isDir = True
        else: gv = QLabel("")
        gv.setMinimumSize(QtCore.QSize(16, 16))
        gv.setMaximumSize(QtCore.QSize(16, 16))
        self.row.addWidget(gv)
        hs = QSpacerItem(5,0,QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.row.addItem(hs)
        self.row.addWidget(QLabel(name))
        if name!="..":
            if not isDir:
                cop = QPushButton("")
                iconCop = QtGui.QIcon()
                iconCop.addPixmap(QtGui.QPixmap(iconPath+'/copy.png'))
                cop.setIcon(iconCop)
                self.row.addWidget(cop)
                cop.clicked.connect(self.copyClicked)
                cop.setMinimumSize(QtCore.QSize(32, 32))
                cop.setMaximumSize(QtCore.QSize(32, 32))
            
            ren = QPushButton("")
            renCop = QtGui.QIcon()
            renCop.addPixmap(QtGui.QPixmap(iconPath+'/rename.png'))
            ren.setIcon(renCop)
            ren.setMinimumSize(QtCore.QSize(32, 32))
            ren.setMaximumSize(QtCore.QSize(32, 32))
            ren.clicked.connect(self.renameClicked)
            self.row.addWidget(ren)
            delB = QPushButton("")
            delCop = QtGui.QIcon()
            delCop.addPixmap(QtGui.QPixmap(iconPath+'/delete.png'))
            delB.setIcon(delCop)
            delB.setMinimumSize(QtCore.QSize(32, 32))
            delB.setMaximumSize(QtCore.QSize(32, 32))
            delB.clicked.connect(self.deleteClicked)
            self.row.addWidget(delB)

        self.setAcceptDrops(True)

        self.setLayout(self.row)
    
    def copyClicked(self):
        self.copy.emit()
    
    def renameClicked(self):
        self.rename.emit()
    
    def deleteClicked(self):
        self.delete.emit()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
    
    def mouseMoveEvent(self, e):
        
        if e.buttons() != Qt.LeftButton:
            return
        
        mimeData = QMimeData()
        
        drag = QDrag(self)
        dragMimeData = QtCore.QMimeData()
        mime = self.name
        if not self.isDir:
            mime = mime+'.json'
        mime = bytes(mime, encoding='utf8')
        dragMimeData.setData('MimeSchemaListRow', QByteArray(mime))
        drag.setMimeData(dragMimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        
        dropAction = drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('MimeSchemaListRow'):
            e.accept()
        else: e.reject()
    
    
    def dropEvent(self, e):
        currentSchemaPath = self.parent.currentSchemaPath
        nameQBA = e.mimeData().data('MimeSchemaListRow')
        name = str(nameQBA.data(), encoding='utf-8')
        if self.isDir:
            if name == self.name:
                self.clicked.emit()
                return
            oldName = currentSchemaPath + '/' + name
            if self.name!="..":
                newName = currentSchemaPath + '/' + self.name + '/' + name
            else: newName = currentSchemaPath[:currentSchemaPath.rfind('/')] + '/' + name
            os.rename(oldName, newName)
            self.redraw.emit()
        else:
            if name == self.name+".json":
                self.clicked.emit()
