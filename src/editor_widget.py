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

# IMPLEMENT RESIZING OF OBJECTS
# IMPLEMENT SERIALIZATION AND DESERIALIZATION
# IMPLEMENT ANCHORING
# IMPLEMNET DRAW STYLING

class EditorItem(QtGui.QGraphicsWidget):
    def __init__(self, pixmap, parent = None, layout = 'horizontal'):
        super(EditorItem, self).__init__(parent)

        self.initializeFlags()
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)

        self.item = QtGui.QGraphicsPixmapItem()
        self.item.setPixmap(pixmap)
        self.resize(QtCore.QSizeF(pixmap.size()))
        self.updateGeometry()
        
        child_layout = None
        if 'horizontal' in layout:
            child_layout = QtGui.QGraphicsLinearLayout()
        elif 'vertical' in layout:
            child_layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        elif 'grid' in layout:
            child_layout = QtGui.QGraphicsGridLayout()
        self.setLayout(child_layout)

    def addChild(self, child):
        self.item.prepareGeometryChange()
        child.setParentLayoutItem(self)
        self.layout().addItem(child)
        self.updateGeometry()

    def paint(self, painter, option, widget = None):
        self.item.paint(painter, option, widget)

    # FUNCTIONS I NEED FOR EDITOR
    def initializeFlags(self):
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges)
    
    def getAnchors(self):
        a = self.geometry()
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

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        menu.addAction("EditorItem")
        menu.exec_(event.screenPos())

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
    def __init__(self, parent):
        super(EditorView,self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.drag_mode_key = QtCore.Qt.Key_Control
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

        scene = EditorScene(self)

        pixmap = QtGui.QPixmap('icons/toolbar/build.png')
        r = EditorItem(pixmap)
        t = EditorItem(pixmap.scaled(pixmap.size() / 2))
        r.addChild(t)
        t = EditorItem(pixmap.scaled(pixmap.size() / 2))
        r.addChild(t)
        t = EditorItem(pixmap.scaled(pixmap.size() / 2))
        r.addChild(t)
        scene.addItem(r)

        self.setScene(scene)
        self.show()

    def keyPressEvent(self, event):
        if event.key() == self.drag_mode_key:
            self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        QtGui.QGraphicsView.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if event.key() == self.drag_mode_key:
            self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        QtGui.QGraphicsView.keyReleaseEvent(self, event)


class TabbedEditor(QtGui.QTabWidget):
    def __init__(self, parent):
        super(TabbedEditor, self).__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setUsesScrollButtons(True)

        self.tabCloseRequested.connect(self.onTabClose)

        newPage = EditorView(self)
        self.addTab(newPage, "test1")
        #newPage = EditorView(self)
        #self.addTab(newPage, "test2")
        
    def onTabClose(self,index):
        self.removeTab(index)
