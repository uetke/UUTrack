# UUTtracking v0.2 #
This program can be used for monitoring a CCD camera. The structure allows to perform high framerate acquisitions while displaying the images to the user at a configurable rate. Data can be accumulated in a queue for saving while acquiring or saving retroactively. 

The GUI has the possibility to show a waterfall and change the ROI of the camera by dragging vertical and horizontal lines. 

The program also allows to trigger special tasks in a separate thread. To activate this option, the user needs to move the mouse on the image while pressing the **Ctrl** button. Pressing **Ctrl+C** triggers the special task, **Ctrl+V** stops it. **Shift+C**  clears the crosshair from the screen. 

To acquire a cross cut of the image and display the standard deviation to mean ratio, press the **Alt** key while moving the mouse over the image. This also works live.

## Documentation
The documentation can be built in the `docs` folder by using sphinx. It can also be found at

http://documents.uetke.com/UUTracking/
http://uutrack.readthedocs.io/en/latest/

## Installation
To install UUTrack it is important to be inside of a virtual environment. From the command line you can run 

```
pip install -U https://github.com/aquilesC/UUTrack/archive/master.zip
```
Remember that in this case master refers to the branch you are installing. In case you want to work with specific branches of the code, you should change it. 

If you are planning to develop code (you need to change, correct a bug or whatever is present), you need to install the package in an editable way. Just run:

```
pip install -e git+git@github.com:aquilesC/UUTrack.git#egg=UUTrack 
```

This will install the package inside of your virtual environment and will generate a copy of the repository in virtualenv/src/UUTrack that you can edit and push to the repository of your choice. This is very handy when you want to test new features, etc.

### Installing your own fork of the code
A smarter way to install the code is to fork it to your own user and the run the previous command from there. This allows you to easily update and track changes without sending pull requests, etc.

## Running the program ##
Once you have installed the package, you can run the following commands to bring up the GUI:

```python
   from UUTrack import startCamera

   ConfigDir = 'Path/to/config'
   ConfigFile = 'config.yml'
   startCamera.start(ConfigDir, ConfigFile)
```

## Building the documentation
The documentation of the program can be build locally and is available at http://uutrack.readthedocs.io. 

To build the documentation locally, you need to have sphinx installed. Go to the folder docs and run the following command:

```python
    sphinx-build -b html source/ build/
```

This will build all the documentation from the source folder into the build folder. Remember that for it to work, the program needs to import every module, therefore you can't build the documentation if you don't have the dependencies in order.

## Software for monitoring a CCD.
The program follows the Model-View-Controller design structure. This allows a rapid exchange of different parts of the code.


### Structure of the folders: 
UUTrap: Main folder. Important executables should be placed here.

* _Controller_ : Houses the files related to periferals, such as python wrappers for cameras. They are organized inside of folders according to the brand. The idea is to copy/paste wrappers already available, without worrying for specific implementations.

* _Model_: Houses the intermediate steps between model and View. It handles the conditioning of data before being presented to the user. A model has to be defined for each different camera and for each different experiment. The skeleton should house all the used functions exposed to the user, in this way, if an implementation has the same functions with the same outputs, nothing will break downstream. Each class here inherits directly from the Controller device; this allows to access lower-level functionality without explicitly importing the Controller modules.

* _View_: Houses everything related to visualization of data. View should communicate only through models to devices and should get the input from the user. Acquisition tasks should be performed in a different thread, in order not to block the GUI. A timer updates the GUI at constant intervals, while the acquisition can happen at a different rate.

## Screenshot

![Alt text](UUTrack/docs/resources/screenshot.png?raw=true "Optional Title")

### Issues with the program

If you have any issues with this program, please refer to the issue tracker of Github. 