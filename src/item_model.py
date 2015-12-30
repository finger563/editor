"""
This implements the model 
for the metamodel in the MVC
paradigm.  It uses Qt's 
AbstractItemModel base class.
"""

from PyQt4 import QtCore, QtGui

class ItemModel(QtCore.QAbstractItemModel):

    sort_role = QtCore.Qt.UserRole
    filter_role = QtCore.Qt.UserRole + 1
    
    def __init__(self, root, parent = None):
        super(ItemModel, self).__init__(parent)
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
        return 1
        
    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() < len(node.attributes.items()):
                return node.attributes.values()[index.column()].value
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                kind = node.kind
                # MAKE THIS GENERIC TO GET ICONS PROPERLY
                return QtGui.QIcon(QtGui.QPixmap("icons/model/" + kind + ".png"))
        if role == ItemModel.sort_role:
            return node.kind            
        if role == ItemModel.filter_role:
            return node.kind
        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            node = index.internalPointer()
            if role == QtCore.Qt.EditRole:
                node.attributes.values()[index.column()].fromQVariant(value)
                self.dataChanged.emit(index,index)
                return True
        return False
    
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Name"
        
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

class SortFilterProxyModel(QtGui.QSortFilterProxyModel):

    def __init__(self, parent):
        super(SortFilterProxyModel,self).__init__(parent)

    def filterAcceptsRow(self, row, parent):
        index0 = self.sourceModel().index(row, self.filterKeyColumn(), parent)
        inChildren = False
        for r in range(index0.internalPointer().child_count()):
            if self.filterAcceptsRow(r,index0):
                inChildren = True
                break
        return QtCore.QString(self.sourceModel().data(index0, self.filterRole())).contains(self.filterRegExp()) or inChildren
