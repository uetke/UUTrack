# -*- coding: utf-8 -*-
"""
    UUTrack.Controller.devices.hamamatsu.hamamatsu_camera.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    File taken from `ZhuangLab <https://github.com/ZhuangLab/storm-control>`_

    A ctypes based interface to Hamamatsu cameras.
    (tested on a sCMOS Flash 4.0).

    The documentation is a little confusing to me on this subject..
    I used c_int32 when this is explicitly specified, otherwise I use c_int.

    .. todo:: I'm using the "old" functions because these are documented. Switch to the "new" functions at some point.

    .. todo:: How to stream 2048 x 2048 at max frame rate to the flash disk? The Hamamatsu software can do this.

    .. sectionauthor:: Hazen Babcock 10/13

"""

import ctypes
import ctypes.util
import numpy

# Hamamatsu constants.
DCAMCAP_EVENT_FRAMEREADY = int("0x0002", 0)

# DCAM3 API.
DCAMERR_ERROR = 0
DCAMERR_NOERROR = 1

DCAMPROP_ATTR_HASVALUETEXT = int("0x10000000", 0)
DCAMPROP_ATTR_READABLE = int("0x00010000", 0)
DCAMPROP_ATTR_WRITABLE = int("0x00020000", 0)

DCAMPROP_OPTION_NEAREST = int("0x80000000", 0)
DCAMPROP_OPTION_NEXT = int("0x01000000", 0)
DCAMPROP_OPTION_SUPPORT = int("0x00000000", 0)

DCAMPROP_TYPE_MODE = int("0x00000001", 0)
DCAMPROP_TYPE_LONG = int("0x00000002", 0)
DCAMPROP_TYPE_REAL = int("0x00000003", 0)
DCAMPROP_TYPE_MASK = int("0x0000000F", 0)

DCAMWAIT_TIMEOUT_INFINITE = int("0x80000000", 0)

DCAM_CAPTUREMODE_SNAP = 0
DCAM_CAPTUREMODE_SEQUENCE = 1

DCAM_DEFAULT_ARG = 0

DCAM_IDPROP_EXPOSURETIME = int("0x001F0110", 0)
DCAM_IDSTR_MODEL = int("0x04000104", 0)

class DCAM_PARAM_PROPERTYATTR(ctypes.Structure):
    """The dcam property attribute structure."""

    _fields_ = [("cbSize", ctypes.c_int32),
                ("iProp", ctypes.c_int32),
                ("option", ctypes.c_int32),
                ("iReserved1", ctypes.c_int32),
                ("attribute", ctypes.c_int32),
                ("iGroup", ctypes.c_int32),
                ("iUnit", ctypes.c_int32),
                ("attribute2", ctypes.c_int32),
                ("valuemin", ctypes.c_double),
                ("valuemax", ctypes.c_double),
                ("valuestep", ctypes.c_double),
                ("valuedefault", ctypes.c_double),
                ("nMaxChannel", ctypes.c_int32),
                ("iReserved3", ctypes.c_int32),
                ("nMaxView", ctypes.c_int32),
                ("iProp_NumberOfElement", ctypes.c_int32),
                ("iProp_ArrayBase", ctypes.c_int32),
                ("iPropStep_Element", ctypes.c_int32)]

class DCAM_PARAM_PROPERTYVALUETEXT(ctypes.Structure):
    """The dcam text property structure."""
    _fields_ = [("cbSize", ctypes.c_int32),
                ("iProp", ctypes.c_int32),
                ("value", ctypes.c_double),
                ("text", ctypes.c_char_p),
                ("textbytes", ctypes.c_int32)]


def convertPropertyName(p_name):
    """"Regularizes" a property name. We are using all lowercase names with
    the spaces replaced by underscores.
    @param p_name The property name string to regularize.
    @return The regularized property name."""

    a = p_name.decode('ascii')
    b = a.lower()
    c = b.replace(" ","_")
    return c

class DCAMException(Exception):
    """Monitor exceptions."""
    def __init__(self, message):
        Exception.__init__(self, message)



# dcam = ctypes.windll.dcamapi
#
# temp = ctypes.c_int32(0)
# if (dcam.dcam_init(None, ctypes.byref(temp), None) != DCAMERR_NOERROR):
#     raise DCAMException("DCAM initialization failed.")
# n_cameras = temp.value

