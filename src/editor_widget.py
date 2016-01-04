'''
Editor Widget 

These classes allow users to view
and edit models in the project in tabs.
'''

__author__ = 'William Emfinger'
__copyright__ = 'Copyright 2016, ROSMOD'
__credits__ = ['William Emfinger', 'Pranav Srinivas Kumar']
__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'William Emfinger'
__email__ = 'emfinger@isis.vanderbilt.edu'
__status__ = 'Production'

from PyQt4 import QtCore
from PyQt4 import QtGui

from collections import OrderedDict

import jsonpickle, copy

from attribute_widget import AttributeEditor
from editor_item import EditorItem
from view_model import ViewModel
from action import Action
from layout import layout_create

class EditorScene(QtGui.QGraphicsScene):
    def __init__(self, parent):
        super(EditorScene, self).__init__(parent)
        self._root = None

    def setRoot(self, r):
        self._root = r

    def getRoot(self):
        return self._root

    def viewModel(self):
        return self.views()[0].viewModel()

    def contextMenuEvent(self, event):
        item = self.itemAt(event.scenePos())
        if item:
            item.contextMenuEvent(event)
        else:
            menu = QtGui.QMenu()
            for a in self.getRoot().model().children._allowed:
                addNewItem = Action('','New {}'.format(a.__name__), self)
                addNewItem.triggered.connect(self.getRoot().addNewItem(a))
                menu.addAction(addNewItem)
            menu.exec_(event.screenPos())

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

    def init_ui(self, obj = None, fname = ''):
        scene = EditorScene(self)
        self.setScene(scene)

        # not the right way to handle model viewing;
        # should not store a reference to the actual model
        self._root_model = obj

        # view model is static; will NEVER be edited or viewed,
        # and will never be used by anything but a scene/view and their
        # children, so we keep a reference to the view model open here
        self.view_model = None

        try:
            if not fname:
                fname = obj.kind + '.view'
            self.loadVM(fname)
            r = self.buildView( model = obj )
        except Exception, e:
            print 'WARNING: Could not load \'{}\' to generate view for {}:\n\t{}'.format(
                fname, obj['name'], e
            )
            # How to initialize self.view_model here?
            r = EditorItem( model = obj )

        scene.setRoot(r)
        scene.addItem(r)

        self.show()

    def viewModel(self):
        return self.view_model

    def buildView(self, model, parent = None):
        t = EditorItem(parent = parent, model = model)
        for cm in model.children:
            t.addChild(self.buildView(cm, t))
        return t

    def loadVM(self, fname):
        with open(fname, 'r') as f:
            vm = jsonpickle.decode(f.read())
        self.view_model = vm

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
