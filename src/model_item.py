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

from view_model import ViewModel
from action import Action
from editor_item import EditorItem

class ModelItem(EditorItem):

    def initializeFlags(self):
        super(ModelItem,self).initializeFlags()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)

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
        t = ModelItem( self,
                       view_model = ViewModel( kind = _type.__name__ ),
                       model = _type()
        )
        self.addChild(t)