class HCamData():
    """Hamamatsu camera data object.
    Initially I tried to use create_string_buffer() to allocate storage for the
    data from the camera but this turned out to be too slow. The software
    kept falling behind the camera and create_string_buffer() seemed to be the
    bottleneck."""

    def __init__(self, size):
        """Create a data object of the appropriate size.
        @param size The size of the data object in bytes."""

        self.np_array = numpy.empty((int(size/2), 1), dtype=numpy.uint16)
        self.size = size

    ## __getitem__
    #
    # @param slice The slice of the item to get.
    #
    def __getitem__(self, slice):
        return self.np_array[slice]


    ## copyData
    #
    # Uses the C memmove function to copy data from an address in memory
    # into memory allocated for the numpy array of this object.
    #
    # @param address The memory address of the data to copy.
    #
    def copyData(self, address):
        ctypes.memmove(self.np_array.ctypes.data, address, self.size)

    ## getData
    #
    # @return A numpy array that contains the camera data.
    #
    def getData(self):
        return self.np_array

    ## getDataPtr
    #
    # @return The physical address in memory of the data.
    #
    def getDataPtr(self):
        return self.np_array.ctypes.data


class HamamatsuCamera():
    CAPTUREMODE_SNAP = 0
    CAPTUREMODE_SEQUENCE = 1
    """Basic camera interface class.
    This version uses the Hamamatsu library to allocate camera buffers.
    Storage for the data from the camera is allocated dynamically and
    copied out of the camera buffers."""

    def __init__(self, camera_id):
        """Open the connection to the camera specified by camera_id.
        @param camera_id The id of the camera (an integer)."""

        self.buffer_index = 0
        self.camera_id = camera_id
        self.dcam = ctypes.windll.dcamapi

        self.debug = False
        self.frame_bytes = 0
        self.frame_x = 0
        self.frame_y = 0
        self.last_frame_number = 0
        self.properties = {}
        self.max_backlog = 0
        self.number_image_buffers = 0

        # Open the camera.
        self.camera_handle = ctypes.c_void_p(0)
        self.temp = ctypes.c_int32(0)
        if (self.dcam.dcam_init(None, ctypes.byref(self.temp), None) != DCAMERR_NOERROR):
            raise DCAMException("DCAM initialization failed.")
        self.n_cameras = self.temp.value

        self.checkStatus(self.dcam.dcam_open(ctypes.byref(self.camera_handle),
                                        ctypes.c_int32(self.camera_id),
                                        None),
                         "dcam_open")
        self.camera_model = self.getModelInfo(camera_id)
        # Get camera properties.
        self.properties = self.getCameraProperties()

        # Get camera max width, height.
        self.max_width = self.getPropertyValue("image_width")[0]
        self.max_height = self.getPropertyValue("image_height")[0]
        self.setmode(self.CAPTUREMODE_SEQUENCE) # By default is a sequence
        self.setPropertyValue("output_trigger_kind[0]", 3)
        self.setPropertyValue("output_trigger_period[0]", 0.003)
        self.setPropertyValue("output_trigger_source[0]", 2)

    def settrigger(self,mode):
        TRIGMODE = ctypes.c_int32(mode)
        self.checkStatus(self.dcam.dcam_settriggermode(self.camera_handle,TRIGMODE),'settriggermode')
        DCAM_TRIGGERMODE = ctypes.c_int32(0)
        self.checkStatus(self.dcam.dcam_gettriggermode(self.camera_handle,ctypes.byref(DCAM_TRIGGERMODE)),'gettrigermode')
        return DCAM_TRIGGERMODE.value

    def setmode(self, mode):
        """Sets the acquisition mode of the camera."""
        self.mode = mode

    def initCamera(self):
        #
        # Initialization
        #
        #self.dcam = ctypes.windll.dcamapi


        self.captureSetup()

    def captureSetup(self):
        """Capture setup (internal use only). This is called at the start
        of new acquisition sequence to determine the current ROI and
        get the camera configured properly."""

        self.buffer_index = -1
        self.last_frame_number = 0

        # Set sub array mode.
        self.setSubArrayMode()

        # Get frame properties.
        self.frame_x = self.getPropertyValue("image_width")[0]
        self.frame_y = self.getPropertyValue("image_height")[0]
        self.frame_bytes = self.getPropertyValue("image_framebytes")[0]

        # Set capture mode.
        self.checkStatus(self.dcam.dcam_precapture(self.camera_handle,
                                              ctypes.c_int(self.mode)),
                         "dcam_precapture")


    def checkStatus(self, fn_return, fn_name= "unknown"):
        """Check return value of the dcam function call.
        Throw an error if not as expected?
        @return The return value of the function."""

        #if (fn_return != DCAMERR_NOERROR) and (fn_return != DCAMERR_ERROR):
        #    raise DCAMException("dcam error: " + fn_name + " returned " + str(fn_return))
        if (fn_return == DCAMERR_ERROR):
            c_buf_len = 80
            c_buf = ctypes.create_string_buffer(c_buf_len)
            c_error = self.dcam.dcam_getlasterror(self.camera_handle,
                                             c_buf,
                                             ctypes.c_int32(c_buf_len))
            raise DCAMException("dcam error " + str(fn_name) + " " + str(c_buf.value))
            #print "dcam error", fn_name, c_buf.value
        return fn_return

    def getCameraProperties(self):
        """Return the ids & names of all the properties that the camera supports. This
        is used at initialization to populate the self.properties attribute.
        @return A python dictionary of camera properties."""

        c_buf_len = 64
        c_buf = ctypes.create_string_buffer(c_buf_len)
        properties = {}
        prop_id = ctypes.c_int32(0)

        # Reset to the start.
        ret = self.dcam.dcam_getnextpropertyid(self.camera_handle,
                                          ctypes.byref(prop_id),
                                          ctypes.c_int32(DCAMPROP_OPTION_NEAREST))
        if (ret != 0) and (ret != DCAMERR_NOERROR):
            self.checkStatus(ret, "dcam_getnextpropertyid")

        # Get the first property.
        ret = self.dcam.dcam_getnextpropertyid(self.camera_handle,
                                          ctypes.byref(prop_id),
                                          ctypes.c_int32(DCAMPROP_OPTION_NEXT))
        if (ret != 0) and (ret != DCAMERR_NOERROR):
            self.checkStatus(ret, "dcam_getnextpropertyid")
        self.checkStatus(self.dcam.dcam_getpropertyname(self.camera_handle,
                                                   prop_id,
                                                   c_buf,
                                                   ctypes.c_int32(c_buf_len)),
                         "dcam_getpropertyname")

        # Get the rest of the properties.
        last = -1
        while prop_id.value != last:
            last = prop_id.value
            properties[convertPropertyName(c_buf.value)] = prop_id.value
            ret = self.dcam.dcam_getnextpropertyid(self.camera_handle,
                                              ctypes.byref(prop_id),
                                              ctypes.c_int32(DCAMPROP_OPTION_NEXT))
            if (ret != 0) and (ret != DCAMERR_NOERROR):
                self.checkStatus(ret, "dcam_getnextpropertyid")
            self.checkStatus(self.dcam.dcam_getpropertyname(self.camera_handle,
                                                       prop_id,
                                                       c_buf,
                                                       ctypes.c_int32(c_buf_len)),
                             "dcam_getpropertyname")
        return properties

    def fireTrigger(self):
        """Triggers the camera when in software mode."""
        self.checkStatus(self.dcam.dcam_firetrigger(self.camera_handle),"dcam_firetrigger")
        print('TRIG')

    def getFrames(self):
        """Gets all of the available frames.
        This will block waiting for new frames even if
        there new frames available when it is called.
        @return [frames, [frame x size, frame y size]]."""

        frames = []
        for n in self.newFrames():

            # Lock the frame in the camera buffer & get address.
            data_address = ctypes.c_void_p(0)
            row_bytes = ctypes.c_int32(0)
            self.checkStatus(self.dcam.dcam_lockdata(self.camera_handle,
                                                ctypes.byref(data_address),
                                                ctypes.byref(row_bytes),
                                                ctypes.c_int32(n)),
                             "dcam_lockdata")

            # Create storage for the frame & copy into this storage.
            hc_data = HCamData(self.frame_bytes)
            hc_data.copyData(data_address)

            # Unlock the frame.
            #
            # According to the documentation, this would be done automatically
            # on the next call to lockdata, but we do this anyway.
            self.checkStatus(self.dcam.dcam_unlockdata(self.camera_handle),
                             "dcam_unlockdata")

            frames.append(hc_data)

        return [frames, [self.frame_x, self.frame_y]]

    def getModelInfo(self, camera_id):
        """Returns the model of the camera
        @param camera_id The (integer) camera id number.
        @return A string containing the camera name."""

        c_buf_len = 20
        c_buf = ctypes.create_string_buffer(c_buf_len)
        self.checkStatus(self.dcam.dcam_getmodelinfo(ctypes.c_int32(camera_id),
                                                ctypes.c_int32(DCAM_IDSTR_MODEL),
                                                c_buf,
                                                ctypes.c_int(c_buf_len)),
                         "dcam_getmodelinfo")
        return c_buf.value

    def getProperties(self):
        """Return the list of camera properties. This is the one to call if you
        want to know the camera properties.
        @return A dictionary of camera properties."""

        return self.properties

    def getPropertyAttribute(self, property_name):
        """Return the attribute structure of a particular property.
        FIXME (OPTIMIZATION): Keep track of known attributes?
        @param property_name The name of the property to get the attributes of.
        @return A DCAM_PARAM_PROPERTYATTR object."""

        p_attr = DCAM_PARAM_PROPERTYATTR()
        p_attr.cbSize = ctypes.sizeof(p_attr)
        p_attr.iProp = self.properties[property_name]
        ret = self.checkStatus(self.dcam.dcam_getpropertyattr(self.camera_handle,
                                                         ctypes.byref(p_attr)),
                               "dcam_getpropertyattr")
        if (ret == 0):
            print(" property %s is not supported" % property_name)
            return False
        else:
            return p_attr

    def getPropertyText(self, property_name):
        """Return the text options of a property (if any).
        @param property_name The name of the property to get the text values of.
        @return A dictionary of text properties (which may be empty)."""

        prop_attr = self.getPropertyAttribute(property_name)
        if not (prop_attr.attribute & DCAMPROP_ATTR_HASVALUETEXT):
            return {}
        else:
            # Create property text structure.
            prop_id = self.properties[property_name]
            v = ctypes.c_double(prop_attr.valuemin)

            prop_text = DCAM_PARAM_PROPERTYVALUETEXT()
            c_buf_len = 64
            c_buf = ctypes.create_string_buffer(c_buf_len)
            #prop_text.text = ctypes.c_char_p(ctypes.addressof(c_buf))
            prop_text.cbSize = ctypes.c_int32(ctypes.sizeof(prop_text))
            prop_text.iProp = ctypes.c_int32(prop_id)
            prop_text.value = v
            prop_text.text = ctypes.addressof(c_buf)
            prop_text.textbytes = c_buf_len

            # Collect text options.
            done = False
            text_options = {}
            while not done:
                # Get text of current value.
                self.checkStatus(self.dcam.dcam_getpropertyvaluetext(self.camera_handle,
                                                                ctypes.byref(prop_text)),
                                 "dcam_getpropertyvaluetext")
                text_options[prop_text.text] = int(v.value)

                # Get next value.
                ret = self.dcam.dcam_querypropertyvalue(self.camera_handle,
                                                   ctypes.c_int32(prop_id),
                                                   ctypes.byref(v),
                                                   ctypes.c_int32(DCAMPROP_OPTION_NEXT))
                prop_text.value = v
                if ret == 0:
                    done = True

            return text_options

    def getPropertyRange(self, property_name):
        """Return the range for an attribute.
        @param property_name The name of the property (as a string).
        @return [minimum value, maximum value]."""

        prop_attr = self.getPropertyAttribute(property_name)
        temp = prop_attr.attribute & DCAMPROP_TYPE_MASK
        if (temp == DCAMPROP_TYPE_REAL):
            return [float(prop_attr.valuemin), float(prop_attr.valuemax)]
        else:
            return [int(prop_attr.valuemin), int(prop_attr.valuemax)]

    def getPropertyRW(self, property_name):
        """Return if a property is readable / writeable.
        @return [True/False (readable), True/False (writeable)]."""

        prop_attr = self.getPropertyAttribute(property_name)
        rw = []

        # Check if the property is readable.
        if (prop_attr.attribute & DCAMPROP_ATTR_READABLE):
            rw.append(True)
        else:
            rw.append(False)

        # Check if the property is writeable.
        if (prop_attr.attribute & DCAMPROP_ATTR_WRITABLE):
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
        prop_id = self.properties[property_name]

        # Get the property attributes.
        prop_attr = self.getPropertyAttribute(property_name)

        # Get the property value.
        c_value = ctypes.c_double(0)
        self.checkStatus(self.dcam.dcam_getpropertyvalue(self.camera_handle,
                                                    ctypes.c_int32(prop_id),
                                                    ctypes.byref(c_value)),
                         "dcam_getpropertyvalue")

        # Convert type based on attribute type.
        temp = prop_attr.attribute & DCAMPROP_TYPE_MASK
        if (temp == DCAMPROP_TYPE_MODE):
            prop_type = "MODE"
            prop_value = int(c_value.value)
        elif (temp == DCAMPROP_TYPE_LONG):
            prop_type = "LONG"
            prop_value = int(c_value.value)
        elif (temp == DCAMPROP_TYPE_REAL):
            prop_type = "REAL"
            prop_value = c_value.value
        else:
            prop_type = "NONE"
            prop_value = False

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


    def newFrames(self):
        """Return a list of the ids of all the new frames since the last check.
        This will block waiting for at least one new frame.
        @return [id of the first frame, .. , id of the last frame]
        """

        # Wait for a new frame.
        dwait = ctypes.c_int(DCAMCAP_EVENT_FRAMEREADY)
        self.checkStatus(self.dcam.dcam_wait(self.camera_handle,
                                        ctypes.byref(dwait),
                                        ctypes.c_int(DCAMWAIT_TIMEOUT_INFINITE),
                                        None),
                         "dcam_wait")

        # Check how many new frames there are.
        b_index = ctypes.c_int32(0)  # Is pointer to receive the number of the frame in which the most recent data is stored.
        f_count = ctypes.c_int32(0)  # is pointer to receive the number of frames captured since the capture operation was begun. If no frames have been captured, a value of –1 is returned
        self.checkStatus(self.dcam.dcam_gettransferinfo(self.camera_handle,
                                                   ctypes.byref(b_index),
                                                   ctypes.byref(f_count)),
                         "dcam_gettransferinfo")

        # Check that we have not acquired more frames than we can store in our buffer.
        # Keep track of the maximum backlog.
        cur_frame_number = f_count.value
        backlog = cur_frame_number - self.last_frame_number
        if backlog > self.number_image_buffers:
            print("warning: hamamatsu camera frame buffer overrun detected!")
        if backlog > self.max_backlog:
            self.max_backlog = backlog
        self.last_frame_number = cur_frame_number

        cur_buffer_index = b_index.value

        # Create a list of the new frames.
        new_frames = []
        if cur_buffer_index < self.buffer_index:
            for i in range(self.buffer_index + 1, self.number_image_buffers):
                new_frames.append(i)
            for i in range(cur_buffer_index + 1):
                new_frames.append(i)
        else:
            for i in range(self.buffer_index, cur_buffer_index):
                new_frames.append(i+1)
        self.buffer_index = cur_buffer_index

        if self.debug:
            print(new_frames)

        return new_frames

    def setPropertyValue(self, property_name, property_value):
        """Set the value of a property.
        @param property_name The name of the property.
        @param property_value The value to set the property to.
        """

        # Check if the property exists.
        if not (property_name in self.properties):
            print(" unknown property name: %s"%property_name)
            return False

        # If the value is text, figure out what the
        # corresponding numerical property value is.
        if (type(property_value) == type("")):
            text_values = self.getPropertyText(property_name)
            if (property_value in text_values):
                property_value = float(text_values[property_value])
            else:
                print(" unknown property text value: %s for %s"%(property_value, property_name))
                return False

        # Check that the property is within range.
        [pv_min, pv_max] = self.getPropertyRange(property_name)
        if (property_value < pv_min):
            print(" set property value %s is less than minimum of %s %s setting to minimum"%(property_value,pv_min,property_name))
            property_value = pv_min
        if (property_value > pv_max):
            print( " set property value %s is greater than maximum of %s %s setting to maximum"%(property_value,pv_min,property_name))
            property_value = pv_max

        # Set the property value, return what it was set too.
        prop_id = self.properties[property_name]
        p_value = ctypes.c_double(property_value)
        self.checkStatus(self.dcam.dcam_setgetpropertyvalue(self.camera_handle,
                                                       ctypes.c_int32(prop_id),
                                                       ctypes.byref(p_value),
                                                       ctypes.c_int32(DCAM_DEFAULT_ARG)),
                         "dcam_setgetpropertyvalue")
        return p_value.value

    def setSubArrayMode(self):
        """This sets the sub-array mode as appropriate based on the current ROI."""

        # Check ROI properties.
        roi_w = self.getPropertyValue("subarray_hsize")[0]
        roi_h = self.getPropertyValue("subarray_vsize")[0]
        # If the ROI is smaller than the entire frame turn on subarray mode
        if roi_w == self.max_width and roi_h == self.max_height:
            self.setPropertyValue("subarray_mode", 1)  # OFF
        else:
            self.setPropertyValue("subarray_mode", 2)  # ON

    def startAcquisition(self):
        """ Start data acquisition."""
        self.captureSetup()

        # Allocate Hamamatsu image buffers.
        # We allocate enough to buffer 2 seconds of data.
        n_buffers = int(2.0*self.getPropertyValue("internal_frame_rate")[0])
        self.number_image_buffers = n_buffers
        self.checkStatus(self.dcam.dcam_allocframe(self.camera_handle,
                                              ctypes.c_int32(self.number_image_buffers)),
                         "dcam_allocframe")

        # Start acquisition.
        self.checkStatus(self.dcam.dcam_capture(self.camera_handle),
                         "dcam_capture")

    def stopAcquisition(self):
        """Stop data acquisition."""

        self.checkStatus(self.dcam.dcam_idle(self.camera_handle),
                         "dcam_idle")

        print("max camera backlog was %s of %s"%(self.max_backlog, self.number_image_buffers))
        self.max_backlog = 0

        # Free image buffers.
        self.number_image_buffers = 0
        self.checkStatus(self.dcam.dcam_freeframe(self.camera_handle),
                         "dcam_freeframe")

    def shutdown(self):
        """Close down the connection to the camera."""
        self.checkStatus(self.dcam.dcam_close(self.camera_handle),
                         "dcam_close")


