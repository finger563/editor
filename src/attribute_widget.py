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
#  * TYPE: variable type, e.g. string, double, list, reference, can use spinbox for ranges
#  * VALUE: current value of the field
#  * VALIDATOR: should return true or false comparing the VALUE to TYPE (and other options)
#  * TOOLTIP: hover text for more description

# SHOULD USE QValidators!
# SHOULD USE sliders, spinboxes, etc.

class AttributeEditor(QtGui.QWidget):
    def __init__(self, parent = None):
        super(AttributeEditor,self).__init__(parent)
        self.layout = QtGui.QVBoxLayout(self)
        self._displayed = False

        self.setStyleSheet("""QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }""")
        self.setMaximumWidth(300)
        self.setLayout(self.layout)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor('#d4d4d4')
        painter.setPen(color)
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawRect(0,0,self.geometry().width(),self.geometry().height())
        painter.end()
        super(AttributeEditor, self).paintEvent( e )

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

        pix = QtGui.QPixmap("icons/model/Client.png").scaled(50,50)
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
        button.clicked.connect(self.hide)
        ok_cancel_layout.addWidget(button)

        button = QtGui.QPushButton('Cancel',self)
        button.setToolTip('Cancel attribute edits.')
        button.clicked.connect(self.hide)
        ok_cancel_layout.addWidget(button)

        ok_cancel_widget.setLayout(ok_cancel_layout)
        self.layout.addWidget(ok_cancel_widget)

    def updateGeo(self):
        rect = self.getNewRect(self._displayed)
        self.setGeometry(rect.x(), rect.y(), rect.x() + rect.width(), rect.y() + rect.height())

    def getNewRect(self, displayed):
        _myw = self.parent().geometry().width()
        _w = self.geometry().width()
        _h = self.parent().geometry().height()
        TL_y = 0
        BR_y = _h
        TL_x = _myw
        BR_x = _myw + _w
        if displayed:
            TL_x -= _w
            BR_x -= _w
        if TL_x < 0:
            BR_x += -TL_x
            TL_x += -TL_x
        return QtCore.QRectF(TL_x, TL_y, BR_x, BR_y)

    def animate(self, event, displayed):
        self.hideAnimation = QtCore.QPropertyAnimation(self, "geometry")
        self.hideAnimation.setDuration(300)

        self.startGeometry = QtCore.QRectF(self.geometry())
        self.endGeometry = self.getNewRect(displayed)

        self.hideAnimation.setStartValue(self.startGeometry)
        self.hideAnimation.setEndValue(self.endGeometry)
        self.hideAnimation.start()

    def hide(self, event):
        self._displayed = False
        self.animate(event,self._displayed)

    def show(self, event):
        self._displayed = True
        self.animate(event,self._displayed)

    def mouseDoubleClickEvent(self, event):
        self.hide(event)
