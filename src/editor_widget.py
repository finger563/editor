#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Editor Widget 

These classes allow users to view
and edit models in the project.

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: July 2015
"""

from PyQt4 import QtCore
from PyQt4 import QtGui

class EditorObjectWidget(QtGui.QGraphicsItem):
    # NEED TO HANDLE MOUSE MOVE EVENTS LOOKING FOR ANCHOR POINTS IN PARENT
    # TO WHICH WE CAN ATTACH?
    def __init__(self,parent, image):
        super(EditorObjectWidget, self).__init__(parent)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setAcceptDrops(True)
        self.image = QtGui.QGraphicsPixmapItem()
        self.image.setPixmap(QtGui.QPixmap(image))

    def mousePressEvent(self, e):
        return QtGui.QGraphicsItem.mousePressEvent(self,e)

    def mouseMoveEvent(self, e):
        return QtGui.QGraphicsItem.mouseMoveEvent(self, e)

    def mouseReleaseEvent(self, e):
        items = [x for x in self.scene().items(e.scenePos()) if x != self]
        print items
        if items:
            self.setParentItem(items[0])
            self.setZValue(items[0].zValue()+1)
        return QtGui.QGraphicsItem.mouseReleaseEvent(self, e)

    def dragEnterEvent(self, e):
        e.accept()
        return QtGui.QGraphicsItem.dragEnterEvent(self, e)

    def dropEvent(self, e):
        print e.pos()
        e.setDropAction(QtCore.Qt.LinkAction)
        e.accept()
        return QtGui.QGraphicsItem.dropEvent(self, QDropEvent(QPoint(e.pos().x(), e.pos().y()), e.possibleActions(), e.mimeData(), e.buttons(), e.modifiers()))
        
    def boundingRect(self):
        return self.image.boundingRect()
        
    def paint(self, painter, option, widget):
        self.image.paint(painter, option, widget)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        menu.addAction("object")
        menu.exec_(event.screenPos())

class EditorWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(EditorWidget,self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.hbox = QtGui.QHBoxLayout(self)

        grview = QtGui.QGraphicsView(self)
        scene = QtGui.QGraphicsScene(self)
        test = EditorObjectWidget(None, 'icons/model/Hardware.png')
        test2 = EditorObjectWidget(test, 'icons/toolbar/generate.png')
        test3 = EditorObjectWidget(test, 'icons/toolbar/build.png')
        test4 = EditorObjectWidget(None, 'icons/model/Hardware.png')
        scene.addItem(test)
        scene.addItem(test4)
        matrix = QtGui.QMatrix()
        matrix.scale(0.5,0.5)
        grview.setMatrix(matrix)
        grview.setScene(scene)
        grview.setAcceptDrops(True)
        #grview.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        #grview.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        grview.show()

        self.hbox.addWidget(grview)
        self.setLayout(self.hbox)

        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        menu.addAction("sample")
        menu.exec_(event.globalPos())

class TabbedEditorWidget(QtGui.QTabWidget):
    def __init__(self, parent):
        super(TabbedEditorWidget, self).__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setUsesScrollButtons(True)

        self.tabCloseRequested.connect(self.onTabClose)

        newPage = EditorWidget(self)
        self.addTab(newPage, "test1")
        newPage = EditorWidget(self)
        self.addTab(newPage, "test2")
        
    def onTabClose(self,index):
        self.removeTab(index)
