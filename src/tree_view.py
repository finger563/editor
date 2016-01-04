#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Meta-Model Editor 

This program allows users to operate 
on meta-models and models using loadable
libraries to perform meta-model specific
operations such as generation, analysis,
and deployment.
"""

__author__ = "William Emfinger"
__copyright__ = "Copyright 2016, ROSMOD"
__credits__ = ["William Emfinger", "Pranav Srinivas Kumar"]
__license__ = "GPL"
__version__ = "0.4"
__maintainer__ = "William Emfinger"
__email__ = "emfinger@isis.vanderbilt.edu"
__status__ = "Production"

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import Qt

class TreeView(QtGui.QTreeView):

    def mouseDoubleClickEvent(self, e):
        #QtGui.QTreeView.mouseDoubleClickEvent(self,e)
        e.ignore()

    def contextMenuEvent(self, e):
        menu = QtGui.QMenu()

        indexes = self.selectedIndexes()
        m = self.model().sourceModel()
        if indexes:
            mi = self.model().mapToSource( indexes[0] )
            item = m.getModel( mi )

            delAction = QtGui.QAction('Delete {}'.format(item['Name']), self)
            delAction.triggered.connect(self.delTreeItem(mi))
            menu.addAction(delAction)

            for a in item.children._allowed:
                addAction = QtGui.QAction('Add New {}'.format(a.__name__), self)
                addAction.triggered.connect(self.addTreeItem(mi, a))
                menu.addAction(addAction)
            
            menu.exec_(e.globalPos())

    def addTreeItem(self, mi, _type):
        def genericItem(e):
            self.model().sourceModel().insertRows( 0, 1, mi, _type )
        return genericItem

    def delTreeItem(self, mi):
        def genericItem(e):
            self.model().sourceModel().removeRows( mi.row(), 1, mi.parent() )
        return genericItem
