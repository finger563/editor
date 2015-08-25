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
    def __init__(self, parent):
        super(AttributeEditor,self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        pass
