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

from attribute_editors import\
    FileEditor,\
    ReferenceEditor,\
    CodeEditor,\
    ComboSortFilterProxyModel,\
    FlatProxyModel

from syntax import\
    ROSHighlighter,\
    PythonHighlighter

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


class AttributeEditor(QtGui.QWidget):
    '''Enables editing of the attributes of a model object.  Interfaces
    with a subclass of a :class:`QDataWidgetMapper` to enable
    automatic updating back and forth between the model and the
    editor.
    '''
    def __init__(self, parent):
        super(AttributeEditor, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)

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
        self.scrollArea.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded
        )
        self.scrollArea.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded
        )

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
        label.setText('Properties:')
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)
        pix = QtGui.QLabel()
        pm = QtGui.QPixmap('icons/model/' + item.kind() + '.png')
        if not pm.isNull():
            pix.setPixmap(
                pm.scaled(30, 30)
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
            obj.setPlainText(attr.value)
        elif attr.kind in ['python']:
            obj = CodeEditor()
            obj.setHighlighterType(PythonHighlighter)
            obj.setPlainText(attr.value)
        elif attr.kind in ['list']:
            options = attr.get_options()
            obj = QtGui.QComboBox()
            obj.addItems(options)
            i = 0
            if attr.value in options:
                i = options.index(attr.value)
            obj.setCurrentIndex(i)
        elif attr.kind in ['reference']:
            obj = ReferenceEditor()
            flatModel = FlatProxyModel()
            flatModel.setSourceModel(self.dataMapper.model())
            CSFPM = ComboSortFilterProxyModel()
            CSFPM.set_filter_type(attr.dst_type)
            CSFPM.setDynamicSortFilter(True)
            CSFPM.setSourceModel(flatModel)
            obj.setModel(CSFPM)
            #obj.setModelColumn(0)
            print attr.value
            if attr.value:
                obj.setCurrentIndex(attr.value)
            r = flatModel.mapFromSource(self.dataMapper.rootIndex())
            r = CSFPM.mapFromSource(r)
            i = r.parent().parent()
            obj.setRootModelIndex(i)
        elif 'file' in attr.kind:
            obj = FileEditor(name=name,
                             fname=attr.value,
                             file_type=attr.kind.split('_')[1],
                             parent=self)
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

    def updateEdits(self, event=None):
        self._unsaved_edits = True

    def updateGeo(self):
        rect = self.getNewRect(self._displayed)
        self.setGeometry(rect.x(), rect.y(), rect.x() + rect.width(),
                         rect.y() + rect.height())
        self.animate(None, self._displayed)

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
        self.hideAnimation = QtCore.QPropertyAnimation(self, 'geometry')
        self.hideAnimation.setDuration(300)

        startGeometry = QtCore.QRectF(self.geometry())
        endGeometry = self.getNewRect(displayed)

        self.hideAnimation.setStartValue(startGeometry)
        self.hideAnimation.setEndValue(endGeometry)
        self.hideAnimation.start()

    def save(self, event):
        pass

    def keyPressEvent(self, event):
        QtGui.QWidget.keyPressEvent(self, event)

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
