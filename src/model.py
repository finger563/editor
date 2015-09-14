'''
blargh
'''

from PyQt4 import QtGui, QtCore

class customRole:
    TypeRole,
    SortRole,
    PosRole,
    InputsRole,
    ModputsRole,
    OutputsRole,
    ConnectionDestinationRole,
    PortType,
    PortDirection,
    PortNumber,
    ReadyRole = range(QtCore.Qt.UserRole,QtCore.Qt.UserRole+11)


class Model(QtCore.QAbstractItemModel):

    def __init__(self):
        super(Model, self).__init__()
        self.rootItem = None
        self.modelFactory = None
    
    def index(self, row, column, parent):
        pass

    def parent(self, index):
        pass

    def rowCount(self, parent):
        pass

    def columnCount(self, parent):
        pass

    def data(self, index, role):
        pass

    def setData(self, index, value, role = QtCore.Qt.EditRole):
        pass

    def dst(self, item):
        pass

    def references(self, index):
        pass

    def insertModel(self, _type, pos = QtCore.QPoint()):
        pass

    def insertConnection(self, a, b):
        pass

    def flags(self, index):
        pass

    def hasChildren(self, parent = QtCore.QModelIndex()):
        pass

    def headerData(self, section, orientation, role):
        pass

    def insertRows(self, row, count, parent = QtCore.QModelIndex(), pos = QtCore.QPoint(), _type = QtCore.QString()):
        pass

    def removeRows(self, items):
        pass

    def data2modelIndex(self, item):
        pass

    def updateModel(self, model):
        pass
