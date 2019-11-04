"""
    UUTrack.Model.Cameras.Basler.py
    ==================================

    Model class for controlling Basler cameras via de Pylon API. 

    .. sectionauthor:: Pritam Pai <p.pai@uu.nl>
"""
import numpy as np

from UUTrack.Controller.devices.basler.basler_camera import BaslerCamera
from ._skeleton import cameraBase


class camera(cameraBase):
    MODE_CONTINUOUS = 1
    MODE_SINGLE_SHOT = 0
    MODE_EXTERNAL = 2

    def __init__(self,camera):
        self.cam_id = camera # Monitor ID
        self.camera = BaslerCamera(camera)
        self.running = False
        self.mode = self.MODE_CONTINUOUS

    def initializeCamera(self):
        """ Initializes the camera.

        :return:
        """

        self.camera.initCamera()
        self.maxWidth = self.GetCCDWidth()
        self.maxHeight = self.GetCCDHeight()
        # Don't adjust pixels that have a significantly different value than their neighboring pixels (outlier pixels)
        self.camera.setPropertyValue("DefectPixelCorrectionMode", "Off")

    def triggerCamera(self):
        """Triggers the camera.
        """
        if self.getAcquisitionMode() == self.MODE_CONTINUOUS:
            self.camera.startAcquisition()
        elif self.getAcquisitionMode() == self.MODE_SINGLE_SHOT:
            self.camera.startAcquisition()
            self.camera.stopAcquisition()

    def setAcquisitionMode(self, mode):
        """
        Set the readout mode of the camera: Single or continuous.
        Parameters
        mode : int
        One of self.MODE_CONTINUOUS, self.MODE_SINGLE_SHOT
        """
        self.mode = mode
        if mode == self.MODE_CONTINUOUS:
            self.camera.settrigger(0)
            self.camera.setmode(self.camera.CAPTUREMODE_SEQUENCE)
        elif mode == self.MODE_SINGLE_SHOT:
            self.camera.settrigger(0)
            self.camera.setmode(self.camera.CAPTUREMODE_SNAP)
        elif mode == self.MODE_EXTERNAL:
            self.camera.settrigger(2)
            self.camera.setmode(self.camera.CAPTUREMODE_SEQUENCE)
        return self.getAcquisitionMode()

    def getAcquisitionMode(self):
        """Returns the acquisition mode, either continuous or single shot.
        """
        return self.mode

    def acquisitionReady(self):
        """Checks if the acquisition in the camera is over.
        """
        return True

    def setExposure(self,exposure):
        """
        Sets the exposure of the camera [in us]
        """
        self.camera.setPropertyValue("ExposureTime",exposure)
        return self.getExposure()

    def getExposure(self):
        """
        Gets the exposure time of the camera [in us].
        """
        return self.camera.getPropertyValue("ExposureTime")

    def readCamera(self):
        """
        Reads the camera
        """
        [img, dims] = self.camera.getFrames()
#        img = []
#        for f in frames:
##            d = f.getData()
#            d = np.asarray(f)
#            d = np.reshape(d, (dims[1], dims[0]))
#            d = d.T
#            img.append(d)
#        img = frames[-1].getData()
#        img = np.reshape(img,(dims[0],dims[1]))
        return img

    def setROI(self,X,Y):
        """
        Sets up the ROI. Not all cameras are 0-indexed, so this is an important
        place to define the proper ROI.
        X -- array type with the coordinates for the ROI X[0], X[1]
        Y -- array type with the coordinates for the ROI Y[0], Y[1]
        """
        # First needs to go full frame, if not, throws an error if subframe not valid
        self.camera.setPropertyValue("OffsetY", 0)
        self.camera.setPropertyValue("OffsetX", 0)
        self.camera.setPropertyValue("Height", self.camera.max_height)
        self.camera.setPropertyValue("Width", self.camera.max_width)
        
        # Because of how Basler works, all the ROI parameters have to be multiple of 2.
        width = int((X[1]-X[0])/2)*2
        offX = int(X[0]/2)*2
        height = int((Y[1]-Y[0])/2)*2
        offY = int(Y[0]/2)*2
        self.camera.setPropertyValue("Height", height)
        self.camera.setPropertyValue("Width", width)
        self.camera.setPropertyValue("OffsetY", offY)
        self.camera.setPropertyValue("OffsetX", offX)
        return self.getSize()

    def getSize(self):
        """Returns the size in pixels of the image being acquired. This is useful for checking the ROI settings.
        """
        X = self.camera.getPropertyValue("Width")
        Y = self.camera.getPropertyValue("Height")
        return X[0], Y[0]

    def getSerialNumber(self):
        """Returns the serial number of the camera.
        """
        return self.camera.getModelInfo(self.cam_id)

    def GetCCDWidth(self):
        """
        Returns
        The CCD width in pixels

        """
        return self.camera.max_width

    def GetCCDHeight(self):
        """
        Returns
        The CCD height in pixels

        """
        return self.camera.max_height

    def stopAcq(self):
        self.camera.stopAcquisition()

    def stopCamera(self):
        """Stops the acquisition and closes the connection with the camera.
        """
        try:
            #Closing the camera
            self.camera.stopAcquisition()
            self.camera.shutdown()
            return True
        except:
            #Monitor failed to close
            return False
