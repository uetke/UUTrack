"""Best place to store variables that can be shared between different classes.
"""
import os
class _session():
    """Stores variables and other classes that are common to several UI or instances of the code.
    """
    def __init__(self):
        self.user = os.getlogin()
        self.base_dir = ''
        ######### PARAMETERS FOR THE QPD #########
        self.adq = {}
        self.monitorTimeresol = 5 # In ms -> resolution of the timetrace
        self.monitorRefresh = 500 # In ms -> Refresh time of the monitor interfase
        self.monitorTime = 10 # In seconds -> The length of the timetrace
        self.dev_conf = '' # Directory with the config file
        self.task_conf = '' # Directory with the task_config file
        self.adq = {} # Device used for data acquisition.
        self.monDevs = {} # Devices used for the monitor
        self.devs = {} # Devices in general
        self.runs = False # Continuous runs of high time accuracy acquisitions
        self.saveDirectory = '' # Directory where to save the data
        self.highSpeedTime = 1 # In seconds
        self.highSpeedAccuracy = .01 # In milliseconds
        ######### PARAMETERS FOR THE CAMERA #########
        self.camera = {}
        self.refreshTime = 60 # Time in ms for refreshing from the camera
        self.exposureTime = 1 # Exposure time of the camera
        self.ROIl = 0
        self.ROIr = 10
        self.ROIu = 10
        self.ROIb = 0
