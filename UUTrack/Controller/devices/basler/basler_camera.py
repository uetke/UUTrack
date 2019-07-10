# -*- coding: utf-8 -*-
"""
Created on Mon Dec 05 13:45:04 2016

@author: LINX
"""

import pypylon
import matplotlib.pyplot as plt
import tqdm
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable    # for plotting
import time
    
#%%
        
""" Basler Camera """      

class BaslerCamera():
    CAPTUREMODE_SNAP = 0
    CAPTUREMODE_SEQUENCE = 1
    
    def __init__(self, camera_id):
        """Open the connection to the camera specified by camera_id.
        @param camera_id The id of the camera (an integer)."""

        self.buffer_index = 0
        self.camera_id = camera_id

        self.debug = False
        self.frame_bytes = 0
        self.frame_x = 0
        self.frame_y = 0
        self.last_frame_number = 0
        self.properties = {}
        self.max_backlog = 0
        self.number_image_buffers = 0

        """Identify the available Basler cameras and assign them names."""
        #print('Build against pylon library version:', pypylon.pylon_version.version)
        available_cameras = pypylon.factory.find_devices()
        #print('Available cameras are', available_cameras)
        
        # Identify cameras according to their serial number
        for i in range(len(available_cameras)):
            cam = pypylon.factory.create_device(available_cameras[i])
            cam.open()
            if cam.properties['DeviceSerialNumber'] == str(22021476):
                cam_horpol = cam    # vertical polarization camera (reflected after PBS)
            elif cam.properties['DeviceSerialNumber'] == str(22021473):
                cam_verpol = cam    # horizontal polarization camera (transmitted after PBS)
            elif cam.properties['DeviceSerialNumber'] == str(22148126):
                cam_refl1 = cam    # reflection camera 1
            elif cam.properties['DeviceSerialNumber'] == str(22148127):
                cam_refl2 = cam    # reflection camera 2
            else:
                print("Cameras with specified serial numbers not found!")
            cam.close()   
            
#        self.cameras = [cam_horpol, cam_verpol, cam_refl1, cam_refl2]
        self.cameras = [cam_horpol, cam_verpol, cam_refl1]
        self.numCams = len(self.cameras)
        
        """From self.cameras, open the camera with index self.camera_id."""
        
        self.cameras[self.camera_id].open()
        self.camera_model = self.getModelInfo(camera_id)
        
        # Get camera properties.
        self.properties = self.getCameraProperties()

        # Get camera max width, height.
        self.max_width = self.getPropertyValue("WidthMax")[0]
        self.max_height = self.getPropertyValue("HeightMax")[0]
        self.setmode(self.CAPTUREMODE_SEQUENCE) # By default is a sequence
        
        # Set basic camera properties
        self.cameras[self.camera_id].properties['PixelFormat'] = 'Mono12'
        self.cameras[self.camera_id].properties['GainAuto'] = 'Off'
        self.cameras[self.camera_id].properties['Gain'] = 0.0
        self.cameras[self.camera_id].properties['Gamma'] = 1.0
        self.cameras[self.camera_id].properties['ExposureMode'] = 'Timed'
        self.cameras[self.camera_id].properties['ExposureAuto'] = 'Off'
        
        # Go to full available speed
        self.cameras[self.camera_id].properties['DeviceLinkThroughputLimitMode'] = 'Off'
        
    def settrigger(self,mode):
        # Mode = 0 : trigger off
        # Mode = 1 : software trigger on
        # Mode = 2 : external trigger
        
        if mode == 0:
            self.cameras[self.camera_id].properties['TriggerMode'] = 'Off'
        elif mode == 1:
            self.cameras[self.camera_id].properties['TriggerMode'] = 'On'
            self.cameras[self.camera_id].properties['TriggerSource'] = 'Software'
        elif mode == 2:
            self.cameras[self.camera_id].properties['TriggerMode'] = 'On'
            self.cameras[self.camera_id].properties['TriggerSource'] = 'Line1'
        
#        self.cameras[self.camera_id].properties['BslImmediateTriggerMode'] = 'Off'
        self.cameras[self.camera_id].properties['TriggerSelector'] = 'FrameStart'
        
    def setmode(self, mode):
        """Sets the acquisition mode of the camera."""
        self.mode = mode
        
    def initCamera(self):
        # Initialization
        self.captureSetup()

    def captureSetup(self):
        """Capture setup (internal use only). This is called at the start
        of new acquisition sequence to determine the current ROI and
        get the camera configured properly."""

        self.buffer_index = -1
        self.last_frame_number = 0

        # Get frame properties.
        self.frame_x = self.getPropertyValue("Width")[0]
        self.frame_y = self.getPropertyValue("Height")[0]
        self.frame_bytes = self.getPropertyValue("PayloadSize")
        
        #make sure camera is opened
        self.cameras[self.camera_id].opened = "opened"
        
    def getCameraProperties(self):
        """Return the ids & names of all the properties that the camera supports. This
        is used at initialization to populate the self.properties attribute.
        @return A python dictionary of camera properties."""
         
        keys = self.cameras[self.camera_id].properties.keys()
        prop_value = []
        for key in self.cameras[self.camera_id].properties.keys():
            try:
                value = self.cameras[self.camera_id].properties[key]
            except IOError:
                value = '<NOT READABLE>'
            prop_value.append(value)
            
        properties = dict(zip(keys, prop_value))            
        return properties
    
    def fireTrigger(self):
        """Triggers the camera when in software mode."""
        if self.cameras[self.camera_id].properties['TriggerMode'] == "On":
            self.cameras[self.camera_id].properties['BslImmediateTriggerMode'] = 'Off'
            self.cameras[self.camera_id].properties['TriggerSource'] = 'Software'
            self.cameras[self.camera_id].properties['TriggerSelector'] = 'FrameStart'
            print('TRIG')
            
    def getFrames(self):
        """Gets all of the available frames.
        This will block waiting for new frames even if
        there are new frames available when it is called.
        @return [frames, [frame x size, frame y size]]."""    
    
        frames = []
