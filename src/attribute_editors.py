'''
These classes allow for special datatypes to be edited and updated
by the MVC paradigm interface with through a :class:`QItemDelegate`
subclass.
'''

__author__ = 'William Emfinger'
__copyright__ = 'Copyright 2016, ROSMOD'
__credits__ = ['William Emfinger', 'Pranav Srinivas Kumar']
__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'William Emfinger'
__email__ = 'emfinger@isis.vanderbilt.edu'
__status__ = 'Production'

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4 import QtCore


class FileEditor(QtGui.QPushButton):
    '''
    Subclass of :class:`QtGui.QPushButton` that enables MVC
    ItemDelegate to set and query the filename.  When the button is
    clicked it spawns a :class:`QFileDialog` for selecting the file
    based on the file_type specified.
    '''

    def __init__(self, name, fname, file_type, parent=None):
        super(FileEditor, self).__init__(parent)
        self._name = name
        self._file_type = file_type
        self.set_file_name(fname)
        self.clicked.connect(self.open_file)

    def set_file_name(self, value):
        self._value = value
        self.setText(self._value.split('/')[-1])

    def file_name(self):
        return self._value

    def open_file(self, event):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self.parent(),
            "Select {} file".format(self._name),
            self.text(),
            "All Files(*);;{} Files (*.{})".format(self._name,
                                                   self._file_type),
            options=QtGui.QFileDialog.Options()
        )
        if fileName:
            self.set_file_name(fileName)


class ListEditor(QtGui.QComboBox):
    '''
    '''

    def __init__(self, *args):
        super(ListEditor, self).__init__(*args)


class FlatProxyModel(QtGui.QAbstractProxyModel):
    '''
    Subclass of :class:`QtGui.QAbstractProxyModel` which flattens a
    tree-structured (heirarchical) model into a list.  Flattening such
    a tree structure allows us to select items from the tree in a
    list-based widget, such as a :class:`QtGui.QComboBox`.
    '''

    def __init__(self, *args):
        super(FlatProxyModel, self).__init__(*args)
        self.rootIndex = None

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def sourceDataChanged(self, topLeft, bottomRight):
        self.dataChanged.emit(self.mapFromSource(topLeft),
                              self.mapFromSource(bottomRight))

    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def sourceRowsInserted(self, parent, start, end):
        self.buildMap(self.sourceModel(), self.rootIndex)
        self.rowsInserted.emit(self.mapFromSource(parent),
                               start,
                               end)

    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def sourceRowsRemoved(self, parent, start, end):
        self.buildMap(self.sourceModel(), self.rootIndex)
        self.rowsRemoved.emit(self.mapFromSource(parent),
                              start,
                              end)

    def buildMap(self, model, parent=QtCore.QModelIndex(), row=0):
        if row == 0:
            self.m_rowMap = {}
            self.m_indexMap = {}
        rows = model.rowCount(parent)
        for r in range(rows):
            index = model.index(r, 0, parent)
            # print 'row', row, 'item', model.data(index, QtCore.Qt.DisplayRole)
            self.m_rowMap[index] = row
            self.m_indexMap[row] = index
            row = row + 1
            if model.hasChildren(index):
                row = self.buildMap(model, index, row)
        return row

    def setRoot(self, root):
        if root:
            index = self.sourceModel().createIndex(root.row(), root.column(), root)
            self.rootIndex = index#.parent()
        else:
            self.rootIndex = QtCore.QModelIndex()
        self.buildMap(self.sourceModel(), self.rootIndex)

    def setSourceModel(self, model, rootObj=None):
        super(FlatProxyModel, self).setSourceModel(model)
        self.setRoot(rootObj)
        self.buildMap(model, self.rootIndex)
        model.dataChanged.connect(self.sourceDataChanged)
        model.rowsInserted.connect(self.sourceRowsInserted)
        model.rowsRemoved.connect(self.sourceRowsRemoved)

    def mapFromSource(self, index):
        if index not in self.m_rowMap:
            return QtCore.QModelIndex()
        return self.createIndex(self.m_rowMap[index], index.column())

    def mapToSource(self, index):
        if not index.isValid() or index.row() not in self.m_indexMap:
            return QtCore.QModelIndex()
        return self.m_indexMap[index.row()]

    def columnCount(self, parent):
        return QtGui.QAbstractProxyModel.sourceModel(self)\
                                        .columnCount(self.mapToSource(parent))

    def rowCount(self, parent):
        return len(self.m_rowMap) if not parent.isValid() else 0

    def index(self, row, column, parent):
        if parent.isValid():
            return QtCore.QModelIndex()
        return self.createIndex(row, column)

    def parent(self, index):
        return QtCore.QModelIndex()


class ComboSortFilterProxyModel(QtGui.QSortFilterProxyModel):
    '''
    Subclasses :class:`QtGui.QSortFilterProxyModel` to provide a proxy
    model to a :class:`QtGui.QComboBox` for selecting references to
    other objects.  By setting the rootIndex of the model and
    customizing the :func:`filterAcceptsRow` function, the reference
    scope and data-type can be enforced.
    '''

    def set_filter_type(self, _type):
        self.filter_type = _type

    def set_filter_func(self, _func):
        self.filter_func = _func

    def filterAcceptsRow(self, row, parent):
        p = self.sourceModel()
        index0 = p.index(
            row,
            self.filterKeyColumn(),
            self.mapToSource(parent)
        )
        i = p.mapToSource(index0)
        m = p.sourceModel()
        item = m.getModel(i)
        test = item.kind() == self.filter_type and self.filter_func(item)
        return test


