"""
Model Item

This class defines the widget
which allows for viewing and editing
of models.

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: August 2015
"""

from PyQt4 import QtCore
from PyQt4 import QtGui

import view_attributes as view_attr
from layout import layout_create, valid_layouts
from graphics_items import RoundRectItem, TextItem
from view_model import ViewModel

class EditorItem(QtGui.QGraphicsWidget):

    def __init__(self,
                 parent = None,
                 model = None,
                 view_model = ViewModel()):
        self._parent = None
        self._model = model
        self._view_model = view_model

        self._mouseOver = False
        self._drag = False
        self._original_pos = None

        self._label = None
        self._item = None
        
        super(EditorItem, self).__init__(parent)

        self._label = TextItem( '' , parent = self)

        self.loadResources()
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        self.initializeFlags()
        self.updateGraphicsItem()

    def viewModel(self):
        return self._view_model

    def model(self):
        return self._model
        
    def __getitem__(self, key):
        return self.model()[key]

    def __setitem__(self, key, value):
        self.model()[key] = value

    def updateLabel(self, width, height):
        if self.isHidden():
            self._label.setPlainText('')
        if self.model():
            if 'name' in self.model().attributes:
                name = self.model()['name'].value
            else:
                name = self.model()['kind'].value
            self._label.setPlainText(name)
            self._label.setAlignment(
                self.viewModel()['text horizontal alignment'].value,
                self.viewModel()['text vertical alignment'].value
            )
            self._label.setPos(self.viewModel()['text location'].value, self.pos(), width, height)

    def createItem(self, width, height):
        if self.isHidden():
            self._item = None
        draw_style = self.viewModel()['draw style'].value
        if self.viewModel()['icon'].value and draw_style == 'icon':
            self._item = QtGui.QGraphicsPixmapItem()
            self._item.setPixmap( QtGui.QPixmap(self.viewModel()['icon'].value).scaled(width,height) )
        else:
            if draw_style == 'rect':
                self._item = QtGui.QGraphicsRectItem(0,0,width,height)
            elif draw_style == 'ellipse':
                self._item = QtGui.QGraphicsEllipseItem(0,0,width,height)
            elif draw_style == 'round rect':
                self._item = RoundRectItem(0,0,width,height)
            if self._item:
                self._item.setBrush(QtGui.QColor(self.viewModel()['color'].value))

    def loadResources(self):
        new_layout = layout_create(self.viewModel()['layout style'].value)
        if type(self.layout()) != type(new_layout):
            new_layout.fromLayout(self.layout())
            self.setLayout(new_layout)

        sh = self.sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF())
        width = sh.width()
        height = sh.height()
        self.updateLabel(width, height)
        self.createItem(width, height)

    def paint(self, painter, option, widget = None):
        super(EditorItem, self).paint(painter, option, widget)
        if not self.isHidden():
            if self._item:
                self._item.paint(painter, option, widget)

    def boundingRect(self):
        minx =0; miny=0; maxx=0;maxy=0
        if self._item:
            brect = self._item.boundingRect()
            minx = min(brect.x(),minx)
            miny = min(brect.y(),miny)
            maxx = max(maxx, brect.x() + brect.width())
            maxy = max(maxy, brect.y() + brect.height())
        if self._label:
            brect = self._label.boundingRect()
            minx = min(brect.x(),minx)
            miny = min(brect.y(),miny)
            maxx = max(maxx, brect.x() + brect.width())
            maxy = max(maxy, brect.y() + brect.height())
        retRect = QtCore.QRectF(minx,miny, maxx-minx, maxy-miny)
        return retRect

    def sizeHint(self, which, constraint):
        shw = 0; shh = 0
        if type(self.layout()) in valid_layouts:
            sh = self.layout().sizeHint(which, constraint)
            shw = sh.width()
            shh = sh.height()
        shw = max( shw, self.boundingRect().width())
        shh = max( shh, self.boundingRect().height())
        return QtCore.QSizeF(
            max(shw, self.viewModel()['width'].value),
            max(shh, self.viewModel()['height'].value)
        )
        
    def updateGraphicsItem(self):
        self.layout().activate()
        self.prepareGeometryChange()
        sh = self.sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF())
        width = sh.width()
        height = sh.height()
        self.updateLabel(width, height)
        self.createItem(width, height)
        self.updateGeometry()
        self.update()
        if self._parent:
            self._parent.updateGraphicsItem()

    def removeChild(self, child):
        self.layout().removeItem(child)
        child._parent = None
        self.updateGraphicsItem()

    def updateChild(self, child):
        self.layout().updateItem(child)
        self.updateGraphicsItem()

    def addChild(self, child):
        self.layout().addItem(child)
        child._parent = self
        self.updateGraphicsItem()

    def mousePressEvent(self, event):
        if not self.isHidden():
            QtGui.QGraphicsWidget.mousePressEvent(self, event)
            self._drag_pos = self.mapFromScene(event.scenePos())
            self._original_pos = self.pos()

    def mouseMoveEvent(self, event):
        QtGui.QGraphicsWidget.mouseMoveEvent(self,event)
        if self.isMovable():
            self._drag = True

    def mouseReleaseEvent(self, event):
        if self.isHidden():
            if self._parent: self._parent.mouseReleaseEvent(event)
        else:
            QtGui.QGraphicsWidget.mouseReleaseEvent(self, event)
            if self._drag:
                self._drag = False
                newParent = [x for x in self.scene().items(event.scenePos()) if x != self and issubclass(type(x),EditorItem)]
                currentParent = self._parent
                if newParent:
                    p = newParent[0]
                    if p == currentParent:
                        p.updateChild(self)
                    else:
                        if currentParent:
                            currentParent.removeChild(self)
                        p.addChild(self)
                elif currentParent:
                    currentParent.removeChild(self)
                    self.setParentItem(None)
                    self.setParent(self.scene())
                    self.setPos(event.scenePos() - self._drag_pos)
            self.updateGraphicsItem()

    def isHidden(self):
        return self.viewModel()['draw style'].value in ['hidden']

    def isMovable(self):
        return bool(self.flags() & QtGui.QGraphicsItem.ItemIsMovable)

    def mouseDoubleClickEvent(self, event):
        if self.isHidden():
            if self._parent: self._parent.mouseDoubleClickEvent(event)
        else:
            QtGui.QGraphicsWidget.mouseDoubleClickEvent(self, event)
            if self.model():
                editor = self.scene().parent().getEditor()
                editor.init_ui(self,
                               self.model().attributes,
                               lambda a : self.updateAttributes(a))
                editor.show()
                editor.raise_()

    def updateAttributes(self,attrs):
        self.loadResources()
        self.updateGraphicsItem()
                
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

    def delete(self, event):
        for i in range(self.layout().count()):
            self.layout().itemAt(0).delete(None)
        if self._parent:
            self._parent.removeChild(self)
        if self.scene():
            self.scene().removeItem(self)
        self._parent = None

