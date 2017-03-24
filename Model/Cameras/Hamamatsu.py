"""Hamamatsu.py
Model class for controlling Hamamatsu cameras via de DCAM-API.
"""
import numpy as np
from Controller.devices.hamamatsu.hamamatsu_camera import *
from ._skeleton import cameraBase


class camera(cameraBase):
    MODE_CONTINUOUS = 1
    MODE_SINGLE_SHOT = 0
    MODE_EXTERNAL = 2

    def __init__(self,camera):
        self.cam_id = camera # Camera ID
        self.camera = HamamatsuCamera(camera)
        self.running = False
        self.mode = self.MODE_SINGLE_SHOT

    def initializeCamera(self):
        """Initializes the camera.
        """
        self.camera.initCamera()
        self.maxWidth = self.GetCCDWidth()
        self.maxHeight = self.GetCCDHeight()
        #This is important to not have shufled patches of the CCD.
        #Have to check documentation!!
        self.camera.setPropertyValue("readout_speed", 1)

    def triggerCamera(self):
        """Triggers the camera.
        """
        if self.getAcquisitionMode() == self.MODE_CONTINUOUS:
            self.camera.startAcquisition()
        elif self.getAcquisitionMode() == self.MODE_SINGLE_SHOT:
            self.camera.startAcquisition()
            self.camera.stopAcquisition()

    def setAcquisitionMode(self, mode):
        """ Set the readout mode of the camera: Single or continuous.
        Parameters
        ==========
        mode : int
            One of self.MODE_CONTINUOUS, self.MODE_SINGLE_SHOT
        """
        self.mode = mode
        if mode == self.MODE_CONTINUOUS:
            #self.camera.setPropertyValue("trigger_source", 1)
            self.camera.settrigger(1)
        elif mode == self.MODE_SINGLE_SHOT:
            #self.camera.setPropertyValue("trigger_source", 3)
            self.camera.settrigger(1)
        elif mode == self.MODE_EXTERNAL:
            #self.camera.setPropertyValue("trigger_source", 2)
            self.camera.settrigger(2)
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
        """Sets the exposure of the camera.
        """
        self.camera.setPropertyValue("exposure_time",exposure/1000)
        return self.getExposure()

    def getExposure(self):
        """Gets the exposure time of the camera.
        """
        return self.camera.getPropertyValue("exposure_time")

    def readCamera(self):
        """Reads the camera
        """
        [frames, dims] = self.camera.getFrames()
        img = []
        for f in frames:
            d = f.getData()
            d = np.reshape(d,(dims[0],dims[1]))
            d = d.T
            img.append(d)
#        img = frames[-1].getData()
#        img = np.reshape(img,(dims[0],dims[1]))
        return img

    def setROI(self,X,Y):
        """Sets up the ROI. Not all cameras are 0-indexed, so this is an important
        place to define the proper ROI.
        X -- array type with the coordinates for the ROI X[0], X[1]
        Y -- array type with the coordinates for the ROI Y[0], Y[1]
        """
        # Because of how Orca Flash 4 works, all the ROI parameters have to be multiple of 4.
        hpos = int(X[0]/4)*4
        self.camera.setPropertyValue("subarray_hpos", hpos)
        vpos = int(Y[0]/4)*4
        self.camera.setPropertyValue("subarray_vpos", vpos)
        hsize = int(abs(X[0]-X[1])/4)*4
        self.camera.setPropertyValue("subarray_hsize", hsize)
        vsize = int(abs(Y[0]-Y[1])/4)*4
        self.camera.setPropertyValue("subarray_vsize", vsize)
        self.camera.setSubArrayMode()
        return self.getSize()

    def getSize(self):
        """Returns the size in pixels of the image being acquired. This is useful for checking the ROI settings.
        """
        X = self.camera.getPropertyValue("subarray_hsize")
        Y = self.camera.getPropertyValue("subarray_vsize")
        return X, Y

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
            #Camera failed to close
            return False
