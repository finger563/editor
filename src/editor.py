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

class EditorWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(EditorWidget,self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.hbox = QtGui.QHBoxLayout(self)

        grview = QtGui.QGraphicsView(self)
        scene = QtGui.QGraphicsScene(self)
        pixmap = scene.addPixmap(QtGui.QPixmap('icons/model/Hardware.png'))
        pixmap.setAcceptHoverEvents(True)
        matrix = QtGui.QMatrix()
        matrix.scale(0.5,0.5)
        #grview.setMatrix(matrix)
        grview.setScene(scene)
        #grview.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        grview.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        grview.show()

        self.hbox.addWidget(grview)
        self.setLayout(self.hbox)

        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        menu.addAction("sample")
        menu.exec_(event.globalPos())

class TabbedEditorWidget(QtGui.QTabWidget):
    def __init__(self, parent):
        super(TabbedEditorWidget, self).__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setUsesScrollButtons(True)

        newPage = EditorWidget(self)
        self.addTab(newPage, "test1")
        newPage = EditorWidget(self)
        self.addTab(newPage, "test2")
        
        
class Editor(QtGui.QMainWindow):

    def __init__(self):
        super(Editor, self).__init__()
        self.init_ui()

    def init_ui(self):

        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        exitAction = Action('icons/toolbar/stop.png', '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.menubar_init()
        self.menubar_add_menu('&File')
        self.menu_add_action('&File',exitAction)

        self.toolbar_init()
        self.toolbar_create("test1")
        self.toolbar_add_action("test1",exitAction)
        self.toolbar_create("test2")
        self.toolbar_add_action("test2",exitAction)

        self.modelTree = ModelTree(self)
        self.modelTree2 = ModelTree(self)
        self.tabbedEditorWidget = TabbedEditorWidget(self)

        self.splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter1.addWidget(self.modelTree)
        self.splitter1.addWidget(self.tabbedEditorWidget)

        self.splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.addWidget(self.modelTree2)

        self.setCentralWidget(self.splitter2)

        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setGeometry(300,300,800,600)
        self.setWindowTitle("Editor")

        self.show()

    from menubar import menubar_init, menubar_add_menu, menu_add_action
    from toolbar import toolbar_init, toolbar_create, toolbar_add_action, toolbar_remove

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    editor = Editor()
    sys.exit(app.exec_())
