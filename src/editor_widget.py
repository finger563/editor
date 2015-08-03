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

# NEED NEW DRAW STYLES
# NEED WAYS OF SPECIFYING ANCHORING
# NEED WAYS OF SPECIFYING LAYOUTS

class EditorItem(QtGui.QGraphicsWidget):
    def __init__(self,
                 parent = None,
                 image_file = "",
                 anchor = "top left",
                 width = 40,
                 height = 40,
                 layout = 'horizontal'):
        super(EditorItem, self).__init__(parent)

        self.image_file = image_file
        self.layout_style = layout
        self.item = None
        self.anchor = anchor
        self.width = width
        self.height = height

        self.loadResources()
        
    def loadResources(self):
        self.resize(self.width, self.height)
        self.initializeFlags()
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        
        child_layout = None
        if 'horizontal' in self.layout_style:
            child_layout = QtGui.QGraphicsLinearLayout()
        elif 'vertical' in self.layout_style:
            child_layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        elif 'grid' in self.layout_style:
            child_layout = QtGui.QGraphicsGridLayout()

        self.setLayout(child_layout)

        if self.image_file:
            self.item = QtGui.QGraphicsPixmapItem()
            self.item.setPixmap(QtGui.QPixmap(self.image_file))
            self.resize(QtCore.QSizeF(self.item.pixmap().size()))

        self.setCursor(QtCore.Qt.OpenHandCursor)

    def sizeHint(self, which, constraint):
        if self.item:
            return self.item.boundingRect().size()
        elif self.layout():
            return self.layout().sizeHint(which, constraint)
        else:
            return QtCore.QSizeF(50,50)
        
    def updateGraphicsItem(self):
        self.item.setPixmap(
            self.item.pixmap().scaled(
                self.layout().sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF()).width(),
                self.layout().sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF()).height()
            )
        )

    def removeChild(self, child):
        self.layout().removeItem(child)
        self.layout().activate()
        self.updateGraphicsItem()

    def addChild(self, child):
        self.layout().addItem(child)
        self.layout().invalidate()
        self.updateGraphicsItem()

    def parentEditorItem(self):
        currentParent = self.parentLayoutItem()
        if currentParent:
            currentParent = currentParent.parentLayoutItem()
        return currentParent

    def paint(self, painter, option, widget = None):
        self.item.paint(painter, option, widget)
    
    def mousePressEvent(self, event):
        if self.shape().contains(event.pos()):
            QtGui.QGraphicsWidget.mousePressEvent(self, event)
            self.dragPos = self.mapFromScene(event.scenePos())
            self.validDrag = True
        else:
            self.validDrag = False

    def mouseReleaseEvent(self, event):
        if self.validDrag:
            self.validDrag = False
            newParent = [x for x in self.scene().items(event.scenePos()) if x != self]
            currentParent = self.parentEditorItem()
            if newParent:
                if newParent[0] != currentParent:
                    if currentParent: currentParent.removeChild(self)
                    newParent[0].addChild(self)
                    self.setPos(newParent[0].mapFromScene(event.scenePos()) - self.dragPos)
            else:
                if currentParent:
                    currentParent.removeChild(self)
                    self.setParentItem(None)
                    self.setParent(self.scene())
                    self.setPos(event.scenePos() - self.dragPos)
            QtGui.QGraphicsWidget.mouseReleaseEvent(self, event)
        else:
            event.ignore()

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

        icon_file = 'icons/toolbar/terminal.png'

        r = EditorItem(image_file = icon_file, layout='vertical')
        scene.addItem(r)

        icon_file = 'icons/toolbar/build.png'

        t = EditorItem(image_file = icon_file)
        scene.addItem(t)
        r.addChild(t)

        t = EditorItem(image_file = icon_file)
        scene.addItem(t)
        r.addChild(t)

        t = EditorItem(image_file = icon_file)
        scene.addItem(t)
        r.addChild(t)


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
        newPage = EditorView(self)
        self.addTab(newPage, "test2")
       
    def onTabClose(self,index):
        self.removeTab(index)
