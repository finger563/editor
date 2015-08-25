#!/usr/bin/env python
import sys

from PyQt4 import QtGui, QtCore

application = QtGui.QApplication(sys.argv)

class Dashboard(QtGui.QWidget):

    """ Dashboard to slide up and down on request. """

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        
        self.pix = QtGui.QPixmap("icons/model/Client.png")
        self.label = QtGui.QLabel(self)
        self.label.setPixmap(self.pix)
        
        self.layout = QtGui.QHBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.setContentsMargins(1,1,1,1)
        self.layout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.setLayout(self.layout)

class MainWindow(QtGui.QWidget):
    """ Main Window hosting button and dashboard"""
    def __init__(self):
        QtGui.QWidget.__init__(self)
    
        self.dashboard = Dashboard(self)
        self.toggleButton = QtGui.QPushButton(QtCore.QString("Open Dashboard"))
        self.toggleButton.setMinimumHeight(27)
        
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.dashboard)
        self.layout.addWidget(self.toggleButton)
        self.layout.setContentsMargins(1,1,1,1)
        self.layout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.setLayout(self.layout)
        
        self.connect(self.toggleButton, QtCore.SIGNAL('clicked()'), self.toggle)

    def toggle(self):

        self.hideAnimation = QtCore.QPropertyAnimation(self.dashboard, "geometry")
        self.parentHideAnimation = QtCore.QPropertyAnimation(self, "geometry")
        self.hideAnimation.setDuration(300)
        self.parentHideAnimation.setDuration(300)
        self.dashboard.startGeometry = QtCore.QRect(self.dashboard.geometry())
        self.startGeometry = QtCore.QRect(self.geometry())
        self.dashboard.endGeometry = QtCore.QRect(0,self.dashboard.geometry().height(),self.dashboard.geometry().width(), 0)
        self.endGeometry = QtCore.QRect(self.geometry().x(),
                                        self.geometry().y() + self.dashboard.geometry().height(),
                                        self.dashboard.width(),
                                        self.toggleButton.geometry().height())
        self.hideAnimation.setStartValue(self.dashboard.startGeometry)
        self.parentHideAnimation.setStartValue(self.startGeometry)
        self.hideAnimation.setEndValue(self.dashboard.endGeometry)
        self.parentHideAnimation.setEndValue(self.endGeometry)
        self.hideAnimation.start()
        self.parentHideAnimation.start()

if __name__ == "__main__":
    main = MainWindow()
    main.show()
    sys.exit(application.exec_())
