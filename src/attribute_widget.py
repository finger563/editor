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
    CodeEditor

from syntax import\
    ROSHighlighter,\
    PythonHighlighter

# TODO: Figure out how nested attributes can be accessed from the
#       model; i.e. how to configure them with the datawidgetmapper?

# TODO: Figure out how to handle dependent attribute editing
#       e.g. options/options_type & scope depending on on the kind of attribute
#
#       Need to figure out how to add/remove attribute widgets dynamically
#       and when/how to trigger the add/remove & update events basd on certain
#       values of other attributes
#
#       Build attribute_editor panes up heirarchically/recursively for
#       each child of each attribute.

# TODO: Propagate reference scope and validation (function) to the
#       ReferenceEditor and its proxy/filter models.

# TODO: Perhaps find a way to import other highlighters and allow the
#       user to select which highlighter to use as another attribute?

# TODO: Integrate validators into the attribute editor


class AttributePanel(QtGui.QWidget):
    '''Enables editing of the attributes of a model object.  Interfaces
    with a subclass of a :class:`QDataWidgetMapper` to enable
    automatic updating back and forth between the model and the
    editor.
    '''
    def __init__(self, parent):
        super(AttributePanel, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)

        self._displayed = False
        self._layout = None

    def clear_layout(self):
        while self._layout and self._layout.count():
            child = self._layout.takeAt(0)
            child.widget().deleteLater()
        self.vbox.removeItem(self.vbox.itemAt(0))

    def init_layout(self):
        self.clear_layout()

        self.viewWidget = QtGui.QWidget(self)
        self._layout = QtGui.QVBoxLayout(self.viewWidget)

        self.scrollArea = QtGui.QScrollArea()
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

    def init_attributes(self, dataMapper, attr):
        i = 0  # index into attributes (if it were a list)
        for key, attr in attr.iteritems():
            if attr.editable:
                self._layout.addWidget(
                    AttributeEditor(
                        self,
                        dataMapper=dataMapper,
                        dataMapperIndex=i,
                        name=key,
                        attr=attr
                    )
                )
            i += 1

    def setDataMapper(self, dataMapper):
        self.dataMapper = dataMapper

    def update(self):
        self.init_layout()

        node = self.dataMapper.model().getModel(
            self.dataMapper.rootIndex()
        )
        if not node:
            return

        self.add_header(node)
        self.init_attributes(self.dataMapper, node.attributes)

        button = QtGui.QPushButton('Close', self)
        button.setToolTip('Close the attribute editor.')
        button.clicked.connect(self.hide)
        self._layout.addWidget(button)

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
        header_widget = QtGui.QWidget()
        header_layout = QtGui.QHBoxLayout(header_widget)
        header_layout.setAlignment(QtCore.Qt.AlignLeft)
        header_layout.addWidget(pix)
        header_layout.addWidget(label)
        header_widget.setLayout(header_layout)
        self._layout.addWidget(header_widget)

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

    def hide(self, event):
        self._displayed = False
        self.animate(event, self._displayed)

    def unhide(self, event):
        self._displayed = True
        self.animate(event, self._displayed)

    def mouseDoubleClickEvent(self, event):
        self.hide(event)


class AttributeEditor(QtGui.QWidget):
    '''Enables editing of the attributes of a model object.  Interfaces
    with a subclass of a :class:`QDataWidgetMapper` to enable
    automatic updating back and forth between the model and the
    editor.
    '''
    def __init__(self, parent, dataMapper, dataMapperIndex, name, attr):
        super(AttributeEditor, self).__init__(parent)
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)

        label = QtGui.QLabel()
        label.setText(name + ':')
        label.setToolTip(attr.tooltip)
        label.setWordWrap(True)

        obj = None
        if attr.getKind() in ['float', 'int', 'double', 'string']:
            obj = QtGui.QLineEdit()
            obj.setText(str(attr.getValue()))
        elif attr.getKind() in ['bool']:
            obj = QtGui.QCheckBox()
            obj.setChecked(attr.getValue())
        elif attr.getKind() in ['code']:
            obj = CodeEditor(self)
            obj.setHighlighterType(ROSHighlighter)
            obj.setPlainText(attr.getValue())
        elif attr.getKind() in ['python']:
            obj = CodeEditor()
            obj.setHighlighterType(PythonHighlighter)
            obj.setPlainText(attr.getValue())
        elif attr.getKind() in ['list']:
            options = attr.get_options()
            obj = QtGui.QComboBox()
            obj.addItems(options)
            i = 0
            if attr.getValue() in options:
                i = options.index(attr.getValue())
            obj.setCurrentIndex(i)
        elif attr.getKind() in ['reference']:
            obj = ReferenceEditor()
            # Need to get filter function here
            obj.setReferenceType(attr.dst_type)
            obj.setModel(dataMapper.model())
            # Do we need to get the root index based on the function?
            # TODO: NEED TO FIX THE ROOT INDEX HERE; PASS IT IN FROM SOMEWHERE
            obj.setRootModelIndex(
                QtCore.QModelIndex()
            )
            obj.setCurrentReference(attr.getValue())
        elif 'file' in attr.getKind():
            obj = FileEditor(name=name,
                             fname=attr.getValue(),
                             file_type=attr.getKind().split('_')[1],
                             parent=self)
        if obj:
            if label:
                self.layout().addWidget(label)
            obj.setToolTip(attr.tooltip)
            dataMapper.addMapping(obj, dataMapperIndex)
            self.layout().addWidget(obj)
            i = 0
            for child_name, child_attr in attr.attributes.iteritems():
                if child_attr.editable:
                    self.layout().addWidget(
                        AttributeEditor(
                            self,
                            dataMapper=dataMapper,
                            dataMapperIndex=i,
                            name=child_name,
                            attr=child_attr
                        )
                    )
                i += 1
