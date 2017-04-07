.. _installing:

Installation instructions
=========================

To install UUTrack it is important to be inside of a virtual environment. If you want to set up a working environment, I suggest you to check :ref:`python_working`. From the command line you can run the following command::

   pip install -U https://github.com/aquilesC/UUTrack/archive/master.zip

Remember that in this case master refers to the branch you are installing. In case you want to work with specific branches of the code, you should change it.

If you are planning to develop code (you need to change, correct a bug or whatever is present), you need to install the package in an editable way. Just run::

   pip install -e git+git@github.com:aquilesC/UUTrack.git#egg=UUTrack

This will install the package inside of your virtual environment and will generate a copy of the repository in virtualenv/src/UUTrack that you can edit and push to the repository of your choice. This is very handy when you want to test new features, etc. It is also possible to work with different branches, making it very easy to keep track of the changes in the upstream code.

After you have installed the program, you can check how to :ref:`starting`