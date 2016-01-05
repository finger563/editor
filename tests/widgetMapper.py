#!/usr/bin/env python
#-*- coding:utf-8 -*-

#---------
# IMPORT
#---------
import sys

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt4 import QtGui, QtCore

#---------
# DEFINE
#---------
class MyItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        super(MyItemDelegate, self).__init__(parent)

    def setEditorData(self, editor, index):
        if type(editor) == QtGui.QCheckBox:
            checkState = int(index.data())
            editor.setChecked(checkState)

            return

        return super(MyItemDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if type(editor) == QtGui.QCheckBox:
            checkState = editor.isChecked()
            model.setData(index, str(int(checkState)))       

            return

        return super(MyItemDelegate, self).setModelData(editor, model, index)

class MyWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)

        self.labelRecord = QtGui.QLabel(self)

        self.pushButtonNext = QtGui.QPushButton(self)
        self.pushButtonNext.setText("Next!")
        self.pushButtonNext.clicked.connect(self.on_pushButtonNext_clicked)

        self.pushButtonPrevious = QtGui.QPushButton(self)
        self.pushButtonPrevious.setText("Previous!")
        self.pushButtonPrevious.clicked.connect(self.on_pushButtonPrevious_clicked)

        self.spacerItem = QtGui.QSpacerItem(
            40, 20,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum
        )

        self.layoutHorizontal = QtGui.QHBoxLayout()
        self.layoutHorizontal.addItem(self.spacerItem)
        self.layoutHorizontal.addWidget(self.pushButtonPrevious)
        self.layoutHorizontal.addWidget(self.pushButtonNext)

        self.labelProperty = QtGui.QLabel(self)
        self.labelProperty.setText("Property")

        self.labelType = QtGui.QLabel(self)
        self.labelType.setText("Type")

        self.checkBoxBool = QtGui.QCheckBox(self)
        self.checkBoxBool.setText("Bool")

        self.lineEditProperty  = QtGui.QLineEdit(self)
        self.lineEditType      = QtGui.QLineEdit(self)
        self.standardItemModel = QtGui.QStandardItemModel(self)
        self.itemDelegate      = MyItemDelegate(self)

        for rowNumber in range(3):
            items = []
            for columnNumber in range(3):
                itemData = "row: {0} column {1}".format(
                    rowNumber,
                    columnNumber 
                )

                item = QtGui.QStandardItem(
                    itemData
                    if columnNumber != 2
                    else str(rowNumber - rowNumber/2*2)
                )
                items.append(item)

            self.standardItemModel.appendRow(items)

        self.tableView = QtGui.QTableView(self)
        self.tableView.setModel(self.standardItemModel)

        self.dataWidgetMapper = QtGui.QDataWidgetMapper(self)
        self.dataWidgetMapper.setModel(self.standardItemModel)
        self.dataWidgetMapper.addMapping(self.lineEditProperty, 0)
        self.dataWidgetMapper.addMapping(self.lineEditType, 1)
        self.dataWidgetMapper.addMapping(self.checkBoxBool, 2)
        self.dataWidgetMapper.setItemDelegate(self.itemDelegate)
        self.dataWidgetMapper.currentIndexChanged.connect(self.on_dataWidgetMapper_currentIndexChanged)
        self.dataWidgetMapper.toFirst()

        self.layoutGrid = QtGui.QGridLayout(self)
        self.layoutGrid.addWidget(self.tableView, 0, 0, 1, 2)
        self.layoutGrid.addWidget(self.labelRecord, 1, 0, 1, 2)
        self.layoutGrid.addWidget(self.labelProperty, 2, 0, 1, 1)
        self.layoutGrid.addWidget(self.lineEditProperty, 2, 1, 1, 1)
        self.layoutGrid.addWidget(self.labelType, 3, 0, 1, 1)
        self.layoutGrid.addWidget(self.lineEditType, 3, 1, 1, 1)
        self.layoutGrid.addWidget(self.checkBoxBool, 4, 1, 1, 1)
        self.layoutGrid.addLayout(self.layoutHorizontal, 5, 0, 1, 2)

    @QtCore.pyqtSlot(int)
    def on_dataWidgetMapper_currentIndexChanged(self, index):
        self.labelRecord.setText("<b>Record {0}</b>".format(index))
        self.pushButtonPrevious.setDisabled(index == 0)
        self.pushButtonNext.setDisabled(index == self.standardItemModel.rowCount() - 1)

    @QtCore.pyqtSlot()
    def on_pushButtonNext_clicked(self):
        self.dataWidgetMapper.toNext()

    @QtCore.pyqtSlot()
    def on_pushButtonPrevious_clicked(self):
        self.dataWidgetMapper.toPrevious()

#---------
# MAIN
#---------
if __name__ == "__main__":    
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('MyWindow')

    main = MyWindow()
    main.setGeometry(0, 0, 333, 333)
    main.show()

    sys.exit(app.exec_())