#        frames = [np.zeros((self.frame_x, self.frame_y)) for _ in range(1)]
#
#        new_frames = self.newFrames()
#        i = 0
#        for frame in new_frames:
#            frames[i] = next(new_frames)
#            i += 1
        frames =  next(self.cameras[self.camera_id].grab_images(nr_images = 1, grab_strategy=0, timeout=5000))
#            frames.append(image)
          
        return [frames, [self.frame_x, self.frame_y]]
    
    def newFrames(self):
        """Return a list of the ids of all the new frames since the last check.
        This will block waiting for at least one new frame.
        @return [id of the first frame, .. , id of the last frame]
        """

#        # Wait for a new frame.
#        
#        # Check how many new frames there are.
#        b_index = ctypes.c_int32(0)  # Is pointer to receive the number of the frame in which the most recent data is stored.
#        f_count = ctypes.c_int32(0)  # is pointer to receive the number of frames captured since the capture operation was begun. If no frames have been captured, a value of –1 is returned
#        self.checkStatus(self.dcam.dcam_gettransferinfo(self.camera_handle,
#                                                   ctypes.byref(b_index),
#                                                   ctypes.byref(f_count)),
#                         "dcam_gettransferinfo")
#
#        
#            
#
#        # Check that we have not acquired more frames than we can store in our buffer.
#        # Keep track of the maximum backlog.
#        self.cur_frame_number = f_count.value
#        backlog = self.cur_frame_number - self.last_frame_number
#        if backlog > self.number_image_buffers:
#            print("warning: basler camera frame buffer overrun detected!")
#        if backlog > self.max_backlog:
#            self.max_backlog = backlog
#        self.last_frame_number = self.cur_frame_number
#
#        cur_buffer_index = b_index.value

        # Create a list of the new frames.

#        GrabStrategy_OneByOne           = 0
#        GrabStrategy_LatestImageOnly    = 1
#        GrabStrategy_LatestImages       = 2
#        GrabStrategy_UpcomingImage      = 3
        new_frames = self.cameras[self.camera_id].grab_images(nr_images = 2, grab_strategy=0, timeout=5000)
#        for image in self.cameras[self.camera_id].grab_images(nr_images = self.number_image_buffers, grab_strategy=2, timeout=5000):
#            new_frames.append(image)
            
#        if cur_buffer_index < self.buffer_index:
#            for i in range(self.buffer_index + 1, self.number_image_buffers):
#                new_frames.append(i)
#            for i in range(cur_buffer_index + 1):
#                new_frames.append(i)
#        else:
#            for i in range(self.buffer_index, cur_buffer_index):
#                new_frames.append(i+1)
#        self.buffer_index = cur_buffer_index
#
#        if self.debug:
#            print(new_frames)

        return new_frames
    
    def getModelInfo(self, camera_id):
        """Returns the model of the camera
        @param camera_id The (integer) camera id number.
        @return A string containing the camera name."""

        return self.cameras[self.camera_id].device_info

    def getProperties(self):
        """Return the list of camera properties. This is the one to call if you
        want to know the camera properties.
        @return A dictionary of camera properties."""

        return self.properties

    def getPropertyText(self, property_name):
        """Return the text options of a property (if any).
        @param property_name The name of the property to get the text values of.
        @return A dictionary of text properties (which may be empty)."""
        
        # Check if the property exists.
        if not (property_name in self.properties):
            print(" unknown property name: %s"%property_name)
            return False
        print("property name is ", property_name)
        return self.properties.get_description(property_name)

    def getPropertyRange(self, property_name):
        """Return the range for an attribute.
        @param property_name The name of the property (as a string).
        @return [minimum value, maximum value]."""

        return [self.properties.get_minmax(property_name)]

    def getPropertyRW(self, property_name):
        """Return if a property is readable / writeable.
        @return [True/False (readable), True/False (writeable)]."""
        
        # Check if the property exists.
        if not (property_name in self.properties):
            print(" unknown property name: %s"%property_name)
            return False
    
        rw = []

        # Check if the property is readable.
        if self.properties.is_readable(property_name) == True:
            rw.append(True)
        else:
            rw.append(False)

        # Check if the property is writeable.
        if self.properties.is_writable(property_name) == True:
            rw.append(True)
        else:
            rw.append(False)

        return rw

    def getPropertyValue(self, property_name):
        """Return the current setting of a particular property.
        @param property_name The name of the property.
        @return [the property value, the property type]."""

        # Check if the property exists.
        if not (property_name in self.properties):
            print(" unknown property name: %s"%property_name)
            return False

        # Get the property value.
        prop_value = self.properties[property_name]
        prop_type = type(prop_value)

        return [prop_value, prop_type]

    def isCameraProperty(self, property_name):
        """Check if a property name is supported by the camera.
        @param property_name The name of the property.
        return True/False if property_name is a supported camera property.
        """

        if (property_name in self.properties):
            return True
        else:
            return False

    def setPropertyValue(self, property_name, property_value):
        """Set the value of a property.
        @param property_name The name of the property.
        @param property_value The value to set the property to.
        """

        # Check if the property exists.
        if not (property_name in self.properties):
            print(" unknown property name: %s"%property_name)
            return False

        # Set the property value, return what it is set to.
        # __setitem__ already checks whether property is within range
        self.cameras[self.camera_id].properties[property_name] = property_value # set value on camera
        self.properties[property_name] = property_value # update property list with new value
        
        return self.properties[property_name]

    def startAcquisition(self):
        """ Start data acquisition."""
        self.captureSetup()

        # Allocate Basler image buffers.
        # We allocate max number of buffers
        n_buffers = self.cameras[self.camera_id].max_num_buffer
        self.number_image_buffers = n_buffers

        # Start acquisition.
