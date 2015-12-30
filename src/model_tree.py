"""
ModelTree for the Meta-Model Editor

This program allows viewing of generic
metamodels as tree structures in Qt.
"""

from PyQt4 import QtCore
from PyQt4 import QtGui

class ModelTreeItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent, obj = None):
        super(ModelTreeItem, self).__init__(parent)
        if obj and obj['Name']:
            self.setText(obj['Name'].value)

class ModelTree(QtGui.QTreeWidget):
    def __init__(self,parent):
        super(ModelTree,self).__init__(parent)
        self.setExpandsOnDoubleClick(False) # needed so that double click can open visualization
        
    def load_model(self, model, parent):
        item = ModelTreeItem(parent, model)
        if not parent:
            self.addTopLevelItem(item)
        for child in model.children:
            self.load_model(child, item)
        item.setExpanded(True)
