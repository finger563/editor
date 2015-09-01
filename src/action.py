"""
Action for the Meta-Model Editor

This program provides an API for 
library code to add actions
to the GUI for use in the viewer, menubar, etc.
"""

from PyQt4 import QtCore
from PyQt4 import QtGui
from collections import OrderedDict

class Action(QtGui.QAction):
    def __init__(self, icon_file, text, parent):
        super(Action, self).__init__(QtGui.QIcon(icon_file), text, parent)

def action_init(self):
    self.actions = {}

def action_create(self, action_name, icon, title, actionFunc, tooltip, shortcut):
    self.actions[action_name] = Action( icon, title, self)
    if tooltip: self.actions[action_name].setStatusTip(tooltip)
    if shortcut: self.actions[action_name].setShortcut(shortcut)
    self.actions[action_name].triggered.connect(actionFunc)
