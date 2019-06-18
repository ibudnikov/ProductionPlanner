from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, Qt, QMimeData, QByteArray
from PyQt5.QtGui import QDrag

class ItemListRow(QWidget):
    isDir = False
    name = ""
    clicked = pyqtSignal()
    redraw = pyqtSignal()
    parent = None
    iconPath = ""
    def __init__(self, name, isDir, iconPath, parent=None):
        self.name = name
        self.parent = parent
        self.iconPath = iconPath
        super(ItemListRow, self).__init__(parent)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(0)
        self.row = layout
        if isDir:
            gv = QLabel("")
            gv.setScaledContents(True)
            gv.setPixmap(QtGui.QPixmap(iconPath+'/folder.png'))
            self.isDir = True
        else:
            gv = QLabel("")
            gv.setScaledContents(True)
            gv.setPixmap(QtGui.QPixmap(iconPath+'/file.png'))
        gv.setMinimumSize(QtCore.QSize(16, 16))
        gv.setMaximumSize(QtCore.QSize(16, 16))
        self.row.addWidget(gv)
        hs = QSpacerItem(5,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.row.addItem(hs)
        self.row.addWidget(QLabel(name))
        if isDir:
            self.setAcceptDrops(True)
        else: self.setAcceptDrops(False)
                        
        self.setLayout(self.row)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.isDir:
                self.clicked.emit()
                event.accept()

    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return
        
        mimeData = QMimeData()
        
        drag = QDrag(self)
        dragMimeData = QtCore.QMimeData()
        mime = self.parent.currentItemsPath + "/" + self.name
        if not self.isDir:
            mime = mime+'.json'
        mime = mime
        mime = bytes(mime, encoding='utf8')
        dragMimeData.setData('MimeItemListRow', QByteArray(mime))
        drag.setMimeData(dragMimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        
        dropAction = drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('MimeItemListRow'):
            e.accept()
        else: e.reject()

    def dropEvent(self, e):
        nameQBA = e.mimeData().data('MimeItemListRow')
        name = str(nameQBA.data(), encoding='utf-8')
        name = name[name.rfind('/')+1:]
        if self.isDir:
            if name == self.name:
                self.clicked.emit()
                e.accept()
