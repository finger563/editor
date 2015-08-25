'''
https://forum.qt.io/topic/8746/solved-slide-animation-and-layout
'''
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
        #self.layout.setContentsMargins(1,1,1,1)
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
        #self.layout.setContentsMargins(1,1,1,1)
        self.setLayout(self.layout)

        self.connect(self.toggleButton, QtCore.SIGNAL('clicked()'), self.toggle)
        self.displayed = True
        self.firstRun = True

    def toggle(self):
        self.hideAnimation = QtCore.QPropertyAnimation(self.dashboard, "geometry")

        self.hideAnimation.setDuration(300)

        if self.firstRun:
            self.firstRun = False
            self.dw = self.dashboard.geometry().width()
            self.dh = self.dashboard.geometry().height()

        TL_y = 0
        BR_y = self.dh

        if self.displayed:
            TL_x = self.dw - 100
            BR_x = 2*self.dw - 100
        else:
            TL_x = 0
            BR_x = self.dw
        self.displayed = not self.displayed

        self.dashboard.startGeometry = QtCore.QRect(self.dashboard.geometry())
        self.dashboard.endGeometry = QtCore.QRect(
            TL_x, TL_y,
            BR_x, BR_y
        )

        self.hideAnimation.setStartValue(self.dashboard.startGeometry)
        self.hideAnimation.setEndValue(self.dashboard.endGeometry)
        self.hideAnimation.start()

if __name__ == "__main__":
    main = MainWindow()
    main.show()
    sys.exit(application.exec_())
