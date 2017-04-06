Setting up a Python working environment
=======================================

This guide is thought for users on Windows willing to either use python 2.7 or 3+

1. Download the version of python you want from https://www.python.org/downloads/windows/ and install it

2. It may be that in Windows after the installation, python is not added to the path, don't worry things are going to be sorted out later.

3. Get pip from::

    bootstrap.pypa.io/get-pip.py

4. Run::

    path/to/python/python.exe get-pip.py

5. Go to ``path/to/python/Scripts``

6. Run::

    pip.exe install virtualenv
    pip.exe install virtualenvwrapper-powershell

At this point you have a working installation of virtual environment that will allow you to isolate your development from your computer, ensuring no mistakes on versions will happen.
Let's create a new working environment called Testing

7. Run::

    virtualenv.exe Testing --python=path\to\python\python.exe

The last piece is important, because it will allow you to select the exact version of python you want to run, it can be either ``python2`` or ``python 3`` and also it can be Python 64 or 32 bit.
You will also create a folder called Testing, in which all the packages you are going to install are going to be kept.

8. Go to the folder ``Testing\Scripts``. Try to run ``activate.bat``
If an error happens (most likely) follow the instructions below.
Windows has a weird way of handling execution policies and we are going to change that.
Open PowerShell with administrator rights (normally, just right click on it and select run as administrator)
Run the following command::

    Set-ExecutionPolicy RemoteSigned

This will allow to run local scripts.
Go back to the PowerShell without administrative rights and run again the script activate

9. Now you are working on a safe development environment. If you just type python you will see that you are running the exact version you wanted. The same goes for packages, you can download specific versions, completely isolated from what is happening in the computer. Imagine there is more than one user and one decides to use numpy 64-bit but you need numpy 32-bit, you both can work isolated from each other.
 Moreover, if you run::

    pip freeze > requirements.txt

You are going to generate a file (requirements.txt) with all the installed packages at that given time

10. For developing GUI's, most likely we are going to use PyQt. Since there is no official repository to install it through pip, we need to download the appropriate wheel from::

    http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4

Afterwards, just run (replacing the last part of the command by the wheel you have just downloaded)::

    pip install PyQt4‑4.11.4‑cp36‑cp36m‑win32.whl

This last bit is useful for people dealing with large datasets, or people who would like to store not only data but also metadata in a future-proof binary file format.

11. For saving data, specially when dealing with big datasets, there is almost nothing better than using HDF5 (https://support.hdfgroup.org/HDF5/). For installing, follow the same procedures than with PyQt, you can find the wheel here:
``http://www.lfd.uci.edu/~gohlke/pythonlibs/#h5py``

Note: *h5py* requires to have some Visual Basic distributables. Go to
``http://landinghub.visualstudio.com/visual-cpp-build-tools``
to download and install. HDF5 is particularly useful when the dataset is bigger than the memory available, since it writes/reads to disk but to the user everything is presented as an array. For example saving to disk is just asigning a value to a variable such as::

    dset[:,:,i] = img

This line would be writing to disk the 2D array img.
When reading::

        img = dset[:,:,1]

Would load to memory only one 2D array. For the documentation and understanding of how HDF5 works, I highly suggest reading the website::

    http://docs.h5py.org/en/latest/quick.html