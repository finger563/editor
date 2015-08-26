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

from attribute_widget import AttributeEditor

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
                 width = 100,
                 height = 100,
                 layout = 'horizontal'):
        super(EditorItem, self).__init__(parent)

        self._image_file = image_file
        self._layout_style = layout
        self._item = None
        self._pixmap = None
        self._width = width
        self._height = height
        self._mouseOver = False

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
            self._pixmap = QtGui.QPixmap(self._image_file)
            self._item = QtGui.QGraphicsPixmapItem()
            self._item.setPixmap(self._pixmap)
            self.resize(QtCore.QSizeF(self._pixmap.size()))

        self.setCursor(QtCore.Qt.OpenHandCursor)

    def paint(self, painter, option, widget = None):
        self._item.paint(painter, option, widget)

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
        self._item.setPixmap( self._pixmap.scaled(width,height) )

    def removeChild(self, child):
        self.layout().removeItem(child)
        self.layout().invalidate()
        self.updateGraphicsItem()
        self.updateGeometry()

    def addChild(self, child):
        self.layout().addItem(child)
        self.layout().invalidate()
        self.updateGraphicsItem()
        self.updateGeometry()

    def parentEditorItem(self):
        currentParent = self.parentLayoutItem()
        if currentParent:
            currentParent = currentParent.parentLayoutItem()
        return currentParent
    
    def mousePressEvent(self, event):
        QtGui.QGraphicsWidget.mousePressEvent(self, event)
        self._drag_pos = self.mapFromScene(event.scenePos())

    def mouseMoveEvent(self, event):
        QtGui.QGraphicsWidget.mouseMoveEvent(self,event)

    def mouseReleaseEvent(self, event):
        newParent = [x for x in self.scene().items(event.scenePos()) if x != self]
        currentParent = self.parentEditorItem()
        if currentParent: currentParent.removeChild(self)
        if newParent:
            newParent[0].addChild(self)
        else:
            self.setParentItem(None)
            self.setParent(self.scene())
            self.setPos(event.scenePos() - self._drag_pos)
        QtGui.QGraphicsWidget.mouseReleaseEvent(self, event)
            
    def hoverEnterEvent(self, event):
        QtGui.QGraphicsWidget.hoverEnterEvent(self, event)

    def hoverLeaveEvent(self, event):
        QtGui.QGraphicsWidget.hoverLeaveEvent(self, event)

    def initializeFlags(self):
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        menu.addAction("EditorItem")
        menu.addAction("SetLayout")
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

    drag_mode_key = QtCore.Qt.Key_Control
    scroll_mode_key = QtCore.Qt.Key_Control

    attr_width = 100

    def __init__(self, parent):
        super(EditorView,self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self._command_key_pressed = False
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
        
        self._displayed = False
        self.aw = AttributeEditor(self)
        self.setAWGeo(self._displayed)

    def mousePressEvent(self, event):
        QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        QtGui.QGraphicsView.mouseReleaseEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        QtGui.QGraphicsView.mouseDoubleClickEvent(self, event)
        self.toggle()
        
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
        self.setAWGeo(self._displayed)

    def getAWGeo(self, displayed):
        _myw = self.geometry().width()
        _w = self.aw.geometry().width()
        _h = self.geometry().height()
        TL_y = 0
        BR_y = _h
        TL_x = _myw
        BR_x = _myw + _w
        if displayed:
            TL_x -= _w
            BR_x -= _w
        if TL_x < 0:
            BR_x += -TL_x
            TL_x += -TL_x
        return TL_x, TL_y, BR_x, BR_y

    def setAWGeo(self, displayed):
        self.aw.setGeometry(*self.getAWGeo(displayed))

    def toggle(self):
        self._displayed = not self._displayed
        if self._displayed:
            self.aw.init_ui()

        self.hideAnimation = QtCore.QPropertyAnimation(self.aw, "geometry")
        self.hideAnimation.setDuration(300)

        self.aw.startGeometry = QtCore.QRectF(self.aw.geometry())
        self.aw.endGeometry = QtCore.QRectF(*self.getAWGeo(self._displayed))

        self.hideAnimation.setStartValue(self.aw.startGeometry)
        self.hideAnimation.setEndValue(self.aw.endGeometry)
        self.hideAnimation.start()
        
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
