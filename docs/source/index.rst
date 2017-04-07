.. UUTracking documentation master file, created by
   sphinx-quickstart on Fri Mar 31 13:48:19 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

UUTracking
==========

**A powerful interface for scientific cameras and instruments**

UUtracking is shipped as a package that can be installed into a virtual environment with the use of pip. It can be both triggered with a built in function or can be included into larger projects.

Installing
----------

The best place to look for the code of the program is the repository at ``https://github.com/aquilesC/UUTrack``. If you need further assistance with the installation of the code, please check :ref:`installing`

Start the program
-----------------
To run the program you can just import the startCamera module from the root of UUTrack and trigger it with a config file::

   from UUTrack import startCamera

   ConfigDir = 'Path/to/config'
   ConfigFile = 'config.yml'
   startCamera.start(ConfigDir, ConfigFile)

Note that the splitting between the config directory and the config file is done to allow users to have different config files in the same directory, for example for different configurations of the setup. It also allows to include a pre-window to select with a GUI the desired configuration and then trigger the ```startCamera.start``` method.

It is important to have a Config file ready for the program to run properly. You can check the example :ref:`config`

Changing the code
-----------------
The program is open source and therefore you can modify all what you want. You have to remember that the code was written with a specific experiment in mind and therefore it may not fulfill or the requirements of more advanced imaging software.

However the design of the program is such that would allow its expansion to meet future needs. In case you are wondering how the code can be improved you can start by reading :ref:`improving`, or directly submerge yourself in the documentation of the different classes :ref:`UUTrack`.

If you want to start right away to improve the code, you can always look at the :ref:`todo`.

.. note:: The naming convention through the code is not very uniform. I've tried to use CamelCase for classes, and underscores for variables, but this has to be sanitized for making it more consistent. Sometimes classes and variables are called the same, making everything very confusing.


.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents:

   modules
   config
   python_working
   installing
   starting
   improving
   UUTrack
   todo


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
