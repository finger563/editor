'''
These classes are custom items implementing
draw styles not natively found in qgraphics*items
'''

__author__ = 'William Emfinger'
__copyright__ = 'Copyright 2016, ROSMOD'
__credits__ = ['William Emfinger', 'Pranav Srinivas Kumar']
__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'William Emfinger'
__email__ = 'emfinger@isis.vanderbilt.edu'
__status__ = 'Production'

from PyQt4 import QtCore
from PyQt4 import QtGui

class PushButton(QtGui.QPushButton):
    def paintEvent(self, event):
        tmp_text = self.text()
        self.setText(tmp_text.split('/')[-1])
        super(PushButton,self).paintEvent(event)
        self.setText(tmp_text)

def alignmentToQt(a):
    aq = a
    if a in ['left']:
        aq = QtCore.Qt.AlignLeft
    elif a in ['right']:
        aq = QtCore.Qt.AlignRight
    elif a in ['horizontal center']:
        aq = QtCore.Qt.AlignHCenter
    elif a in ['justify']:
        aq = QtCore.Qt.AlignJustify
    elif a in ['top']:
        aq = QtCore.Qt.AlignTop
    elif a in ['bottom']:
        aq = QtCore.Qt.AlignBottom
    elif a in ['vertical center']:
        aq = QtCore.Qt.AlignVCenter
    return aq

class TextItem(QtGui.QGraphicsTextItem):
    '''
    Acts as a label for a :class:`EditorItem`.  Extends :class:`QGraphicsTextItem` with
    more functionality for setting the alignment and position of the text relative to its
    parent :class:`EditorItem`.
    '''
    def __init__(self, text = '', parent = None, scene = None,
                 ha = QtCore.Qt.AlignLeft,
                 va = QtCore.Qt.AlignTop):
        super(TextItem, self).__init__(text, parent = parent, scene = scene)
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtGui.QGraphicsItem.ItemClipsToShape, False)
        self.setAlignment(ha, va)
        self.init()

    def init(self):
        self.updateGeometry()
        self.document().contentsChange.connect(self.updateGeometry)

    def setPos(self, pos_str, origin_pos, width, height):
        newpos = QtCore.QPointF()
        if 'right' in pos_str:
            newpos.setX( newpos.x() + width )
        elif 'left' in pos_str:
            newpos.setX( newpos.x() - self.boundingRect().width() )
        if 'top' in pos_str:
            newpos.setY( newpos.y() - self.boundingRect().height() )
        elif 'bottom' in pos_str:
            newpos.setY( newpos.y() + height )
        super(TextItem, self).setPos(newpos)

    def setAlignment(self, ha, va):
        self._ha = alignmentToQt(ha)
        self._va = alignmentToQt(va)
        _format = QtGui.QTextBlockFormat()
        _format.setAlignment(self._ha | self._va)
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.Document)
        cursor.mergeBlockFormat(_format)
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def updateGeometry(self):
        self.setTextWidth(-1)
        #self.setTextWidth(self.boundingRect().width())
        self.setAlignment(self._ha, self._va)

class RoundRectItem(QtGui.QGraphicsRectItem):
    '''
    Extends :class:`QGraphicsRectItem` to support drawing a rectangle with
    rounded edges.
    '''
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
