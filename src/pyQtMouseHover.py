#!/usr/local/bin/python

import os, sys
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MyView(QGraphicsView):
    def __init__(self):
        QGraphicsView.__init__(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.scene = QGraphicsScene(self)
        self.item = GraphicsWidget('item', 100, 50)
        self.widget = GraphicsWidget('widget', 100, 50)
        self.widget2 = GraphicsWidget('widget', 100, 50)

        self.columnLayout = QGraphicsLinearLayout(Qt.Vertical)
        self.columnLayout.addItem(self.item)
        self.columnLayout.addItem(self.widget)
        self.columnLayout.addItem(self.widget2)
        self.column = QGraphicsWidget()
        self.column.setLayout(self.columnLayout)

        self.item = GraphicsWidget('item', 100, 50)
        self.widget = GraphicsWidget('widget', 100, 50)
        self.widget2 = GraphicsWidget('widget', 100, 50)
        self.rowLayout = QGraphicsLinearLayout()
        self.rowLayout.addItem(self.item)
        self.rowLayout.addItem(self.widget)
        self.rowLayout.addItem(self.widget2)
        self.row = QGraphicsWidget()
        self.row.setLayout(self.rowLayout)

        self.anchorLayout = QGraphicsAnchorLayout()
        #self.anchorLayout.addCornerAnchors(self.column, Qt.TopRightCorner, self.row, Qt.BottomLeftCorner)
        self.anchorWidget = QGraphicsWidget()
        self.anchorWidget.setLayout(self.anchorLayout)
        self.anchorLayout.addAnchors(self.row,self.column, Qt.Vertical)
        #self.anchorLayout.addAnchor(self.row, Qt.AnchorTop, self.column, Qt.AnchorBottom)
        #self.anchorLayout.addAnchor(self.row, Qt.AnchorRight, self.column, Qt.AnchorLeft)

        self.scene.addItem(self.anchorWidget)
        self.setScene(self.scene)

class GraphicsItem(QGraphicsItem):
    def __init__(self, name, width, height):
        QGraphicsItem.__init__(self)
        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)
        self.name = name
        self.__width = width
        self.__height = height

    def boundingRect(self): 
        return QRectF(0, 0, self.__width, self.__height)

    def hoverEnterEvent(self, event):
        self.__printGeometryDetails()

    def paint(self, painter, option, widget):
        bgRect = self.boundingRect()
        painter.drawRects(bgRect)
        painter.fillRect(bgRect, QColor('blue'))

    def __printGeometryDetails(self):
        print self.name
        print '  pos (%.0f, %0.0f)' % (self.pos().x(), self.pos().y())
        print '  boundingRect (%.0f, %0.0f, %.0f, %0.0f)' % (self.boundingRect().x(), self.boundingRect().y(), self.boundingRect().width(), self.boundingRect().height())

class GraphicsWidget(QGraphicsWidget):
    def __init__(self, name, width, height):
        QGraphicsWidget.__init__(self)
        self.setAcceptHoverEvents(True)
        self.name = name
        self.resize(width, height)

    def hoverEnterEvent(self, event):
        self.__printGeometryDetails()

    def paint(self, painter, option, widget):
        bgRect = self.boundingRect()
        painter.drawRects(bgRect)
        painter.fillRect(bgRect, QColor('red'))

    def __printGeometryDetails(self):
        print self.name
        print '  pos (%.0f, %0.0f)' % (self.pos().x(), self.pos().y())
        print '  boundingRect (%.0f, %0.0f, %.0f, %0.0f)' % (self.boundingRect().x(), self.boundingRect().y(), self.boundingRect().width(), self.boundingRect().height())
        print '  geometry (%.0f, %0.0f, %.0f, %0.0f)' % (self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height())
        print '  rect (%.0f, %0.0f, %.0f, %0.0f)' % (self.rect().x(), self.rect().y(), self.rect().width(), self.rect().height())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = MyView()
    view.setGeometry(600, 100, 400, 370)
    view.show()
    sys.exit(app.exec_())
