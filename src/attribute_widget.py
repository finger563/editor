"""
Attribute Editor Widget 

These classes allow for an object in the 
editor's attributes to be edited in a widget
that slides in from the right of the screen.

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: August 2015
"""

from PyQt4 import QtCore
from PyQt4 import QtGui

class AttributeEditor(QtGui.QGraphicsWidget):
    def __init__(self, parent = None):
        super(AttributeEditor,self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self._width = 100
        self._height = 100
        self.resize(self._width, self._height)
        
        self._pixmap = QtGui.QPixmap("icons/model/Server.png")
        self._item = QtGui.QGraphicsPixmapItem()
        self._item.setPixmap(self._pixmap)
        self.resize(QtCore.QSizeF(self._pixmap.size()))

    def paint(self, painter, option, widget = None):
        self._item.paint(painter, option, widget)

    def boundingRect(self):
        return self._item.boundingRect()

    def sizeHint(self, which, constraint):
        if self._item:
            return self._item.boundingRect().size()
        elif self.layout():
            return self.layout().sizeHint(which, constraint)
        else:
            return QtCore.QSizeF(self._width,self._height)
        
    def updateGraphicsItem(self, width = 0, height = 0):
        if not width and not height:
            width = self.layout().sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF()).width()
            height = self.layout().sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF()).height()
        self._item.setPixmap( self._pixmap.scaled(width,height) )
