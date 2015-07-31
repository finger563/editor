"""
Editor Widget 

These classes allow users to view
and edit models in the project in tabs.

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: July 2015
"""

from PyQt4 import QtCore
from PyQt4 import QtGui

import jsonpickle

class EditorObjectWidget(QtGui.QGraphicsItem):
    # NEED TO HANDLE MOUSE MOVE EVENTS LOOKING FOR ANCHOR POINTS IN PARENT
    # TO WHICH WE CAN ATTACH?
    def __init__(self,parent, image):
        super(EditorObjectWidget, self).__init__(parent)

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QtGui.QGraphicsItem.ItemClipsToShape)
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)

        self.image = QtGui.QImage(image)
        self.pixmapItem = QtGui.QGraphicsPixmapItem()
        self.pixmapItem.setPixmap(QtGui.QPixmap.fromImage(self.image))

        self.validDrag = False

    def setAnchorPoint(self, anchor):
        pass

    def mousePressEvent(self, event):
        if self.shape().contains(event.pos()):
            QtGui.QGraphicsItem.mousePressEvent(self,event)
            self.dragPos = self.mapFromScene(event.scenePos())
            self.validDrag = True
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if self.validDrag:
            QtGui.QGraphicsItem.mouseReleaseEvent(self, event)
            pos = event.scenePos()
            items = [x for x in self.scene().items(event.scenePos()) if x != self]
            if items:
                self.setParentItem(items[0])
                self.setZValue(items[0].zValue()+1)
                self.setPos(self.parentItem().mapFromScene(pos) - self.dragPos)
            elif self.parentItem():
                scene = self.scene()
                self.setParentItem(None)
                scene.addItem(self)
                self.setPos(pos - self.dragPos)
            self.setCursor(QtCore.Qt.OpenHandCursor)
            self.validDrag = False
        else:
            event.ignore()

    def boundingRect(self):
        return self.pixmapItem.boundingRect()
        
    def paint(self, painter, option, widget = None):
        self.pixmapItem.paint(painter, option, widget)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        menu.addAction("object")
        menu.exec_(event.screenPos())

class EditorView(QtGui.QGraphicsView):
    def __init__(self, parent = None):
        super(EditorView, self).__init__(parent)

    def dragMoveEvent(self, event):
        QtGui.QGraphicsView.dragMoveEvent(self,event)

    def dropEvent(self, event):
        QtGui.QGraphicsView.dropEvent(self,event)

class EditorScene(QtGui.QGraphicsScene):
    def __init__(self, parent = None):
        super(EditorScene, self).__init__(parent)

    def dragMoveEvent(self, event):
        QtGui.QGraphicsScene.dragMoveEvent(self,event)

    def dropEvent(self, event):
        QtGui.QGraphicsScene.dropEvent(self,event)

class EditorWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(EditorWidget,self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.hbox = QtGui.QHBoxLayout(self)

        scene = EditorScene(self)

        test = EditorObjectWidget(None, 'icons/model/Hardware.png')
        test2 = EditorObjectWidget(test, 'icons/toolbar/generate.png')
        test3 = EditorObjectWidget(test, 'icons/toolbar/build.png')
        scene.addItem(test)


        view = EditorView(scene)
        view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        #view.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        matrix = QtGui.QMatrix()
        matrix.scale(0.5,0.5)
        view.setMatrix(matrix)

        view.show()

        self.hbox.addWidget(view)
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

        self.tabCloseRequested.connect(self.onTabClose)

        newPage = EditorWidget(self)
        self.addTab(newPage, "test1")
        newPage = EditorWidget(self)
        self.addTab(newPage, "test2")
        
    def onTabClose(self,index):
        self.removeTab(index)
