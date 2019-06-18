from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal

class TabBarPlus(QtWidgets.QTabBar):
    """Tab bar that has a plus button floating to the right of the tabs."""
    
    plusClicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Plus Button
        self.plusButton = QtWidgets.QPushButton("+")
        self.plusButton.setParent(self)
        
        self.plusButton.setFixedSize(35, 27)  # Small Fixed size
        self.plusButton.clicked.connect(self.plusClicked.emit)
        self.movePlusButton() # Move to the correct location
    # end Constructor
    
    def sizeHint(self):
        """Return the size of the TabBar with increased width for the plus button."""
        sizeHint = QtWidgets.QTabBar.sizeHint(self)
        width = sizeHint.width()
        height = sizeHint.height()
        return QtCore.QSize(width+25, height)
    # end tabSizeHint

    def resizeEvent(self, event):
        """Resize the widget and make sure the plus button is in the correct location."""
        super().resizeEvent(event)
        
        self.movePlusButton()
    # end resizeEvent
    
    def tabLayoutChange(self):
        """This virtual handler is called whenever the tab layout changes.
            If anything changes make sure the plus button is in the correct location.
            """
        super().tabLayoutChange()
        
        self.movePlusButton()
    # end tabLayoutChange
    
    def movePlusButton(self):
        """Move the plus button to the correct location."""
        # Find the width of all of the tabs
        size = sum([self.tabRect(i).width() for i in range(self.count())])
        # size = 0
        # for i in range(self.count()):
        #     size += self.tabRect(i).width()
        
        # Set the plus button location in a visible area
        h = self.geometry().top()-2
        w = self.width()
        if size > w: # Show just to the left of the scroll buttons
            self.plusButton.move(w-54, h)
        else:
            self.plusButton.move(size-6, h)
# end movePlusButton
# end class TabBarPlus

class TabPlusWidget(QtWidgets.QTabWidget):
    """Tab Widget that that can have new tabs easily added to it."""
    plusClicked = pyqtSignal()
    parent = None
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Tab Bar
        self.tab = TabBarPlus()
        self.setTabBar(self.tab)
        
        # Properties
        self.setMovable(True)
        self.setTabsClosable(True)
        
        # Signals
        self.tab.plusClicked.connect(self.addTab)
        self.tab.tabMoved.connect(self.moveTab)
        self.tabCloseRequested.connect(self.removeTab)
    # end Constructor
    
    def addTab(self, tab=None, str=""):
        if tab is not None:
            super().addTab(tab, str)
        else:
            self.plusClicked.emit()

    def moveTab(self):
        return

    def removeTab(self, index):
        if self.count()==1:
            self.plusClicked.emit()
        
        widget = self.widget(index)
        super().removeTab(index)
        self.parent.openSchemas = self.parent.openSchemas[:index] + self.parent.openSchemas[index+1:]
        widget.close()
        widget.deleteLater()
        del widget
# end class CustomTabWidget
