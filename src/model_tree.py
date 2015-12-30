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
        self.setObject(obj)

    def setObject(self, obj):
        self._object = obj

    def Object(self):
        return self._object

class ModelTree(QtGui.QTreeWidget):
    def __init__(self,parent):
        super(ModelTree,self).__init__(parent)
        self.setExpandsOnDoubleClick(False)
        
    def load_model(self, model, parent):
        item = ModelTreeItem(parent)
        if not parent:
            self.addTopLevelItem(item)
        item.setObject(model)
        for key,attr in model.attributes.iteritems():
            if attr:
                if "name" in key:
                    item.setText(0, str(attr.value))
        for child in model.children:
            self.load_model(child, item)
        item.setExpanded(True)

    def load_meta_model(self, meta_model, parent):
        item = ModelTreeItem(parent)
        if not parent:
            self.addTopLevelItem(item)
        item.setObject(meta_model)
        item.setText(0, str(meta_model.kind))
        for a in meta_model.children._allowed:
            self.load_meta_model(a(), item)
        item.setExpanded(True)
