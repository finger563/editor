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
from editor_widget import TabbedEditor, EditorView
from output import TabbedOutputWidget

from item_model import ItemModel, SortFilterProxyModel

import metamodel.importer as rosmod

rootNode = rosmod.Project()
rootNode['name'].value = "Project Root"

dep = rosmod.Deployment()
dep['name'].value = "My Deployment"
rootNode.add_child(dep)

sw = rosmod.Software()
sw['name'].value = "My Software"
rootNode.add_child(sw)

pkg = rosmod.Package()
pkg['name'].value = "My Package"
sw.add_child(pkg)

msg = rosmod.Message()
msg['name'].value = "My Message"
msg['definition'].value = "int8 testInt = 2\nbool testBool = False"
pkg.add_child(msg)

srv = rosmod.Service()
srv['name'].value = "My Service"
srv['definition'].value = "int8 testInt = 2\nbool testBool = False\n---\nbool retVal"
pkg.add_child(srv)

comp = rosmod.Component()
comp['name'].value = "My Component"
pkg.add_child(comp)

tmr = rosmod.Timer()
tmr['name'].value = "My Timer"
comp.add_child(tmr)
    
hw = rosmod.Hardware()
hw['name'].value = "My Hardware"
rootNode.add_child(hw)

root_node = rootNode

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

        testAction = Action('icons/toolbar/build.png', '&Build', self)
        testAction.setStatusTip('Build code.')
        testAction.triggered.connect(self.testEvent)

        saveAction = Action('icons/toolbar/save.png', '&Save', self)
        saveAction.setStatusTip('Save.')
        saveAction.triggered.connect(self.saveEvent)

        self.mode_selector = QtGui.QComboBox()
        self.mode_selector.addItems(['model','meta model','view model'])
        self.mode_selector.currentIndexChanged.connect(self.changeMode)

        self.menubar_init()
        self.menubar_add_menu('&File')
        self.menu_add_action('&File',exitAction)

        self.toolbar_init()
        self.toolbar_create("toolbar1")
        self.toolbar_add_action("toolbar1",exitAction)
        self.toolbar_add_widget('toolbar1',self.mode_selector)
        self.toolbar_create("toolbar2")
        self.toolbar_add_action("toolbar2",testAction)
        self.toolbar_add_action("toolbar2",saveAction)

        self.proxy_model = SortFilterProxyModel()
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy_model.setSortRole(ItemModel.sort_role)
        self.proxy_model.setFilterRole(ItemModel.filter_role)

        self.model = ItemModel(root_node)

        self.proxy_model.setSourceModel(self.model)

        self.tree_view = QtGui.QTreeView()
        self.tree_view.setModel(self.proxy_model)
        self.tree_view.doubleClicked.connect(self.treeItemDoubleClicked)
        self.tree_view.setSortingEnabled(False)
        #self.tree_view.selectionModel().currentChanged.connnect(self.treeItemDoubleClicked)

        self.filter_edit = QtGui.QLineEdit()
        self.filter_edit.textChanged.connect(self.proxy_model.setFilterRegExp)
        self.filter_label = QtGui.QLabel("Filter:")

        self.navigator = QtGui.QWidget()
        self.navigator_vbox = QtGui.QVBoxLayout()
        self.navigator_vbox.addWidget(self.filter_label)
        self.navigator_vbox.addWidget(self.filter_edit)
        self.navigator_vbox.addWidget(self.tree_view)
        self.navigator.setLayout(self.navigator_vbox)
        
        self.tabbedEditorWidget = TabbedEditor(self)
        self.openEditorTabs = {}

        self.splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter1.addWidget(self.navigator)
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

    def treeItemDoubleClicked(self, modelIndex):
        mi = self.proxy_model.mapToSource(modelIndex)
        item = self.model.getModel( mi )
        name = item["name"].value
        if name not in self.openEditorTabs:
            ev = EditorView( self.tabbedEditorWidget )
            ev.init_ui(
                obj = item,
                fname = item.kind + '.view',
                view_type = self.editor_mode
            )
            ev.getEditor().setModel(self.proxy_model)
            # TODO: FIX THIS SO THAT THE VIEW'S EDITOR MODEL IS SET TO THE VIEW'S SELECTION CHANGED
            self.tree_view.selectionModel().currentChanged.connect(ev.getEditor().setSelection)
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
        

    def changeMode(self, index):
        text = self.mode_selector.currentText()
        if text != self.editor_mode:
            self.editor_mode = text
            self.clearEditor()
            # TODO: NEED TO UPDATE TREE VIEW MODEL WITH NEW TYPE OF MODEL
        
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
    from toolbar import toolbar_init, toolbar_create, toolbar_add_action, toolbar_add_widget, toolbar_remove
    from action import action_init, action_create
    from context_menu import context_menu_init, context_menu_create, context_menu_add_action

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    editor = Editor()
    sys.exit(app.exec_())
