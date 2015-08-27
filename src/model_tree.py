"""
ModelTree for the Meta-Model Editor

This program allows viewing of generic
metamodels as tree structures in Qt.
"""

from PyQt4 import QtGui

from classes import *

class ModelTree(QtGui.QTreeWidget):
    def __init__(self,parent):
        super(ModelTree,self).__init__(parent)
        self.setColumnCount(2)
        
    def populate(self, model = project, parent = None):
        if parent:
            item = QtGui.QTreeWidgetItem(parent)
        else:
            item = QtGui.QTreeWidgetItem()
            self.addTopLevelItem(item)
        for key,attr in model.attributes.iteritems():
            if attr:
                if "name" in key:
                    item.setText(0, str(attr.value))
                else:
                    attrItem = QtGui.QTreeWidgetItem(item)
                    attrItem.setText(0, key)
                    attrItem.setText(1, str(attr.value))
        for child in model.children:
            self.populate(child, item)    

