"""
Layout

These functions allow for easy creation 
and modifications of layouts.

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: August 2015
"""

from PyQt4 import QtCore, QtGui

def layout_create(style):
    new_layout = None
    if style in ['horizontal']:
        new_layout = QtGui.QGraphicsLinearLayout()
    elif style in ['vertical']:
        new_layout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical)
    elif style in ['grid']:
        grid_row = 0
        new_layout = QtGui.QGraphicsGridLayout()
    elif style in ['anchor']:
        new_layout = QtGui.QGraphicsAnchorLayout()
    return new_layout

def layout_add(layout, style, item,
               gr = 0, gc = 0,
               anchor_item = None, item_ap = None, anchor_ap = None ):
    if style in ['grid']:
        layout.addItem(item, gr, gc)
    elif style in ['anchor']:
        layout.addCornerAnchors(item, item_ap,
                                anchor_item, anchor_ap);
    else:
        layout.addItem(item)
    
def layout_remove(layout, style, item):
    if style in ['grid']:
        pass
    elif style in ['anchor']:
        pass
    else:
        layout.removeItem(item)

def layout_move(old_layout, new_layout, new_style):
    for i in range(0,old_layout.count()):
        item = old_layout.itemAt(0)
        old_layout.removeAt(0)
        if self['layout style'].value in ['grid']:
            new_layout.addItem(item, grid_row, 0)
            print "added {} to grid row {}, count {}".format(item,
                                                             grid_row+1,
                                                             new_layout.count())
            grid_row += 1
        elif self['layout style'].value in ['anchor']:
            new_layout.addCornerAnchors(item, QtCore.Qt.TopLeftCorner,
                                        new_layout, QtCore.Qt.TopLeftCorner);
        else:
            new_layout.addItem(item)
