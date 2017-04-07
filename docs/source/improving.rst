.. _improving:

Improving the code
==================

The design pattern chosen for the program is called MVC, that stands for Model-View-Controller. This pattern splits the different attributions of the code in order to make it more reusable. It was popularized for the creation of websites, where the user is in front of his computer, triggering actions in a remote server. Without the factor of the distance, and experiment is the same: the user triggers actions on a device from his computer. Before starting to change the code, it is important to understand the structure of **UUTrack**.

Model
-----
Model is a subpackage of the UUTrack program. Models define the way the user will interact with the devices. For example when dealing with a camera, one of the most likely actions is to set the exposure time, trigger an acquisition and read the image. How this is achieved is dependent on every camera.

Therefore in :ref:`model` we will place classes that have always the same methods and outputs defined, but that behave completely different when communicating with the devices. The starting point is the :ref:`skeleton`, where the ``cameraBase`` class is defined. In this class all the methods and variables needed by the rest of the program are defined. This strategy not only allows to keep track of the functions, it also enables the subclassing, which will be discussed later.

Having models also allow to quickly change from one camera to another. For example, if one desires to switch from a :ref:`hamamatsu` to a :ref:`PSI`, the only needed thing to do is to replace::

    from UUTrack.Model.Cameras.Hamamatsu import camera

With::

    from UUTrack.Model.Cameras.PSI import camera

As you see, both modules ``Hamamatsu`` and ``PSI`` define a class called camera. And this classes will have the same methods defined, therefore whatever code relies on camera will be working just fine. One of the obvious advantages of having a Model is that we can define a :ref:`dummyCamera` that allows to test the code without being connected to any real device.

If you go through the code, you'll notice that the classes defined in Models inherit ``cameraBase`` for the :ref:`skeleton`. The quick advantage of this is that any function defined in the skeleton will be already available in the child objects. Therefore, if you want to add a new function, let's say ``set_gain``, one has to start by adding that method to the ``_skeleton``. This will make the function readily available to all the models, even if just as a mockup or to ``raise NotImplementedError``. Then we can overload the method by defining it again in the class we are working on. It may be that not all the cameras are able to set a gain, and we can just leave a function that ``return True``. If it is a functionality that you expect any camera to have, for example triggering an image, you can set the _skeleton function to ``raise NotImplementedError``. This will give a very descriptive error of what went wrong if you haven't implemented the function in your model class.

View
----
:ref:`View` is where the GUI lives. But also is where the logic of our program is. **UUTrack** was built as a graphical program for controlling cameras, but in principle many experiments don't need a GUI, a command line interface would suffice. 

