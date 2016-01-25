#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
The Tree View provides a viewer for the model
as a collapsable, editable tree.  Furthermore the
tree supports filtering on its proxy model for quickly
navigating large projects.
'''

__author__ = 'William Emfinger'
__copyright__ = 'Copyright 2016, ROSMOD'
__credits__ = ['William Emfinger', 'Pranav Srinivas Kumar']
__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'William Emfinger'
__email__ = 'emfinger@isis.vanderbilt.edu'
__status__ = 'Production'

from PyQt4 import QtGui, QtCore

# TODO: Refactor contextMenu to not use children, but instead use the
#       current meta-model to determine available actions.

# TODO: Add completer to show available filter text


class SortFilterProxyModel(QtGui.QSortFilterProxyModel):
    '''
    Extends :class:`QtGui.QSortFilterProxyModel` to customize filtering
    on a :class:`QtCoreQAbstractItemModel` or its subclass.
    '''

    def columnCount(self, parent):
        return 1

    def filterAcceptsRow(self, row, parent):
        index0 = self.sourceModel().index(row, self.filterKeyColumn(), parent)
        text = self.sourceModel().data(index0, self.filterRole())
        if not text:
            return False
        text = QtCore.QString(text)
        filtered = text.contains(self.filterRegExp())

        inChildren = False
        for r in range(index0.internalPointer().child_count()):
            if self.filterAcceptsRow(r, index0):
                inChildren = True
                break

        filtered = filtered or inChildren
        return filtered


class TreeView(QtGui.QTreeView):
    '''
    '''

    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def rowsRemoved(self, parent, start, end):
        '''Seems to fix segfault when deleting item and then clicking certain areas.'''
        super(TreeView, self).rowsRemoved(parent, start, end)
        self.setCurrentIndex(QtCore.QModelIndex())

    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def rowsInserted(self, parent, start, end):
        '''Implemented to auto-expand item when children are added.'''
        super(TreeView, self).rowsInserted(parent, start, end)
        self.setExpanded(parent, True)

    def edit(self, index, trigger, event):
        # don't want to enter renaming mode every time we
        # want to open the graphical editor
        if trigger == QtGui.QAbstractItemView.DoubleClicked:
            return False
        return QtGui.QTreeView.edit(self, index, trigger, event)

    def contextMenuEvent(self, e):
        menu = QtGui.QMenu()
        hasActions = False

        indexes = self.selectedIndexes()
        m = self.model().sourceModel()
        if indexes:
            mi = self.model().mapToSource(indexes[0])
        else:
            mi = self.model().mapToSource(QtCore.QModelIndex())
        item = m.getModel(mi)

        if item.parent:
            num_allowed = item.parent.children.min_number_of(item)
            num_existing = item.parent.children.number_of(item)
            if num_allowed < num_existing:
                hasActions = True
                delAction = QtGui.QAction(
                    'Delete {}'.format(item['Name']), self)
                delAction.triggered.connect(self.delTreeItem(mi))
                menu.addAction(delAction)
        for a in item.children.allowed():
            num_allowed = item.children.max_number_of(a())
            number_of = item.children.number_of(a())
            if num_allowed == -1 or number_of < num_allowed:
                hasActions = True
                addAction = QtGui.QAction(
                    'Add New {}'.format(a.__name__),
                    self
                )
                addAction.triggered.connect(self.addTreeItem(mi, a))
                menu.addAction(addAction)
        if hasActions:
            menu.exec_(e.globalPos())

    def addTreeItem(self, mi, _type):
        def genericItem(e):
            row_count = self.model().sourceModel().rowCount(mi)
            self.model().sourceModel().insertRows(row_count, 1, mi, _type)
        return genericItem

    def delTreeItem(self, mi):
        def genericItem(e):
            self.model().sourceModel().removeRows(mi.row(), 1, mi.parent())
        return genericItem
