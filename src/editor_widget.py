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

# IMPLEMENT SERIALIZATION AND DESERIALIZATION
# IMPLEMENT ANCHORING
# IMPLEMNET DRAW STYLING

class EditorObjectWidget(QtGui.QGraphicsItem):
    # NEED TO HANDLE MOUSE MOVE EVENTS LOOKING FOR ANCHOR POINTS IN PARENT
    # TO WHICH WE CAN ATTACH?
    def __init__(self, parent = None):
        super(EditorObjectWidget, self).__init__(parent)

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QtGui.QGraphicsItem.ItemClipsToShape)
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)

        self.anchorPoint = None
        self.width = 50
        self.height = 50
        self.anchor = "center"
        self.anchor_distance = 10
        self.validDrag = False

        print self.getAnchors()

    def getAnchors(self):
        a = QtCore.QRectF(0, 0, self.width, self.height)
        anchorList = {
            "bottom left": a.bottomLeft(),
            "bottom right": a.bottomRight(),
            "top left": a.topLeft(),
            "top right": a.topRight(),
            "center": a.center(),
            "center left": (a.topLeft() + a.bottomLeft()) / 2.0,
            "center right": (a.topRight() + a.bottomRight()) / 2.0,
            "top center": (a.topLeft() + a.topRight()) / 2.0,
            "bottom center": (a.bottomLeft() + a.bottomRight()) / 2.0
        }
        return anchorList

    def hoverEnterEvent(self, event):
        QtGui.QGraphicsItem.hoverEnterEvent(self, event)

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
        #return QtGui.QGraphicsItem.boundingRect(self)
        return QtCore.QRectF(0, 0, self.width, self.height)
        
    def paint(self, painter, option, widget = None):
        bgRect = self.boundingRect()
        painter.drawRects(bgRect)
        painter.fillRect(bgRect, QtGui.QColor('blue'))
        #QtGui.QGraphicsItem.paint( self, painter, option, widget)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        menu.addAction("graphicsItem")
        menu.exec_(event.screenPos())

class EditorLayoutWidget(EditorObjectWidget):
    def __init__(self, parent = None, kind = "none"):
        super(EditorLayoutWidget, self).__init__(parent)
        self.kind = kind

class EditorViewWidget(EditorObjectWidget):
    def __init__(self, parent = None, name = "", color = ""):
        super(EditorObjectWidget, self).__init__(parent)
        self.color = color
        self.name = name

class EditorView(QtGui.QGraphicsView):
    def __init__(self, parent = None):
        super(EditorView, self).__init__(parent)
        #self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.drag_mode_key = QtCore.Qt.Key_Control

    def keyPressEvent(self, event):
        if event.key() == self.drag_mode_key:
            self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        QtGui.QGraphicsView.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if event.key() == self.drag_mode_key:
            self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        QtGui.QGraphicsView.keyReleaseEvent(self, event)

    def mousePressedEvent(self, event):
        QtGui.QGraphicsView.mousePressedEvent(self, event)

    def dragMoveEvent(self, event):
        QtGui.QGraphicsView.dragMoveEvent(self,event)

    def dropEvent(self, event):
        QtGui.QGraphicsView.dropEvent(self,event)

class EditorScene(QtGui.QGraphicsScene):
    def __init__(self, parent = None):
        super(EditorScene, self).__init__(parent)

    def keyPressEvent(self, event):
        QtGui.QGraphicsScene.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        QtGui.QGraphicsScene.keyReleaseEvent(self, event)

    def mousePressedEvent(self, event):
        QtGui.QGraphicsView.mousePressedEvent(self, event)

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

        test = EditorObjectWidget(None)
        test2 = EditorObjectWidget(test)
        test3 = EditorObjectWidget(test)
        scene.addItem(test)


        view = EditorView(scene)
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
