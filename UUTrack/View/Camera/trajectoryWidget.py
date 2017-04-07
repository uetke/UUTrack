"""
    UUTrack.View.Camera.trajectoryWidget.py
    ========================================
    This widget only displays the output of the special worker. It is mainly for prototyping purposes. It displays a scatter 2D plot because it is the current output of the special task worker, but in principle it can be adapted to any other need. 
    
    .. todo:: adapt this widget for a useful case.
    
    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui


class trajectoryWidget(QtGui.QWidget):
    """Simple plot class for showing the 2D trajectory"""
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QHBoxLayout(self)
        self.view = pg.GraphicsLayoutWidget()
        # self.setCentralWidget(self.view)
        self.vb = self.view.addViewBox()
        self.plot = pg.ScatterPlotItem()
        self.vb.addItem(self.plot)
        self.layout.addWidget(self.view)
        # self.setLayout(self.layout)
