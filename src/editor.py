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
from editor_widget import TabbedEditor, EditorView
from output import TabbedOutputWidget

import metamodel.project as ROSMOD
from interface import ROSMOD_Interface

rosmod_intf = ROSMOD_Interface()
rosmod_intf.new_project( path = ROSMOD.Path("./") )

project = rosmod_intf.project

class Editor(QtGui.QMainWindow):

    editor_modes = ['view model','model','meta model']

    def __init__(self):
        super(Editor, self).__init__()
        self.editor_mode = 'model'
        self.init_ui()

    def init_ui(self):
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setStyleSheet("""QToolTip {
                           background-color: black;
                           color: white;
                           border: black solid 1px
                           }""")
        self.setGeometry(300,300,800,600)
        self.setWindowTitle("Editor")

        exitAction = Action('icons/toolbar/stop.png', '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close) # note that this will call closeEvent

        modeAction = Action('icons/toolbar/run.png', '&Mode', self)        
        modeAction.setStatusTip('Select editor mode')
        modeAction.triggered.connect(self.changeMode)

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
        self.toolbar_add_action("test1",modeAction)
        self.toolbar_create("test2")
        self.toolbar_add_action("test2",testAction)
        self.toolbar_add_action("test2",saveAction)

        self.modelTree = ModelTree(None)
        self.buildTree(self.modelTree)
        self.modelTree.itemDoubleClicked.connect(self.modelTreeItemDoubleClicked)
        self.tabbedEditorWidget = TabbedEditor(self)
        self.openEditorTabs = {}

        self.splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter1.addWidget(self.modelTree)
        self.splitter1.addWidget(self.tabbedEditorWidget)
        self.splitter1.setSizes([self.geometry().x()/4.0, 3.0 * self.geometry().x()/4.0])

        self.splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter2.addWidget(self.splitter1)
        self.tabbedOutput = TabbedOutputWidget(self)
        self.splitter2.addWidget(self.tabbedOutput)
        self.splitter2.setSizes([3.0 * self.geometry().y()/4.0, self.geometry().y()/4.0])

        self.setCentralWidget(self.splitter2)

        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def clearEditor(self):
        self.openEditorTabs = {}
        self.tabbedEditorWidget.clear()

    def buildTree(self, tree):
        tree.clear()
        if self.editor_mode in ['model']:
            tree.load_model(project)
        elif self.editor_mode in ['view model','meta model']:
            tree.load_meta_model(project)

    def modelTreeItemDoubleClicked(self, item, col):
        name = item.text(0)
        if name not in self.openEditorTabs:
            ev = EditorView( self.tabbedEditorWidget )
            ev.init_ui(
                obj = item.Object(),
                fname = item.Object().kind + '.view',
                view_type = self.editor_mode
            )
            self.openEditorTabs[name] = ev
            self.tabbedEditorWidget.addTab( ev, name )
        elif self.tabbedEditorWidget.indexOf(self.openEditorTabs[name]) < 0:
            ev = self.openEditorTabs[name]
            self.tabbedEditorWidget.addTab( ev, name )
        self.tabbedEditorWidget.setCurrentIndex(
            self.tabbedEditorWidget.indexOf(self.openEditorTabs[name]))
            
    def saveEvent(self, event):
        if self.editor_mode == 'view model':
            self.saveCurrentViewModel()
        elif self.editor_mode == 'model':
            self.saveCurrentModel()
            
    def saveCurrentModel(self):
        pass

    def saveCurrentViewModel(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                     "Save view file",
                                                     '',
                                                     "View Files (*.view)",
                                                     options = QtGui.QFileDialog.Options())
        if fileName:
            if fileName[-5:] != '.view': fileName += '.view'
            if self.tabbedEditorWidget.currentWidget().saveVM(fileName) == 0:
                test = QtGui.QMessageBox.information(self, 'Build',
                                                     'Saved {}.'.format(fileName))
        

    def changeMode(self, event):
        item, ok = QtGui.QInputDialog.getItem(self, "Select View Mode",
                                              "View Mode:", self.editor_modes,
                                              self.editor_modes.index(self.editor_mode), False)
        if ok and item:
            if item != self.editor_mode:
                self.editor_mode = item
                self.clearEditor()
                self.buildTree(self.modelTree)
        
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
    from action import action_init, action_create
    from context_menu import context_menu_init, context_menu_create, context_menu_add_action

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    editor = Editor()
    sys.exit(app.exec_())
