"""
Editor Widget 

These classes allow users to view
and edit models in the project in tabs.

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

        self.dragOver = False
        
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setAcceptDrops(True)
        self.image = QtGui.QGraphicsPixmapItem()
        self.image.setPixmap(QtGui.QPixmap(image))
        self.setCursor(QtCore.Qt.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            event.ignore()
            return
        self.setCursor(QtCore.Qt.ClosedHandCursor)
        #return QtGui.QGraphicsItem.mousePressEvent(self,event)

    def mouseMoveEvent(self, event):
        if QtCore.QLineF(QtCore.QPointF(event.screenPos()), QtCore.QPointF(event.buttonDownScreenPos(QtCore.Qt.LeftButton))).length() < QtGui.QApplication.startDragDistance():
            return

        drag = QtGui.QDrag(event.widget())
        mime = QtCore.QMimeData()
        drag.setMimeData(mime)

        drag.exec_()
        self.setCursor(QtCore.Qt.OpenHandCursor)

    def mouseReleaseEvent(self, event):
        self.setCursor(QtCore.Qt.OpenHandCursor)

    def dragEnterEvent(self, event):
        if event.mimeData().hasColor():
            event.setAccepted(True)
            self.dragOver = True
            self.update()
        else:
            event.setAccepted(False)

    def dragLeaveEvent(self, event):
        self.dragOver = False
        self.update()

    def dropEvent(self, event):
        self.dragOver = False
        if event.mimeData().hasColor():
            self.color = QtGui.QColor(event.mimeData().colorData())
        elif event.mimeData().hasImage():
            self.pixmap = QtGui.QPixmap(event.mimeData().imageData())

        self.update()
        
    def boundingRect(self):
        return self.image.boundingRect()
        
    def paint(self, painter, option, widget = None):
        self.image.paint(painter, option, widget)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        menu.addAction("object")
        menu.exec_(event.screenPos())

class EditorScene(QtGui.QGraphicsScene):
    def __init__(self, parent = None):
        super(EditorScene, self).__init__(parent)

    def dragMoveEvent(self, event):
        event.setAccepted(True)

    def dropEvent(self, event):
        # need to set position for the new object here!
        pass
        
class EditorWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(EditorWidget,self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.hbox = QtGui.QHBoxLayout(self)

        grview = QtGui.QGraphicsView(self)
        scene = EditorScene(self)
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
