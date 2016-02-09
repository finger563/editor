# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Mon Feb  8 11:49:41 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1525, 1203)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.mainSplitter = QtGui.QSplitter(self.centralWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainSplitter.sizePolicy().hasHeightForWidth())
        self.mainSplitter.setSizePolicy(sizePolicy)
        self.mainSplitter.setOrientation(QtCore.Qt.Vertical)
        self.mainSplitter.setObjectName(_fromUtf8("mainSplitter"))
        self.modelSplitter = QtGui.QSplitter(self.mainSplitter)
        self.modelSplitter.setAutoFillBackground(False)
        self.modelSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.modelSplitter.setObjectName(_fromUtf8("modelSplitter"))
        self.treeView = QtGui.QTreeView(self.modelSplitter)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.setAcceptDrops(True)
        self.treeView.setDragEnabled(True)
        self.treeView.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.treeView.setRootIsDecorated(True)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setHeaderHidden(True)
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.tabbedModelView = TabbedModelViewer(self.modelSplitter)
        self.tabbedModelView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tabbedModelView.setTabPosition(QtGui.QTabWidget.North)
        self.tabbedModelView.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabbedModelView.setElideMode(QtCore.Qt.ElideNone)
        self.tabbedModelView.setTabsClosable(True)
        self.tabbedModelView.setMovable(True)
        self.tabbedModelView.setObjectName(_fromUtf8("tabbedModelView"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.modelView = QtGui.QGraphicsView(self.tab)
        self.modelView.setDragMode(QtGui.QGraphicsView.NoDrag)
        self.modelView.setObjectName(_fromUtf8("modelView"))
        self.verticalLayout_2.addWidget(self.modelView)
        self.tabbedModelView.addTab(self.tab, _fromUtf8(""))
        self.outputWidget = QtGui.QTabWidget(self.mainSplitter)
        self.outputWidget.setObjectName(_fromUtf8("outputWidget"))
        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName(_fromUtf8("tab_5"))
        self.outputWidget.addTab(self.tab_5, _fromUtf8(""))
        self.verticalLayout.addWidget(self.mainSplitter)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1525, 31))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menuEditor = QtGui.QMenu(self.menuBar)
        self.menuEditor.setObjectName(_fromUtf8("menuEditor"))
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtGui.QToolBar(MainWindow)
        self.mainToolBar.setObjectName(_fromUtf8("mainToolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MainWindow.setStatusBar(self.statusBar)
        self.pluginToolBar = QtGui.QToolBar(MainWindow)
        self.pluginToolBar.setObjectName(_fromUtf8("pluginToolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.pluginToolBar)
        MainWindow.insertToolBarBreak(self.pluginToolBar)
        self.actionNew = QtGui.QAction(MainWindow)
        self.actionNew.setObjectName(_fromUtf8("actionNew"))
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.menuEditor.addAction(self.actionNew)
        self.menuEditor.addAction(self.actionOpen)
        self.menuEditor.addAction(self.actionSave)
        self.menuEditor.addAction(self.actionQuit)
        self.menuBar.addAction(self.menuEditor.menuAction())
        self.mainToolBar.addAction(self.actionQuit)
        self.mainToolBar.addAction(self.actionNew)
        self.mainToolBar.addAction(self.actionOpen)
        self.mainToolBar.addAction(self.actionSave)

        self.retranslateUi(MainWindow)
        self.tabbedModelView.setCurrentIndex(0)
        self.outputWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.tabbedModelView, QtCore.SIGNAL(_fromUtf8("tabCloseRequested(int)")), self.tabbedModelView.onTabClose)
        QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.tabbedModelView.setTabText(self.tabbedModelView.indexOf(self.tab), _translate("MainWindow", "Tab 1", None))
        self.outputWidget.setTabText(self.outputWidget.indexOf(self.tab_5), _translate("MainWindow", "Tab 1", None))
        self.menuEditor.setTitle(_translate("MainWindow", "File", None))
        self.pluginToolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.actionNew.setText(_translate("MainWindow", "New", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionSave.setText(_translate("MainWindow", "Save", None))
        self.actionQuit.setText(_translate("MainWindow", "Quit", None))

from tabbedmodelviewer import TabbedModelViewer
