'''
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


class ModelViewDelegate(QtGui.QItemDelegate):
    '''Handles the mapping between :class:`ModelView`'s data and the
    model's data.  Ensures that whenever the view's data are edited,
    the model's data get updated and vise-versa.  This enables
    ensuring that the tab's name changes whenever its associated model
    changes, for instance.
    '''
    def setEditorData(self, editor, index):
        if type(editor) == ModelView:
            attr = index.model().getModel(index)
            text = attr.scoped()
            i = editor.parent().parent().indexOf(editor)
            editor.parent().parent().setTabText(i, text)
            return
        return super(ModelViewDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if type(editor) == ModelView:
            return
        return super(ModelViewDelegate, self).setModelData(editor,
                                                            model, index)


class ModelView(QtGui.QGraphicsView):
    '''Subclass of :class:`QGraphicsView` which acts as a viewer for some
    subset of the model.  Automatically loads whatever
    :class:`ViewModel` is associated with the view's model, as *<Model
    Name>.view*.  If the view file cannot be loaded or found, a
    default implementation simply creates a :class:`EditorItem` object
    representing the model.
    '''

    drag_mode_key = QtCore.Qt.Key_Control
    scroll_mode_key = QtCore.Qt.Key_Control
    close_aw_key = QtCore.Qt.Key_Escape

    def __init__(self, parent):
        super(ModelView, self).__init__(parent)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

        self._command_key_pressed = False

        self._model = None
        self._dataMapper = QtGui.QDataWidgetMapper()
        self._itemDelegate = ModelViewDelegate(self)
        self._dataMapper.setItemDelegate(self._itemDelegate)

    def viewModel(self):
        # the view model is not encapsulated by data/item models
        # it is directly accessible class objects with attributes etc.
        return self.view_model

    def model(self):
        return self._model

    def setModel(self, model):
        self._model = model
        self._dataMapper.setModel(self.model())

    def init_ui(self, index, fname=''):
        scene = QtGui.QGraphicsView(self)
        self.setScene(scene)

        self._dataMapper.setModel(index.model())
        self._dataMapper.setOrientation(QtCore.Qt.Vertical)

        self._dataMapper.setRootIndex(index)
        self._dataMapper.setCurrentIndex(1)

        self._dataMapper.addMapping(self, 0)

        # view model is static; will NEVER be edited or viewed,
        # and will never be used by anything but a scene/view and their
        # children, so we keep a reference to the view model open here
        self.view_model = None

        r = self.buildView(index)
        scene.addItem(r)

        self.show()

    def buildView(self, index, parent=None):
        t = None
        if self.viewModel():
            pass
        else:
            t = EditorItem(index=index, parent=parent)
            numPtrs = len(index.model().getModel(index).pointers)
            above = t
            for i in range(numPtrs):
                ptrIndex = index.child(i, 2)
                newT = EditorItem(index=ptrIndex, parent=t)
                newT.setPos(above.pos().x(),
                            above.pos().y() + above.size().height())
                above = newT
        return t

    def keyPressEvent(self, event):
        if event.key() == self.drag_mode_key:
            self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
            self._command_key_pressed = True
        else:
            QtGui.QGraphicsView.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if event.key() == self.drag_mode_key:
            self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
            self._command_key_pressed = False
        elif event.key() == self.close_aw_key:
            self.attribute_panel.hide(None)
        else:
            QtGui.QGraphicsView.keyReleaseEvent(self, event)

    def wheelEvent(self, event):
        if self._command_key_pressed:
            zoomInFactor = 1.25
            zoomOutFactor = 1 / zoomInFactor
            oldPos = self.mapToScene(event.pos())
            if event.delta() > 0:
                zoomFactor = zoomInFactor
            else:
                zoomFactor = zoomOutFactor
            self.scale(zoomFactor, zoomFactor)
            oldPosNow = self.mapFromScene(oldPos)
            move = oldPosNow - event.pos()
            self.horizontalScrollBar().setValue(
                move.x() +
                self.horizontalScrollBar().value()
            )
            self.verticalScrollBar().setValue(
                move.y() +
                self.verticalScrollBar().value()
            )
        else:
            QtGui.QGraphicsView.wheelEvent(self, event)
