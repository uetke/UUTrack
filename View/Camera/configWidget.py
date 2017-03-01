from pyqtgraph.Qt import QtCore, QtGui

class configWidget(QtGui.QWidget):
    """Widget for configuring the main parameters of the camera.
    """
    def __init__(self,session,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._session = session

        self.layout = QtGui.QFormLayout()

        self.exposureTime = QtGui.QLineEdit()
        self.ROIbottom = QtGui.QLineEdit()
        self.ROIupper = QtGui.QLineEdit()
        self.ROIleft = QtGui.QLineEdit()
        self.ROIright = QtGui.QLineEdit()
        self.refreshTime = QtGui.QLineEdit()
        self.applyButton = QtGui.QPushButton('Apply')
        self.cancelButton = QtGui.QPushButton('Cancel')

        self.connect(self.cancelButton,QtCore.SIGNAL('clicked()'),self.populateValues)
        self.connect(self.applyButton,QtCore.SIGNAL('clicked()'),self.updateValues)

        self.layout.addRow('Exposure Time (ms):',self.exposureTime)
        self.layout.addRow('ROI bottom:',self.ROIbottom)
        self.layout.addRow('ROI uppter:',self.ROIupper)
        self.layout.addRow('ROI left:',self.ROIleft)
        self.layout.addRow('ROI right',self.ROIright)
        self.layout.addRow('Refresh Time (ms):',self.refreshTime)
        self.layout.addRow(self.applyButton)
        self.layout.addRow(self.cancelButton)
        self.setLayout(self.layout)
        self.populateValues()

    def populateValues(self):
        """Puts values to the fields in the form.
        """
        self.exposureTime.setText('%s'%self._session.exposureTime)
        self.ROIleft.setText('%s'%self._session.ROIl)
        self.ROIright.setText('%s'%self._session.ROIr)
        self.ROIupper.setText('%s'%self._session.ROIu)
        self.ROIbottom.setText('%s'%self._session.ROIb)
        self.refreshTime.setText('%s'%self._session.refreshTime)

    def updateValues(self):
        """Updates the values of _session and emits a signal.
        """
        self._session.exposureTime = float(self.exposureTime.text())
        self._session.ROIl = int(self.ROIleft.text())
        self._session.ROIr = int(self.ROIright.text())
        self._session.ROIu = int(self.ROIupper.text())
        self._session.ROIb = int(self.ROIbottom.text())
        self._session.refreshTime = int(self.refreshTime.text())
        print(self._session.refreshTime)
        self.emit(QtCore.SIGNAL('updateConfig'),self._session)
