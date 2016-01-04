"""
Toolbar for the Meta-Model Editor

This program provides an API for 
library code to add toolbars,
buttons and actions to the GUI.
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

def toolbar_add_widget(self, tb_name, tb_widget):
    """
    :param in string tb_name: name used to create the toolbar from :func:`Editor.toolbar_create`.
    :param in Action tb_widget: any pyQt widget to add to the toolbar.
    """
    if tb_name in self.toolbars:
        self.toolbars[tb_name].addWidget(tb_widget)

def toolbar_remove(self, tb_name):
    pass

