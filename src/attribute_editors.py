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


class ComboSortFilterProxyModel(QtGui.QSortFilterProxyModel):
    '''
    Subclasses :class:`QtGui.QSortFilterProxyModel` to provide a proxy
    model to a :class:`QtGui.QComboBox` for selecting references to
    other objects.  By setting the rootIndex of the model and
    customizing the :func:`filterAcceptsRow` function, the reference
    scope and data-type can be enforced.
    '''

    def columnCount(self, parent):
        return 1

    def set_filter_type(self, _type):
        self.filter_type = _type

    def set_filter_func(self, _func):
        self.filter_func = _func

    def filterAcceptsRow(self, row, parent):
        return True
        index0 = self.sourceModel().index(row, self.filterKeyColumn(), parent)
        item = self.sourceModel().getModel(index0)
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

        self.treeView = QtGui.QTreeView(self)
        self.treeView.setFrameShape(QtGui.QFrame.NoFrame)
        self.treeView.setEditTriggers(QtGui.QTreeView.NoEditTriggers)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setSelectionBehavior(QtGui.QTreeView.SelectRows)
        self.treeView.setRootIsDecorated(False)
        self.treeView.setWordWrap(True)
        self.treeView.setAllColumnsShowFocus(True)
        self.treeView.header().setVisible(False)
        self.setView(self.treeView)

        # self.setEditable(True)

    def presetIndex(self, index):
        self.setRootModelIndex(index.parent())
        self.setModelColumn(index.column())
        self.setCurrentIndex(index.row())
        self.setRootModelIndex(QtCore.QModelIndex())
        self.view().setCurrentIndex(index)

    def selectIndex(self, index):
        self.setRootModelIndex(index.parent())
        self.setCurrentIndex(index.row())

    def showPopup(self):
        self.setRootModelIndex(QtCore.QModelIndex())
        #self.setRootModelIndex(self.model().mapFromSource(QtCore.QModelIndex()))
        self.treeView.expandAll()
        self.treeView.setIndentation(0)
        self.treeView.setItemsExpandable(False)
        super(ReferenceEditor, self).showPopup()

    def hidePopup(self):
        self.setRootModelIndex(self.view().currentIndex().parent())
        self.setCurrentIndex(self.view().currentIndex().row())
        super(ReferenceEditor, self).hidePopup()

    def setCurrentReference(self, ref):

        index = self.findData(
            ref,
            self.getRootItemModel().reference_role
        )
        # print "found index:",index, ref, ref['Name'], ref.row(), ref.column()
        
        if ref is not None and ref.row() is not None and ref.column() is not None and ref.parent is not None:
            mi = self.getRootItemModel().createIndex(
                ref.row(),
                ref.column(),
                ref
            )
            #mi = self.model().mapFromSource(mi)
            self.selectIndex(mi)
        else:
            self.setRootModelIndex(QtCore.QModelIndex())
            #self.setRootModelIndex(self.model().mapFromSource(QtCore.QModelIndex()))
            self.setCurrentIndex(0)
        return

    def setRoot(self, root):
        index = self.getRootItemModel().createIndex(
            root.row(),
            root.column(),
            root
        )
        #self.setRootModelIndex(self.model().mapFromSource(index))
        self.setRootModelIndex(index)

    def getRootItemModel(self):
        return self.model()#.sourceModel()


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
