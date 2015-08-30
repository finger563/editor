"""
Graphics Items

These classes are custom items implementing
draw styles not natively found in qgraphics*items

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: August 2015
"""

from PyQt4 import QtCore
from PyQt4 import QtGui

class PushButton(QtGui.QPushButton):
    def paintEvent(self, event):
        tmp_text = self.text()
        self.setText(tmp_text.split('/')[-1])
        super(PushButton,self).paintEvent(event)
        self.setText(tmp_text)

class RoundRectItem(QtGui.QGraphicsRectItem):
    def __init__(self, x, y, w, h, xr = 0.1, yr = 0.1, parent = None):
        super(RoundRectItem, self).__init__(x,y,w,h,parent)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.xr = xr
        self.yr = yr

    # gotten from qt_graphicsItem_highlightSelected, qgraphicsitem.cpp : 7574
    def highlightSelected(item, painter, option):
        murect = painter.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
        if not murect.width() or not murect.height():
            return

        mbrect = painter.transform().mapRect(item.boundingRect())
        if min(mbrect.width(), mbrect.height()) < 1.0:
            return

        itemPenWidth = item.pen().widthF()
        
        pad = itemPenWidth / 2

        penWidth = 0 # cosmetic pen

        fgcolor = option.palette.windowText().color()
        bgcolor = QtGui.QColor(
            0 if fgcolor.red()   > 127 else 255,
            0 if fgcolor.green() > 127 else 255,
            0 if fgcolor.blue()  > 127 else 255)

        painter.setPen(QtGui.QPen(bgcolor, penWidth, QtCore.Qt.SolidLine));
        painter.setBrush(QtCore.Qt.NoBrush);
        painter.drawRect(item.boundingRect().adjusted(pad, pad, -pad, -pad));

        painter.setPen(QtGui.QPen(option.palette.windowText(), 0, QtCore.Qt.DashLine));
        painter.setBrush(QtCore.Qt.NoBrush);
        painter.drawRect(item.boundingRect().adjusted(pad, pad, -pad, -pad));

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen());
        painter.setBrush(self.brush());
        minR = min(self.rect().width()*self.xr, self.rect().height()*self.yr)
        painter.drawRoundedRect(self.rect(), minR, minR)
        if option.state & QtGui.QStyle.State_Selected:
            self.highlightSelected(painter, option)
