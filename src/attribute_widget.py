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
        self.layout = QtGui.QVBoxLayout(self)

        self.setStyleSheet("""QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }""")
        self.setMaximumWidth(300)
        self.setLayout(self.layout)
        self.show()

    def paintEvent(self, e):
        super(AttributeEditor, self).paintEvent( e )
        painter = QtGui.QPainter()
        painter.begin(self)
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor('#d4d4d4')
        painter.setPen(color)
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawRect(0,0,self.geometry().width(),self.geometry().height())
        painter.end()

    def clear_ui(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            child.widget().deleteLater()
        
    def init_ui(self):
        self.clear_ui()
        self.label = QtGui.QLabel(self)
        self.label.setText("Attribute Editor")
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label)

        self.pix = QtGui.QPixmap("icons/model/Client.png").scaled(100,100)
        self.label2 = QtGui.QLabel(self)
        self.label2.setPixmap(self.pix)
        self.label2.setToolTip("This is a label tooltip.")
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

    def mouseDoubleClickEvent(self, event):
        self.parent().mouseDoubleClickEvent(event)
