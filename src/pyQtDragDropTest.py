import sys
from PyQt4 import QtGui, QtCore

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.list_test = TestListWidget(self)
        self.setCentralWidget(self.list_test)

class TestListWidget(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(TestListWidget, self).__init__(parent)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.set_model_testdata()

    def set_model_testdata(self):
        for i in range(0, 4):
            item = QtGui.QListWidgetItem(self)
            item_widget = TestListItem("testitem %s" % i, self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)

class TestListItem(QtGui.QWidget):
    def __init__(self, name, parent=None):
        super(TestListItem, self).__init__(parent)
        item_name_label = QtGui.QLabel("Name:")
        item_name = QtGui.QLineEdit()
        item_name.setText(name)

        vert = QtGui.QVBoxLayout()
        vert.addWidget(item_name_label)
        vert.addWidget(item_name)
        self.setLayout(vert)

if __name__ == "__main__":
    app  = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    app.exec_()
