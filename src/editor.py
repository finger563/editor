#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This program allows users to operate
on meta-models and models using loadable
libraries to perform meta-model specific
operations such as generation, analysis,
and deployment.
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
from collections import OrderedDict

from action import\
    Action

from editor_widget import\
    TabbedEditor, EditorView

from item_model import\
    ItemModel

from meta import\
    MetaModel

from view_model import\
    ViewModel

from tree_view import\
    TreeView,\
    SortFilterProxyModel

from output import\
    TabbedOutputWidget

# TODO: Need to close all related widgets when an item is removed from
#       the model

# TODO: Refactor editor so that it the meta-model is contained
#       separately and merely invoked to get the root object for the
#       editor, e.g. meta-meta-root = Model(), meta-view-root =
#       ViewModel(), etc.

# TODO: Refactor ContextMenus and such so that they query on the
#       meta-model instead of directly querying the children data
#       structure.

# TODO: Need to be able to load multiple models and compose them
#       together; e.g if two people are working on a large model and
#       want to separately make packages or components or hardwares.
#       This would be useful for splitting out relevant parts of the
#       model and reusing it as a library, e.g. the cluster hardware
#       model would be a good example.  To do this we need to solve
#       the issues of meta-model conflicts and model composition (need
#       to figure out which one is root and where the other 'root'
#       goes.
#
#       Perhaps make the loaded model read-only?

# TODO: possibly change serialization to use dicts?  I.e. convert all
#       models into dicts before serializing?  This would still allow
#       object references (by having the value of the pointer be the
#       object's key into the dict; but would also allow lookups into
#       deserialized data and storage of meta-data (e.g.  UUID for
#       meta-model/version number: import uuid)

# TODO: Figure out how to update the meta-model without completely
#       losing the edits to existing models if possible.  Perhaps just
#       allow loading simultaneously the model + meta-model; and
#       attempting to resolve model changes when meta-model edits are
#       performed.

# TODO: Need to look further into monkeypatching (adding or
#       overwriting instance methods) and how it relates to pickling.
#       Need to make sure these objects maintain consistency when
#       being (de-)serialized.  This is especially important for
#       pointers, their attributes, their constraints, and their
#       options.


