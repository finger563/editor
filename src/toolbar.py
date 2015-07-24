"""
Toolbar for the Meta-Model Editor

This program provides an API for 
library code to add toolbars,
buttons and actions to the GUI.
"""

from PyQt4 import QtCore
from PyQt4 import QtGui

def toolbar_init(self):
    self.toolbars = {}

def toolbar_create(self, tb_name):
    """
    :param in string tb_name: name of the toolbar
    """
    if tb_name not in self.toolbars:
        self.toolbars[tb_name] = self.addToolBar(tb_name)

def toolbar_add_action(self, tb_name, tb_action):
    """
    :param in string tb_name: name used to create the toolbar from :func:`Editor.toolbar_create`.
    :param in Action tb_action: :class:`action.Action` object to bind to the toolbar.
    """
    if tb_name in self.toolbars:
        self.toolbars[tb_name].addAction(tb_action)

def toolbar_remove(self, tb_name):
    pass

