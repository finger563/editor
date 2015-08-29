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

