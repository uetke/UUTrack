"""
    UUTrack.View.Monitor.popOut.py
    ===================================
    Pop-out window that can show messages

    .. sectionauthor:: Sanli Faez <s.faez@uu.nl>
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui


class popOutWindow(QtGui.QMainWindow):
    """
    Simple window that relies on its parent for updating a 1-D plot.
    """
    def __init__(self, parent=None):
        super(popOutWindow, self).__init__(parent=parent)

    def showtext(self, text="cheatsheet"):
        pass