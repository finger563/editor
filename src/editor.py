#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Meta-Model Editor 

This program allows users to operate 
on meta-models and models using loadable
libraries to perform meta-model specific
operations such as generation, analysis,
and deployment.

author: William Emfinger
website: github.com/finger563/editor 
last edited: July 2015
"""

from PyQt4 import QtCore
from PyQt4 import QtGui

from menubar import MenuBar
from action import Action
from worker import Worker

class Editor(QtGui.QMainWindow):

    def __init__(self):
        super(Editor, self).__init__()
        self.init_ui()

    def init_ui(self):

        exitAction = Action('icons/toolbar/stop.png', '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.menus = {}
        self.menubar = self.menuBar()
        self.menubar_add_menu('&File')
        self.menu_add_action('&File',exitAction)

        self.toolbars = {}
        self.toolbar_create("test1")
        self.toolbar_add_action("test1",exitAction)
        self.toolbar_create("test2")
        self.toolbar_add_action("test2",exitAction)

        self.show()

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
        :param in Action menu_action: :class:`Action.Action` object to bind to the menu.
        """
        dict_name = menu_name.strip('&')
        if dict_name in self.menus:
            self.menus[dict_name].addAction(menu_action)


    def toolbar_create(self, tb_name):
        """
        :param in string tb_name: name of the toolbar
        """
        if tb_name not in self.toolbars:
            self.toolbars[tb_name] = self.addToolBar(tb_name)

    def toolbar_add_action(self, tb_name, tb_action):
        """
        :param in string tb_name: name used to create the toolbar from :func:`Editor.toolbar_create`.
        :param in Action tb_action: :class:`Action.Action` object to bind to the toolbar.
        """
        if tb_name in self.toolbars:
            self.toolbars[tb_name].addAction(tb_action)

    def toolbar_remove(self, tb_name):
        pass

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    editor = Editor()
    sys.exit(app.exec_())
