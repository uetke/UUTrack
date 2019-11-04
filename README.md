# UUTtracking for Potiodynamics Scattering Microscopy v0.2 #
_A nanoLINX instrumentation project based on the Pynta module, previously UUTrack_

This program can be used for monitoring a CCD camera. The structure allows to perform high framerate acquisitions while displaying the images to the user at a configurable rate. Data can be accumulated in a queue for saving while acquiring or saving retroactively.

The GUI has the possibility to show a waterfall and change the ROI of the camera by dragging vertical and horizontal lines. 

The program also allows to trigger special tasks in a separate thread. To activate this option, the user needs to move the mouse on the image while pressing the **Ctrl** button. Pressing **Ctrl+C** triggers the special task, **Ctrl+V** stops it. **Shift+C**  clears the crosshair from the screen. 

To acquire a cross cut of the image and display the standard deviation to mean ratio, press the **Alt** key while moving the mouse over the image. This also works live.

## Documentation ## 
The documentation can be built in the `docs` folder by using sphinx. The documentation for the ori can also be found at

http://documents.uetke.com/UUTracking/
http://uutrack.readthedocs.io/en/latest/

## Installation ##
To install UUTrack it is important to be inside of a virtual environment. To install the code clone it to your lab computer using your own user. This allows you to easily update and track changes. Always keep the tested version in the master branch to be sure that you can run the setup without difficulty.

## Running the program ##
Once you have installed the package, enter the virtual environment and run the following commands to bring up the GUI:

```python
 <virtualENV> Python startProgram.py
```

## Building the documentation
The documentation of the program can be built locally and is available at http://uutrack.readthedocs.io.

To build the documentation locally, you need to have sphinx installed. Go to the folder docs and run the following command:

```python
    sphinx-build -b html source/ build/
```

This will build all the documentation from the source folder into the build folder. Remember that for it to work, the program needs to import every module, therefore you can't build the documentation if you don't have the dependencies in order.

## Software for monitoring a CCD. ##
The program follows the Model-View-Controller design structure. This allows a rapid exchange of different parts of the code.


### Structure of the folders: ###
UUTrap: Main folder. Important executables should be placed here.

* _Controller_ : Houses the files related to periferals, such as python wrappers for cameras. They are organized inside of folders according to the brand. The idea is to copy/paste wrappers already available, without worrying for specific implementations.

* _Model_: Houses the intermediate steps between model and View. It handles the conditioning of data before being presented to the user. A model has to be defined for each different camera and for each different experiment. The skeleton should house all the used functions exposed to the user, in this way, if an implementation has the same functions with the same outputs, nothing will break downstream. Each class here inherits directly from the Controller device; this allows to access lower-level functionality without explicitly importing the Controller modules.

* _View_: Houses everything related to visualization of data. View should communicate only through models to devices and should get the input from the user. Acquisition tasks should be performed in a different thread, in order not to block the GUI. A timer updates the GUI at constant intervals, while the acquisition can happen at a different rate.

## Screenshot ##

- to be added

### Workplan and Issue tracker ###

check [WORKPLAN](WORKPLAN.txt) file (please link here)