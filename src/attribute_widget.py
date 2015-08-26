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

# NEED TO FIX MAXIMUM WIDTH : CALCULATE IT EVERY TIME WE RUN INIT_UI?
# NEED TO FIGURE OUT HOW TO FORMAT AND RETURN ATTRIBUTES
# REQUIRES:
#  * NAME: display name for the label
#  * TYPE: variable type, e.g. string, double, list, reference
#  * VALUE: current value of the field
#  * VALIDATOR: should return true or false comparing the VALUE to TYPE (and other options)
#  * TOOLTIP: hover text for more description

class AttributeEditor(QtGui.QWidget):
    def __init__(self, parent = None, closeFunc = None):
        super(AttributeEditor,self).__init__(parent)
        self.layout = QtGui.QVBoxLayout(self)
        self.closeFunc = closeFunc

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
        label = QtGui.QLabel(self)
        label.setText("Attribute Editor")
        label.setWordWrap(True)
        self.layout.addWidget(label)

        pix = QtGui.QPixmap("icons/model/Client.png").scaled(100,100)
        label2 = QtGui.QLabel(self)
        label2.setPixmap(pix)
        label2.setToolTip("This is a label tooltip.")
        self.layout.addWidget(label2)

        cb = QtGui.QComboBox(self)
        cb.addItems(["Hello","World"])
        cb.setToolTip('This is a combo box tool tip.')
        self.layout.addWidget(cb)

        le = QtGui.QLineEdit(self)
        le.setToolTip('This is a line editor tool tip.')
        self.layout.addWidget(le)

        te = QtGui.QTextEdit(self)
        te.setToolTip('This is a text editor tool tip.')
        self.layout.addWidget(te)

        ok_cancel_widget = QtGui.QWidget(self)
        ok_cancel_layout = QtGui.QHBoxLayout(ok_cancel_widget)
        
        button = QtGui.QPushButton('OK',self)
        button.setToolTip('Save the updated attributes.')
        button.clicked.connect(self.closeFunc)
        ok_cancel_layout.addWidget(button)

        button = QtGui.QPushButton('Cancel',self)
        button.setToolTip('Cancel attribute edits.')
        button.clicked.connect(self.closeFunc)
        ok_cancel_layout.addWidget(button)

        ok_cancel_widget.setLayout(ok_cancel_layout)
        self.layout.addWidget(ok_cancel_widget)

    def mouseDoubleClickEvent(self, event):
        self.closeFunc(event)
