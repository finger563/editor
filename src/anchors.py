"""
Anchors

These functions handle anchor
management for editor items

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: August 2015
"""

from PyQt4 import QtCore, QtGui

import math
def distance(p1, p2):
    p = p2 - p1
    return math.sqrt(p.x()*p.x() + p.y()*p.y())

def getClosestPoint(cp, pDict):
    minDist = -1
    closestPoint = None
    for k,p in pDict.iteritems():
        dist = distance(cp,p)
        if minDist == -1 or dist < minDist:
            minDist = dist
            closestPoint = k
    return closestPoint, minDist

def convertAnchorToQt(anchor_name):
    qtAnchor = None
    if anchor_name in ['top left']:
        qtAnchor = QtCore.Qt.TopLeftCorner
    elif anchor_name in ['top right']:
        qtAnchor = QtCore.Qt.TopRightCorner
    elif anchor_name in ['bottom left']:
        qtAnchor = QtCore.Qt.BottomLeftCorner
    elif anchor_name in ['bottom right']:
        qtAnchor = QtCore.Qt.BottomRightCorner
    elif anchor_name in ['center left']:
        qtAnchor = QtCore.Qt.AnchorLeft
    elif anchor_name in ['center right']:
        qtAnchor = QtCore.Qt.AnchorRight
    elif anchor_name in ['top center']:
        qtAnchor = QtCore.Qt.AnchorTop
    elif anchor_name in ['bottom center']:
        qtAnchor = QtCore.Qt.AnchorBottom
    return qtAnchor

class AnchorLayout(QtGui.QGraphicsAnchorLayout):
    def __init__(self, parent = None):
        super(AnchorLayout, self).__init__(parent)

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

        maxW = maxX - minX
        maxH = maxY - minY
        return QtCore.QSizeF(maxW,maxH)
