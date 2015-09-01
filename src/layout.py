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

    def boundingRect(self):
        return self.geometry()

    def sizeHint(self, which, constraint):
        geo = self.geometry()
        return QtCore.QSizeF(geo.width(), geo.height)

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
        self.removeItem(item)
        if self.count():
            d, a1_str, a2_str, ci = self.getClosestAnchors(item)
            a1 = convertAnchorToQt(a1_str)
            a2 = convertAnchorToQt(a2_str)
            if d > 0 and d < self.min_anchoring_dist:
                item.viewModel()['layout config'].value['anchor'] = (a2_str, ci, a1_str)
                if isinstance(a1,QtCore.Qt.Corner) and isinstance(a2,QtCore.Qt.Corner):
                    self.addCornerAnchors(item, a2,
                                            ci, a1)
                elif isinstance(a1, QtCore.Qt.AnchorPoint) and isinstance(a2, QtCore.Qt.AnchorPoint):
                    self.addAnchor(item, a2,
                                     ci, a1)
        else:
            item.viewModel()['layout config'].value['anchor'] = (a2_str, self, a1_str)
            self.addCornerAnchors(item, convertAnchorToQt('top left'),
                                  self, convertAnchorToQt('top left'))

    def updateItem(self, item):
        self.removeItem(item)
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

    def boundingRect(self):
        return self.geometry()

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

    def boundingRect(self):
        return self.geometry()

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

    def boundingRect(self):
        return self.geometry()

    def fromLayout(self, otherLayout):
        if not otherLayout:
            return
        for i in range(otherLayout.count()):
            item = otherLayout.itemAt(0)
            otherLayout.removeAt(0)
            self.addItem(item)

    def addItem(self,item):
        self.removeItem(item)
        if 'grid' not in item.viewModel()['layout config'].value:
            if 'name' in item.model().attributes:
                name = item['name'].value
            else:
                name = item.viewModel()['kind'].value
            gr, ok = QtGui.QInputDialog.getInteger(None,
                                                   "Item '{}' Row".format(name),
                                                   "Row:", 0, 0)
            if not ok: gr = -1
            gc, ok = QtGui.QInputDialog.getInteger(None,
                                                   "Item '{}' Column".format(name),
                                                   "Column:", 0, 0)
            if not ok: gc = -1
        else:
            gr,gc = item.viewModel()['layout config'].value['grid']
        if gc >= 0 and gr >= 0:
            super(GridLayout,self).addItem(item, gr, gc)
            item.viewModel()['layout config'].value['grid'] = (gr, gc)
        else:
            if item._original_pos:
                item.setPos(item._original_pos)
            else:
                item.delete()

    def updateItem(self, item):
        self.removeItem(item)
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
