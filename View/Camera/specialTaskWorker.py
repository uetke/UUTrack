from time import sleep
from pyqtgraph.Qt import QtCore
from scipy.ndimage.measurements import center_of_mass
class specialTaskWorker(QtCore.QThread):
    """Thread for performing a specific task, for example tracking of a particle in 'real-time'.
        It takes as an input the variable _session, and two coordinates X, Y.
        What the coordinates are, depends on specific applications.
    """
    def __init__(self,_session,camera,X,Y):
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
        while self.keep_running:
            self.camera.triggerCamera()
            img = self.camera.readCamera()
            X = center_of_mass(img)
            print('Special task running... Coordinate X: %sCoordinate Y: %s'%(X[0],X[1]))
            self.emit(QtCore.SIGNAL('Image'), img, 'SpecialTask')
            self.emit(QtCore.SIGNAL('Coordinates'),X[0],X[1])
        print('Special task finished')
        return
