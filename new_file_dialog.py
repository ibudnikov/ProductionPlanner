from PyQt5 import QtWidgets
import newFileDialog
from PyQt5.QtCore import Qt

class NewFileDialog(QtWidgets.QDialog, newFileDialog.Ui_newFileDialogBox):
    parent = None
    name = ""
    def __init__(self, parent, name=""):
        super().__init__()
        self.name = name
        self.parent = parent
        self.setupUi(self)
        self.buttonOk.clicked.connect(self.buttonOkClick)
        self.buttonCancel.clicked.connect(self.buttonCancelClick)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        if self.name != "":
            self.lineEdit.setText(self.name)
    
    def buttonOkClick(self):
        res = self.lineEdit.text()
        allowedChars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_ "
        resFiltered = ""
        for c in res:
            if c in allowedChars:
                resFiltered += c
        self.parent.newName = resFiltered[:26]
        self.close()
    
    def buttonCancelClick(self):
        self.parent.newName = ""
        self.close()
