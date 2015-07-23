"""
MenuBar for the Meta-Model Editor

This program provides an API for 
library code to add menus and actions
to the GUI menubar.
"""

from PyQt4 import QtCore
from PyQt4 import QtGui
from collections import OrderedDict

class MenuBar(QtGui.QMenuBar):
    def __init__(self, parent):
        super(MenuBar, self).__init__(parent)
        self.menus = OrderedDict()

    def add_menu(self, menu_name):
        """
        :param in string menu_name: name of the menu, shortcut (denoted by &) optional (note that the & will be stripped)
        """
        dict_name = menu_name.strip('&')
        self.menus[dict_name] = self.addMenu(menu_name)

    def add_action(self, menu_name, menu_action):
        """
        :param in string menu_name: name used to create the menu from :func:`MenuBar.add_menu`.
        :param in Action menu_action: :class:`Action.Action` object to bind to the menu.
        """
        dict_name = menu_name.strip('&')
        self.menus[dict_name].addAction(menu_action)

