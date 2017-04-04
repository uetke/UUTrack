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
  name: Aquiles

Saving:
  auto_save: False
  directory: C:\\Users\\Aquiles\\Data
  filename_video: Video # Can be the same filename for video and photo
  filename_photo: Snap

GUI:
  length_waterfall: 100 # Total length of the Waterfall (lines)
  refresh_time: 100 # Refresh rate of the GUI (in ms)

Camera:
  camera: dummyCamera # the camera to use
  model: dummy
  exposure_time: 35 # Initial exposure time (in ms)
  binning_x: 1 # Binning
  binning_y: 1
  roi_x1: 0 # Leave at 0 for full camera
  roi_x2: 0
  roi_y1: 0
  roi_y2: 0
  background: '' # Full path to background file, or empty for none.
  background_method: [Method1, Method2]

Tracking: # Not yet implemented, will show up in the config window
  param_1: 0.
  param_2: 0
"""

if not os.path.exists('Config'):
    os.makedirs('Config')

file = open('Config/camera_defaults.yml','w')
file.write(f)
file.close()