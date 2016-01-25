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

    def getRootItems(self):
        return self.rootNode.children

    def setMeta(self, meta):
        self.META = meta
    
    def getMeta(self):
        return self.META

    def getModel(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self.rootNode

    def hasChildren(self, parent):
        if parent.isValid():
            return self.rowCount(parent) > 0
        else:
            return True

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self.rootNode
        else:
            parentNode = parent.internalPointer()
        return parentNode.row_count()

    def columnCount(self, parent):
        if not parent.isValid():
            parentNode = self.rootNode
        else:
            parentNode = parent.internalPointer()
        return parentNode.column_count()

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            #  columns 0 and 2 are children and pointers respectively
            if index.column() == 0 or index.column() == 2:
                return node['Name']
            # column 1 is attributes
            elif index.column() == 1:
                return node.getValue()
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
            if index.column() == 0:
                return node['Name']
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid() and role == QtCore.Qt.EditRole:
            node = index.internalPointer()
            if index.column() == 0 or index.column() == 2:
                attr = node.get_attribute('Name')
            elif index.column() == 1:
                attr = node
            if attr.editable:
                valid, errMsg = attr.fromQVariant(value)
                if not valid:
                    print 'ERROR: ', errMsg
                self.dataChanged.emit(index, index)
                if index.internalPointer() == attr:
                    self.dataChanged.emit(
                        index.parent(),
                        index.parent()
                    )
                else:
                    self.dataChanged.emit(
                        index.child(0, 1),
                        index.child(0, 1)
                    )
                return True
        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return QtCore.QVariant('Model')

    def flags(self, index):
        if not index.isValid():
            return None
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
        childItem = parentNode.child(row, column)
        if not childItem:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(row, column, childItem)

    def parent(self, index):
        '''Returns a :class:`QModelIndex` for the parent of index.'''
        node = self.getModel(index)
        parentNode = node.parent
        if (parentNode == self.rootNode or
            parentNode.row() is None or
            parentNode.column() is None):
            return QtCore.QModelIndex()
        return self.createIndex(
            parentNode.row(),
            parentNode.column(),
            parentNode
        )

    def insertRows(self, position, rows, parent=QtCore.QModelIndex(),
                   _type=None):
        '''Adds children to the model at position.

        :param in position: a :class:`QModelIndex` where the new children go
        :param in rows: number of new children to insert
        :param in parent: :class:`QModelIndex` of the parent of new children
        '''

        assert _type != None

        parentNode = self.getModel(parent)

        self.layoutAboutToBeChanged.emit()
        self.beginInsertRows(parent, position, position + rows - 1)
        for row in range(rows):

            childNode = _type()

            success = parentNode.insert_child(position + row, childNode)

            if success:
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

        self.endInsertRows()
        self.layoutChanged.emit()
        self.dataChanged.emit(parent, self.index(position + rows, 0, parent))

        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        '''Removes children from the model at position.

        :param in position: a :class:`QModelIndex` where the children start
        :param in rows: number of children to delete
        :param in parent: :class:`QModelIndex` of the parent of the children
        '''
        parentNode = self.getModel(parent)

        self.layoutAboutToBeChanged.emit()
        self.beginRemoveRows(parent, position, position + rows - 1)

        for row in range(rows):
            success = parentNode.remove_child(position)

        self.endRemoveRows()
        self.layoutChanged.emit()
        self.dataChanged.emit(parent, parent)

        return success

