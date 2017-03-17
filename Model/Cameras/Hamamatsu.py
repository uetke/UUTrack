"""Hamamatsu.py
Model class for controlling Hamamatsu cameras via de DCAM-API.
"""
import numpy as np
from Controller.devices.hamamatsu.hamamatsu_camera import *

class camera():
    MODE_CONTINUOUS = 1
    MODE_SINGLE_SHOT = 0
    def __init__(self,camera):
        self.cam_id = camera # Camera ID
        self.camera = HamamatsuCameraMR(camera)
        self.running = False
        self.mode = self.MODE_SINGLE_SHOT

    def initializeCamera(self):
        """Initializes the camera.
        """
        self.camera.initCamera()
        self.maxWidth = self.GetCCDWidth()
        self.maxHeight = self.GetCCDHeight()

    def triggerCamera(self):
        """Triggers the camera.
        """
        if self.getAcquisitionMode() == self.MODE_CONTINUOUS:
            print('Cont Acq')
            self.camera.startAcquisition()
        else:
            print('Shot')
            self.camera.startAcquisition()
            print('End shot')
            #self.camera.stopAcquisition()
            print('Stop shot')

    def setAcquisitionMode(self, mode):
        """ Set the readout mode of the camera: Single or continuous.
        Parameters
        ==========
        mode : int
            One of self.MODE_CONTINUOUS, self.MODE_SINGLE_SHOT
        """
        self.mode = mode

    def getAcquisitionMode(self):
        """Returns the acquisition mode, either continuous or single shot.
        """
        return self.mode

    def acquisitionReady(self):
        """Checks if the acquisition in the camera is over.
        """
        return True

    def setExposure(self,exposure):
        """Sets the exposure of the camera.
        """
        self.camera.setPropertyValue("exposure_time",exposure)
        return exposure

    def getExposure(self):
        """Gets the exposure time of the camera.
        """
        return self.camera.getPropertyValue("exposure_time")

    def readCamera(self):
        """Reads the camera
        """
        [frames, dims] = self.camera.getFrames()
        img = frames[-1].getData()
        img = np.reshape(img,(dims[0],dims[1]))
        return img.T

    def setROI(self,X,Y):
        """Sets up the ROI. Not all cameras are 0-indexed, so this is an important
        place to define the proper ROI.
        X -- array type with the coordinates for the ROI X[0], X[1]
        Y -- array type with the coordinates for the ROI Y[0], Y[1]
        """
        self.camera.setPropertyValue("subarray_hpos",X[0])
        self.camera.setPropertyValue("subarray_vpos",Y[0])
        self.camera.setPropertyValue("subarray_hsize",int(abs(X[0]-X[1])))
        self.camera.setPropertyValue("subarray_vsize",int(abs(Y[0]-Y[1])))
        self.camera.setSubArrayMode()
        return self.getSize()

    def getSize(self):
        """Returns the size in pixels of the image being acquired. This is useful for checking the ROI settings.
        """
        X = self.camera.getPropertyValue("subarray_hsize")
        Y = self.camera.getPropertyValue("subarray_vsize")
        return X,Y

    def getSerialNumber(self):
        """Returns the serial number of the camera.
        """
        return self.camera.getModelInfo(self.cam_id)

    def GetCCDWidth(self):
        """
        Returns
        -------
        The CCD width in pixels

        """
        return self.camera.frame_x

    def GetCCDHeight(self):
        """
        Returns
        -------
        The CCD height in pixels

        """
        return self.camera.frame_y


    def stopCamera(self):
        """Stops the acquisition and closes the connection with the camera.
        """
        try:
            #Closing the camera
            self.camera.stopAcquisition()
            return True
        except:
            #Camera failed to close
            return False
