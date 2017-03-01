import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from pyqtgraph import GraphicsLayoutWidget

class waterfallWidget(QtGui.QWidget):
    """Widget for plotting a waterfall plot.
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QVBoxLayout(self)
        self.viewport = GraphicsLayoutWidget()
        self.view = self.viewport.addViewBox(enableMenu=True)
        self.img = pg.ImageItem()
        self.view.addItem(self.img)
        self.layout.addWidget(self.viewport)
