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

    sort_role = QtCore.Qt.UserRole
    filter_role = QtCore.Qt.UserRole + 1
    
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
        return 5
        
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
                if kind == "Hardware":
                    return QtGui.QIcon(QtGui.QPixmap("icons/model/Hardware.png"))
        if role == itemModel.sort_role:
            return node.kind            
        if role == itemModel.filter_role:
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

class mySortFilterProxyModel(QtGui.QSortFilterProxyModel):

    def __init__(self):
        super(mySortFilterProxyModel,self).__init__()

    def filterAcceptsRow(self, row, parent):
        index0 = self.sourceModel().index(row, self.filterKeyColumn(), parent)
        inChildren = False
        for r in range(index0.internalPointer().child_count()):
            if self.filterAcceptsRow(r,index0):
                inChildren = True
                break
        return QtCore.QString(self.sourceModel().data(index0, self.filterRole())).contains(self.filterRegExp()) or inChildren

def main():
    import sys
    from attribute_widget import AttributeEditor

    app = QtGui.QApplication(sys.argv)

    rootNode = rosmod.Project()
    rootNode['name'].value = "Project Root"

    dep = rosmod.Deployment()
    dep['name'].value = "My Deployment"
    rootNode.add_child(dep)

    sw = rosmod.Software()
    sw['name'].value = "My Software"
    rootNode.add_child(sw)

    pkg = rosmod.Package()
    pkg['name'].value = "My Package"
    sw.add_child(pkg)

    comp = rosmod.Component()
    comp['name'].value = "My Component"
    pkg.add_child(comp)

    tmr = rosmod.Timer()
    tmr['name'].value = "My Timer"
    comp.add_child(tmr)

    hw = rosmod.Hardware()
    hw['name'].value = "My Hardware"
    rootNode.add_child(hw)

    ''' SET UP THE MODEL, PROXY MODEL '''
    
    #proxyModel = QtGui.QSortFilterProxyModel()
    proxyModel = mySortFilterProxyModel()
    proxyModel.setDynamicSortFilter(True)
    proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
    proxyModel.setSortRole(itemModel.sort_role)
    proxyModel.setFilterRole(itemModel.filter_role)

    model = itemModel(rootNode)

    proxyModel.setSourceModel(model)

    ''' SET UP THE ACTUAL WIDGETS '''

    mainWidget = QtGui.QWidget()

    filterEdit = QtGui.QLineEdit()
    filterEdit.textChanged.connect(proxyModel.setFilterRegExp)

    ae = AttributeEditor(mainWidget)
    ae.setModel(proxyModel)

    treeView = QtGui.QTreeView()
    treeView.setModel(proxyModel)
    treeView.setSortingEnabled(True)
    treeView.selectionModel().currentChanged.connect(ae.setSelection)
    treeView.show()

    treeView2 = QtGui.QTreeView()
    treeView2.setModel(model)
    treeView2.show()

    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(filterEdit)
    vbox.addWidget(treeView)
    vbox.addWidget(treeView2)
    #vbox.addWidget(ae)
    mainWidget.setLayout(vbox)
    mainWidget.show()
    app.setActiveWindow(mainWidget)

    ae.show()
    ae.raise_()

    swIndex = model.index(1,0, QtCore.QModelIndex())
    model.insertRows(0,5,swIndex)
    #model.removeRows(1,1)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
