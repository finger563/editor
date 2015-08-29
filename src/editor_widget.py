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

from attribute_widget import AttributeEditor
import view_attributes as view_attr

# NEED RESIZE
# NEED NEW DRAW STYLES
# NEED WAYS OF SPECIFYING ANCHORING
# NEED WAYS OF SPECIFYING LAYOUTS

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

    def __init__(self,
                 parent = None,
                 kind = '',
                 anchor = 'top left',
                 text_loc = 'top',
                 text_ha = 'center',
                 text_va = 'center',
                 scope = 'view',
                 draw_style = 'icon',
                 color = 'blue',
                 image_file = "",
                 width = 100,
                 height = 100,
                 layout = 'horizontal'):
        super(EditorItem, self).__init__(parent)

        self.attributes = OrderedDict()
        self['kind'] = view_attr.Object(kind)
        self['text location'] = view_attr.Text_Location(text_loc)
        self['text horizontal alignment'] = view_attr.Text_Horizontal_Alignment(text_ha)
        self['text vertical alignment'] = view_attr.Text_Vertical_Alignment(text_va)
        self['anchor'] = view_attr.Anchor(anchor)
        self['scope'] = view_attr.Scope(scope)
        self['icon'] = view_attr.Icon(image_file)
        self['draw style'] = view_attr.Draw_Style(draw_style)
        self['color'] = view_attr.Color(color)
        self['layout style'] = view_attr.Layout_Style(layout)
        self['width'] = view_attr.Width(width)
        self['height'] = view_attr.Height(height)
        
        self._item = None
        self._pixmap = None
        self._mouseOver = False
        self._drag = False
        self._parent = None

        self.resize(self['width'].value, self['height'].value)
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        self.initializeFlags()
        self.loadResources()

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value
        
    def loadResources(self):
        
        child_layout = None
        if 'horizontal' in self['layout style'].value:
            child_layout = QtGui.QGraphicsLinearLayout()
        elif 'vertical' in self['layout style'].value:
            child_layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        elif 'grid' in self['layout style'].value:
            child_layout = QtGui.QGraphicsGridLayout()
        elif 'anchor' in self['layout style'].value:
            child_layout = QtGui.QGraphicsAnchorLayout()

        if self.layout():
            for i in range(0,self.layout().count()):
                item = self.layout().itemAt(0)
                self.layout().removeItem(item)
                child_layout.addItem(item)

        self.setLayout(child_layout)

        if self['icon'].value and self['draw style'].value == 'icon':
            self._pixmap = QtGui.QPixmap(self['icon'].value)
            self._item = QtGui.QGraphicsPixmapItem()
            self._item.setPixmap(self._pixmap)
            self.resize(QtCore.QSizeF(self._pixmap.size()))
        else:
            if self['draw style'].value == 'rect':
                self._item = QtGui.QGraphicsRectItem(0,0,self['width'].value, self['height'].value)
            elif self['draw style'].value == 'ellipse':
                self._item = QtGui.QGraphicsEllipseItem(0,0,self['width'].value, self['height'].value)
            elif self['draw style'].value == 'round rect':
                self._item = RoundRectItem(0,0,self['width'].value, self['height'].value, self['width'].value / 10.0, self['height'].value / 10.0)
            if self._item:
                self._item.setBrush(QtGui.QColor(self['color'].value))

        self.setCursor(QtCore.Qt.OpenHandCursor)

    def paint(self, painter, option, widget = None):
        super(EditorItem, self).paint(painter, option, widget)
        self._item.paint(painter, option, widget)

    def boundingRect(self):
        return self._item.boundingRect()

    def sizeHint(self, which, constraint):
        if self.layout() and self.layout().count():
            return self.layout().sizeHint(which, constraint)
        elif self._item:
            return self._item.boundingRect().size()
        else:
            return QtCore.QSizeF(self['width'].value,self['height'].value)
        
    def updateGraphicsItem(self, width = 0, height = 0):
        self.layout().invalidate()
        if not width and not height:
            if self.layout().count():
                width = self.layout().sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF()).width()
                height = self.layout().sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF()).height()
            else:
                width = self['width'].value
                height = self['height'].value
        if self['draw style'].value == 'icon':
            self._item.setPixmap( self._pixmap.scaled(width,height) )
        else:
            self._item.setRect(0,0,width,height)
        self.updateGeometry()
        self.update()
        if self._parent:
            self._parent.updateGraphicsItem()

    def removeChild(self, child):
        self.layout().removeItem(child)
        child._parent = None
        self.updateGraphicsItem()

    def addChild(self, child):
        self.layout().addItem(child)
        child._parent = self
        self.updateGraphicsItem()

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

    def updateAttributes(self,attrs):
        self.loadResources()
        self.updateGraphicsItem()
                
    def mouseDoubleClickEvent(self, event):
        QtGui.QGraphicsWidget.mouseDoubleClickEvent(self, event)
        editor = self.scene().parent().getEditor()
        editor.init_ui(self.attributes, self.attributes, lambda a : self.updateAttributes(a))
        editor.show(None)
            
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

        r = EditorItem(image_file = icon_file, layout='vertical', kind = 'Container')
        scene.addItem(r)

        icon_file = 'icons/toolbar/build.png'

        t = EditorItem(image_file = icon_file, kind = 'Component')
        scene.addItem(t)
        r.addChild(t)

        t = EditorItem(image_file = icon_file, kind = 'Client', draw_style = 'ellipse')
        scene.addItem(t)
        r.addChild(t)

        t = EditorItem(image_file = icon_file, kind = 'Server', draw_style = 'round rect')
        scene.addItem(t)
        r.addChild(t)

        self.setScene(scene)
        self.show()
        
        self.aw = AttributeEditor(self)
        self.aw.updateGeo()

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

        newPage = EditorView(self)
        self.addTab(newPage, "test1")
        newPage = EditorView(self)
        self.addTab(newPage, "test2")
       
    def onTabClose(self,index):
        self.removeTab(index)
