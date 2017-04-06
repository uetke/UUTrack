.. UUTracking documentation master file, created by
   sphinx-quickstart on Fri Mar 31 13:48:19 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

UUTracking a powerful interface for scientific cameras and instruments
======================================

UUtracking is shipped as a package that can be installed into a virtual environment with the use of pip. It can be both triggered with a built in function or can be included into larger projects.

Installing
----------

To install UUTrack it is important to be inside of a virtual environment. If you want to set up a working environment, I suggest you to check :ref:`python.working`. From the command line you can run the following command::

   pip install -U https://github.com/aquilesC/UUTrack/archive/master.zip

Remember that in this case master refers to the branch you are installing. In case you want to work with specific branches of the code, you should change it.

If you are planning to develop code (you need to change, correct a bug or whatever is present), you need to install the package in an editable way. Just run::

   pip install -e git+git@github.com:aquilesC/UUTrack.git#egg=UUTrack

This will install the package inside of your virtual environment and will generate a copy of the repository in virtualenv/src/UUTrack that you can edit and push to the repository of your choice. This is very handy when you want to test new features, etc. It is also possible to work with different branches, making it very easy to keep track of the changes in the upstream code.

Your own fork of the code
-------------------------

A smarter way to install the code is to fork it to your own user and the run the previous command from there. This allows you to easily update and track changes without sending pull requests, etc.



.. toctree::
   :maxdepth: 8
   modules
   python.working
   :caption: Contents:



.. automodule:: UUTrack

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
