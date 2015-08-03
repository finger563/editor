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

# NEED RESIZE
# NEED NEW DRAW STYLES
# NEED WAYS OF SPECIFYING ANCHORING
# NEED WAYS OF SPECIFYING LAYOUTS

import math
def distance(p1, p2):
    p = p2 - p1
    return math.sqrt(p.x()*p.x() + p.y()*p.y())

def getClosestPoint(cp, pDict):
    minDist = -1
    closestPoint = None
    for k,p in pDict.iteritems():
        dist = distance(cp,p)
        if minDist == -1 or dist < minDist:
            minDist = dist
            closestPoint = k
    return closestPoint, minDist

class EditorItem(QtGui.QGraphicsWidget):
    def __init__(self,
                 parent = None,
                 image_file = "",
                 anchor = "top left",
                 anchorRadius = 10,
                 anchorSize = 5,
                 width = 100,
                 height = 100,
                 layout = 'horizontal'):
        super(EditorItem, self).__init__(parent)

        self._image_file = image_file
        self._layout_style = layout
        self._item = None
        self._anchor = anchor
        self._anchorRadius = anchorRadius
        self._anchorSize = anchorSize
        self._width = width
        self._height = height
        self._mouseOver = False

        self._anchoredTo = []
        self._hasAnchored = {}

        self.loadResources()
        
    def loadResources(self):
        self.resize(self._width, self._height)
        self.initializeFlags()
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        
        child_layout = None
        if 'horizontal' in self._layout_style:
            child_layout = QtGui.QGraphicsLinearLayout()
        elif 'vertical' in self._layout_style:
            child_layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        elif 'grid' in self._layout_style:
            child_layout = QtGui.QGraphicsGridLayout()
        elif 'anchor' in self._layout_style:
            child_layout = QtGui.QGraphicsAnchorLayout()

        self.setLayout(child_layout)

        if self._image_file:
            self._item = QtGui.QGraphicsPixmapItem()
            self._item.setPixmap(QtGui.QPixmap(self._image_file))
            self.resize(QtCore.QSizeF(self._item.pixmap().size()))

        self.setCursor(QtCore.Qt.OpenHandCursor)

    def boundingRect(self):
        return self._item.boundingRect()

    def sizeHint(self, which, constraint):
        if self._item:
            return self._item.boundingRect().size()
        elif self.layout():
            return self.layout().sizeHint(which, constraint)
        else:
            return QtCore.QSizeF(self._width,self._height)
        
    def updateGraphicsItem(self, width = 0, height = 0):
        if not width and not height:
            width = self.layout().sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF()).width()
            height = self.layout().sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF()).height()
        self._item.setPixmap( self._item.pixmap().scaled(width,height) )

    def removeChild(self, child):
        self.layout().removeItem(child)
        self.layout().activate()
        self.updateGraphicsItem()
        self.updateGeometry()
        self.updateAnchoredPos()

    def addChild(self, child):
        self.layout().addItem(child)
        self.layout().invalidate()
        self.updateGraphicsItem()
        self.updateGeometry()
        self.updateAnchoredPos()

    def parentEditorItem(self):
        currentParent = self.parentLayoutItem()
        if currentParent:
            currentParent = currentParent.parentLayoutItem()
        return currentParent

    def paint(self, painter, option, widget = None):
        self._item.paint(painter, option, widget)
        if self._mouseOver:
            for k,a in self.getAnchors().iteritems():
                a = self.mapFromScene( a )
                anchorRect = QtCore.QRectF(
                    a.x() - self._anchorSize,
                    a.y() - self._anchorSize,
                    2*self._anchorSize, 2*self._anchorSize)
                painter.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
                painter.drawRect(anchorRect)
    
    def updateAnchoredPos(self):
        for i,p in self._hasAnchored.iteritems():
            pos = self.getAnchors()[p]
            i.setPos(pos)
            i.updateAnchoredPos()

    def mousePressEvent(self, event):
        if self.shape().contains(event.pos()):
            self._dragPos = self.mapFromScene(event.scenePos())
            self._validDrag = True
        else:
            self._validDrag = False
        QtGui.QGraphicsWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if not self.parentEditorItem():
            #self.updateAnchoredPos()
            QtGui.QGraphicsWidget.mouseMoveEvent(self,event)


    # if item will have a parent, place it in the parent's layout
    # else see if it will be anchored
    def mouseReleaseEvent(self, event):
        if self._validDrag:
            self._validDrag = False
            newParent = [x for x in self.scene().items(event.scenePos()) if x != self]
            currentParent = self.parentEditorItem()
            if newParent:
                if newParent[0] != currentParent:
                    if currentParent: currentParent.removeChild(self)
                    if self._anchoredTo:
                        self._anchoredTo[0].unAnchor(self)
                    self._anchoredTo = []
                    newParent[0].addChild(self)
                    self.setPos(newParent[0].mapFromScene(event.scenePos()) - self._dragPos)
            else:
                if currentParent:
                    if self._anchoredTo:
                        self._anchoredTo[0].unAnchor(self)
                    self._anchoredTo = []
                    currentParent.removeChild(self)
                    self.setParentItem(None)
                    self.setParent(self.scene())
                item, pointName = self.getClosestAnchor()
                dist = distance(self.getAnchor(), item.getAnchors()[pointName])
                if dist <= self._anchorRadius:
                    self._anchoredTo = [item, pointName]
                    item.anchor(self, pointName)
                    self.setPos(item.getAnchors()[pointName])
                else:
                    if self._anchoredTo:
                        self._anchoredTo[0].unAnchor(self)
                    self._anchoredTo = []
                    self.setPos(event.scenePos() - self._dragPos)
                QtGui.QGraphicsWidget.mouseReleaseEvent(self, event)
        else:
            event.ignore()
            
    def hoverEnterEvent(self, event):
        self._mouseOver = True

    def hoverLeaveEvent(self, event):
        self._mouseOver = False

    def initializeFlags(self):
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges)

    def anchor(self, item, pName):
        if item not in self._hasAnchored:
            self._hasAnchored[item] = pName

    def unAnchor(self, item):
        self._hasAnchored.pop(item, None)
    
    def getAnchor(self):
        return self.getAnchors()[self._anchor]
            
    def getClosestAnchor(self):
        myAnchorPos = self.getAnchor()
        otherItems = [x for x in self.scene().items() if x != self]
        minDist = -1
        cp = None
        for i in otherItems:
            closestPoint, dist = getClosestPoint(myAnchorPos, i.getAnchors())
            if minDist == -1 or dist < minDist:
                minDist = dist
                cp = [i, closestPoint]
        return cp

    def getAnchors(self):
        a = self.boundingRect()
        anchorList = {
            "bottom left": self.mapToScene(a.bottomLeft()),
            "bottom right": self.mapToScene(a.bottomRight()),
            "top left": self.mapToScene(a.topLeft()),
            "top right": self.mapToScene(a.topRight()),
            "center": self.mapToScene(a.center()),
            "center left": self.mapToScene((a.topLeft() + a.bottomLeft()) / 2.0),
            "center right": self.mapToScene((a.topRight() + a.bottomRight()) / 2.0),
            "top center": self.mapToScene((a.topLeft() + a.topRight()) / 2.0),
            "bottom center": self.mapToScene((a.bottomLeft() + a.bottomRight()) / 2.0)
        }
        return anchorList

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        menu.addAction("EditorItem")
        menu.addAction("SetLayout")
        menu.addAction("SetAnchor")
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
