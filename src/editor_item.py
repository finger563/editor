'''
Model Item

This class defines the widget
which allows for viewing and editing
of models.
'''

__author__ = 'William Emfinger'
__copyright__ = 'Copyright 2016, ROSMOD'
__credits__ = ['William Emfinger', 'Pranav Srinivas Kumar']
__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'William Emfinger'
__email__ = 'emfinger@isis.vanderbilt.edu'
__status__ = 'Production'

from PyQt4 import QtCore
from PyQt4 import QtGui

import view_attributes as view_attr
from layout import layout_create, valid_layouts
from graphics_items import RoundRectItem, TextItem

class EditorItem(QtGui.QGraphicsWidget):

    def __init__(self,
                 parent = None,
                 model = None):
        super(EditorItem, self).__init__(parent)
        # scene parent of this item, e.g. the scene or an enclosing object
        self._parent = None

        # perhaps just point this to the ItemModel()?
        
        # Should not store a pointer to the model here,
        # it is bad practice.  Should figure out which 
        # index into the model this points to (since this
        # is just a view) and then use that index to fetch 
        # the updated model any time an action is required
        # e.g. edit, add, delete
        self._model = model

        # graphics item which represents
        self._item = None
        # text label of this item
        self._label = TextItem( '' , parent = self)

        self.loadResources()
        #self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        self.initializeFlags()
        self.updateGraphicsItem()

    def model(self):
        return self._model
        
    def __getitem__(self, key):
        return self.model()[key]

    def __setitem__(self, key, value):
        self.model()[key] = value

    def viewModel(self):
        return self.scene().viewModel()

    def updateLabel(self, width, height):
        if self.isHidden():
            self._label.setPlainText('')
        if self.model():
            if 'name' in self.model().attributes:
                name = self['name']
            else:
                name = self['kind']
            self._label.setPlainText(name)
            self._label.setAlignment(
                self.viewModel()['text horizontal alignment'],
                self.viewModel()['text vertical alignment']
            )
            self._label.setPos(self.viewModel()['text location'], self.pos(), width, height)

    def createItem(self, width, height):
        if self.isHidden():
            self._item = None
        draw_style = self.viewModel()['draw style']
        if self.viewModel()['icon'] and draw_style == 'icon':
            self._item = QtGui.QGraphicsPixmapItem()
            self._item.setPixmap( QtGui.QPixmap(self.viewModel()['icon']).scaled(width,height) )
        else:
            if draw_style == 'rect':
                self._item = QtGui.QGraphicsRectItem(0,0,width,height)
            elif draw_style == 'ellipse':
                self._item = QtGui.QGraphicsEllipseItem(0,0,width,height)
            elif draw_style == 'round rect':
                self._item = RoundRectItem(0,0,width,height)
            if self._item:
                self._item.setBrush(QtGui.QColor(self.viewModel()['color']))

    def loadResources(self):
        new_layout = layout_create(self.viewModel()['layout style'])
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
            max(shw, self.viewModel()['width']),
            max(shh, self.viewModel()['height'])
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
        # Should this just point down to the underlying model's 
        # removeRows() method and then let the updating take effect?
        self.layout().removeItem(child)
        child._parent = None
        self.updateGraphicsItem()

    def updateChild(self, child):
        self.layout().updateItem(child)
        self.updateGraphicsItem()

    def addChild(self, child):
        # Should this just point down to the underlying model's 
        # insertRows() method and then let the updating take effect?
        self.layout().addItem(child)
        child._parent = self
        self.updateGraphicsItem()

    def mousePressEvent(self, event):
        QtGui.QGraphicsWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        QtGui.QGraphicsWidget.mouseMoveEvent(self,event)

    def mouseReleaseEvent(self, event):
        QtGui.QGraphicsWidget.mouseReleaseEvent(self, event)

    def isMovable(self):
        return bool(self.flags() & QtGui.QGraphicsItem.ItemIsMovable)

    def mouseDoubleClickEvent(self, event):
        QtGui.QGraphicsWidget.mouseDoubleClickEvent(self, event)
        # TODO: need to add the index here; call setSelection() with proper indices
        editor = self.scene().parent().getEditor()
        editor.init_ui(self)
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
            'bottom left': a.bottomLeft(),
            'bottom right': a.bottomRight(),
            'top left': a.topLeft(),
            'top right': a.topRight(),
            'center left': (a.topLeft() + a.bottomLeft()) / 2.0,
            'center right': (a.topRight() + a.bottomRight()) / 2.0,
            'top center': (a.topLeft() + a.topRight()) / 2.0,
            'bottom center': (a.bottomLeft() + a.bottomRight()) / 2.0
        }
        return anchorList

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()

        delSelf = Action('', 'Delete', self)
        delSelf.triggered.connect(self.delete)
        menu.addAction(delSelf)

        for a in self.model().children._allowed:
            addAction = Action('', 'Add new {}'.format(a.__name__), self)
            addAction.triggered.connect(self.addNewItem(a))
            menu.addAction(addAction)
        
        menu.exec_(event.screenPos())

    def addNewItem(self, _type):
        def genericItem(e):
            print _type.__name__
            child = _type()
            self.addChild( EditorItem( parent = self, model = child ) )
        return genericItem

    def delete(self, event):
        # What should this method do?
        # Should this just point down to the underlying model's 
        # removeRows() method and then let the updating take effect?
        for i in range(self.layout().count()):
            self.layout().itemAt(0).delete(None)
        if self._parent:
            self._parent.removeChild(self)
        if self.scene():
            self.scene().removeItem(self)
        self._parent = None

