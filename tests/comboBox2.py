#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui


class Model(QtCore.QAbstractListModel):
    def __init__(self, *args, **kwargs):
        QtCore.QAbstractListModel.__init__(self, *args, **kwargs)
        self.items = []

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid() is True:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.items[index.row()])
            elif role == QtCore.Qt.ItemDataRole:
                return QtCore.QVariant(self.items[index.row()])
        return QtCore.QVariant()

    def itemsAdded(self, items):
        # insert items into their sorted position
        items = sorted(items)
        row = 0
        while row < len(self.items) and len(items) > 0:
            if items[0] < self.items[row]:
                self.beginInsertRows(QtCore.QModelIndex(), row, row)
                self.items.insert(row, items.pop(0))
                self.endInsertRows()
                row += 1
            row += 1
        # add remaining items to end of the list
        if len(items) > 0:
            self.beginInsertRows(
                QtCore.QModelIndex(),
                len(self.items),
                len(self.items) + len(items) - 1
            )
            self.items.extend(items)
            self.endInsertRows()

    def itemsRemoved(self, items):
        # remove items from the list
        for item in items:
            for row in range(0, len(self.items)):
                if self.items[row] == item:
                    self.beginRemoveRows(QtCore.QModelIndex(), row, row)
                    self.items.pop(row)
                    self.endRemoveRows()
                    break


def main():
    app = QtGui.QApplication([])
    w = QtGui.QWidget()
    w.resize(300, 200)
    layout = QtGui.QVBoxLayout()

    model = Model()
    model.itemsAdded(['a', 'b', 'd', 'e'])

    combobox = QtGui.QComboBox()
    combobox.setModel(model)
    combobox.setCurrentIndex(3)
    layout.addWidget(combobox)

    def insertC(self):
        model.itemsAdded('c')

    def removeC(self):
        model.itemsRemoved('c')

    buttonInsert = QtGui.QPushButton('Insert "c"')
    buttonInsert.clicked.connect(insertC)
    layout.addWidget(buttonInsert)

    buttonRemove = QtGui.QPushButton('Remove "c"')
    buttonRemove.clicked.connect(removeC)
    layout.addWidget(buttonRemove)

    w.setLayout(layout)
    w.show()
    app.exec_()

if __name__ == '__main__':
    main()
