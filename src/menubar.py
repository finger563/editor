"""
MenuBar for the Meta-Model Editor

This program provides an API for 
library code to add menus and actions
to the GUI menubar.
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

def menubar_init(self):
    self.menus = {}
    self.menubar = self.menuBar()

def menubar_add_menu(self, menu_name):
    """
    :param in string menu_name: name of the menu, shortcut (denoted by &) optional (note that the & will be stripped)
    """
    dict_name = menu_name.strip('&')
    if dict_name not in self.menus:
        self.menus[dict_name] = self.menubar.addMenu(menu_name)

def menu_add_action(self, menu_name, menu_action):
    """
    :param in string menu_name: name used to create the menu from :func:`Editor.menubar_add_menu`.
    :param in Action menu_action: :class:`action.Action` object to bind to the menu.
    """
    dict_name = menu_name.strip('&')
    if dict_name in self.menus:
        self.menus[dict_name].addAction(menu_action)

