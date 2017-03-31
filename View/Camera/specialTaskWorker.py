from time import sleep
from pyqtgraph.Qt import QtCore
from scipy.ndimage.measurements import center_of_mass
import numpy as np

class specialTaskWorker(QtCore.QThread):
    """Thread for performing a specific task, for example tracking of a particle in 'real-time'.
        It takes as an input the variable _session, and two coordinates X, Y.
        What the coordinates are, depends on specific applications.
    """
    def __init__(self, _session, camera, X, Y):
        QtCore.QThread.__init__(self)
        self._session = _session
        self.camera = camera
        self.keep_running = True
        self.X = X
        self.Y = Y
    def __del__(self):
        self.wait()

    def run(self):
        """ Performs a task, for example acquires an image and computes the centroid.
        """
        first = True
        while self.keep_running:
            if first:
                self.camera.setAcquisitionMode(self.camera.MODE_CONTINUOUS)
                self.camera.triggerCamera() # Triggers the camera only once
                first = False
            img = self.camera.readCamera()
            if isinstance(img, list):
                img = img[-1]

            X = center_of_mass(img/np.max(np.max(img)))
            # print(X)
            # print('Special task running... Coordinate X: %sCoordinate Y: %s'%(X[0], X[1]))
            self.emit(QtCore.SIGNAL('Image'), img, 'SpecialTask')
            self.emit(QtCore.SIGNAL('Coordinates'), X[0], X[1])
        print('Special task finished')
        return
