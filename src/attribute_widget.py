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

from collections import OrderedDict

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

# attribute is a dict of key:val pairs:
#  * NAME: display name for the label
#  * TYPE: variable type, e.g. string, double, list, reference, can use spinbox for ranges
#  * VALUE: current value of the field
#  * VALIDATOR: should return true or false comparing the VALUE to TYPE (and other options)
#  * OPTIONS: if the user selects between multiple options, they are specified here
#  * TOOLTIP: hover text for more description

class AttributeEditor(QtGui.QWidget):
    def __init__(self, parent = None):
        super(AttributeEditor,self).__init__(parent)
        self.vbox = QtGui.QVBoxLayout(self)
        self.scrollArea = QtGui.QScrollArea()

        self.viewWidget = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout(self.viewWidget)

        self.scrollArea.setWidget(self.viewWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.vbox.addWidget(self.scrollArea)

        self._displayed = False

        self.setStyleSheet("""QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }""")
        self.setMaximumWidth(300)

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

    def add_header(self, attrs):
        label = QtGui.QLabel()
        label.setText("Attribute Editor")
        label.setWordWrap(True)
        self.layout.addWidget(label)
        obj = None
        if attrs['draw style'].value in ['icon']:
            pix = QtGui.QPixmap( attrs['icon'].value).scaled( attrs['width'].value, attrs['height'].value)
            obj = QtGui.QLabel()
            obj.setPixmap(pix)

        if obj:
            self.layout.addWidget(obj)

    def add_attribute(self, name, attr):
        label = QtGui.QLabel()
        label.setText(name + ':')
        label.setToolTip(attr.tooltip)
        label.setWordWrap(True)

        obj = None
        if attr.kind in ['float','int','double','string','file']:
            obj = QtGui.QLineEdit()
            obj.setText(str(attr.value))
        elif attr.kind in ['code']:
            obj = QtGui.QTextEdit()
            obj.setText(attr.value)
        elif attr.kind in ['list'] and attr.value in attr.options:
            obj = QtGui.QComboBox()
            obj.addItems(attr.options)
            obj.setCurrentIndex(attr.options.index(attr.value))

        if obj:
            self._input_dict[name] = obj
            self.layout.addWidget(label)
            obj.setToolTip(attr.tooltip)
            self.layout.addWidget(obj)

    def clear_ui(self):
        self._input_dict = {}
        while self.layout.count():
            child = self.layout.takeAt(0)
            child.widget().deleteLater()
        
    def init_ui(self, attrs=OrderedDict(), output_obj=None, output_func = None):
        self.clear_ui()
        self._output_obj = output_obj
        self._output_func = output_func
        self.add_header(attrs)
        for key,attr in attrs.iteritems():
            self.add_attribute(key,attr)
        
        ok_cancel_widget = QtGui.QWidget(self)
        ok_cancel_layout = QtGui.QHBoxLayout(ok_cancel_widget)
        
        button = QtGui.QPushButton('Save',self)
        button.setToolTip('Save the updated attributes.')
        button.clicked.connect(self.save)
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

    def save(self, event):
        for name,obj in self._input_dict.iteritems():
            kind = self._output_obj[name].kind
            if kind in ['string','file']:
                self._output_obj[name].value = obj.text()
            elif kind in ['code']:
                self._output_obj[name].value = obj.toPlainText()
            elif kind in ['float','double']:
                self._output_obj[name].value = float(obj.text())
            elif kind in ['int']:
                self._output_obj[name].value = int(obj.text())
            elif kind in ['list']:
                self._output_obj[name].value = self._output_obj[name].options[obj.currentIndex()]
        self.hide(event)
        if self._output_func: self._output_func(self._output_obj)

    def hide(self, event):
        self._displayed = False
        self.animate(event,self._displayed)

    def show(self, event):
        self._displayed = True
        self.animate(event,self._displayed)

    def mouseDoubleClickEvent(self, event):
        self.hide(event)
