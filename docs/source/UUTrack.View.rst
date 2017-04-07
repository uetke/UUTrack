.. _view:

View Package
============
:ref:`View` is where the GUI lives. But also is where the logic of our program is. **UUTrack** was built as a graphical program for controlling cameras, but in principle many experiments don't need a GUI, a command line interface would suffice. View is the most complex part of the program, since it handles a lot of asynchronous tasks, user interactions and more. The starting point for the View is the module :mod:`~UUTrack.View.Camera.cameraMain`. The module holds the main window and all the interactions between the different parts of the code.

Threading
^^^^^^^^^
Acquiring from cameras can be slow, for example one can set an exposure time of several seconds. It can also be very fast, acquiring an image every couple of milliseconds. The first example poses the problem of how to acquire without freezing the GUI presented to the user. The last example poses the problem of how to keep high acqusition framerates if the user will never see more than 30fps. The solution to both problems is Threading. Qt comes with a very handy threading class that is implemented in the :class:`~UUTrack.View.Camera.workerThread.workThread`. The worker runs in a separate thread and therefore its execution will not block the main GUI. When there is data available, it will emit a :ref:`signal`. This signal will be catch in the main program by the function :meth:`~UUTrack.View.Camera.cameraMain.cameraMain.getData`. This function stores the data in a variable called *tempImage*; if the proper parameters are set, the data is accumulated in a Queue.

The refreshing of the GUI happens at a fixed framerate given by a Timer. The function responsible is :meth:`~UUTrack.View.Camera.cameraMain.cameraMain.updateGUI`. This function will display the data available in the *tempImage* variable. It is important to note that this ensures a fixed framerate to the user, regardless of the acquisition done by the camera. If the data is being acquired much faster than what the user can see, there is no point at displaying it, and if the acquisition is too slow, there is no point in freezing the interaction until it is fetched.

Threading in Qt is a very powerful tool that has to be implemented in all the GUI programs. It ensures that the main Thread is responsive, while a background thread is busy acquiring, or performing some other operation, for example downloading data from the internet. Python offers threading, but without the signalling capabilities of Qt. Since the program is built around PyQt4 there is no point in not using it.

For stopping a Thread, the best strategy is to change the status of a variable that the thread checks periodically. In the case of :class:`~UUTrack.View.Camera.workerThread.workThread` is *self.keep_acquiring*. This strategy is used in :meth:`~UUTrack.View.Camera.cameraMain.cameraMain.stopMovie`. As an example on how to extend this, :class:`~UUTrack.View.Camera.specialTaskWorker.specialTaskWorker` implements a tracking algorithm and emits signals accordingly. It is very basic, but it pinpoints the direction that needs to be followed.

Subpackages
-----------

.. toctree::
    :maxdepth: 1

    UUTrack.View.Camera
