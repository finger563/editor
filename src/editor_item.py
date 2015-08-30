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

import view_attributes as view_attr
from layout import layout_create, layout_add, layout_remove, layout_move
from anchors import convertAnchorToQt

# NEED RESIZE
# NEED NEW DRAW STYLES
# NEED WAYS OF SPECIFYING ANCHORING
# NEED WAYS OF SPECIFYING LAYOUTS

class RoundRectItem(QtGui.QGraphicsRectItem):
    def __init__(self, x, y, w, h, xr = 0.1, yr = 0.1, parent = None):
        super(RoundRectItem, self).__init__(x,y,w,h,parent)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.xr = xr
        self.yr = yr

    # gotten from qt_graphicsItem_highlightSelected, qgraphicsitem.cpp : 7574
    def highlightSelected(item, painter, option):
        murect = painter.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
        if not murect.width() or not murect.height():
            return

        mbrect = painter.transform().mapRect(item.boundingRect())
        if min(mbrect.width(), mbrect.height()) < 1.0:
            return

        itemPenWidth = item.pen().widthF()
        
        pad = itemPenWidth / 2

        penWidth = 0 # cosmetic pen

        fgcolor = option.palette.windowText().color()
        bgcolor = QtGui.QColor(
            0 if fgcolor.red()   > 127 else 255,
            0 if fgcolor.green() > 127 else 255,
            0 if fgcolor.blue()  > 127 else 255)

        painter.setPen(QtGui.QPen(bgcolor, penWidth, QtCore.Qt.SolidLine));
        painter.setBrush(QtCore.Qt.NoBrush);
        painter.drawRect(item.boundingRect().adjusted(pad, pad, -pad, -pad));

        painter.setPen(QtGui.QPen(option.palette.windowText(), 0, QtCore.Qt.DashLine));
        painter.setBrush(QtCore.Qt.NoBrush);
        painter.drawRect(item.boundingRect().adjusted(pad, pad, -pad, -pad));

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen());
        painter.setBrush(self.brush());
        minR = min(self.rect().width()*self.xr, self.rect().height()*self.yr)
        painter.drawRoundedRect(self.rect(), minR, minR)
        if option.state & QtGui.QStyle.State_Selected:
            self.highlightSelected(painter, option)

class EditorItem(QtGui.QGraphicsWidget):

    def __init__(self,
                 parent = None,
                 viewModel = None):
        super(EditorItem, self).__init__(parent)

        self._view_model = viewModel
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
        return self._view_model.attributes[key]

    def __setitem__(self, key, value):
        self._view_model.attributes[key] = value

    def viewModel(self):
        return self._view_model
        
    def loadResources(self):
        old_layout = self.layout()
        new_layout = layout_create(self['layout style'].value)

        if old_layout:
            layout_move(old_layout, new_layout, self['layout style'].value)

        self.setLayout(new_layout)

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
                self._item = RoundRectItem(0,0,self['width'].value, self['height'].value)
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
            sh = self.layout().sizeHint(which, constraint)
            return sh
        elif self._item:
            return self._item.boundingRect().size()
        else:
            return QtCore.QSizeF(self['width'].value,self['height'].value)
        
    def updateGraphicsItem(self):
        self.layout().invalidate()
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
        layout_remove(self.layout(), self['layout style'].value, child)
        self.viewModel().removeChild(child.viewModel())
        child._parent = None
        self.updateGraphicsItem()

    def addChild(self, child):
        layout_add(self.layout(), self['layout style'].value, child)
        self.viewModel().addChild(child.viewModel())
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
                p = newParent[0]
                style = p.viewModel()['layout style'].value
                anchorUpdated = False
                if style in ['anchor']:
                    d, a1, a2, ci = p.layout().getClosestAnchors(self)
                    if d > 0 and d < 10:
                        anchorUpdated = True
                        layout_add(p.layout(),
                                   style,
                                   self,
                                   anchor_item = ci,
                                   item_ap = convertAnchorToQt(a2),
                                   anchor_ap = convertAnchorToQt(a1))
                if currentParent:
                    if p != currentParent:
                        currentParent.removeChild(self)
                        p.addChild(self)
                    else:
                        if not anchorUpdated:
                            self.setPos(self._original_pos)
                else:
                    p.addChild(self)
                self.updateGraphicsItem()
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
        editor.init_ui(self.viewModel().attributes,
                       self.viewModel().attributes,
                       lambda a : self.updateAttributes(a))
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

    def getAnchors(self):
        a = self.boundingRect()
        anchorList = {
            "bottom left": a.bottomLeft(),
            "bottom right": a.bottomRight(),
            "top left": a.topLeft(),
            "top right": a.topRight(),
            "center left": (a.topLeft() + a.bottomLeft()) / 2.0,
            "center right": (a.topRight() + a.bottomRight()) / 2.0,
            "top center": (a.topLeft() + a.topRight()) / 2.0,
            "bottom center": (a.bottomLeft() + a.bottomRight()) / 2.0
        }
        return anchorList

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        menu.addAction("EditorItem")
        menu.addAction("SetLayout")
        menu.exec_(event.screenPos())
