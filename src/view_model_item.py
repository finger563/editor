"""
View Model Item

This class defines the widget
which allows for viewing and editing
of view models.

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
from editor_item import EditorItem

class ViewModelItem(EditorItem):

    def __getitem__(self, key):
        return self.viewModel()[key]

    def __setitem__(self, key, value):
        self.viewModel()[key] = value

    def model(self):
        return self.viewModel()
        
    def createLabel(self, width, height):
        self._label = TextItem(self.viewModel()['kind'].value)
        self._label.setAlignment(
            self.viewModel()['text horizontal alignment'].value,
            self.viewModel()['text vertical alignment'].value
        )
        self._label.setPos(self.viewModel()['text location'].value, self.pos(), width, height)

    def removeChild(self, child):
        self.viewModel().removeChild(child.viewModel())
        super(ViewModelItem,self).removeChild(child)

    def addChild(self, child):
        self.viewModel().addChild(child.viewModel())
        super(ViewModelItem,self).addChild(child)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()

        delSelf = Action('', 'Delete', self)
        delSelf.triggered.connect(self.delete)
        menu.addAction(delSelf)
        
        addSelf = Action('', 'Add new Item', self)
        addSelf.triggered.connect(self.addNewItem)
        menu.addAction(addSelf)
        
        menu.exec_(event.screenPos())

    def addNewItem(self, event):
        self.addChild(ViewModelItem(self, view_model = ViewModel()))
