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
from layout import layout_create
from graphics_items import RoundRectItem, TextItem
from view_model import ViewModel

import copy

class EditorItem(QtGui.QGraphicsWidget):

    def __init__(self,
                 parent = None,
                 model= None,
                 viewModel = ViewModel()):
        super(EditorItem, self).__init__(parent)

        self._parent = None
        self._model = model
        self._view_model = copy.deepcopy(viewModel)

        self._item = None
        self._label = None

        self._mouseOver = False
        self._drag = False
        self._original_pos = None

        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        self.initializeFlags()
        self.loadResources()

    def viewModel(self):
        return self._view_model

    def model(self):
        return self._model
        
    def createLabel(self, width, height):
        pass

    def createItem(self, width, height):
        draw_style = self.viewModel()['draw style'].value
        if draw_style in ['hidden']:
            return
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
        self.createLabel(width, height)
        self.createItem(width, height)

    def paint(self, painter, option, widget = None):
        super(EditorItem, self).paint(painter, option, widget)
        if self.viewModel()['draw style'].value not in ['hidden']:
            if self._item:
                self._item.paint(painter, option, widget)
            if self._label:
                self._label.paint(painter, option, widget)

    def boundingRect(self):
        if self._item:
            return self._item.boundingRect()
        elif self.layout():
            return self.layout().boundingRect()

    def sizeHint(self, which, constraint):
        shw = 0; shh = 0
        if self.layout():
            sh = self.layout().sizeHint(which, constraint)
            shw = sh.width()
            shh = sh.height()
        return QtCore.QSizeF(
            max(shw, self.viewModel()['width'].value),
            max(shh, self.viewModel()['height'].value)
        )
        
    def updateGraphicsItem(self):
        self.prepareGeometryChange()
        self.layout().invalidate()
        sh = self.sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF())
        width = sh.width()
        height = sh.height()
        self.createLabel(width, height)
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

    def mouseDoubleClickEvent(self, event):
        QtGui.QGraphicsWidget.mouseDoubleClickEvent(self, event)
        editor = self.scene().parent().getEditor()
        editor.init_ui(self,
                       self.model().attributes,
                       lambda a : self.updateAttributes(a))
        editor.show(None)
            
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
        else:
            self.scene().removeItem(self)

