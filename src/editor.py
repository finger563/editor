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

        exitAction = Action('exit.png', '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.menubar = MenuBar(self)
        self.menubar.add_menu('&File')
        self.menubar.add_action('&File',exitAction)

        self.show()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    editor = Editor()
    sys.exit(app.exec_())
