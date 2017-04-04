"""Classes and methods for working with cameras. It should provide an abstraction
layer for the most common uses of cameras.
"""
import numpy as np

from UUTrack.Controller import GEVSCMOS
from ._skeleton import cameraBase

NUMPY_MODES = {"L":np.uint8, "I;16":np.uint16}
class camera(cameraBase):
    def __init__(self,camera):
        self.cam_num = camera
        self.camera = GEVSCMOS('C:\\Users\\Experimentor\\Programs\\UUTrack\\Controller\\devices\\PhotonicScience','SCMOS')
        self.running = False

    def initializeCamera(self):
        """Initializes the camera.
        """
        self.camera.Open()
        self.maxSize = self.camera.UpdateSizeMax()
        self.camera.SetClockSpeed('50MHz')
        self.camera.SetGainMode("gain1")
        self.camera.SetTrigger("FreeRunning")
        self.camera.EnableAutoLevel(0)
        self.camera.SetExposure(10,"Millisec")
        self.triggerCamera()
        size = self.getSize()
        self.maxWidth = size[0]
        self.maxHeight = size[1]

    def triggerCamera(self):
        """Triggers the camera.
        """
        self.camera.Snap()

    def setExposure(self,exposure):
        """Sets the exposure of the camera.
        """
        exposure = exposure*1000 # in order to always use microseconds
        while self.camera.GetStatus(): # Wait until exposure is finished.
            self.camera.SetExposure(np.int(exposure), 'Microsec')

    def readCamera(self):
        """Reads the camera
        """
        size,data = self.camera.GetImage()
        w,h = size
        mode = self.camera.GetMode()
        img = np.frombuffer(data,NUMPY_MODES[mode]).reshape((h,w))
        img = np.array(img)
        return np.transpose(img)

    def setROI(self,X,Y):
        """Sets up the ROI.
        """
        X -= 1
        Y -= 1
        # Left, top, right, bottom
        l = np.int(X[0])
        t = np.int(Y[0])
        r = np.int(X[1])
        b = np.int(Y[1])
        self.camera.SetSubArea(l,t,r,b)
        return self.camera.GetSize()

    def getSize(self):
        """Returns the size in pixels of the image being acquired.
        """
        return self.camera.GetSize()

    def setupCamera(self,params):
        """Setups the camera with the given parameters.
        -- params['exposureTime']
        -- params['binning']
        -- params['gain']
        -- params['frequency']
        -- params['ROI']
        """
        pass

    def getParameters(self):
        """Returns all the parameters passed to the camera, such as exposure time,
        ROI, etc. Not necessarily the parameters go to the hardware, it may be
        that some are just software related.
        Returns: dict = keyword => value.
        """
        pass

    def GetCCDWidth(self):
        return self.getSize()[0]

    def GetCCDHeight(self):
        return self.getSize()[1]


    def stopCamera(self):
        """Stops the acquisition
        """
        self.camera.AbortSnap()
        self.camera.Close()
