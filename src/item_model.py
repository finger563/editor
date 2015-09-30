"""
This implements the model 
for the metamodel in the MVC
paradigm.  It uses Qt's 
AbstractItemModel base class.
"""

from PyQt4 import QtCore, QtGui
import metamodel.base as classes
import metamodel.importer as rosmod

class itemModel(QtCore.QAbstractItemModel):
    def __init__(self, root, parent=None):
        super(itemModel, self).__init__(parent)
        self.rootNode = root

    def getModel(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self.rootNode

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self.rootNode
        else:
            parentNode = parent.internalPointer()
        return parentNode.child_count()  # should be implemented by data model
        
    def columnCount(self, parent):
        return 2
        
    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node['name'].value # should make this more generic
            else:
                return node.kind
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                kind = node.kind
                if kind == "Software":
                    return QtGui.QIcon(QtGui.QPixmap("icons/model/Hardware.png"))
        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node['name'].value = value  # should make this more generic
                return True
        return False
    
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
        parentNode = self.getModel(parent)
        childItem = parentNode.child(row)   # child should be implemented by data model
        if not childItem:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(row, column, childItem)
        
    def parent(self, index):
        #index.row() , index.column()
        node = self.getModel(index)
        parentNode = node.parent
        if parentNode == self.rootNode:
            return QtCore.QModelIndex()
        return self.createIndex(parentNode.row(), 0, parentNode)  # data model needs to have a row method, e.g. parent.children.index(self)

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode= self.getModel(parent)
        self.beginInsertRows(parent, position, position + rows - 1)

        for row in range(rows):
            childCount = parentNode.child_count()
            _type = parentNode.children._allowed[0]
            childNode = _type(
                name=rosmod.Name( "new {} {}".format(_type.__name__,
                                                     childCount) )
            )
            success = parentNode.insert_child(position, childNode)

        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode= self.getModel(parent)
        self.beginRemoveRows(parent, position, position + rows  -1)

        for row in range(rows):
            success = parentNode.remove_child(position)

        self.endRemoveRows()
        return success

def main():
    import sys

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

    swIndex = model.index(0,3, QtCore.QModelIndex())

    model.insertRows(1,5,swIndex)
    #model.removeRows(1,1)

    treeView = QtGui.QTreeView()
    treeView.show()

    treeView.setModel(model)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
