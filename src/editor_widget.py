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

import jsonpickle

from attribute_widget import AttributeEditor
from editor_item import EditorItem
from view_model import ViewModel
from action import Action

class EditorScene(QtGui.QGraphicsScene):
    def __init__(self, parent = None):
        super(EditorScene, self).__init__(parent)
        self._root = None

    def setRoot(self, r):
        self._root = r

    def getRoot(self):
        return self._root

    '''
    def contextMenuEvent(self, event):
        item = self.itemAt(event.scenePos())
        if item:
            item.contextMenuEvent(event)
        else:
            menu = QtGui.QMenu()

            addNewItem = Action('','New Editor Item', self)
            addNewItem.triggered.connect(lambda e : self.createNewItem(e, event.scenePos()))
            menu.addAction(addNewItem)

            menu.exec_(event.screenPos())

    def createNewItem(self, event, pos):
        self.getRoot().addChild(EditorItem(self.getRoot(), viewModel = ViewModel()))
    '''

class EditorView(QtGui.QGraphicsView):

    drag_mode_key = QtCore.Qt.Key_Control
    scroll_mode_key = QtCore.Qt.Key_Control
    close_aw_key = QtCore.Qt.Key_Escape

    def __init__(self, parent):
        super(EditorView,self).__init__(parent)
        self.aw = AttributeEditor(self)
        self.aw.updateGeo()

    def init_ui(self, obj = None, fname = ''):
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self._command_key_pressed = False
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

        scene = EditorScene(self)
        self.setScene(scene)

        try:
            if not fname:
                fname = obj.kind + '.view'
            vm = self.openVM(fname)
            r = self.buildView(vm)
        except:
            r = EditorItem(
                viewModel = ViewModel(kind = obj.kind)
            )
        scene.setRoot(r)
        scene.addItem(r)

        self.show()

    def saveVM(self, fname):
        jsonpickle.set_encoder_options('simplejson',indent=4)
        root_items = [x for x in self.scene().items() if not x._parent]
        if not root_items:
            print "ERROR: MUST HAVE AT LEAST ONE ITEM"
            return
        elif len(root_items) > 1:
            print "WARNING: ADDING TOP LEVEL CONTAINER TO {}".format(fname)
            root = EditorItem( viewModel = ViewModel() )
            for r in root_items:
                root.addChild(r)
        else:
            root = root_items[0]
        encoded_output = jsonpickle.encode(root.viewModel()) + '\n'
        with open(fname, 'w') as f:
            f.write(encoded_output)

    def openVM(self, fname):
        with open(fname, 'r') as f:
            vm = jsonpickle.decode(f.read())
        return vm

    def buildView(self, viewModel, parent = None):
        t = EditorItem(parent=parent,viewModel=viewModel)
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
        elif event.key() == self.close_aw_key:
            self.aw.cancel(None)

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
       
    def onTabClose(self,index):
        self.removeTab(index)
