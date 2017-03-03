import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from pyqtgraph import GraphicsLayoutWidget

class waterfallWidget(QtGui.QWidget):
    """Widget for plotting a waterfall plot.
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.layout = QtGui.QHBoxLayout(self)
        self.viewport = GraphicsLayoutWidget()
        self.view = self.viewport.addViewBox(colspan=3, rowspan=3, lockAspect = False, enableMenu=True)
        self.img = pg.ImageItem()
        self.view.addItem(self.img)

        self.h = self.viewport.addViewBox(enableMenu=False, colspan=3)
        self.hist = pg.HistogramLUTItem(image=self.img, fillHistogram=False)
        self.hist.setImageItem(self.img)
        self.h.addItem(self.hist)

        self.imv = pg.ImageView(view=self.view, imageItem=self.img)

        self.layout.addWidget(self.imv)
        self.setLayout(self.layout)

