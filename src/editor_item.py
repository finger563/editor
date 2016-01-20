'''
This class defines the graphical widget which allows for viewing
and editing of models on a scrollable, zoomable canvas, with custom
drawing styles available to each model.
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

from attribute_editors import\
    FileEditor,\
    CodeEditor,\
    ReferenceEditor

# TODO: Mouse click isn't working properly; the drawn area (of the
#       rect/text) is not necessarily the clickable area

# TODO: Make ItemDelegate work for dictionary editor created in
#       attribute editor

# TODO: there is a dependency between the text size and the item size
#       of EditorItem because it's all max-based, when the text
#       shrinks the item should shrink too but can't because the rect
#       is preventing it


class EditorItemWidget(QtGui.QWidget):
    '''Wrapper class for :class:`EditorItem` so that an
    :class:`EditorItem` can be configured and automatically used with
    :class:`EditorItemDelegate`
    '''
    def __init__(self, parent=None, ei=None):
        super(EditorItemWidget, self).__init__(parent)
        self.item = ei


class EditorItemDelegate(QtGui.QItemDelegate):
    '''Handles the mapping between :class:`EditorItem`'s data and the
    model's data.  Ensures that whenever the item's data are edited,
    the model's data get updated and vise-versa.  This eables ensuring
    that the graphics object's text label changes whenever its
    associated model changes, for instance.
    '''

    def eventFilter(self, editor, event):
        '''Required to allow tabbing in a
        :class:`attribute_editors.CodeEditor`.
        '''
        if type(editor) == CodeEditor and type(event) is not QtGui.QFocusEvent:
            return False
        else:
            return super(EditorItemDelegate, self).eventFilter(editor, event)

    def setEditorData(self, editor, index):
        if type(editor) == EditorItemWidget:
            text = index.data().toString()
            # SET THE EDITOR ITEM TEXT HERE
            editor.item._label.setPlainText(text)
            editor.item.updateGraphicsItem()
            return
        elif type(editor) == FileEditor:
            text = str(index.data().toString())
            editor.set_file_name(text)
        elif type(editor) == CodeEditor:
            text = str(index.data().toString())
            editor.setPlainText(text)
            return
        elif type(editor) == ReferenceEditor:
            editor.setCurrentModelIndex(index)
            return
        return super(EditorItemDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if (type(editor) == EditorItemWidget or 
            type(editor) == QtGui.QWidget):
            return
        elif type(editor) == FileEditor:
            text = str(editor.file_name())
            model.setData(index, text)
            return
        elif type(editor) == CodeEditor:
            text = editor.toPlainText()
            model.setData(index, text)
            return
        elif type(editor) == ReferenceEditor:
            data = editor.itemData(
                editor.currentIndex(),
                editor.getRootItemModel().reference_role
            ).toPyObject()
            model.setData(
                index,
                data
            )
            return
        return super(EditorItemDelegate,
                     self).setModelData(editor, model, index)


class EditorItem(QtGui.QGraphicsWidget):
    '''
    Graphical representation of the data-model.
    '''
    def __init__(self,
                 index,
                 parent=None):
        super(EditorItem, self).__init__(parent)

        # Perhaps need an ItemDelegate/StyledItemDelegate
        # which transforms data from editor to model and back

        # perhaps just point this to the ItemModel()?
        self.modelindex = index
        self.dataMapper = QtGui.QDataWidgetMapper()
        self.dataMapper.setModel(self.modelindex.model())
        self.dataMapper.setOrientation(QtCore.Qt.Vertical)

        self.dataMapper.setRootIndex(self.modelindex)
        self.dataMapper.setCurrentIndex(1)

        self.delegate = EditorItemDelegate(self)
        self.dataMapper.setItemDelegate(self.delegate)

        self.itemWidget = EditorItemWidget(None, self)
        self.dataMapper.addMapping(self.itemWidget, 0)

        # graphics item which represents
        self._item = None
        # text label of this item
        item = self.modelindex.model().getModel(self.modelindex)
        self._label = TextItem(item['Name'], parent=self)

        self.loadResources()
        # self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        self.initializeFlags()
        self.updateGraphicsItem()

    def viewModel(self):
        return self.scene().viewModel()

    def updateLabel(self, width, height):
        self._label.updateGeometry()
        '''
        self._label.setAlignment(
            self.viewModel()[item.kind()]['text horizontal alignment'],
            self.viewModel()[item.kind()]['text vertical alignment']
        )
        self._label.setPos(
            self.viewModel()['text location'],
            self.pos(),
            width,
            height
        )
        '''

    def createItem(self, width, height):
        self._item = RoundRectItem(0, 0, width, height)
        self._item.setBrush(QtGui.QColor('light blue'))
        '''
        draw_style = self.viewModel()['draw style']
        if self.viewModel()['icon'] and draw_style == 'icon':
            self._item = QtGui.QGraphicsPixmapItem()
            self._item.setPixmap(
                QtGui.QPixmap(self.viewModel()['icon']).scaled(width,height)
            )
        else:
            if draw_style == 'rect':
                self._item = QtGui.QGraphicsRectItem(0,0,width,height)
            elif draw_style == 'ellipse':
                self._item = QtGui.QGraphicsEllipseItem(0,0,width,height)
            elif draw_style == 'round rect':
                self._item = RoundRectItem(0,0,width,height)
            if self._item:
                self._item.setBrush(QtGui.QColor(self.viewModel()['color']))
        '''

    def loadResources(self):
        self.setLayout(layout_create('horizontal'))
        '''
        new_layout = layout_create(self.viewModel()['layout style'])
        if type(self.layout()) != type(new_layout):
            new_layout.fromLayout(self.layout())
            self.setLayout(new_layout)
        '''
        sh = self.sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF())
        width = sh.width()
        height = sh.height()
        self.updateLabel(width, height)
        self.createItem(width, height)

    def paint(self, painter, option, widget=None):
        super(EditorItem, self).paint(painter, option, widget)
        if self._item:
            self._item.paint(painter, option, widget)

    def boundingRect(self):
        minx = 0
        miny = 0
        maxx = 0
        maxy = 0
        '''
        if self._item:
            brect = self._item.boundingRect()
            minx = min(brect.x(),minx)
            miny = min(brect.y(),miny)
            maxx = max(maxx, brect.x() + brect.width())
            maxy = max(maxy, brect.y() + brect.height())
        '''
        if self._label:
            brect = self._label.boundingRect()
            minx = min(brect.x(), minx)
            miny = min(brect.y(), miny)
            maxx = max(maxx, brect.x() + brect.width())
            maxy = max(maxy, brect.y() + brect.height())
        retRect = QtCore.QRectF(minx, miny, maxx-minx, maxy-miny)
        return retRect

    def sizeHint(self, which, constraint):
        shw = 0
        shh = 0
        sh = self.layout().sizeHint(which, constraint)
        shw = sh.width()
        shh = sh.height()
        shw = max(shw, self.boundingRect().width())
        shh = max(shh, self.boundingRect().height())
        return QtCore.QSizeF(
            max(shw, 50),  # self.viewModel()['width']),
            max(shh, 50)  # self.viewModel()['height'])
        )
        
    def updateGraphicsItem(self):
        # self.layout().activate()
        self.prepareGeometryChange()
        sh = self.sizeHint(QtCore.Qt.SizeHint(), QtCore.QSizeF())
        width = sh.width()
        height = sh.height()
        self.updateLabel(width, height)
        self.createItem(width, height)
        self.updateGeometry()
        self.update()

    def updateChild(self, child):
        self.layout().updateItem(child)
        self.updateGraphicsItem()

    def removeChild(self, child):
        # Should this just point down to the underlying model's
        # removeRows() method and then let the updating take effect?
        self.layout().removeItem(child)
        self.updateGraphicsItem()

    def addChild(self, child):
        # Should this just point down to the underlying model's
        # insertRows() method and then let the updating take effect?
        self.layout().addItem(child)
        self.updateGraphicsItem()

    def isMovable(self):
        return bool(self.flags() & QtGui.QGraphicsItem.ItemIsMovable)

    def mouseDoubleClickEvent(self, event):
        QtGui.QGraphicsWidget.mouseDoubleClickEvent(self, event)
        '''
        e = QtGui.QMouseEvent(
            QtCore.QEvent.GraphicsSceneMouseDoubleClick,
            event.screenPos(),
            event.button(),
            event.buttons(),
            event.modifiers()
        )
        self.itemWidget.mouseDoubleClickEvent(e)
        '''
        editor = self.scene().parent().getEditor()
        editor.setDataMapper(self.dataMapper)
        editor.update()
        editor.show()
        editor.raise_()

    def updateAttributes(self, attrs):
        self.loadResources()
        self.updateGraphicsItem()
                
    '''
    BELOW HERE ARE NOT AS RELEVANT RIGHT NOW
    '''
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

        item = self.modelindex.model().getModel(self.modelindex)

        if item.parent and \
           '0' in item.parent.children.get_cardinality_of(type(item)):
            delSelf = QtGui.QAction('Delete', self)
            delSelf.triggered.connect(self.delete)
            menu.addAction(delSelf)

        for a in item.children.allowed():
            addAction = QtGui.QAction('Add new {}'.format(a.__name__), self)
            addAction.triggered.connect(self.addNewItem(a))
            menu.addAction(addAction)
        
        menu.exec_(event.screenPos())

    def addNewItem(self, _type):
        def genericItem(e):
            self.modelindex.model().insertRows(0, 1, self.modelindex, _type)
        return genericItem

    def delete(self, event):
        # What should this method do?
        # Should this just point down to the underlying model's
        # removeRows() method and then let the updating take effect?
        for i in range(self.layout().count()):
            self.layout().itemAt(0).delete(None)
        if self.scene():
            self.scene().removeItem(self)

    def mousePressEvent(self, event):
        QtGui.QGraphicsWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        QtGui.QGraphicsWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        QtGui.QGraphicsWidget.mouseReleaseEvent(self, event)

    def hoverEnterEvent(self, event):
        QtGui.QGraphicsWidget.hoverEnterEvent(self, event)

    def hoverLeaveEvent(self, event):
        QtGui.QGraphicsWidget.hoverLeaveEvent(self, event)

