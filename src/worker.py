"""
"""

from PyQt4 import QtCore

class Worker(QtCore.QThread):

    def __init__(self, parent):
        super(Worker, self).__init__(parent)
        self.exiting = False

    def __del__(self):
        self.exiting = True
        self.wait()

    def run(self):
        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.

        while not self.exiting:
            print "test"
            print >> sys.stderr, "err test"

