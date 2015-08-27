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

class RoundRectItem(QtGui.QGraphicsRectItem):
    def __init__(self, x, y, w, h, xr, yr, parent = None):
        super(RoundRectItem, self).__init__(x,y,w,h,parent)
        self.xr = xr
        self.yr = yr

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen());
        painter.setBrush(self.brush());
        painter.drawRoundedRect(self.rect(), self.xr, self.yr)

class EditorItem(QtGui.QGraphicsWidget):

    layout_styles = ['horizontal','vertical','grid','anchor']
    draw_styles = ['icon', 'ellipse', 'rect', 'round rect']

    def __init__(self,
                 parent = None,
                 kind = '',
                 draw_style = 'icon',
                 image_file = "",
                 width = 100,
                 height = 100,
                 layout = 'horizontal'):
        super(EditorItem, self).__init__(parent)

        self._kind = kind
        self._image_file = image_file
        self._draw_style = draw_style
        self._layout_style = layout
        self._item = None
        self._pixmap = None
        self._width = width
        self._height = height
        self._mouseOver = False
        self._drag = False

        self.resize(self._width, self._height)
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        self.initializeFlags()
        self.loadResources()
        
    def loadResources(self):
        
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

        if self._image_file and self._draw_style == 'icon':
            self._pixmap = QtGui.QPixmap(self._image_file)
            self._item = QtGui.QGraphicsPixmapItem()
            self._item.setPixmap(self._pixmap)
            self.resize(QtCore.QSizeF(self._pixmap.size()))
        elif self._draw_style == 'rect':
            self._item = QtGui.QGraphicsRectItem(0,0,self._width, self._height)
        elif self._draw_style == 'ellipse':
            self._item = QtGui.QGraphicsEllipseItem(0,0,self._width, self._height)
        elif self._draw_style == 'round rect':
            self._item = RoundRectItem(0,0,self._width, self._height, self._width / 10.0, self._height / 10.0)

        self.setCursor(QtCore.Qt.OpenHandCursor)

    def get_static(self):
        static =  {
            'name' : self._kind,
            'type' : self._draw_style,
        }
        if self._draw_style in ['icon']:
            static['value'] = self._image_file
            static['scale'] = (50,50)
        return static

    def get_attr(self):
        attrs = [
            {
                'name' : 'Draw Style',
                'type' : 'list',
                'value' : self._draw_style,
                'options' : self.draw_styles,
                'tooltip' : ''
            },
            {
                'name' : 'Layout',
                'type' : 'list',
                'value' : self._layout_style,
                'options' : self.layout_styles,
                'tooltip' : ''
            },
        ]
        return attrs

    def paint(self, painter, option, widget = None):
        super(EditorItem, self).paint(painter, option, widget)
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
        if self._draw_style == 'icon':
            self._item.setPixmap( self._pixmap.scaled(width,height) )
        else:
            self._item.setRect(0,0,width,height)

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
        self._original_pos = self.pos()

    def mouseMoveEvent(self, event):
        QtGui.QGraphicsWidget.mouseMoveEvent(self,event)
        self._drag = True

    def mouseReleaseEvent(self, event):
        QtGui.QGraphicsWidget.mouseReleaseEvent(self, event)
        if self._drag:
            self._drag = False
            newParent = [x for x in self.scene().items(event.scenePos()) if x != self]
            currentParent = self.parentEditorItem()
            if newParent:
                if currentParent:
                    if newParent[0] != currentParent:
                        currentParent.removeChild(self)
                        newParent[0].addChild(self)
                    else:
                        self.setPos(self._original_pos)
                else:
                    newParent[0].addChild(self)
            elif currentParent:
                currentParent.removeChild(self)
                self.setParentItem(None)
                self.setParent(self.scene())
                self.setPos(event.scenePos() - self._drag_pos)

    def mouseDoubleClickEvent(self, event):
        QtGui.QGraphicsWidget.mouseDoubleClickEvent(self, event)
        self.scene().parent().showAW(self.get_static(), self.get_attr())
            
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

        r = EditorItem(image_file = icon_file, layout='vertical', kind = 'base')
        scene.addItem(r)

        icon_file = 'icons/toolbar/build.png'

        t = EditorItem(image_file = icon_file, kind = 'test 1')
        scene.addItem(t)
        r.addChild(t)

        t = EditorItem(image_file = icon_file, kind = 'test 2', draw_style = 'ellipse')
        scene.addItem(t)
        r.addChild(t)

        t = EditorItem(image_file = icon_file, kind = 'test 3', draw_style = 'round rect')
        scene.addItem(t)
        r.addChild(t)

        self.setScene(scene)
        self.show()
        
        self.aw = AttributeEditor(self)
        self.aw.updateGeo()

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

    def showAW(self, static = None, attr = None, save_func = None):
        self.aw._displayed = True
        self.aw.init_ui(static, attr, save_func)
        self.aw.animate(None,self.aw._displayed)

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
