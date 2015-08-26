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

class AttributeEditor(QtGui.QWidget):
    def __init__(self, parent = None):
        super(AttributeEditor,self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QtGui.QVBoxLayout(self)

        self.label = QtGui.QLabel(self)
        self.label.setText("Attribute Editor")
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label)

        self.pix = QtGui.QPixmap("icons/model/Client.png").scaled(100,100)
        self.label2 = QtGui.QLabel(self)
        self.label2.setPixmap(self.pix)
        self.label2.setToolTip('This is a label tool tip.')
        self.layout.addWidget(self.label2)

        self.cb = QtGui.QComboBox(self)
        self.cb.addItems(["Hello","World"])
        self.cb.setToolTip('This is a combo box tool tip.')
        self.layout.addWidget(self.cb)

        self.le = QtGui.QLineEdit(self)
        self.le.setToolTip('This is a line editor tool tip.')
        self.layout.addWidget(self.le)

        self.te = QtGui.QTextEdit(self)
        self.te.setToolTip('This is a text editor tool tip.')
        self.layout.addWidget(self.te)

        self.button = QtGui.QPushButton('Button',self)
        self.button.setToolTip('This is a button tooltip.')
        self.layout.addWidget(self.button)

        #self.layout.setContentsMargins(1,1,1,1)
        #self.setMaximumSize(100,200)
        self.setMaximumWidth(300)
        self.setLayout(self.layout)

    def mousePressEvent(self, event):
        self.parent().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.parent().mouseReleaseEvent(event)
