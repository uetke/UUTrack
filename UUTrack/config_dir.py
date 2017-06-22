# -*- coding: utf-8 -*-
"""
    config_dir
    ----------
    Just stores a variable with the name of the current directory, that 
    is the base directory of the entire filesystem. 
"""
import os

f = """ 
%YAML 1.2
---
# Default parameters for the Tracking program
# All parameters can be changed to accommodate user needs.
# All parameters can be changed at runtime with the appropriate config window
User:
  name: ghost
  measurement: Sample

Saving:
  autosave_raw_images: False
  autosave_trajectory: True
  directory: C:\\tmp\\Data\\openCET
  filename_video: Video # Can be the same filename for video and photo
  filename_photo: Snap
  filename_waterfall: Waterfall
  filename_trajectory: Trajectory
  filename_log: Log
  max_memory: 800 # In megabytes

GUI:
  length_waterfall: 100 # Number of Waterfall lines collected before saving and refreshing
  vbin_waterfall: 20 # Number of pixels summed up at the vertical center of the captured frame for waterfall
  refresh_time: 100 # Refresh rate of the GUI (in ms)

Camera:
  camera: dummyCamera # the camera to use
  model: none
  exposure_time: 35 # Initial exposure time (in ms)
  binning_x: 1 # Binning
  binning_y: 1
  roi_x1: 0 # Leave at 0 for full camera
  roi_x2: 0
  roi_y1: 0
  roi_y2: 0
  future_background_method: [Method1, Method2]

Tracking: # implementation in progress, expect errors
  particle_size: 5 # expected particle size (FWHM) in pixels
  step_size: 1 # expected particle jump between frames for adjusting the search area
  noise_level: 100 # dark counts plus noise level, all values below will be set to zero for tracking an object
  future_view_track: [X-I, X-Y] # the desired type of track to view: x-intensity, or x-y coordinates
  future_localization_method: [CenMass, Fit] # localization method
  future_snr: 0 # expected signal to noise ratio, set to zero for automatic estimation

Debug:
  queue_memory: False
  to_screen: True
"""

if not os.path.exists('Config'):
    os.makedirs('Config')

file = open('Config/camera_defaults.yml','w')
file.write(f)
file.close()