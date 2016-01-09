'''
These classes allow for an object in the
editor's attributes to be edited in a widget
that slides in from the right of the screen.

Each EditorView (i.e. tab in the editor widget)
has its own AttributeEditor.
'''

__author__ = 'William Emfinger'
__copyright__ = 'Copyright 2016, ROSMOD'
__credits__ = ['William Emfinger', 'Pranav Srinivas Kumar']
__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'William Emfinger'
__email__ = 'emfinger@isis.vanderbilt.edu'
__status__ = 'Production'

from PyQt4 import QtCore
from PyQt4 import QtGui

from graphics_items import PushButton

from code_editor import CodeEditor
from syntax import ROSHighlighter, PythonHighlighter

# TODO: Perhaps find a way to import other highlighters and allow the
#       user to select which highlighter to use as another attribute?

# TODO: Integrate validators into the attribute editor

# TODO: Figure out how to handle dependent attribute editing
#       e.g. options/options_type & scope depending on on the kind of attribute
#
#       Need to figure out how to add/remove attribute widgets dynamically
#       and when/how to trigger the add/remove & update events basd on certain
#       values of other attributes

# TODO: Convert attribute editor dataMapper to ManualSubmit to allow
#       cancelling edits Make sure that changing it here doesn't
#       affect the EditorItem's interaction

# TODO: Create an object here which fully encapsulates dictionary editing

# TODO: Probably need objects which display strings for
#       editing/choosing, but which actually map to objects underneath
#       (e.g. pointer selection).  Need some sort of mapper/delegate
#       for these editors which perofrm the mapping


class AttributeEditor(QtGui.QWidget):
    '''Enables editing of the attributes of a model object.  Interfaces
    with a subclass of a :class:`QDataWidgetMapper` to enable
    automatic updating back and forth between the model and the
    editor.
    '''
    def __init__(self, parent):
        super(AttributeEditor, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMaximumWidth(300)

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)
        self._displayed = False
        self._unsaved_edits = False
        self._layout = None

        self.dataMapper = QtGui.QDataWidgetMapper()

    def init_layout(self):
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
        self._layout.setContentsMargins(20, 20, 20, 20)

        self.updateGeo()

    def init_attributes(self, attr):
        i = 0  # index into attributes (if it were a list)
        for key, attr in attr.iteritems():
            if attr.editable:
                obj = self.add_attribute(key, attr)
                if obj:
                    self.dataMapper.addMapping(obj, i)
            i += 1

    def update(self, dataMapper):
        self.dataMapper = dataMapper
        self.init_layout()

        r = self.dataMapper.model().getModel(self.dataMapper.rootIndex())
        node = r.child(self.dataMapper.currentIndex())
        if not node:
            return

        self.add_header(node)
        self.init_attributes(node.attributes)
        self.add_ok_cancel()
        self.unhide(None)

    def add_header(self, item):
        label = QtGui.QLabel()
        label.setText("Properties:")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)
        pix = QtGui.QLabel()
        pm = QtGui.QPixmap('icons/model/' + item.kind() + '.png')
        if not pm.isNull():
            pix.setPixmap(
                pm.scaled(30,30)
            )
        qw = QtGui.QWidget()
        hbox = QtGui.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        qw.setLayout(hbox)
        hbox.addWidget(pix)
        hbox.addWidget(label)
        self._layout.addWidget(qw)

    def add_attribute(self, name, attr):
        label = QtGui.QLabel()
        label.setText(name + ':')
        label.setToolTip(attr.tooltip)
        label.setWordWrap(True)

        obj = None
        if attr.kind in ['float', 'int', 'double', 'string']:
            obj = QtGui.QLineEdit()
            obj.setText(str(attr.value))
        elif attr.kind in ['bool']:
            obj = QtGui.QCheckBox()
            obj.setChecked(attr.value)
        elif attr.kind in ['code']:
            obj = CodeEditor(self)
            obj.setHighlighterType(ROSHighlighter)
            obj.setText(attr.value)
        elif attr.kind in ['python']:
            obj = CodeEditor(self)
            obj.setHighlighterType(PythonHighlighter)
            obj.setText(attr.value)
        elif attr.kind in ['list']:
            options = attr.get_options()
            obj = QtGui.QComboBox()
            obj.addItems(options)
            i = 0
            if attr.value in options:
                i = options.index(attr.value)
            obj.setCurrentIndex(i)
        elif 'file' in attr.kind:
            obj = PushButton()
            obj.setText(attr.value)
            obj.setMaximumWidth(self.maximumWidth() * 0.8)
            obj.clicked.connect(
                lambda: self.open_file(name, obj, attr.kind.split('_')[1])
            )
        elif 'dictionary' in attr.kind:
            label = None
            _type = attr.kind.split('_')[1]
            obj = QtGui.QGroupBox(name)
            layout = QtGui.QFormLayout()
            for key_name in attr.options:
                if 'bool' in _type:
                    cb = QtGui.QCheckBox()
                    cb.setChecked(bool(attr.value[key_name]))
                    layout.addRow(QtGui.QLabel(key_name+':'), cb)
                else:
                    print 'Unknown dictionary value type: {}'.format(_type)
                    break
            obj.setLayout(layout)
        if obj:
            if label:
                self._layout.addWidget(label)
            obj.setToolTip(attr.tooltip)
            self.obj = obj
            self._layout.addWidget(obj)
        return obj

    def add_ok_cancel(self):
        ok_cancel_widget = QtGui.QWidget(self)
        ok_cancel_layout = QtGui.QHBoxLayout(ok_cancel_widget)

        button = QtGui.QPushButton('Save', self)
        button.setToolTip('Save the updated attributes.')
        button.clicked.connect(self.save)
        ok_cancel_layout.addWidget(button)

        button = QtGui.QPushButton('Close', self)
        button.setToolTip('Close the attribute editor.')
        button.clicked.connect(self.cancel)
        ok_cancel_layout.addWidget(button)

        ok_cancel_widget.setLayout(ok_cancel_layout)
        self._layout.addWidget(ok_cancel_widget)

    def open_file(self, name, obj, file_type):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self,
            "Select {} file".format(name),
            obj.text(),
            "All Files (*);;{} Files (*.{})".format(name, file_type),
            options=QtGui.QFileDialog.Options()
        )
        if fileName:
            obj.setText(fileName)

    def open_dir(self, name, obj):
        pass

    def updateEdits(self, event=None):
        self._unsaved_edits = True

    def updateGeo(self):
        rect = self.getNewRect(self._displayed)
        self.setGeometry(rect.x(), rect.y(), rect.x() + rect.width(),
                         rect.y() + rect.height())

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
        pass
        '''
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
        '''

    def cancel(self, event):
        self.hide(event)
        self._unsaved_edits = False

    def hide(self, event):
        self._displayed = False
        self.animate(event, self._displayed)

    def unhide(self, event):
        self._displayed = True
        self.animate(event, self._displayed)

    def mouseDoubleClickEvent(self, event):
        self.hide(event)
