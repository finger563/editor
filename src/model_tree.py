"""
ModelTree for the Meta-Model Editor

This program allows viewing of generic
metamodels as tree structures in Qt.
"""

from PyQt4 import QtGui

class ModelTree(QtGui.QTreeWidget):
    def __init__(self,parent):
        super(ModelTree,self).__init__(parent)
        
    def populate(self, model, parent):
        item = QtGui.QTreeWidgetItem(parent)
        for key,attr in model.attributes.iteritems():
            if "name" in key:
                item.setText(0, attr.value)
            else:
                attrItem = QtGui.QTreeWidgetItem(item)
                attrItem.setText(0, key)
                attrItem.setText(1, attr.value)
        for child in model.children:
            self.populate(child, item)    

