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
from action import Action

class ModelItem(QtGui.QGraphicsWidget):

    def __init__(self,
                 parent = None,
                 viewModel = ViewModel()):
        super(ModelItem, self).__init__(parent)

        self._view_model = viewModel
        self._item = None
        self._label = None
        self._pixmap = None
        self._mouseOver = False
        self._drag = False
        self._parent = None

        #self.resize(self['width'].value, self['height'].value)
        #self.setCursor(QtCore.Qt.OpenHandCursor)
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
        
    def createItem(self, width, height):
        self._label = TextItem(self.viewModel()['kind'].value)
        self._label.setAlignment(
            self.viewModel()['text horizontal alignment'].value,
            self.viewModel()['text vertical alignment'].value
        )

        if self['icon'].value and self['draw style'].value == 'icon':
            self._item = QtGui.QGraphicsPixmapItem()
            self._item.setPixmap( QtGui.QPixmap(self['icon'].value).scaled(width,height) )
        else:
            if self['draw style'].value == 'rect':
                self._item = QtGui.QGraphicsRectItem(0,0,width,height)
            elif self['draw style'].value == 'ellipse':
                self._item = QtGui.QGraphicsEllipseItem(0,0,width,height)
            elif self['draw style'].value == 'round rect':
                self._item = RoundRectItem(0,0,width,height)
            if self._item:
                self._item.setBrush(QtGui.QColor(self['color'].value))

    def loadResources(self):
        new_layout = layout_create(self['layout style'].value)
        if type(self.layout()) != type(new_layout):
            new_layout.fromLayout(self.layout())
            self.setLayout(new_layout)

        sh = self.sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF())
        width = sh.width()
        height = sh.height()
        self.createItem(width, height)

    def paint(self, painter, option, widget = None):
        super(ModelItem, self).paint(painter, option, widget)
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
            max(shw, self['width'].value),
            max(shh, self['height'].value)
        )
        
    def updateGraphicsItem(self):
        self.prepareGeometryChange()
        self.layout().invalidate()
        sh = self.sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF())
        width = sh.width()
        height = sh.height()
        self.createItem(width,height)
        self.updateGeometry()
        self.update()
        if self._parent:
            self._parent.updateGraphicsItem()

    def removeChild(self, child):
        self.viewModel().removeChild(child.viewModel())
        self.layout().removeItem(child)
        child._parent = None
        self.updateGraphicsItem()

    def updateChild(self, child):
        self.layout().updateItem(child)
        self.updateGraphicsItem()

    def addChild(self, child):
        self.layout().addItem(child)
        self.viewModel().addChild(child.viewModel())
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
            '''
            else:
                self.setPos(self._original_pos)
            '''
        self.updateGraphicsItem()

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

        delSelf = Action('', 'Delete', self)
        delSelf.triggered.connect(self.delete)
        menu.addAction(delSelf)
        
        addSelf = Action('', 'Add new Item', self)
        addSelf.triggered.connect(self.addNewItem)
        menu.addAction(addSelf)
        
        menu.exec_(event.screenPos())

    def delete(self, event):
        for i in range(self.layout().count()):
            self.layout().itemAt(0).delete(None)
        if self._parent:
            self._parent.removeChild(self)
        else:
            self.scene().removeItem(self)

    def addNewItem(self, event):
        self.addChild(ModelItem(self, viewModel = ViewModel()))
