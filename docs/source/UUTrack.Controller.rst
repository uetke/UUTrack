Controller package
==========================

The last part of the program are the :mod:`controllers <UUTrack.Controller>` for different devices. The focus of the entire UUTrack program are cameras. Controllers for cameras normally rely on library files (.dll files on Windows) that can be more or less documented. For example :mod:`~UUTrack.Controller.devices.hamamatsu` uses the *DCAM-API*, while :mod:`~UUTrack.Controller.devices.PhotonicScience` uses *scmoscam.dll*. The idea of having a Controller module separated from the Model module is the ability to copy pasting code from other sources. For example the Hamamatsu code is available on Zhuangs lab github repository, while the Photonic Science code was sent by the company itself.

Having separate modules for the controller and the model allows to share code between different setups making it more transparent for the users. For example, one may not need to set the ROI of the camera, therefore should not worry about implementing it. However learning from the *Models* of others can be extremely useful; for instance, Hamamatsu only allows to set ROI parameters that are multiple of 4. Moreover if you don't reset the ROI before changing it, the dll crashes. Photonic Science has its own share with setting the gain.

Between the controllers there is a module named :mod:`~UUTrack.Controller.devices.keysight` that holds the drivers for an oscilloscope and function generator. It works, but was never implemented into the main window. The idea is to use it in the :class:`~UUTrack.View.Camera.specialTaskWorker.specialTaskWorker` for generating signals or acquiring fast timetraces.


Subpackages
-----------

.. toctree::
    :maxdepth: 1

    UUTrack.Controller.devices.hamamatsu
    UUTrack.Controller.devices.keysight
    UUTrack.Controller.devices.PhotonicScience


Module contents
---------------

.. automodule:: UUTrack.Controller
    :members:
    :show-inheritance:
