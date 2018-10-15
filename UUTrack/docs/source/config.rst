.. _config:

Config File
===========

.. highlight:: yaml

The config file is a Yaml file that doesn't have predefined needs. Whatever is in it is passed to the session variable of the program. New fields can be added. However the program relies on some of the attributes for proper working; for example the camera model is used to import the proper model. The exposure time is set to the camera at the beginning. The path and filename for saving are also important.::

    %YAML 1.2
    ---
    # Default parameters for the Tracking program
    # All parameters can be changed to accommodate user needs.
    # All parameters can be changed at runtime with the appropriate config window
    User:
      name: Test Subject

    Saving:
      auto_save: False
      directory: C:\data\Testing
      filename_video: Video # Can be the same filename for video and photo
      filename_photo: Snap

    GUI:
      length_waterfall: 100 # Total length of the Waterfall (lines)
      refresh_time: 100 # Refresh rate of the GUI (in ms)

    Camera:
      camera: dummyCamera # the camera to use
      model: dummyModel # This hasn't been implemented, but is useful for metadata storing.
      exposure_time: 200 # Initial exposure time (in ms)
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


