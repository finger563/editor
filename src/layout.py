"""
Layout

These functions allow for easy creation 
and modifications of layouts.

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: August 2015
"""

from PyQt4 import QtCore, QtGui

from anchors import convertAnchorToQt, closestAnchors

class AnchorLayout(QtGui.QGraphicsAnchorLayout):

    min_anchoring_dist = 20
    edge_padding = 10
    item_spacing = 10
    
    def __init__(self, parent = None):
        super(AnchorLayout, self).__init__(parent)
        self.setSpacing(self.item_spacing)

    def sizeHint(self, which, constraint):
        maxW = 0
        maxH = 0
        minX = 0
        maxX = 0
        minY = 0
        maxY = 0
        for i in range(self.count()):
            item = self.itemAt(i)
            geo = item.geometry()
            width = geo.width()
            height = geo.height()
            minX = min(minX,geo.x())
            minY = min(minY,geo.y())
            maxX = max(maxX,geo.x() + width)
            maxY = max(maxY,geo.y() + height)
        if minX < 0 or minY < 0:
            for i in range(self.count()):
                item = self.itemAt(i)
                geo = item.geometry()
                newx = geo.x() - minX
                newy = geo.y() - minY
                item.setPos(newx,newy)
        maxW = maxX - minX
        maxH = maxY - minY
        return QtCore.QSizeF(maxW + self.edge_padding,
                             maxH + self.edge_padding)

    def updateGeometry(self):
        super(AnchorLayout,self).updateGeometry()

    def getClosestAnchors(self, newItem):
        minDist = -1
        anchor1 = None
        anchor2 = None
        closestItem = None
        if newItem:
            for i in range(self.count()):
                item = self.itemAt(i)
                if item != newItem:
                    dist, a1, a2 = closestAnchors(item,newItem)
                    if minDist == -1 or dist < minDist:
                        minDist = dist
                        anchor1, anchor2 = a1, a2
                        closestItem = item
        return abs(minDist), anchor1, anchor2, closestItem

    def addItem(self, item):
        if self.count():
            d, a1, a2, ci = self.getClosestAnchors(item)
            a1 = convertAnchorToQt(a1)
            a2 = convertAnchorToQt(a2)
            if d > 0 and d < self.min_anchoring_dist:
                if isinstance(a1,QtCore.Qt.Corner) and isinstance(a2,QtCore.Qt.Corner):
                    self.addCornerAnchors(item, a2,
                                            ci, a1)
                elif isinstance(a1, QtCore.Qt.AnchorPoint) and isinstance(a2, QtCore.Qt.AnchorPoint):
                    self.addAnchor(item, a2,
                                     ci, a1)
        else:
            self.addCornerAnchors(item, convertAnchorToQt('top left'),
                                  self, convertAnchorToQt('top left'))

    def updateItem(self, item):
        self.addItem(item)

    def removeItem(self, item):
        for i in range(self.count()):
            if item == self.itemAt(i):
                self.removeAt(i)
                break

    def fromLayout(self, otherLayout):
        if not otherLayout:
            return
        for i in range(otherLayout.count()):
            item = otherLayout.itemAt(0)
            otherLayout.removeAt(0)
            self.addItem(item)

class HorizontalLayout(QtGui.QGraphicsLinearLayout):
    def __init__(self):
        super(HorizontalLayout, self).__init__()

    def fromLayout(self, otherLayout):
        if not otherLayout:
            return
        for i in range(otherLayout.count()):
            item = otherLayout.itemAt(0)
            otherLayout.removeAt(0)
            self.addItem(item)

    def updateItem(self, item):
        item.setPos(item._original_pos)
            
class VerticalLayout(QtGui.QGraphicsLinearLayout):
    def __init__(self):
        super(VerticalLayout, self).__init__(QtCore.Qt.Vertical)

    def fromLayout(self, otherLayout):
        if not otherLayout:
            return
        for i in range(otherLayout.count()):
            item = otherLayout.itemAt(0)
            otherLayout.removeAt(0)
            self.addItem(item)
            
    def updateItem(self, item):
        item.setPos(item._original_pos)
            
class GridLayout(QtGui.QGraphicsGridLayout):
    def __init__(self):
        super(GridLayout,self).__init__()

    def fromLayout(self, otherLayout):
        if not otherLayout:
            return
        for i in range(otherLayout.count()):
            item = otherLayout.itemAt(0)
            otherLayout.removeAt(0)
            self.addItem(item)

    def addItem(self,item):
        gr, ok = QtGui.QInputDialog.getInteger(None,
                                               "Item '{}' Row".format(item['kind'].value),
                                               "Row:", 0, 0)
        if not ok:
            gr = self.count()
        gc, ok = QtGui.QInputDialog.getInteger(None,
                                               "Item '{}' Column".format(item['kind'].value),
                                               "Column:", 0, 0)
        if not ok:
            gc = self.count()
        super(GridLayout,self).addItem(item, gr, gc)

    def updateItem(self, item):
        self.addItem(item)

    def removeItem(self, item):
        for i in range(self.count()):
            if item == self.itemAt(i):
                self.removeAt(i)
                break

def layout_create(style):
    new_layout = None
    if style in ['horizontal']:
        new_layout = HorizontalLayout()
    elif style in ['vertical']:
        new_layout = VerticalLayout()
    elif style in ['grid']:
        new_layout = GridLayout()
    elif style in ['anchor']:
        new_layout = AnchorLayout()
    return new_layout
