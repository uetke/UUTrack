"""
    UUTrack.View.Camera.specleWidget.py
    ===================================
    Window that displays the variance of the specle pattern in the center of the current ROI over time

    .. sectionauthor:: Kevin Namink <k.w.namink@uu.nl>
"""


import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtGui


class SpecleWindow(QtGui.QMainWindow):
    """
    Simple window that relies on its parent for updating a 1-D plot.
    """

    def __init__(self, parent=None):
        super(SpecleWindow, self).__init__(parent=parent)
        self.cc = pg.PlotWidget()
        self.setCentralWidget(self.cc)
        self.parent = parent
        self.p = self.cc.plot()
        changing_label = QtGui.QLabel()
        font = changing_label.font()
        font.setPointSize(16)
        self.text = pg.TextItem(text='', color=(200, 200, 200), border='w', fill=(0, 0, 255, 100))
        self.text.setFont(font)
        self.cc.addItem(self.text)

        self.sizeofplot = 100
        self.SROIbinsize = 8
        # Use about more than 200 by 200 bins, dependingon SROIbinsize.
        self.SROIbins = (int(200/self.SROIbinsize) + 1)
        self.sizeofSROI = self.SROIbins * self.SROIbinsize

        self.cc.setXRange(0, self.sizeofplot)
        self.plotLoc = 0
        self.plotted = np.full(2, 1)

    def getVarianceData(self):
        # Add the variance of at most the center sizeofSROI squared pixels of the frame to the plot
        # Use binning for SROIbinning squared size bins
        if len(self.parent.tempimage) < 1:
            return 0, 0, 0
        
        tempim = self.parent.tempimage
        xbinsize = self.SROIbinsize
        xbins = self.SROIbins
        ybinsize = self.SROIbinsize
        ybins = self.SROIbins
        
        xstart, xend = 0, len(tempim) - 1
        ystart, yend = 0, len(tempim[0]) - 1
        if xend > self.sizeofSROI:
            xstart = int(xend/2 - self.sizeofSROI/2)
            xend = int(xend/2 + self.sizeofSROI/2)
        else:
            xbins = int((xend - xstart)/xbinsize)
            xend = xstart + xbins*xbinsize
        if yend > self.sizeofSROI:
            ystart = int(yend/2 - self.sizeofSROI/2)
            yend = int(yend/2 + self.sizeofSROI/2)
        else:
            ybins = int((yend - ystart)/ybinsize)
            yend = ystart + ybins*ybinsize
            
        # Binning the image:
        imageSROI = tempim[xstart:xend, ystart:yend].reshape(
                            xbins, xbinsize,
                            ybins, ybinsize).mean(-1).mean(1)
        
        # Calculating the variance and mean:
        var = np.std(imageSROI)
        mean = np.mean(imageSROI)
        if mean != 0:
            meas = var/mean**2
        else:
            meas = var 
        return var, mean, meas

    def update(self):
        """ Updates the plot. It is called externally from the main window.
        """
        if self.parent is not None and self.parent.acquiring:
            if len(self.parent.tempimage) > 0:
                if len(self.plotted) != self.sizeofplot:  # Set full size of plot to initial value to be able to read it
                    var, mean, measure = self.getVarianceData()
                    self.plotted = np.full(self.sizeofplot, measure)
                    
                self.plotLoc += 1  # Add to plot on next location (oscilloscope order)
                if self.plotLoc == self.sizeofplot:
                    self.plotLoc = 0

                var, mean, measure = self.getVarianceData()
                minimum, maximum = self.plotted.min(), self.plotted.max()
                if isinstance(measure, (int, float)) and measure == measure:  # Test for non numbers
                    self.plotted[self.plotLoc] = measure  # Add the value of variance devided by the mean squared to the plot
                
                n_maxvalued = (self.parent.tempimage.ravel() == 65535).sum()
                
                self.cc.setYRange(minimum*0.9, maximum*1.1)
                self.p.setData(self.plotted)
                self.text.setText('Plotting variance over mean^2  Number max I.: %.3e\nCurrent variance: %.3e     Current mean: %.3e' % (n_maxvalued, var, mean))
                self.text.setPos(0, maximum*1.1)

            else:
                self.text.setText("Blank image")
                self.cc.setYRange(-50, 50)










