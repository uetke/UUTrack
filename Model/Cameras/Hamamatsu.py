"""Hamamatsu.py
Model class for controlling Hamamatsu cameras via de DCAM-API.
"""

class camera():
    MODE_CONTINUOUS = 1
    MODE_SINGLE_SHOT = 0
    def __init__(self,camera):
        self.camera = camera
        self.running = False

    def initializeCamera(self):
        """Initializes the camera.
        """
        self.camera.initCamera()

    def triggerCamera(self):
        """Triggers the camera.
        """

   def setAcquisitionMode(self, mode):
        """ Set the readout mode of the camera: Single or continuous.
        Parameters
        ==========
        mode : int
            One of self.MODE_CONTINUOUS, self.MODE_SINGLE_SHOT
        """

    def getAcquisitionMode(self):
        """Returns the acquisition mode, either continuous or single shot.
        """
        return self.MODE_CONTINUOUS

    def acquisitionReady(self):
        """Checks if the acquisition in the camera is over.
        """
        return True

    def setExposure(self,exposure):
        """Sets the exposure of the camera.
        """
        return exposure

    def getExposure(self):
        """Gets the exposure time of the camera.
        """
        return 10

    def readCamera(self):
        """Reads the camera
        """
        return np.empty(shape=(20,20))

    def setROI(self,X,Y):
        """Sets up the ROI. Not all cameras are 0-indexed, so this is an important
        place to define the proper ROI.
        X -- array type with the coordinates for the ROI X[0], X[1]
        Y -- array type with the coordinates for the ROI Y[0], Y[1]
        """
        return self.getSize()

    def getSize(self):
        """Returns the size in pixels of the image being acquired. This is useful for checking the ROI settings.
        """
        return 20,20

    def getSerialNumber(self):
        """Returns the serial number of the camera.
        """
        return "Serial Number"

    def GetCCDWidth(self):
        """
        Returns
        -------
        The CCD width in pixels

        """

    def GetCCDHeight(self):
        """
        Returns
        -------
        The CCD height in pixels

        """


    def stopCamera(self):
        """Stops the acquisition and closes the connection with the camera.
        """
        try:
            #Closing the camera
            return True
        except:
            #Camera failed to close
            return False
