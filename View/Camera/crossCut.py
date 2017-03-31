import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui


class crossCutWindow(QtGui.QMainWindow):
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
        if self.parent != None:
            if len(self.parent.tempImage) > 0:
                #self.cc.plot(self.parent.tempImage[:, 50])
                slice = self.parent.camWidget.crossCut.value()
                d = np.ascontiguousarray(self.parent.tempImage[:, slice])
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