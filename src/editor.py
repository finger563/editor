#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Meta-Model Editor 

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
from PyQt4.QtCore import Qt

import copy
from collections import OrderedDict

from action import Action
from editor_widget import TabbedEditor, EditorView

from item_model import ItemModel, SortFilterProxyModel

from meta import Model, Pointer, Model_Attribute, Attribute, Children, get_children
from view_model import ViewModel

from tree_view import TreeView

from output import TabbedOutputWidget

# TODO: Need to be able to load multiple models and compose themn together; e.g if two people
#       are working on a large model and want to separately make packages or components or hardwares.
#       This would be useful for splitting out relevant parts of the model and reusing it as a library,
#       e.g. the cluster hardware model would be a good example.  To do this we need to solve the issues
#       of meta-model conflicts and model composition (need to figure out which one is root and where the
#       other 'root' goes.

# TODO: Allow for messages/services which are purely references to libarary/standard messages/services.
#       Perhaps just allow publishers/subscribers/clients/servers to point to messages/services which
#       are not in the model and are specified as a string just as they would be in the code?

# TODO: View-Models are incomplete and not usable; their attributes don't necessarily work and editing
#       a view model should probably require knowledge of the meta-model, so the meta-model should be 
#       loaded as well

# TODO: Figure out how to update the meta-model without completely losing the edits to existing models if
#       possible.  Perhaps just allow loading simultaneously the model + meta-model; and attempting to 
#       resolve model changes when meta-model edits are performed.

def convertModelToMeta(model):
    '''
    This function is used to create classes based on the editor's current model.
    It works on Model instances, which can have pointers, models, and model_attributes
    as children.  By converting the models in to named classes subclassing Model and adding
    named attributes subclassing Attribute it forms a new class structure which describes the
    meta model and which can be used to instantiate models.  

    Returns the class of the root type of the meta model
    '''

    allowed_kids = OrderedDict()
    attr_dict = OrderedDict()
    for obj in model.children:
        # These will be the available children_types of the class
        if type(obj) == Model:
            allowed_kids[convertModelToMeta(obj)] = obj['Cardinality']
        # These will be pointers to other classes
        elif type(obj) == Pointer:
            # TODO: Go through the children of 'model' who are POINTERS and add new children
            pass
        # These will be the attributes of the new class
        elif type(obj) == Model_Attribute:
            def attrInit(self):
                # TODO: Test to make sure that all possible attributes get workable values
                Attribute.__init__(self, obj['Kind'], Attribute.default_vals[obj['Kind']])
            new_attr = type(
                obj['Name'],
                (Attribute, object, ),
                {
                    '__init__' : attrInit,
                    'tooltip' : obj['Tooltip'],
                    'display' : obj['Display'],
                    'editable' : obj['Editable'],
                }
            )
            attr_dict[obj['Name']] = new_attr()

    # Define the init function inline here for the new class, make sure all attributes,
    # pointers, children, etc. are set up properly
    def modelInit(self, parent = None):
        Model.__init__(self, parent)
        self.attributes = OrderedDict()
        self.add_attribute('Name', 'string', '{}'.format(self.__class__.__name__))
        self.children = Children(allowed=allowed_kids.keys(), cardinality = allowed_kids)
        for name,attr in attr_dict.iteritems():
            self.set_attribute(name, attr)

    # TODO: Fix this so that everything is properly initialized:
    #       e.g. attributes, pointers, Children (_allowed), etc.
    new_type = type( 
        model['Name'], 
        (Model, object, ), 
        { 
            '__init__' : modelInit
        }
    )
    return new_type

