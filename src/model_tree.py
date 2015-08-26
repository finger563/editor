"""
ModelTree for the Meta-Model Editor

This program allows viewing of generic
metamodels as tree structures in Qt.
"""

from PyQt4 import QtGui

from classes import *

p = Project("test project")
p.add_child(Software("software"))
p.children[-1].add_child(Package("Package 1"))
p.children[-1].children[-1].add_child(Message("Message 1", "int8 test"))
p.children[-1].children[-1].add_child(Message("Service 1", "int8 test"))
p.children[-1].children[-1].add_child(Message("Service 2", "int8 test"))
p.children[-1].add_child(Package("Package 2"))
p.children[-1].children[-1].add_child(Message("Message 2", "int8 test"))
p.children[-1].children[-1].add_child(Message("Message 3", "int8 test"))
p.children[-1].add_child(Package("Package 3"))
p.children[-1].children[-1].add_child(Message("Message 4", "int8 test"))
p.children[-1].add_child(Package("Package 4"))
p.children[-1].children[-1].add_child(Message("Message 5", "int8 test"))
p.add_child(Hardware("hardware"))
p.add_child(Deployment("deployment"))

class ModelTree(QtGui.QTreeWidget):
    def __init__(self,parent):
        super(ModelTree,self).__init__(parent)
        self.setColumnCount(2)
        
    def populate(self, model = p, parent = None):
        if parent:
            item = QtGui.QTreeWidgetItem(parent)
        else:
            item = QtGui.QTreeWidgetItem()
            self.addTopLevelItem(item)
        for key,attr in model.attributes.iteritems():
            if "name" in key:
                item.setText(0, attr)
            else:
                attrItem = QtGui.QTreeWidgetItem(item)
                attrItem.setText(0, key)
                attrItem.setText(1, attr)
        for child in model.children:
            self.populate(child, item)    

