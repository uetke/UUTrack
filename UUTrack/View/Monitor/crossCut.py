"""
    UUTrack.View.Camera.crossCut.py
    ===================================
    Window that displays a 1D plot of a cross cut on the main window.

    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""

import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtGui


class crossCutWindow(QtGui.QMainWindow):
    """
    Simple window that relies on its parent for updating a 1-D plot.
    """
    def __init__(self, parent=None):
        super(crossCutWindow, self).__init__(parent=parent)
        self.cc = pg.PlotWidget()
        self.setCentralWidget(self.cc)
        self.parent = parent
        y = np.random.random(100)
        self.p = self.cc.plot()
        changingLabel = QtGui.QLabel()
        font = changingLabel.font()
        font.setPointSize(24)
        self.text =  pg.TextItem(text='', color=(200, 200, 200), border='w', fill=(0, 0, 255, 100))
        self.text.setFont(font)
        self.cc.addItem(self.text)

    def update(self):
        """ Updates the 1-D plot. It is called externally from the main window.
        """
        if self.parent != None:
            if len(self.parent.tempImage) > 0:
                #self.cc.plot(self.parent.tempImage[:, 50])
                s = self.parent.camWidget.crossCut.value()
                if s<np.shape(self.parent.tempImage)[1]:
                    d = np.ascontiguousarray(self.parent.tempImage[:, s])
                    self.p.setData(d)
                    self.text.setText(str(np.std(d)/np.mean(d)))


if __name__ == '__main__':
    import numpy as np
    app = QtGui.QApplication([])
    win = crossCutWindow()
    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    win.cc.plot(x,y)
    win.show()
    app.instance().exec_()