class Editor(QtGui.QMainWindow):
    '''
    The main editor class, which enables creating, loading, editing, and saving of 
    models, meta-models, and view-models.  

    Models are saved as *.model files and contain the metamodel they were created with.

    Meta-models are saved as *.meta files and can be used to create new models.

    View-models are saved as *.view files and are automatically loaded as <Model Type>.view
    for each model that is opened in the visualizer.
    '''

    '''
    Models the editor is designed to load/edit/save
    All inherit at some point from the original base model classes
    Defined in meta.py
    '''
    editor_modes = ['Model','Meta Model','View Model']

    # Ways the tree view can filter the model (based on Meta-Type or Name)
    filter_types = ['Meta','Name']

    def __init__(self):
        super(Editor, self).__init__()

        # Set up the editor mode
        self.editor_mode = self.editor_modes[1]
        self.filter_mode = self.filter_types[0]

        self.init_ui()
        self.clearModels()
        #self.open_model('test_model.meta')
        #from test_model import TestModel
        #self.load_model(TestModel)

        self.setWindowIcon(QtGui.QIcon('icons/editor.png'))

    def init_ui(self):
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setStyleSheet('''QToolTip {
                           background-color: black;
                           color: white;
                           border: black solid 1px
                           }''')
        self.setGeometry(300,300,800,600)
        self.setWindowTitle('Editor')

        # Create the actions for the program
        exitAction = Action('icons/toolbar/stop.png', 'Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close) # note that this will call closeEvent

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

        # Create the widgets for the program (embeddable in the toolbar or elsewhere)
        self.mode_selector = QtGui.QComboBox(self)
        self.mode_selector.addItems(self.editor_modes)
        self.mode_selector.setCurrentIndex(self.editor_modes.index(self.editor_mode))
        self.mode_selector.currentIndexChanged.connect(self.changeMode)

        # Set up the Menus for the program
        self.menubar_init()
        self.menubar_add_menu('&File')
        self.menu_add_action('&File',exitAction)
        self.menu_add_action('&File',newAction)
        self.menu_add_action('&File',openAction)
        self.menu_add_action('&File',saveAction)

        # Set up the toolbars for the program
        self.toolbar_init()
        self.toolbar_create('toolbar1')
        self.toolbar_add_action('toolbar1',exitAction)
        self.toolbar_add_action('toolbar1',newAction)
        self.toolbar_add_action('toolbar1',openAction)
        self.toolbar_add_action('toolbar1',saveAction)
        self.toolbar_add_widget('toolbar1',self.mode_selector)

        # Set up the Tree View Widget
        self.tree_view = TreeView()
        self.tree_view.setSortingEnabled(False)
        self.tree_view.doubleClicked.connect(self.openModelView)
        self.tree_view.setExpandsOnDoubleClick(False) # don't want the tree collapsing when we open views

        # Set up filtering on the tree_view
        self.filter_widget = QtGui.QWidget()
        self.filter_hbox = QtGui.QHBoxLayout()
        self.filter_label = QtGui.QLabel('Filter:')
        self.filter_type = QtGui.QComboBox(self)
        self.filter_type.addItems(self.filter_types)
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
        self.splitter1.setSizes([self.geometry().x()/4.0, 3.0 * self.geometry().x()/4.0])

        # Set up the tabbed output viewer
        self.tabbedOutput = TabbedOutputWidget(self)

        # Split the Editor to show output
        self.splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.addWidget(self.tabbedOutput)
        self.splitter2.setSizes([3.0 * self.geometry().y()/4.0, self.geometry().y()/4.0])

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
        self.model = None
        self.proxy_model = None
        self.tree_view.reset()
        self.tree_view.setModel(None)

    def clearViewer(self):
        '''Close all visualizer views.'''
        self.openEditorTabs = {}
        self.tabbedEditorWidget.clear()

    def changeFilter(self, index):
        '''Event callback for when the user changes the filter type for the navigator.'''
        text = self.filter_type.currentText()
        self.filter_mode = text
        if self.model and self.proxy_model:
            self.model.set_filter_type(text)
            self.proxy_model.invalidate()

    def changeMode(self, index):
        '''Event callback for when the user changes the editor mode.'''
        text = str(self.mode_selector.currentText())
        if text != self.editor_mode:
            self.editor_mode = text
            self.clearModels()
            self.clearViewer()
            # TODO: NEED TO UPDATE TREE VIEW MODEL WITH NEW TYPE OF MODEL

    def openModelView(self, modelIndex):
        '''
        Event callback for when the user double-clicks on a model item in the tree-viewer.
        Sends the model item to the visualizer and creates a new EditorView for it if one does not exist.

        :param in modelIndex: index into the AbstractItemModel which has been selected for viewing.
        '''
        # TODO: Models can have same names depending on scope; make sure we use uniqueness here!
        mi = self.proxy_model.mapToSource(modelIndex)
        item = self.model.getModel( mi )
        name = item["Name"]
        if name not in self.openEditorTabs:
            ev = EditorView( self.tabbedEditorWidget )
            ev.setProxyModel( self.proxy_model )
            # TODO: FIX THIS SO THAT THE VIEW'S EDITOR MODEL IS SET TO THE VIEW'S SELECTION CHANGED
            self.openEditorTabs[name] = ev
        else:
            ev = self.openEditorTabs[name]
        self.tabbedEditorWidget.addTab( ev, name )
        ev.init_ui( index = mi,
                    fname = item.kind() + '.view' )
        self.tabbedEditorWidget.setCurrentIndex(
            self.tabbedEditorWidget.indexOf(ev) )
        
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
                options = QtGui.QFileDialog.Options()
            )
            if fname:
                meta_root = self.open_model(fname)
                base = convertModelToMeta(meta_root)
                root = base()
        elif self.editor_mode == 'Meta Model':
            root = Model()
            root['Name'] = 'New_Model'
        elif self.editor_mode == 'View Model':
            root = ViewModel()
            root['Name'] = 'New_View_Model'
        if root:
            self.load_model(root)

    def openModel(self, event):
        '''Callback to allow the user to select a model file based on the current mode of the editor.'''
        ftype = '{}'.format(self.editor_mode.lower().split()[0])
        fname = QtGui.QFileDialog.getOpenFileName(
            self,
            'Open {}'.format(self.editor_mode),
            '',
            '{} Files (*.{})'.format(self.editor_mode, ftype),
            options = QtGui.QFileDialog.Options()
        )
        if fname:
            self.clearModels()
            self.clearViewer()
            root = self.open_model(fname)
            self.load_model(root)

    def open_model(self, fname):
        '''Decodes a saved *.{model, meta, view} file and loads it into the editor.'''
        import dill
        with open(fname, 'r') as f:
            m = dill.load(f)
            return m

    def load_model(self, model):
        '''
        :param in model: the root object of a model, which is loaded into the tree-viewer and proxy models
        '''

        # Set up the hidden Root model, with the 'model' object as its only child
        root = Model()
        root.children._allowed = [model.__class__]
        root.children._cardinality = { model.__class__ : '1' }
        root.add_child(model)

        # Set up the proxy model for sorting/filtering
        self.proxy_model = SortFilterProxyModel(self)
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy_model.setSortRole(ItemModel.sort_role)
        self.proxy_model.setFilterRole(ItemModel.filter_role)

        # the model stores the reference to the model that is currently
        # being edited/viewed; this can be a regular model, a view model,
        # or even a meta-model.  All these models inherit from the meta-metamodel
        # so have the same interfaces and can be interacted with in the same way
        self.model = ItemModel(root)
        self.model.set_filter_type(self.filter_mode)
        # Link the actual model and the proxy model
        self.proxy_model.setSourceModel(self.model)
        self.filter_edit.textChanged.connect(self.proxy_model.setFilterRegExp)
        self.tree_view.setModel(self.proxy_model)
        self.tree_view.expandAll()
        
    def saveModel(self, event):
        '''Saves a model according to the current mode of the editor.'''
        import dill
        ftype = '{}'.format(self.editor_mode.lower().split()[0])
        fname = QtGui.QFileDialog.getSaveFileName(
            self,
            'Save {}'.format(self.editor_mode),
            '',
            '{} Files (*.{})'.format(self.editor_mode, ftype),
            options = QtGui.QFileDialog.Options()
        )
        if fname:
            if fname[-len(ftype):] != ftype: fname += '.{}'.format(ftype)
            root = self.model.getModel(QtCore.QModelIndex())
            root = root.children[0] # the actual root is not displayed and is always a Model()
            # TODO: Test with meta, view, and model
            with open(fname, 'w') as f:
                dill.dump(root, f)
            return 0

    def closeEvent(self, event):
        event.accept()
        return
        reply = QtGui.QMessageBox.question(self, 'Quit',
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