class HamamatsuCameraMR(HamamatsuCamera):
    """# Memory recycling camera class.
    This version allocates "user memory" for the Hamamatsu camera
    buffers. This memory is also the location of the storage for
    the np_array element of a HCamData() class. The memory is
    allocated once at the beginning, then recycled. This means
    that there is a lot less memory allocation & shuffling compared
    to the basic class, which performs one allocation and (I believe)
    two copies for each frame that is acquired.
    WARNING: There is the potential here for chaos. Since the memory
      is now shared there is the possibility that downstream code
      will try and access the same bit of memory at the same time
      as the camera and this could end badly.
    FIXME: Use lockbits (and unlockbits) to avoid memory clashes?
      This would probably also involve some kind of reference counting
      scheme."""

    def __init__(self, camera_id):
        """@param camera_id The id of the camera."""

        HamamatsuCamera.__init__(self, camera_id)

        self.hcam_data = []
        self.hcam_ptr = False
        self.old_frame_bytes = -1

        self.setPropertyValue("output_trigger_kind[0]", 2)

    def getFrames(self):
        """Gets all of the available frames.
        This will block waiting for new frames even if there new frames
        available when it is called.
        FIXME: It does not always seem to block? The length of frames can
               be zero. Are frames getting dropped? Some sort of race condition?
        return [frames, [frame x size, frame y size]]
        """

        frames = []
        for n in self.newFrames():
            frames.append(self.hcam_data[n])

        return [frames, [self.frame_x, self.frame_y]]

    def startAcquisition(self):
        """Allocate as many frames as will fit in 2GB of memory and start data acquisition."""
        self.captureSetup()

        # Allocate new image buffers if necessary.
        # Allocate as many frames as can fit in 2GB of memory.
        if (self.old_frame_bytes != self.frame_bytes):

            n_buffers = int((0.1 * 1024 * 1024 * 1024)/self.frame_bytes)
            self.number_image_buffers = n_buffers

            # Allocate new image buffers.
            ptr_array = ctypes.c_void_p * self.number_image_buffers
            self.hcam_ptr = ptr_array()
            self.hcam_data = []
            for i in range(self.number_image_buffers):
                hc_data = HCamData(self.frame_bytes)
                self.hcam_ptr[i] = hc_data.getDataPtr()
                self.hcam_data.append(hc_data)

            self.old_frame_bytes = self.frame_bytes

        # Attach image buffers.
        #
        # We need to attach & release for each acquisition otherwise
        # we'll get an error if we try to change the ROI in any way
        # between acquisitions.
        self.checkStatus(dcam.dcam_attachbuffer(self.camera_handle,
                                                self.hcam_ptr,
                                                ctypes.sizeof(self.hcam_ptr)),
                         "dcam_attachbuffer")

        # Start acquisition.
        self.checkStatus(dcam.dcam_capture(self.camera_handle),
                         "dcam_capture")



    def stopAcquisition(self):
        """Stops the acquisition and releases the memory associated with the frames."""

        # Stop acquisition.
        self.checkStatus(dcam.dcam_idle(self.camera_handle),
                         "dcam_idle")

        # Release image buffers.
        if (self.hcam_ptr):
            self.checkStatus(dcam.dcam_releasebuffer(self.camera_handle),
                             "dcam_releasebuffer")

        print("max camera backlog was: %s"%self.max_backlog)
        self.max_backlog = 0


