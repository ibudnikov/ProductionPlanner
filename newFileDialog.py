# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newFileDialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_newFileDialogBox(object):
    def setupUi(self, newFileDialogBox):
        newFileDialogBox.setObjectName("newFileDialogBox")
        newFileDialogBox.setWindowModality(QtCore.Qt.WindowModal)
        newFileDialogBox.resize(200, 70)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(newFileDialogBox.sizePolicy().hasHeightForWidth())
        newFileDialogBox.setSizePolicy(sizePolicy)
        newFileDialogBox.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        newFileDialogBox.setModal(True)
        self.mainWidget = QtWidgets.QWidget(newFileDialogBox)
        self.mainWidget.setGeometry(QtCore.QRect(0, 0, 200, 70))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainWidget.sizePolicy().hasHeightForWidth())
        self.mainWidget.setSizePolicy(sizePolicy)
        self.mainWidget.setObjectName("mainWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.mainWidget)
        self.verticalLayout.setContentsMargins(5, 10, 5, 5)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.mainWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.widget = QtWidgets.QWidget(self.mainWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(5, 0, 5, 5)
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonOk = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonOk.sizePolicy().hasHeightForWidth())
        self.buttonOk.setSizePolicy(sizePolicy)
        self.buttonOk.setObjectName("buttonOk")
        self.horizontalLayout.addWidget(self.buttonOk)
        self.buttonCancel = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonCancel.sizePolicy().hasHeightForWidth())
        self.buttonCancel.setSizePolicy(sizePolicy)
        self.buttonCancel.setObjectName("buttonCancel")
        self.horizontalLayout.addWidget(self.buttonCancel)
        self.verticalLayout.addWidget(self.widget)

        self.retranslateUi(newFileDialogBox)
        QtCore.QMetaObject.connectSlotsByName(newFileDialogBox)

    def retranslateUi(self, newFileDialogBox):
        _translate = QtCore.QCoreApplication.translate
        newFileDialogBox.setWindowTitle(_translate("newFileDialogBox", "Type name"))
        self.buttonOk.setText(_translate("newFileDialogBox", "Ok"))
        self.buttonCancel.setText(_translate("newFileDialogBox", "Cancel"))

