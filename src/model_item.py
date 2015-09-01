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
from editor_item import EditorItem

class ModelItem(EditorItem):

    def __getitem__(self, key):
        return self.model()[key]

    def __setitem__(self, key, value):
        self.model()[key] = value

    def createLabel(self, width, height):
        if self.viewModel()['draw style'].value in ['hidden']:
            return
        if self.model():
            self._label = TextItem(self.model()['name'].value)
            self._label.setAlignment(
                self.viewModel()['text horizontal alignment'].value,
                self.viewModel()['text vertical alignment'].value
            )
            self._label.setPos(self.viewModel()['text location'].value, self.pos(), width, height)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()

        delSelf = Action('', 'Delete', self)
        delSelf.triggered.connect(self.delete)
        menu.addAction(delSelf)

        for a in self.model().children._allowed:
            addAction = Action('', 'Add new {}'.format(a.__name__), self)
            addAction.triggered.connect(lambda : self.addNewItem(a) )
            menu.addAction(addAction)
        
        menu.exec_(event.screenPos())

    def addNewItem(self, _type):
        self.addChild(ModelItem(self, view_model = ViewModel( kind = _type.__name__ ),
                                model = _type()))