#        GrabStrategy_OneByOne           = 0
#        GrabStrategy_LatestImageOnly    = 1
#        GrabStrategy_LatestImages       = 2
#        GrabStrategy_UpcomingImage      = 3
#        self.cameras[self.camera_id].grab_images(nr_images = -1, grab_strategy = 2, timeout = 5000)

    def stopAcquisition(self):
        """Stop data acquisition."""
        
        self.cameras[self.camera_id].stop_grabbing()        
                
        print("max camera backlog was %s of %s"%(self.max_backlog, self.number_image_buffers))
        self.max_backlog = 0
        
        # Free image buffers.
        self.number_image_buffers = 0

    def shutdown(self):
        """Close down the connection to the camera."""
        self.cameras[self.camera_id].close()
        
#%%        
#
# Testing.
#
if __name__ == "__main__":
    print('MAIN')

#    print ("found: %s cameras"%numCams)
#    if (numCams > 0):

    bcam = BaslerCamera(0)
    print(bcam.setPropertyValue("DefectPixelCorrectionMode", "Off"))
    print("camera 0 model:", bcam.getModelInfo(0))

    # List support properties.
    if 0:
        print("Supported properties:")
        props = bcam.getProperties()
        for i, id_name in enumerate(sorted(props.keys())):
            [p_value, p_type] = bcam.getPropertyValue(id_name)
            p_rw = bcam.getPropertyRW(id_name)
            read_write = ""
            if (p_rw[0]):
                read_write += "read"
            if (p_rw[1]):
                read_write += ", write"
            print("  %s)%s = %s type is:%s,%s"%(i,id_name,p_value,p_type,read_write))
            text_values = bcam.getPropertyText(id_name)
            if (len(text_values) > 0):
                print("          option / value")
                for key in sorted(text_values, key = text_values.get):
                    print("         %s/%s"%(key,text_values[key]))

    # Test setting & getting some parameters.
    if 1:
        print(bcam.setPropertyValue("ExposureTime", 500))

        print(bcam.setPropertyValue("Height", 900))
        print(bcam.setPropertyValue("Width", 900))
        print(bcam.setPropertyValue("OffsetX", 190))
        print(bcam.setPropertyValue("OffsetY", 30))

        print(bcam.setPropertyValue("BinningHorizontal", 1))
        print(bcam.setPropertyValue("BinningVertical", 1))

        bcam.startAcquisition()
        bcam.stopAcquisition()

        params = ["ResultingFrameRate",
                  "ResultingFramePeriod",
                  "ExposureTime",
                  "HeightMax",
                  "WidthMax",
                  "PayloadSize",
                  #"buffer_framebytes",
                  #"buffer_rowbytes",
                  #"buffer_top_offset_bytes",
                  "Height",
                  "Width",
                  #"binning"
                  ]
        for param in params:
            print(param, bcam.getPropertyValue(param)[0])

        # Test acquisition.
        if 1:
            bcam.startAcquisition()
            cnt = 1

            start = time.time()
            for i in range(10):
                [frames, dims] = bcam.getFrames()
                for aframe in frames:
#                    print(cnt, aframe[0:5])
                    cnt += 1
            stop = time.time()
            
            print(stop-start)

            bcam.stopAcquisition()
            bcam.shutdown()
            plt.imshow(aframe)
            plt.show()
        