#
# Testing.
#
if __name__ == "__main__":
    print('MAIN')

    print ("found: %s cameras"%n_cameras)
    if (n_cameras > 0):

        hcam = HamamatsuCamera(0)
        print(hcam.setPropertyValue("defect_correct_mode", 1))
        print("camera 0 model:", hcam.getModelInfo(0))

        # List support properties.
        if 0:
            print("Supported properties:")
            props = hcam.getProperties()
            for i, id_name in enumerate(sorted(props.keys())):
                [p_value, p_type] = hcam.getPropertyValue(id_name)
                p_rw = hcam.getPropertyRW(id_name)
                read_write = ""
                if (p_rw[0]):
                    read_write += "read"
                if (p_rw[1]):
                    read_write += ", write"
                print("  %s)%s = %s type is:%s,%s"%(i,id_name,p_value,p_type,read_write))
                text_values = hcam.getPropertyText(id_name)
                if (len(text_values) > 0):
                    print("          option / value")
                    for key in sorted(text_values, key = text_values.get):
                        print("         %s/%s"%(key,text_values[key]))

        # Test setting & getting some parameters.
        if 1:
            print(hcam.setPropertyValue("exposure_time", 0.001))

            #print(hcam.setPropertyValue("subarray_hsize", 2048))
            #print(hcam.setPropertyValue("subarray_vsize", 2048))
            print(hcam.setPropertyValue("subarray_hpos", 512))
            print(hcam.setPropertyValue("subarray_vpos", 512))
            print(hcam.setPropertyValue("subarray_hsize", 1024))
            print(hcam.setPropertyValue("subarray_vsize", 1024))

            print(hcam.setPropertyValue("binning", "1x1"))
            print(hcam.setPropertyValue("readout_speed", 2))

            hcam.setSubArrayMode()
            hcam.startAcquisition()
            hcam.stopAcquisition()

            params = ["internal_frame_rate",
                      "timing_readout_time",
                      "exposure_time",
                      "image_height",
                      "image_width",
                      "image_framebytes",
                      #"buffer_framebytes",
                      #"buffer_rowbytes",
                      #"buffer_top_offset_bytes",
                      "subarray_hsize",
                      "subarray_vsize",
                      "binning"]
            for param in params:
                print(param, hcam.getPropertyValue(param)[0])

        # Test acquisition.
        if 0:
            import numpy as np
            import matplotlib.pyplot as plt
            hcam.startAcquisition()
            cnt = 1
            for i in range(300):
                [frames, dims] = hcam.getFrames()
                for aframe in frames:
                    print(cnt, aframe[0:5])
                    cnt += 1

            hcam.stopAcquisition()
            plt.imshow(aframe)
            plt.show()


#
# The MIT License
#
# Copyright (c) 2013 Zhuang Lab, Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
