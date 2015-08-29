"""
ModelTree for the Meta-Model Editor

This program allows viewing of generic
metamodels as tree structures in Qt.
"""

from PyQt4 import QtCore
from PyQt4 import QtGui

from classes import test_project

project = test_project()

class ModelTreeItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent = None, obj = None):
        super(ModelTreeItem, self).__init__(parent)
        self.setObject(obj)

    def setObject(self, obj):
        self._object = obj

    def Object(self):
        return self._object

class ModelTree(QtGui.QTreeWidget):
    def __init__(self,parent):
        super(ModelTree,self).__init__(parent)
        self.setExpandsOnDoubleClick(False)
        #self.setColumnCount(2)
        
    def populate(self, model = project, parent = None):
        if parent:
            item = ModelTreeItem(parent)
        else:
            item = ModelTreeItem()
            self.addTopLevelItem(item)
        item.setObject(model)
        for key,attr in model.attributes.iteritems():
            if attr:
                if "name" in key:
                    item.setText(0, str(attr.value))
        for child in model.children:
            self.populate(child, item)

