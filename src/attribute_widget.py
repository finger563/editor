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
from graphics_items import PushButton

# NEED TO USE VALIDATORS

class AttributeEditor(QtGui.QWidget):
    def __init__(self, parent = None):
        super(AttributeEditor,self).__init__(parent)
        self.setContentsMargins(0,0,0,0)
        self.setMaximumWidth(300)

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)
        self._displayed = False
        self._unsaved_edits = False
        self._layout = None

        self._dataMapper = QtGui.QDataWidgetMapper()

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())

    def init_layout(self):
        self._input_dict = {}
        while self._layout and self._layout.count():
            child = self._layout.takeAt(0)
            child.widget().deleteLater()
        self.vbox.removeItem(self.vbox.itemAt(0))
        self.scrollArea = QtGui.QScrollArea()

        self.viewWidget = QtGui.QWidget()
        self._layout = QtGui.QVBoxLayout(self.viewWidget)

        self.scrollArea.setWidget(self.viewWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.vbox.addWidget(self.scrollArea)
        self._layout.setContentsMargins(20,20,20,20)
        
        self.updateGeo()

    def setSelection(self, current, old):
        current = self._proxyModel.mapToSource(current)
        
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        #self._dataMapper.clearMapping()
        self._dataMapper.setCurrentModelIndex(current)

        self.init_layout()

        node = current.internalPointer()

        self.add_header(node)
        i = 0
        for key,attr in node.attributes.iteritems():
            if attr.editable:
                obj = self.add_attribute(key, attr)
                if obj:
                    self._dataMapper.addMapping(obj, i)
                    i += 1
        self.add_ok_cancel()
        self.unhide(None)

    def init_ui(self, item, output_obj, output_func = None):
        if self._unsaved_edits:
            reply = QtGui.QMessageBox.question(self, 'Save?',
                                             "Save attribute edits?",
                                             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                             QtGui.QMessageBox.Yes)
            if reply == QtGui.QMessageBox.Yes:
                self.save(None)
        self.init_layout()
        self._output_obj = output_obj
        self._output_func = output_func
        self.add_header(item.viewModel())
        for key,attr in item.model().attributes.iteritems():
            if attr.editable:
                self.add_attribute(key,attr)
        self.add_ok_cancel()
        self._unsaved_edits = False

    def add_header(self, item):
        label = QtGui.QLabel()
        label.setText("Properties")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)
        self._layout.addWidget(label)
        '''
        obj = None
        if attrs['draw style'].value in ['icon']:
            pix = QtGui.QPixmap( attrs['icon'].value).scaled(30,30)
            obj = QtGui.QLabel()
            obj.setPixmap(pix)

        if obj:
            self._layout.addWidget(obj)
        '''

    def add_attribute(self, name, attr):
        label = QtGui.QLabel()
        label.setText(name + ':')
        label.setToolTip(attr.tooltip)
        label.setWordWrap(True)

        obj = None
        if attr.kind in ['float','int','double','string']:
            obj = QtGui.QLineEdit()
            #obj.editingFinished.connect(self.updateEdits)
            obj.setText(str(attr.value))
            #self._input_dict[name] = obj
        elif attr.kind in ['code']:
            obj = QtGui.QTextEdit()
            #obj.textChanged.connect(self.updateEdits)
            obj.setText(attr.value)
            #self._input_dict[name] = obj
        elif attr.kind in ['list_entry'] and attr.value in attr.options:
            obj = QtGui.QComboBox()
            #obj.currentIndexChanged.connect(self.updateEdits)
            obj.addItems(attr.options)
            obj.setCurrentIndex(attr.options.index(attr.value))
            #self._input_dict[name] = obj
        '''
        elif 'file' in attr.kind:
            obj = PushButton()
            obj.setText(attr.value)
            obj.setMaximumWidth(self.maximumWidth() * 0.8)
            obj.clicked.connect(
                lambda : self.open_file(name, obj, attr.kind.split('_')[1])
            )
            self._input_dict[name] = obj
        elif 'dictionary' in attr.kind:
            label = None
            _type = attr.kind.split('_')[1]
            obj = QtGui.QGroupBox(name)
            layout = QtGui.QFormLayout()
            self._input_dict[name] = {}
            for key_name in attr.options:
                if 'bool' in _type:
                    cb = QtGui.QCheckBox()
                    cb.setChecked(bool(attr.value[key_name]))
                    layout.addRow(QtGui.QLabel(key_name+':'), cb)
                    self._input_dict[name][key_name] = cb
                else:
                    print 'Unknown dictionary value type: {}'.format(_type)
                    break
            obj.setLayout(layout)
        '''
        if obj:
            if label: self._layout.addWidget(label)
            obj.setToolTip(attr.tooltip)
            self._layout.addWidget(obj)
        return obj

    def add_ok_cancel(self):
        ok_cancel_widget = QtGui.QWidget(self)
        ok_cancel_layout = QtGui.QHBoxLayout(ok_cancel_widget)
        
        button = QtGui.QPushButton('Save',self)
        button.setToolTip('Save the updated attributes.')
        button.clicked.connect(self.save)
        ok_cancel_layout.addWidget(button)

        button = QtGui.QPushButton('Close',self)
        button.setToolTip('Close the attribute editor.')
        button.clicked.connect(self.cancel)
        ok_cancel_layout.addWidget(button)

        ok_cancel_widget.setLayout(ok_cancel_layout)
        self._layout.addWidget(ok_cancel_widget)

    def open_file(self, name, obj, file_type):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                     "Select {} file".format(name),
                                                     obj.text(),
                                                     "All Files (*);;{} Files (*.{})".format(name,file_type),
                                                     options = QtGui.QFileDialog.Options())
        if fileName:
            obj.setText(fileName)

    def open_dir(self, name, obj):
        pass

    def updateEdits(self, event = None):
        self._unsaved_edits = True

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
            if kind in ['string']:
                self._output_obj[name].value = str(obj.text())
            elif kind in ['code']:
                self._output_obj[name].value = str(obj.toPlainText())
            elif kind in ['float','double']:
                self._output_obj[name].value = float(obj.text())
            elif kind in ['int']:
                self._output_obj[name].value = int(obj.text())
            elif kind in ['list']:
                self._output_obj[name].value = self._output_obj[name].options[obj.currentIndex()]
            elif 'file' in kind:
                self._output_obj[name].value = str(obj.text())
            elif 'dictionary' in kind:
                _type = kind.split('_')[1]
                if 'bool' in _type:
                    for key_name in self._output_obj[name].options:
                        self._output_obj[name][key_name] = bool(obj[key_name].checkState() & QtCore.Qt.Checked)
        #self.hide(event)
        if self._output_func: self._output_func(self._output_obj)
        self._unsaved_edits = False

    def cancel(self, event):
        self.hide(event)
        self._unsaved_edits = False

    def hide(self, event):
        self._displayed = False
        self.animate(event,self._displayed)

    def unhide(self, event):
        self._displayed = True
        self.animate(event,self._displayed)

    def mouseDoubleClickEvent(self, event):
        #self.hide(event)
        return
