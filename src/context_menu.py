"""
Context Menu for the Editor

This program provides an API for
library code to add context menus
to objects of certain types in the model
"""

__author__ = "William Emfinger"
__copyright__ = "Copyright 2016, ROSMOD"
__credits__ = ["William Emfinger", "Pranav Srinivas Kumar"]
__license__ = "GPL"
__version__ = "0.4"
__maintainer__ = "William Emfinger"
__email__ = "emfinger@isis.vanderbilt.edu"
__status__ = "Production"

from PyQt4 import QtGui

def context_menu_init(self):
    self.context_menus = {}

def context_menu_create(self, cm_name):
    self.context_menus[cm_name] = QtGui.QMenu()

def context_menu_add_action(self, cm_name, cm_action):
    self.context_menus[cm_name].addAction(cm_action)
