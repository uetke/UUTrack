.. _starting:

Start the program
=================

To run the program you can just import the startCamera module from the root of UUTrack and trigger it with a config file::

   from UUTrack import startCamera

   ConfigDir = 'Path/to/config'
   ConfigFile = 'config.yml'
   startCamera.start(ConfigDir, ConfigFile)

Note that the splitting between the config directory and the config file is done to allow users to have different config files in the same directory, for example for different configurations of the setup. It also allows to include a pre-window to select with a GUI the desired configuration and then trigger the ```startCamera.start``` method.

It is important to have a Config file ready for the program to run properly. You can check the example :ref:`config`