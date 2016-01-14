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


class TreeView(QtGui.QTreeView):

    def edit(self, index, trigger, event):
        # don't want to enter renaming mode every time we
        # want to open the graphical editor
        if trigger == QtGui.QAbstractItemView.DoubleClicked:
            return False
        return QtGui.QTreeView.edit(self, index, trigger, event)

    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def rowsInserted(self, parent, start, end):
        super(TreeView, self).rowsInserted(parent, start, end)
        self.setExpanded(parent, True)

    def contextMenuEvent(self, e):
        indexes = self.selectedIndexes()
        m = self.model().sourceModel()
        if indexes:
            menu = QtGui.QMenu()
            hasActions = False

            mi = self.model().mapToSource(indexes[0])
            if not mi.isValid():
                return
            item = m.getModel(mi)

            if item.parent and \
               '0' in item.parent.children.get_cardinality_of(type(item)):
                hasActions = True
                delAction = QtGui.QAction(
                    'Delete {}'.format(item['Name']), self)
                delAction.triggered.connect(self.delTreeItem(mi))
                menu.addAction(delAction)
            for a in item.children.allowed():
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
            self.model().sourceModel().insertRows(0, 1, mi, _type)
        return genericItem

    def delTreeItem(self, mi):
        def genericItem(e):
            self.model().sourceModel().removeRows(mi.row(), 1, mi.parent())
        return genericItem
