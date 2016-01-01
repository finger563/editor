#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Meta-Model Editor 

This program allows users to operate 
on meta-models and models using loadable
libraries to perform meta-model specific
operations such as generation, analysis,
and deployment.

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: July 2015
"""

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import Qt

class TreeView(QtGui.QTreeView):

    def mouseDoubleClickEvent(self, e):
        QtGui.QTreeView.mouseDoubleClickEvent(self,e)

    def contextMenuEvent(self, e):
        menu = QtGui.QMenu()

        indexes = self.selectedIndexes()
        m = self.model().sourceModel()
        if indexes:
            mi = self.model().mapToSource( indexes[0] )
            item = m.getModel( mi )

            delAction = QtGui.QAction('Delete {}'.format(item['Name'].value), self)
            delAction.triggered.connect(self.delTreeItem(mi))
            menu.addAction(delAction)

            for a in item.children._allowed:
                addAction = QtGui.QAction('Add New {}'.format(a.__name__), self)
                addAction.triggered.connect(self.addTreeItem(mi, a))
                menu.addAction(addAction)
            
            menu.exec_(e.globalPos())

    def addTreeItem(self, mi, _type):
        def genericItem(e):
            self.model().sourceModel().insertRows( 0, 1, mi )
        return genericItem

    def delTreeItem(self, mi):
        def genericItem(e):
            item = self.model().sourceModel().getModel(mi)
            r = item.row()
            p = self.model().sourceModel().parent(mi)
            self.model().sourceModel().removeRows( r, 1, p )
        return genericItem
