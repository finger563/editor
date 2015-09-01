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
from view_model_item import ViewModelItem
from model_item import ModelItem
from view_model import ViewModel
from action import Action
from layout import layout_create

class EditorScene(QtGui.QGraphicsScene):
    def __init__(self, parent = None, itemType = ViewModelItem):
        super(EditorScene, self).__init__(parent)
        self._root = None
        self._item_type = itemType

    def setRoot(self, r):
        self._root = r

    def getRoot(self):
        return self._root

    def contextMenuEvent(self, event):
        item = self.itemAt(event.scenePos())
        if item:
            item.contextMenuEvent(event)
        else:
            menu = QtGui.QMenu()

            addNewItem = Action('','New {}'.format(self._item_type.__name__), self)
            addNewItem.triggered.connect(lambda e : self.createNewItem(e, event.scenePos()))
            menu.addAction(addNewItem)

            menu.exec_(event.screenPos())

    def createNewItem(self, event, pos):
        r = self._item_type( view_model = ViewModel())
        r.setPos(pos)
        self.addItem(r)

class EditorView(QtGui.QGraphicsView):

    drag_mode_key = QtCore.Qt.Key_Control
    scroll_mode_key = QtCore.Qt.Key_Control
    close_aw_key = QtCore.Qt.Key_Escape

    def __init__(self, parent):
        super(EditorView,self).__init__(parent)
        self.aw = AttributeEditor(self)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self._command_key_pressed = False
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

    def init_ui(self, obj = None, fname = '', view_type = 'model'):
        if view_type in ['meta model','view model']:
            scene = EditorScene(self, ViewModelItem)
        elif view_type in ['model']:
            scene = EditorScene(self, ModelItem)
        self.setScene(scene)
        self.view_type = view_type
        self._root_model = obj

        try:
            if not fname:
                fname = obj.kind + '.view'
            vm = self.openVM(fname)
            if self.view_type == 'model':
                r = self.buildModel( model = obj, view_model = vm)
            elif self.view_type == 'view model':
                r = self.buildViewModel( view_model = vm)
        except Exception, e:
            print "WARNING: Could not load '{}' to generate '{}' view for {}:\n\t{}".format(
                fname, self.view_type, obj['name'].value, e
            )
            if self.view_type in ['model']:
                r = ModelItem(
                    model = obj,
                    view_model = ViewModel(kind = obj.kind)
                )
            elif self.view_type in ['view model','meta model']:
                r = ViewModelItem(
                    view_model = ViewModel(kind = obj.kind)
                )
        scene.setRoot(r)
        scene.addItem(r)

        self.show()

    def buildModel(self, model, view_model, parent = None):
        vm = view_model
        _kind = vm['kind'].value
        objs = []
        t = ModelItem( parent = parent, view_model = vm, model = model )
        if _kind in ['Container']:
            t.viewModel()['draw style'].value = 'hidden'
        for cvm in vm.children:
            _kind = cvm['kind'].value
            _scope = cvm['scope'].value
            if _scope in ['view','project']:
                objs = self._root_model.get_children(_kind)
            elif _scope in ['parent']:
                objs = model.get_children(_kind)
            if objs:
                layout_item = ModelItem( parent = t, view_model = cvm )
                layout_item.viewModel()['kind'].value = 'Container'
                for obj in objs:
                    layout_item.addChild(self.buildModel( model = obj,
                                                          view_model = cvm,
                                                          parent = layout_item ) )
                t.addChild(layout_item)
        return t

    def buildViewModel(self, view_model, parent = None):
        vm = view_model
        t = ViewModelItem(parent = parent, view_model = vm)
        for cvm in vm.children:
            t.addChild(self.buildViewModel(cvm, t))
        return t

    def saveVM(self, fname):
        root_items = [x for x in self.scene().items() if not x._parent]
        if not root_items:
            print "ERROR: MUST HAVE AT LEAST ONE ITEM"
            return -1
        elif len(root_items) > 1:
            print "WARNING: ADDING TOP LEVEL CONTAINER TO {}".format(fname)
            root = ViewModelItem( view_model = ViewModel() )
            for r in root_items:
                root.addChild(r)
        else:
            root = root_items[0]
        print root.viewModel().toStr()
        jsonpickle.set_encoder_options('simplejson',indent=4)
        encoded_output = jsonpickle.encode(root.viewModel())
        with open(fname, 'w') as f:
            f.write(encoded_output)
        return 0

    def openVM(self, fname):
        with open(fname, 'r') as f:
            vm = jsonpickle.decode(f.read())
        return vm

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
            oldPos = self.mapToScene(event.pos())
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
