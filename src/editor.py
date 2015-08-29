#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Meta-Model Editor 

This program allows users to operate 
on meta-models and models using loadable
libraries to perform meta-model specific
operations such as generation, analysis,
and deployment.

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: July 2015
"""

from PyQt4 import QtCore
from PyQt4 import QtGui

from action import Action
from worker import Worker
from model_tree import ModelTree
from editor_widget import TabbedEditor
from output import TabbedOutputWidget

class Editor(QtGui.QMainWindow):

    def __init__(self):
        super(Editor, self).__init__()
        self.init_ui()

    def init_ui(self):
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setGeometry(300,300,800,600)
        self.setWindowTitle("Editor")

        exitAction = Action('icons/toolbar/stop.png', '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close) # note that this will call closeEvent

        testAction = Action('icons/toolbar/build.png', '&Build', self)
        testAction.setStatusTip('Build code.')
        testAction.triggered.connect(self.testEvent)

        saveAction = Action('icons/toolbar/save.png', '&Save', self)
        saveAction.setStatusTip('Save.')
        saveAction.triggered.connect(self.saveEvent)

        self.menubar_init()
        self.menubar_add_menu('&File')
        self.menu_add_action('&File',exitAction)

        self.toolbar_init()
        self.toolbar_create("test1")
        self.toolbar_add_action("test1",exitAction)
        self.toolbar_create("test2")
        self.toolbar_add_action("test2",testAction)
        self.toolbar_add_action("test2",saveAction)

        self.modelTree = ModelTree(None)
        self.modelTree.populate()
        self.modelTree.itemDoubleClicked.connect(self.modelTreeItemDoubleClicked)
        self.tabbedEditorWidget = TabbedEditor(self)

        self.splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter1.addWidget(self.modelTree)
        self.splitter1.addWidget(self.tabbedEditorWidget)
        self.splitter1.setSizes([self.geometry().x()/4.0, 3.0 * self.geometry().x()/4.0])

        self.splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter2.addWidget(self.splitter1)
        self.tabbedOutput = TabbedOutputWidget(self)
        self.splitter2.addWidget(self.tabbedOutput)

        self.setCentralWidget(self.splitter2)

        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def modelTreeItemDoubleClicked(self, item, col):
        print 'Clicked on {}'.format(item.Object())

    def saveEvent(self, event):
        fname = 'view.txt'
        self.tabbedEditorWidget.currentWidget().saveVM(fname)
        test = QtGui.QMessageBox.information(self, 'Build',
                                             'Saved {}.'.format(fname))
        
        
    def testEvent(self, event):
        test = QtGui.QMessageBox.information(self, 'Build',
                                             'Build succeeded.')

    def closeEvent(self, event):
        event.accept()
        return
        reply = QtGui.QMessageBox.question(self, 'Quit',
                                           "You're sure you want to quit?", QtGui.QMessageBox.Yes | 
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore() 

    from menubar import menubar_init, menubar_add_menu, menu_add_action
    from toolbar import toolbar_init, toolbar_create, toolbar_add_action, toolbar_remove

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    editor = Editor()
    sys.exit(app.exec_())
