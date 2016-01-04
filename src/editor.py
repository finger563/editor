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
from PyQt4.QtCore import Qt

import copy

from action import Action
from editor_widget import TabbedEditor, EditorView

from item_model import ItemModel, SortFilterProxyModel

from meta import Model, Attribute, Children

from tree_view import TreeView

from test_model import TestModel

class Editor(QtGui.QMainWindow):

    # Models the editor is designed to load/edit/save
    # All inherit at some point from the original base model classes
    # Defined in meta.py
    editor_modes = ['model','meta model','view model']

    filter_types = ['Meta','Name']

    def __init__(self):
        super(Editor, self).__init__()
        self.init_model()
        self.init_ui()
        self.setWindowIcon(QtGui.QIcon("icons/editor.png"))

    def init_model(self):
        # Set up the editor mode
        self.editor_mode = 'meta model'
        self.meta_model = None
        self.model = None
        self.view_model = None

        # Set up the proxy model for sorting/filtering
        self.proxy_model = SortFilterProxyModel(self)
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy_model.setSortRole(ItemModel.sort_role)
        self.proxy_model.setFilterRole(ItemModel.filter_role)

        # Set up the actual model
        self.model = ItemModel(TestModel)

        # Link the actual model and the proxy model
        self.proxy_model.setSourceModel(self.model)
        

    def init_ui(self):
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setStyleSheet("""QToolTip {
                           background-color: black;
                           color: white;
                           border: black solid 1px
                           }""")
        self.setGeometry(300,300,800,600)
        self.setWindowTitle("Editor")

        # Create the actions for the program
        exitAction = Action('icons/toolbar/stop.png', '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close) # note that this will call closeEvent

        # Create the widgets for the program (embeddable in the toolbar or elsewhere)
        self.mode_selector = QtGui.QComboBox(self)
        self.mode_selector.addItems(self.editor_modes)
        self.mode_selector.setCurrentIndex(self.editor_modes.index(self.editor_mode))
        self.mode_selector.currentIndexChanged.connect(self.changeMode)

        # Set up the Menus for the program
        self.menubar_init()
        self.menubar_add_menu('&File')
        self.menu_add_action('&File',exitAction)

        # Set up the toolbars for the program
        self.toolbar_init()
        self.toolbar_create("toolbar1")
        self.toolbar_add_action("toolbar1",exitAction)
        self.toolbar_add_widget('toolbar1',self.mode_selector)

        # Set up the Tree View Widget
        self.tree_view = TreeView()
        self.tree_view.setModel(self.proxy_model)
        self.tree_view.setSortingEnabled(False)

        # Set up filtering on the tree_view
        self.filter_widget = QtGui.QWidget()
        self.filter_hbox = QtGui.QHBoxLayout()
        self.filter_label = QtGui.QLabel("Filter:")
        self.filter_type = QtGui.QComboBox(self)
        self.filter_type.addItems(self.filter_types)
        self.filter_type.setCurrentIndex(self.filter_types.index(self.model.filter_type))
        self.filter_type.currentIndexChanged.connect(self.changeFilter)
        self.filter_hbox.addWidget(self.filter_label)
        self.filter_hbox.addWidget(self.filter_type)
        self.filter_widget.setLayout(self.filter_hbox)
        self.filter_edit = QtGui.QLineEdit()
        self.filter_edit.textChanged.connect(self.proxy_model.setFilterRegExp)

        # Set up the navigator (tree viewer + filter)
        self.navigator = QtGui.QWidget()
        self.navigator_vbox = QtGui.QVBoxLayout()
        self.navigator_vbox.addWidget(self.filter_widget)
        self.navigator_vbox.addWidget(self.filter_edit)
        self.navigator_vbox.addWidget(self.tree_view)
        self.navigator.setLayout(self.navigator_vbox)
        
        # Create the Visualizer
        self.tabbedEditorWidget = TabbedEditor(self)
        self.openEditorTabs = {}

        # Split the main part into visualizer and tree_view
        self.splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter1.addWidget(self.navigator)
        self.splitter1.addWidget(self.tabbedEditorWidget)
        self.splitter1.setSizes([self.geometry().x()/4.0, 3.0 * self.geometry().x()/4.0])

        # Set the central widget of the application (the visualizer + tree_view)
        self.setCentralWidget(self.splitter1)

        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def clearModels(self):
        self.meta_model = None
        self.model = None
        self.view_model = None

    def clearEditor(self):
        self.openEditorTabs = {}
        self.tabbedEditorWidget.clear()

    def changeFilter(self, index):
        text = self.filter_type.currentText()
        if text != self.model.filter_type:
            self.model.set_filter_type(text)
            self.proxy_model.invalidate()

    def changeMode(self, index):
        text = self.mode_selector.currentText()
        if text != self.editor_mode:
            self.editor_mode = text
            self.clearEditor()
            # TODO: NEED TO UPDATE TREE VIEW MODEL WITH NEW TYPE OF MODEL
        
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

    from menubar import \
        menubar_init, \
        menubar_add_menu, \
        menu_add_action

    from toolbar import \
        toolbar_init, \
        toolbar_create, \
        toolbar_add_action, \
        toolbar_add_widget, \
        toolbar_remove

    from action import \
        action_init, \
        action_create

    from context_menu import \
        context_menu_init, \
        context_menu_create, \
        context_menu_add_action

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    editor = Editor()
    sys.exit(app.exec_())
