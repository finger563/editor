"""
Editor Widget 

These classes allow users to view
and edit models in the project in tabs.

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: August 2015
"""

from PyQt4 import QtCore
from PyQt4 import QtGui

from collections import OrderedDict

import json,jsonpickle

from attribute_widget import AttributeEditor
from editor_item import EditorItem
from view_model import ViewModel

class EditorScene(QtGui.QGraphicsScene):
    def __init__(self, parent = None):
        super(EditorScene, self).__init__(parent)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.scenePos())
        if item:
            item.contextMenuEvent(event)
        else:
            menu = QtGui.QMenu()
            menu.addAction("EditorScene")
            menu.exec_(event.screenPos())

class EditorView(QtGui.QGraphicsView):

    drag_mode_key = QtCore.Qt.Key_Control
    scroll_mode_key = QtCore.Qt.Key_Control

    def __init__(self, parent):
        super(EditorView,self).__init__(parent)
        self.init_ui()
        self.root = None

    def init_ui(self):
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self._command_key_pressed = False
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

        scene = EditorScene(self)

        fname = 'view.txt'
        vm = self.openVM(fname)
        r = self.buildView(vm)
        self.root = r
        scene.addItem(r)

        self.saveVM(fname)
        
        self.setScene(scene)
        self.show()

        self.aw = AttributeEditor(self)
        self.aw.updateGeo()

    def saveVM(self, fname):
        with open(fname, 'w') as f:
            f.write(json.dumps(json.loads(jsonpickle.encode(self.root.viewModel())), indent=4))

    def openVM(self, fname):
        with open(fname, 'r') as f:
            vm = jsonpickle.decode(f.read())
        return vm

    def buildView(self, viewModel, parent = None):
        t = EditorItem(viewModel=viewModel)
        for cvm in viewModel.children:
            t.addChild(self.buildView(cvm, t))
        return t

    def getEditor(self):
        return self.aw

    def mousePressEvent(self, event):
        QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        QtGui.QGraphicsView.mouseReleaseEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        QtGui.QGraphicsView.mouseDoubleClickEvent(self, event)
        
    def keyPressEvent(self, event):
        QtGui.QGraphicsView.keyPressEvent(self, event)
        if event.key() == self.drag_mode_key:
            self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
            self._command_key_pressed = True

    def keyReleaseEvent(self, event):
        QtGui.QGraphicsView.keyReleaseEvent(self, event)
        if event.key() == self.drag_mode_key:
            self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
            self._command_key_pressed = False

    def resizeEvent(self, event):
        QtGui.QGraphicsView.resizeEvent(self, event)
        self.aw.updateGeo()

    def wheelEvent(self, event):
        if self._command_key_pressed:
            zoomInFactor = 1.25
            zoomOutFactor = 1 / zoomInFactor

            # Save the scene pos
            oldPos = self.mapToScene(event.pos())

            # Zoom
            if event.delta() > 0:
                zoomFactor = zoomInFactor
            else:
                zoomFactor = zoomOutFactor
            self.scale(zoomFactor, zoomFactor)

            oldPosNow = self.mapFromScene(oldPos)
            move = oldPosNow - event.pos()
            self.horizontalScrollBar().setValue(move.x() + self.horizontalScrollBar().value())
            self.verticalScrollBar().setValue(move.y() + self.verticalScrollBar().value())
        else:
            QtGui.QGraphicsView.wheelEvent(self, event)

class TabbedEditor(QtGui.QTabWidget):
    def __init__(self, parent):
        super(TabbedEditor, self).__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setUsesScrollButtons(True)

        self.tabCloseRequested.connect(self.onTabClose)

        newPage = EditorView(self)
        self.addTab(newPage, "test1")
        newPage = EditorView(self)
        self.addTab(newPage, "test2")
       
    def onTabClose(self,index):
        self.removeTab(index)
