"""
Layout

These functions allow for easy creation 
and modifications of layouts.

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: August 2015
"""

from PyQt4 import QtCore, QtGui

from anchors import convertAnchorToQt, AnchorLayout

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
        new_layout = AnchorLayout()
    return new_layout

def layout_add(layout, style, item,
               gr = 0, gc = 0,
               anchor_item = None, item_ap = None, anchor_ap = None ):
    if style in ['grid']:
        layout.addItem(item, gr, gc)
    elif style in ['anchor']:
        if isinstance(item_ap,QtCore.Qt.Corner) and\
           isinstance(anchor_ap,QtCore.Qt.Corner):
            layout.addCornerAnchors(item, item_ap,
                                    anchor_item, anchor_ap)
        elif isinstance(item_ap, QtCore.Qt.AnchorPoint) and\
        isinstance(anchor_ap, QtCore.Qt.AnchorPoint):
            layout.addAnchor(item, item_ap,
                             anchor_item, anchor_ap)
    else:
        layout.addItem(item)
    
def layout_remove(layout, style, item):
    if style in ['grid', 'anchor', 'vertical', 'horizontal']:
        for i in range(layout.count()):
            if item == layout.itemAt(i):
                layout.removeAt(i)
                break

def layout_move(old_layout, new_layout, new_style):
    grid_row = 0
    for i in range(0,old_layout.count()):
        item = old_layout.itemAt(0)
        old_layout.removeAt(0)
        if new_style in ['grid']:
            new_layout.addItem(item, grid_row, grid_row)
            grid_row += 1
        elif new_style in ['anchor']:
            if new_layout.count():
                layout_add(new_layout, new_style,
                           item,
                           item_ap = convertAnchorToQt('center left'),
                           anchor_item = new_layout.itemAt(new_layout.count()-1),
                           anchor_ap = convertAnchorToQt('center right'))
            else:
                layout_add(new_layout, new_style,
                           item,
                           item_ap = convertAnchorToQt('top left'),
                           anchor_item = new_layout,
                           anchor_ap = QtCore.Qt.TopLeftCorner)
        else:
            new_layout.addItem(item)
