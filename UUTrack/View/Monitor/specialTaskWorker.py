"""
    UUTrack.View.Camera.specialTaskWorker.py
    ========================================
    Similar to the :ref:`UUTrack.View.Camera.workerThread`, the special task worker is designed for running in a separate thread a task other than just acquiring from the camera.
    For example, one can use this to activate some feedback loop.
    In order to see this in action, check :meth:`startSpecialTask <UUTrack.View.Camera.cameraMain.cameraMain.startSpecialTask>`

    .. todo:: Make something out of this class more than just extracting the centroid.
"""

import numpy as np
from pyqtgraph.Qt import QtCore
from .LocateParticle import LocatingParticle

class specialTaskWorker(QtCore.QThread):
    """Thread for performing a specific task, for example tracking of a particle in 'real-time'.
        It takes as an input variables _session, camera,  and inipos: x, y, particle position.
        What the coordinates are, depends on specific applications.
    """
    def __init__(self, _session, camera, iniloc):
        QtCore.QThread.__init__(self)
        self._session = _session
        self.camera = camera
        self.keep_running = True
        self.loc = iniloc
        self.psize = _session.Tracking['particle_size']
        self.step = _session.Tracking['step_size']
        self.locator = LocatingParticle(self.psize, self.step, iniloc)

    def __del__(self):
        self.wait()

    def run(self):
        """ Performs a task after calling the start() method, for example acquires an image and computes the centroid.
        """
        first = True
        while self.keep_running:
            if first:
                self.camera.setAcquisitionMode(self.camera.MODE_CONTINUOUS)
                self.camera.triggerCamera() # Triggers the camera only once
                first = False
            img = self.camera.readCamera()
            if isinstance(img, list):
                trackinfo = np.zeros((5,len(img)))
                if self.psize == 0:
                    self.psize = self.locator.findParticleSize(img[0], self.loc)
                n=0
                for i in img:
                    trackinfo[:,n] = self.locator.Locate(i)
                    n+=1
            else:
                X = np.array(center_of_mass(img/np.max(np.max(img))))
            # print(X)
            # print('Special task running... Coordinate X: %sCoordinate Y: %s'%(X[0], X[1]))
            self.emit(QtCore.SIGNAL('Image'), img, 'SpecialTask')
            self.emit(QtCore.SIGNAL('Coordinates'), X)
        self.camera.stopAcq()
        print('Special task finished! Estimated particle size is %s' %(self.psize))
        return
