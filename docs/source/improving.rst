.. _improving:

Improving the code
==================

The design pattern chosen for the program is called MVC, that stands for Model-View-Controller. This pattern splits the different attributions of the code in order to make it more reusable. It was popularized for the creation of websites, where the user is in front of his computer, triggering actions in a remote server. Without the factor of the distance, and experiment is the same: the user triggers actions on a device from his computer.

Model
-----
Model is a subpackage of the UUTrack program. Models define the way the user will interact with the devices. For example when dealing with a camera, one of the most likely actions is to set the exposure time, trigger an acquisition and read the image. How this is achieved is dependent on every camera.

Therefore in :ref:`UUTrack.Model` we will place classes that have always the same methods and outputs defined, but that behave completely different when communicating with the devices.