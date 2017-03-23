from pyqtgraph.Qt import QtCore

class workThread(QtCore.QThread):
    """Thread for acquiring from the camera. If the exposure time is long, this is
    needed to avoid freezing the GUI.
    """
    def __init__(self,_session,camera):
        QtCore.QThread.__init__(self)
        self._session = _session
        self.camera = camera
        self.origin = None
        self.keep_acquiring = True
    def __del__(self):
        self.wait()

    def run(self):
        """ Triggers the Camera to acquire a new Image.
        """
        first = True
        while self.keep_acquiring:
            if self.origin == 'snap':
                self.keep_acquiring = False
            if first:
                self.camera.triggerCamera() # Triggers the camera only once
                first = False
            img = self.camera.readCamera()
            self.emit( QtCore.SIGNAL('Image'), img, self.origin)
        return
