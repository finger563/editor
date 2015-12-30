"""
Output Widget 

These classes allow output windows (in tabs)
to which stderr/stdout can be redirected.  

They should also support color.

* author: William Emfinger
* website: github.com/finger563/editor 
* last edited: July 2015
"""

from PyQt4 import QtCore
from PyQt4 import QtGui

#import syntax
import sys
import logging

class QtHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
    def emit(self, record):
        record = self.format(record)
        if record: XStream.stdout().write('%s\n'%record)
        # originally: XStream.stdout().write("{}\n".format(record))


"""
logger = logging.getLogger(__name__)
handler = QtHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
"""
class XStream(QtCore.QObject):
    _stdout = None
    _stderr = None
    messageWritten = QtCore.pyqtSignal(str)
    def flush( self ):
        pass
    def fileno( self ):
        return -1
    def write( self, msg ):
        if ( not self.signalsBlocked() ):
            self.messageWritten.emit(unicode(msg))
    @staticmethod
    def stdout():
        if ( not XStream._stdout ):
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout
    @staticmethod
    def stderr():
        if ( not XStream._stderr ):
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr

class OutputWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(OutputWidget, self).__init__(parent)

        self._console = QtGui.QTextBrowser(self)

        #self._highlight = syntax.PythonHighlighter(self._console.document())

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self._console)
        self.setLayout(layout)

        #XStream.stdout().messageWritten.connect( self._console.insertPlainText )
        #XStream.stderr().messageWritten.connect( self._console.insertPlainText )

class TabbedOutputWidget(QtGui.QTabWidget):
    def __init__(self, parent):
        super(TabbedOutputWidget, self).__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setUsesScrollButtons(True)

        ow = OutputWidget(self)
        self.addTab(ow, "Output 1")
        ow = OutputWidget(self)
        self.addTab(ow, "Output 2")
        
        self.tabCloseRequested.connect(self.onTabClose)

    def onTabClose(self,index):
        self.removeTab(index)
