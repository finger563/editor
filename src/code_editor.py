"""
Code Editor Widget

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: December 2015
"""

from PyQt4.QtCore import Qt
from PyQt4 import QtCore
from PyQt4 import QtGui

from collections import OrderedDict

from syntax import CodeHighlighter

class CodeEditor(QtGui.QTextEdit):
    """
    """

    def __init__(self, parent):
        super(CodeEditor, self).__init__(parent)
        self.completer = QtGui.QCompleter()
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insertCompletion)

        self.model = QtGui.QStringListModel()
        self.completer.setModel(self.model)
        self.model.setStringList(
            ['string', 'float32', 'float64', 'bool', 'time', 'duration',
             'int8', 'int16', 'int32', 'int64',
             'uint8', 'uint16', 'uint32', 'uint64']
        )

        self.highlighter = CodeHighlighter(self.document())

    def insertCompletion(self, completion):
        if (self.completer.widget() != self):
            return
        tc = self.textCursor()
        extra = completion.length() - self.completer.completionPrefix().length()
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

        isShortcut = (event.modifiers() and Qt.ControlModifier and event.key() == Qt.Key_E)
        if (not self.completer or not isShortcut):
            QtGui.QTextEdit.keyPressEvent(self, event)
        
        ctrlOrShift = (event.modifiers() and (Qt.ControlModifier or Qt.ShiftModifier))
        if (not self.completer or (not ctrlOrShift and event.text().isEmpty())):
            return

        eow = QtCore.QString("~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=")
        hasModifier = ((event.modifiers() != Qt.NoModifier) and not ctrlOrShift)
        completionPrefix = self.textUnderCursor()
        
        if (not isShortcut and (hasModifier or event.text().isEmpty() or completionPrefix.length() <= 1 or\
                             eow.contains(event.text().right(1)))):
            self.completer.popup().hide()
            return

        if (completionPrefix != self.completer.completionPrefix()):
            self.completer.setCompletionPrefix(completionPrefix)
            self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))
        
        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) +\
                    self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)
