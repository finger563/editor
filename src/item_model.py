#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This implements the model
for the metamodel in the MVC
paradigm.  It uses Qt's
AbstractItemModel base class.
'''

__author__ = 'William Emfinger'
__copyright__ = 'Copyright 2016, ROSMOD'
__credits__ = ['William Emfinger', 'Pranav Srinivas Kumar']
__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'William Emfinger'
__email__ = 'emfinger@isis.vanderbilt.edu'
__status__ = 'Production'

from PyQt4 import QtCore, QtGui


class ItemModel(QtCore.QAbstractItemModel):
    '''Implements the :class:`QtCore.QAbstractItemModel` to interact with
    the underlying data-model, and create :class:`QModelIndex` objects
    for retrieving and setting data.
    '''
    sort_role = QtCore.Qt.UserRole
    # filter_role = QtCore.Qt.UserRole + 1
    filter_meta_role = QtCore.Qt.UserRole + 1
    filter_data_role = QtCore.Qt.UserRole + 2
    reference_role = QtCore.Qt.UserRole + 3

    def __init__(self, root, parent=None):
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
                kind = node.kind()
                return QtGui.QIcon(
                    QtGui.QPixmap('icons/model/' + kind + '.png')
                )
        if role == ItemModel.sort_role:
            return node.kind()
        if role == ItemModel.reference_role:
            return node
        if role == ItemModel.filter_meta_role:
            return node.kind()
        if role == ItemModel.filter_data_role:
            return node.attributes.values()[index.column()].value
        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            node = index.internalPointer()
            if role == QtCore.Qt.EditRole:
                attr = node.attributes.values()[index.column()]
                if attr.editable:
                    valid, errMsg = node.attributes.values()[
                        index.column()].fromQVariant(value)
                    if not valid:
                        print 'ERROR: ', errMsg
                    self.dataChanged.emit(index, index)
                    return True
        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return 'Model'

    def flags(self, index):
        f = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        if index.column() == 0:
            f = f | QtCore.Qt.ItemIsEditable
        return f

    def index(self, row, column, parent):
        '''Returns a :class:`QModelIndex` for the child of the parent at row,
        col.

        :param in int row: row number
        :param in int column: column number
        :param in parent: :class:`QModelIndex` of the parent
        '''
        parentNode = self.getModel(parent)
        # child should be implemented by data model
        childItem = parentNode.child(row)
        if not childItem:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(row, column, childItem)

    def parent(self, index):
        '''Returns a :class:`QModelIndex` for the parent of index.'''
        # index.row() , index.column()
        node = self.getModel(index)
        parentNode = node.parent
        if parentNode == self.rootNode:
            return QtCore.QModelIndex()
        return self.createIndex(parentNode.row(), 0, parentNode)
        # data model needs to have a row method,
        # e.g. parent.children.index(self)

    def insertRows(self, position, rows, parent=QtCore.QModelIndex(),
                   _type=None):
        '''Adds children to the model at position.

        :param in position: a :class:`QModelIndex` where the new children go
        :param in rows: number of new children to insert
        :param in parent: :class:`QModelIndex` of the parent of new children
        '''
        parentNode = self.getModel(parent)

        for row in range(rows):
            childNode = _type()

            self.beginInsertRows(parent, row, row)
            success = parentNode.insert_child(position, childNode)
            self.endInsertRows()

            childCount = parentNode.child_count()
            newName = 'New_{}_{}'.format(_type.__name__,
                                         childCount)
            validName = False
            while not validName:
                newName = 'New_{}_{}'.format(_type.__name__,
                                             childCount)
                validName, errMsg = childNode.get_attribute(
                    'Name'
                ).setValue(newName)
                childCount += 1

            self.dataChanged.emit(parent, self.index(row, 0, parent))

        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        '''Removes children from the model at position.

        :param in position: a :class:`QModelIndex` where the children start
        :param in rows: number of children to delete
        :param in parent: :class:`QModelIndex` of the parent of the children
        '''
        parentNode = self.getModel(parent)

        for row in range(rows):
            self.beginRemoveRows(parent, row, row)
            success = parentNode.remove_child(position)
            self.endRemoveRows()
            self.dataChanged.emit(parent, self.index(row, 0, parent))

        count = parentNode.child_count()
        self.dataChanged.emit(parent, parent.child(count, 0))
        return success


class SortFilterProxyModel(QtGui.QSortFilterProxyModel):
    '''
    Extends :class:`QtGui.QSortFilterProxyModel` to customize filtering
    on a :class:`QtCoreQAbstractItemModel` or its subclass.
    '''

    rowFiltered = QtCore.pyqtSignal(QtCore.QModelIndex, bool)

    def __init__(self, parent):
        super(SortFilterProxyModel, self).__init__(parent)

    def setSourceModel(self, model):
        super(SortFilterProxyModel, self).setSourceModel(model)
        model.rowsInserted.connect(self.sourceRowsInserted)

    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def sourceRowsInserted(self, parent, start, end):
        self.rowsInserted.emit(self.mapFromSource(parent),
                               start,
                               end)

    def filterAcceptsRow(self, row, parent):
        index0 = self.sourceModel().index(row, self.filterKeyColumn(), parent)
        text = self.sourceModel().data(index0, self.filterRole())
        filtered = QtCore.QString(text).contains(self.filterRegExp())

        inChildren = False
        for r in range(index0.internalPointer().child_count()):
            if self.filterAcceptsRow(r, index0):
                inChildren = True
                break

        filtered = filtered or inChildren
        self.rowFiltered.emit(index0, filtered)
        return filtered


def main():
    import sys
    from attribute_widget import AttributeEditor
    from meta import Model

    app = QtGui.QApplication(sys.argv)

    rootNode = Model()
    rootNode['Name'] = 'Project_Root'

    dep = Model()
    dep['Name'] = 'My_Deployment'
    rootNode.add_child(dep)

    sw = Model()
    sw['Name'] = 'My_Software'
    rootNode.add_child(sw)

    pkg = Model()
    pkg['Name'] = 'My_Package'
    sw.add_child(pkg)

    comp = Model()
    comp['Name'] = 'My_Component'
    pkg.add_child(comp)

    tmr = Model()
    tmr['Name'] = 'My_Timer'
    comp.add_child(tmr)

    hw = Model()
    hw['Name'] = 'My_Hardware'
    rootNode.add_child(hw)

    ''' SET UP THE MODEL, PROXY MODEL '''
    
    proxyModel = SortFilterProxyModel(None)
    proxyModel.setDynamicSortFilter(True)
    proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
    proxyModel.setSortRole(ItemModel.sort_role)
    proxyModel.setFilterRole(ItemModel.filter_role)

    model = ItemModel(rootNode)

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
    treeView2.setModel(proxyModel)
    treeView2.setSortingEnabled(True)
    treeView2.setSelectionModel(treeView.selectionModel())
    treeView2.show()

    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(filterEdit)
    vbox.addWidget(treeView)
    vbox.addWidget(treeView2)
    mainWidget.setLayout(vbox)
    mainWidget.show()
    app.setActiveWindow(mainWidget)

    ae.show()
    ae.raise_()

    swIndex = model.index(1, 0, QtCore.QModelIndex())
    model.insertRows(0, 5, swIndex)
    # model.removeRows(1, 1)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