class ReferenceEditor(QtGui.QComboBox):
    '''
    Required for mapping model items into a :class:`QtGui.QComboBox`.
    Internally it uses :class:`ComboSortFilterProxyModel` for
    filtering the available objects from its flattened proxy model,
    which is a :class:`FlatProxyModel`.  Connects to these models'
    signals so that it can properly update and maintain state when the
    underlying model changes, e.g. when referentiable objects are
    added or removed from the model.  This feature is necessary
    because the ReferenceEditor widget can be active
    (viewed/interacted with) at the same time the underlying
    :class:`item_model.ItemModel` is changing.
    '''

    def __init__(self, *args):
        super(ReferenceEditor, self).__init__(*args)
        
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        # self.setEditable(True)
        
        # Add the flatModel that we'll use
        self.flatModel = FlatProxyModel(self)

        # add filter model
        self.pFilterModel = ComboSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.pFilterModel.setDynamicSortFilter(True)

    def setReferenceType(self, _type):
        self.pFilterModel.set_filter_type(_type)

    def setFilterFunc(self, _func):
        self.pFilterModel.set_filter_func(_func)

    def setModelAndRoot(self, model, root):
        self.flatModel.setSourceModel(model, root)
        self.pFilterModel.setSourceModel(self.flatModel)
        super(ReferenceEditor, self).setModel(self.pFilterModel)

    def setCurrentReference(self, ref):
        index = self.findData(
            ref,
            self.getRootItemModel().reference_role
        )
        if index < 0:
            index = 0
            ref = self.itemData(
                index,
                self.getRootItemModel().reference_role
            ).toPyObject()
        self.setCurrentIndex(index)
        self.activated[str].emit(self.itemText(index))

    def getRootItemModel(self):
        return self.model().sourceModel().sourceModel()


class CodeEditor(QtGui.QTextEdit):
    '''
    Multi-line text editor subclassing :class:`QtGui.QTextEdit` to
    allow for the editing of 'code' objects, such as ROS Message
    definitions, python code, etc.  Supports code completion and
    syntax highlighting.
    '''

    def __init__(self, *args):
        super(CodeEditor, self).__init__(*args)

        self.setLineWrapMode(self.NoWrap)
        self.setTabChangesFocus(False)

        font = QtGui.QFont("Monospace", 10, QtGui.QFont.Normal)
        self.setCurrentFont(font)
        tabStop = 4
        metrics = QtGui.QFontMetrics(font)
        self.setTabStopWidth(tabStop * metrics.width(' '))

        self.completer = QtGui.QCompleter()
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insertCompletion)

        self.model = QtGui.QStringListModel()
        self.completer.setModel(self.model)

    def setHighlighterType(self, highlighter_type):
        compl_list = []
        compl_list.extend(highlighter_type.keywords)
        compl_list.extend(highlighter_type.keywords2)
        compl_list.extend(highlighter_type.datatypes)
        self.model.setStringList(compl_list)
        self.highlighter = highlighter_type(self.document())

    def insertCompletion(self, completion):
        if (self.completer.widget() != self):
            return
        tc = self.textCursor()
        extra = completion.length()-self.completer.completionPrefix().length()
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion.right(extra))
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, event):
        if (self.completer):
            self.completer.setWidget(self)
        QtGui.QTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if (self.completer and self.completer.popup().isVisible()):
            if (event.key() == Qt.Key_Enter):
                event.ignore()
                return
            elif (event.key() == Qt.Key_Return):
                event.ignore()
                return
            elif (event.key() == Qt.Key_Escape):
                event.ignore()
                return
            elif (event.key() == Qt.Key_Tab):
                event.ignore()
                return
            elif (event.key() == Qt.Key_Backtab):
                event.ignore()
                return

        isShortcut = (event.modifiers() and
                      Qt.ControlModifier and event.key() == Qt.Key_E)
        if (not self.completer or not isShortcut):
            super(CodeEditor, self).keyPressEvent(event)

        ctrlOrShift = (event.modifiers() and
                       (Qt.ControlModifier or Qt.ShiftModifier))
        if (not self.completer or
            (not ctrlOrShift and
             event.text().isEmpty())):
            return

        eow = QtCore.QString('~!@#$%^&*()_+{}|:"<>?,./;\'[]\\-=')
        hasModifier = ((event.modifiers() != Qt.NoModifier) and
                       not ctrlOrShift)
        completionPrefix = self.textUnderCursor()

        if (not isShortcut and
            (hasModifier or
             event.text().isEmpty() or
             completionPrefix.length() <= 1 or
             eow.contains(event.text().right(1)))):
            self.completer.popup().hide()
            return

        if (completionPrefix != self.completer.completionPrefix()):
            self.completer.setCompletionPrefix(completionPrefix)
            self.completer.popup().setCurrentIndex(
                self.completer.completionModel().index(0, 0)
            )

        cr = self.cursorRect()
        cr.setWidth(
            self.completer.popup().sizeHintForColumn(0) +
            self.completer.popup().verticalScrollBar().sizeHint().width()
        )
        self.completer.complete(cr)
