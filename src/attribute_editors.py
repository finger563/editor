'''
These classes allow for special datatypes to be edited and updated
by the MVC paradigm interface with through a :class:`QItemDelegate`
subclass.
'''

__author__ = 'William Emfinger'
__copyright__ = 'Copyright 2016, ROSMOD'
__credits__ = ['William Emfinger', 'Pranav Srinivas Kumar']
__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'William Emfinger'
__email__ = 'emfinger@isis.vanderbilt.edu'
__status__ = 'Production'

from PyQt4 import QtGui

# TODO: Create an object here which fully encapsulates dictionary editing

# TODO: Probably need objects which display strings for
#       editing/choosing, but which actually map to objects underneath
#       (e.g. pointer selection).  Need some sort of mapper/delegate
#       for these editors which perofrm the mapping


class FileEditor(QtGui.QPushButton):
    '''
    Subclass of :class:`QtGui.QPushButton` that enables MVC
    ItemDelegate to set and query the filename.  When the button is
    clicked it spawns a :class:`QFileDialog` for selecting the file
    based on the file_type specified.
    '''

    def __init__(self, name, fname, file_type, parent=None):
        super(FileEditor, self).__init__(parent)
        self._name = name
        self._file_type = file_type
        self.set_file_name(fname)
        self.clicked.connect(self.open_file)

    def set_file_name(self, value):
        self._value = value
        self.setText(self._value.split('/')[-1])

    def file_name(self):
        return self._value

    def open_file(self, event):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self.parent(),
            "Select {} file".format(self._name),
            self.text(),
            "All Files(*);;{} Files (*.{})".format(self._name,
                                                   self._file_type),
            options=QtGui.QFileDialog.Options()
        )
        if fileName:
            self.set_file_name(fileName)
