.. _improving:

Improving the code
==================
.. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>

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
:ref:`View` is where the GUI lives. But also is where the logic of our program is. **UUTrack** was built as a graphical program for controlling cameras, but in principle many experiments don't need a GUI, a command line interface would suffice. View is the most complex part of the program, since it handles a lot of asynchronous tasks, user interactions and more. The starting point for the View is the module :mod:`~UUTrack.View.Camera.cameraMain`. The module holds the main window and all the interactions between the different parts of the code.

Threading
^^^^^^^^^
Acquiring from cameras can be slow, for example one can set an exposure time of several seconds. It can also be very fast, acquiring an image every couple of milliseconds. The first example poses the problem of how to acquire without freezing the GUI presented to the user. The last example poses the problem of how to keep high acqusition framerates if the user will never see more than 30fps. The solution to both problems is Threading. Qt comes with a very handy threading class that is implemented in the :class:`~UUTrack.View.Camera.workerThread.workThread`. The worker runs in a separate thread and therefore its execution will not block the main GUI. When there is data available, it will emit a :ref:`signal`. This signal will be catch in the main program by the function :meth:`~UUTrack.View.Camera.cameraMain.cameraMain.getData`. This function stores the data in a variable called *tempImage*; if the proper parameters are set, the data is accumulated in a Queue.

The refreshing of the GUI happens at a fixed framerate given by a Timer. The function responsible is :meth:`~UUTrack.View.Camera.cameraMain.cameraMain.updateGUI`. This function will display the data available in the *tempImage* variable. It is important to note that this ensures a fixed framerate to the user, regardless of the acquisition done by the camera. If the data is being acquired much faster than what the user can see, there is no point at displaying it, and if the acquisition is too slow, there is no point in freezing the interaction until it is fetched.

Threading in Qt is a very powerful tool that has to be implemented in all the GUI programs. It ensures that the main Thread is responsive, while a background thread is busy acquiring, or performing some other operation, for example downloading data from the internet. Python offers threading, but without the signalling capabilities of Qt. Since the program is built around PyQt4 there is no point in not using it.

For stopping a Thread, the best strategy is to change the status of a variable that the thread checks periodically. In the case of :class:`~UUTrack.View.Camera.workerThread.workThread` is *self.keep_acquiring*. This strategy is used in :meth:`~UUTrack.View.Camera.cameraMain.cameraMain.stopMovie`. As an example on how to extend this, :class:`~UUTrack.View.Camera.specialTaskWorker.specialTaskWorker` implements a tracking algorithm and emits signals accordingly. It is very basic, but it pinpoints the direction that needs to be followed.

Controller
----------
The last part of the program are the :mod:`controllers <UUTrack.Controller>` for different devices. The focus of the entire UUTrack program are cameras. Controllers for cameras normally rely on library files (.dll files on Windows) that can be more or less documented. For example :mod:`~UUTrack.Controller.devices.hamamatsu` uses the *DCAM-API*, while :mod:`~UUTrack.Controller.devices.PhotonicScience` uses *scmoscam.dll*. The idea of having a Controller module separated from the Model module is the ability to copy pasting code from other sources. For example the Hamamatsu code is available on Zhuangs lab github repository, while the Photonic Science code was sent by the company itself.

Having separate modules for the controller and the model allows to share code between different setups making it more transparent for the users. For example, one may not need to set the ROI of the camera, therefore should not worry about implementing it. However learning from the *Models* of others can be extremely useful; for instance, Hamamatsu only allows to set ROI parameters that are multiple of 4. Moreover if you don't reset the ROI before changing it, the dll crashes. Photonic Science has its own share with setting the gain.

Between the controllers there is a module named :mod:`~UUTrack.Controller.devices.keysight` that holds the drivers for an oscilloscope and function generator. It works, but was never implemented into the main window. The idea is to use it in the :class:`~UUTrack.View.Camera.specialTaskWorker.specialTaskWorker` for generating signals or acquiring fast timetraces.
