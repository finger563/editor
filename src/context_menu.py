"""
Context Menu for the Editor

This program provides an API for
library code to add context menus
to objects of certain types in the model
"""

from PyQt4 import QtGui

def context_menu_init(self):
    self.context_menus = {}

def context_menu_create(self, cm_name):
    self.context_menus[cm_name] = QtGui.QMenu()

def context_menu_add_action(self, cm_name, cm_action):
    self.context_menus[cm_name].addAction(cm_action)
