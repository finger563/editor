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

from view_model import ViewModel
from action import Action
from editor_item import EditorItem

class ViewModelItem(EditorItem):

    def model(self):
        return self.viewModel()
        
    def removeChild(self, child):
        self.viewModel().remove_child(child.viewModel())
        super(ViewModelItem,self).removeChild(child)

    def addChild(self, child):
        self.viewModel().add_child(child.viewModel())
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

    def addNewItem(self):
        def genericItem(e):
            self.addChild(
                ViewModelItem( self,
                               view_model = ViewModel()
                           )
            )
        return genericItem

