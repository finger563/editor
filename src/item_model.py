"""
This implements the model 
for the metamodel in the MVC
paradigm.  It uses Qt's 
AbstractItemModel base class.
"""

from PyQt4 import QtCore, QtGui

class itemModel(QtCore.QAbstractItemModel):
    def __init__(self, root, parent=None):
        super(itemModel, self).__init__(parent)
        self.rootNode = root

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self.rootNode
        else:
            parentNode = parent.internalPointer()
        return parentNode.childCount()  # should be implemented by data model
        
    def columnCount(self, parent):
        return 2
        
    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return node['name'].value
            else:
                return node.kind
        return None

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Name"
            else:
                return "Kind"
        
    def flags(self, index):
        f = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        if index.column() == 0:
            f = f | QtCore.Qt.ItemIsEditable
        return f
        
    def index(self, row, column, parent):
        if not parent.isValid():
            parentNode = self.rootNode
        else:
            parentNode = parent.internalPointer()
        childItem = parentNode.child(row)   # child should be implemented by data model
        if not childItem:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(row, column, childItem)
        
    def parent(self, index):
        #index.row() , index.column()
        node = index.internalPointer()
        parentNode = node.parent
        if parentNode == self.rootNode:
            return QtCore.QModelIndex()
        return self.createIndex(parentNode.row(), 0, parentNode)  # data model needs to have a row method, e.g. parent.children.index(self)

if __name__ == "__main__":
    import sys
    import metamodel.base as classes
    import metamodel.importer as rosmod

    app = QtGui.QApplication(sys.argv)

    rootNode = rosmod.Project()
    rootNode['name'].value = "Project Root"
    sw = rosmod.Software()
    sw['name'].value = "My Software"
    rootNode.add_child(sw)
    pkg = rosmod.Package()
    pkg['name'].value = "My Package"
    sw.add_child(pkg)
    hw = rosmod.Hardware()
    hw['name'].value = "My Hardware"
    rootNode.add_child(hw)
    dep = rosmod.Deployment()
    dep['name'].value = "My Deployment"
    rootNode.add_child(dep)

    model = itemModel(rootNode)

    treeView = QtGui.QTreeView()
    treeView.show()

    treeView.setModel(model)

    sys.exit(app.exec_())