class Editor(QtGui.QMainWindow):
    '''The main editor class, which enables creating, loading, editing,
    and saving of models, meta-models, and view-models.

    Models are saved as \*.model files and contain the metamodel they
    were created with.

    Meta-models are saved as \*.meta files and can be used to create
    new models.

    View-models are saved as \*.view files and are automatically
    loaded as <Model Type>.view for each model that is opened in the
    visualizer.

    '''

    '''
    Models the editor is designed to load/edit/save
    All inherit at some point from the original base model classes
    Defined in meta.py
    '''
    editor_modes = ['Model', 'Meta Model', 'View Model']

    # Ways the tree view can filter the model (based on Meta-Type or Name)
    filter_roles = OrderedDict({
        'Meta': ItemModel.filter_meta_role,
        'Name': ItemModel.filter_data_role
    })

    def __init__(self):
        super(Editor, self).__init__()

        # Set up the editor mode
        self.editor_mode = self.editor_modes[1]
        self.filter_role = self.filter_roles['Meta']

        self.init_ui()
        self.clearModels()

        self.setWindowIcon(QtGui.QIcon('icons/editor.png'))

    def init_ui(self):
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setStyleSheet('''QToolTip {
                           background-color: black;
                           color: white;
                           border: black solid 1px
                           }''')
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Editor')

        # Create the actions for the program
        exitAction = Action('icons/toolbar/stop.png', 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        # note that this will call closeEvent
        exitAction.triggered.connect(self.close)

        newAction = Action('icons/toolbar/new.png', 'New', self)
        newAction.setStatusTip('New.')
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.newModel)

        openAction = Action('icons/toolbar/open.png', 'Open', self)
        openAction.setStatusTip('Open.')
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.openModel)

        saveAction = Action('icons/toolbar/save.png', 'Save', self)
        saveAction.setStatusTip('Save.')
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveModel)

        # Create the widgets for the program (embeddable in the
        # toolbar or elsewhere)
        self.mode_selector = QtGui.QComboBox(self)
        self.mode_selector.addItems(self.editor_modes)
        self.mode_selector.setCurrentIndex(
            self.editor_modes.index(self.editor_mode)
        )
        self.mode_selector.currentIndexChanged.connect(self.changeMode)

        # Set up the Menus for the program
        self.menubar_init()
        self.menubar_add_menu('&File')
        self.menu_add_action('&File', exitAction)
        self.menu_add_action('&File', newAction)
        self.menu_add_action('&File', openAction)
        self.menu_add_action('&File', saveAction)

        # Set up the toolbars for the program
        self.toolbar_init()
        self.toolbar_create('toolbar1')
        self.toolbar_add_action('toolbar1', exitAction)
        self.toolbar_add_action('toolbar1', newAction)
        self.toolbar_add_action('toolbar1', openAction)
        self.toolbar_add_action('toolbar1', saveAction)
        self.toolbar_add_widget('toolbar1', self.mode_selector)

        # Set up the Tree View Widget
        self.tree_view = TreeView()
        self.tree_view.setSortingEnabled(False)
        self.tree_view.activated.connect(self.openModelView)
        # don't want the tree collapsing when we open views
        self.tree_view.setExpandsOnDoubleClick(False)

        # Set up filtering on the tree_view
        self.filter_widget = QtGui.QWidget()
        self.filter_hbox = QtGui.QHBoxLayout()
        self.filter_label = QtGui.QLabel('Filter:')
        self.filter_type = QtGui.QComboBox(self)
        self.filter_type.addItems(self.filter_roles.keys())
        self.filter_type.setCurrentIndex(0)
        self.filter_type.currentIndexChanged.connect(self.changeFilter)
        self.filter_hbox.addWidget(self.filter_label)
        self.filter_hbox.addWidget(self.filter_type)
        self.filter_widget.setLayout(self.filter_hbox)
        self.filter_edit = QtGui.QLineEdit()

        # Set up the navigator (tree viewer + filter)
        self.navigator = QtGui.QWidget()
        self.navigator_vbox = QtGui.QVBoxLayout()
        self.navigator_vbox.addWidget(self.filter_widget)
        self.navigator_vbox.addWidget(self.filter_edit)
        self.navigator_vbox.addWidget(self.tree_view)
        self.navigator.setLayout(self.navigator_vbox)

        # Create the Visualizer
        self.tabbedEditorWidget = TabbedEditor(self)
        self.openEditorTabs = {}

        # Split the main part into visualizer and tree_view
        self.splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter1.addWidget(self.navigator)
        self.splitter1.addWidget(self.tabbedEditorWidget)
        self.splitter1.setSizes([self.geometry().width()/4.0, 3.0 *
                                 self.geometry().width()/4.0])

        # Set up the tabbed output viewer
        self.tabbedOutput = TabbedOutputWidget(self)

        # Split the Editor to show output
        self.splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.addWidget(self.tabbedOutput)
        self.splitter2.setSizes([4.0 * self.geometry().height()/5.0,
                                 self.geometry().height()/5.0])

        # Set the central widget of the application
        self.setCentralWidget(self.splitter2)

        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def clearModels(self):
        '''Clears all model data from the editor.'''
        self.META = None
        self.model = None
        self.proxy_model = None
        self.tree_view.reset()
        self.tree_view.setModel(None)

    def clearViewer(self):
        '''Close all visualizer views.'''
        self.openEditorTabs = {}
        self.tabbedEditorWidget.clear()

    def changeFilter(self, index):
        '''Event callback for when the user changes the filter type for the
        navigator.
        '''
        text = str(self.filter_type.currentText())
        self.filter_role = self.filter_roles[text]
        if self.model and self.proxy_model:
            self.proxy_model.setFilterRole(self.filter_role)
            # self.proxy_model.invalidate()

    def changeMode(self, index):
        '''Event callback for when the user changes the editor mode.'''
        text = str(self.mode_selector.currentText())
        if text != self.editor_mode:
            self.editor_mode = text
            self.clearModels()
            self.clearViewer()

    def openModelView(self, modelIndex):
        '''Event callback for when the user double-clicks on a model item in
        the tree-viewer.  Sends the model item to the visualizer and
        creates a new EditorView for it if one does not exist.

        :param in modelIndex: index into the AbstractItemModel which
            has been selected for viewing.

        '''
        mi = self.proxy_model.mapToSource(modelIndex)
        item = self.model.getModel(mi)
        key = str(item.uuid)
        name = item.get_attribute('Name').scoped()
        if key not in self.openEditorTabs:
            ev = EditorView(self.tabbedEditorWidget)
            ev.setProxyModel(self.proxy_model)
            self.openEditorTabs[key] = ev
        else:
            ev = self.openEditorTabs[key]
        self.tabbedEditorWidget.addTab(ev, name)
        ev.init_ui(index=mi, fname=item.kind() + '.view')
        self.tabbedEditorWidget.setCurrentIndex(
            self.tabbedEditorWidget.indexOf(ev)
        )

    def newModel(self, event):
        '''Callback for creating a new (meta-, view-) model.'''
        self.clearModels()
        self.clearViewer()
        root = None
        if self.editor_mode == 'Model':
            fname = QtGui.QFileDialog.getOpenFileName(
                self,
                'Select Meta Model',
                '',
                'Meta Model Files (*.meta)',
                options=QtGui.QFileDialog.Options()
            )
            if fname:
                meta_root = self.open_model(fname)
                base = MetaModel.toMeta(meta_root)
                # meta_dict['__root__'] = base
                # self.META = meta_dict
                root = base()
        elif self.editor_mode == 'Meta Model':
            root = MetaModel()
            root['Name'] = 'New_Model'
        elif self.editor_mode == 'View Model':
            root = ViewModel()
            root['Name'] = 'New_View_Model'
        if root:
            self.load_model(root)

    def openModel(self, event):
        '''Callback to allow the user to select a model file based on the
        current mode of the editor.
        '''
        ftype = '{}'.format(self.editor_mode.lower().split()[0])
        fname = QtGui.QFileDialog.getOpenFileName(
            self,
            'Open {}'.format(self.editor_mode),
            '',
            '{} Files (*.{})'.format(self.editor_mode, ftype),
            options=QtGui.QFileDialog.Options()
        )
        if fname:
            self.clearModels()
            self.clearViewer()
            root = self.open_model(fname)
            self.load_model(root)

    def open_model(self, fname):
        '''Decodes a saved \*.{model, meta, view} file and loads it into the
        editor.
        '''
        import json
        with open(fname, 'r') as f:
            model_dict = json.loads(f.read())
            root = MetaModel.fromMeta(model_dict)
            print root().__dict__
            print root().row_count()
            return root()

    def load_model(self, model):
        '''
        :param in model: the root object of a model, which is loaded into
            the tree-viewer and proxy models
        '''

        # Set up the hidden Root model, with the 'model' object as its
        # only child
        root = MetaModel()
        root.children.set_cardinality({model.__class__: '1'})
        root.add_child(model)

        # Set up the proxy model for sorting/filtering
        self.proxy_model = SortFilterProxyModel(self)
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy_model.setSortRole(ItemModel.sort_role)
        self.proxy_model.setFilterRole(self.filter_role)

        # the model stores the reference to the model that is
        # currently being edited/viewed; this can be a regular model,
        # a view model, or even a meta-model.  All these models
        # inherit from the meta-metamodel so have the same interfaces
        # and can be interacted with in the same way
        self.model = ItemModel(root)
        # Link the actual model and the proxy model
        self.proxy_model.setSourceModel(self.model)
        self.filter_edit.textChanged.connect(self.proxy_model.setFilterRegExp)
        self.tree_view.setModel(self.proxy_model)
        self.proxy_model.rowsInserted.connect(self.tree_view.rowsInserted)
        self.tree_view.expandAll()

    def saveModel(self, event):
        '''Saves a model according to the current mode of the editor.'''
        import json
        ftype = '{}'.format(self.editor_mode.lower().split()[0])
        fname = QtGui.QFileDialog.getSaveFileName(
            self,
            'Save {}'.format(self.editor_mode),
            '',
            '{} Files (*.{})'.format(self.editor_mode, ftype),
            options=QtGui.QFileDialog.Options()
        )
        if fname:
            if fname[-len(ftype):] != ftype:
                fname += '.{}'.format(ftype)
            root = self.model.getModel(QtCore.QModelIndex())
            # the actual root is not displayed and is always a Model()
            root = root.children[0]
            modelDict = MetaModel.toDict(root)
            dictStr = json.dumps(modelDict, indent=4)
            with open(fname, 'w') as f:
                f.write(dictStr)
            return 0

    def closeEvent(self, event):
        event.accept()
        return
        reply = QtGui.QMessageBox.question(
            self, 'Quit',
            'Sure you want to quit?', QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    from menubar import \
        menubar_init, \
        menubar_add_menu, \
        menu_add_action

    from toolbar import \
        toolbar_init, \
        toolbar_create, \
        toolbar_add_action, \
        toolbar_add_widget, \
        toolbar_remove

    from action import \
        action_init, \
        action_create

    from context_menu import \
        context_menu_init, \
        context_menu_create, \
        context_menu_add_action

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    editor = Editor()
    sys.exit(app.exec_())
