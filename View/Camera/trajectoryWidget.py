import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from pyqtgraph import GraphicsLayoutWidget

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
