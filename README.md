# UUTtracking v0.1 #
This program can be used for monitoring a CCD camera. The structure allows to perform high framerate acquisitions while displaying the images to the user at a configurable rate. Data can be accumulated in a queue for saving while acquiring or saving retroactively. 

The GUI has the possibility to show a waterfall and change the ROI of the camera by dragging vertical and horizontal lines. 

The program also allows to trigger special tasks in a separate thread. To activate this option, the user needs to move the mouse on the image while pressing the **Ctrl** button. Pressing **Ctrl+C** triggers the special task, **Ctrl+V** stops it. **Shift+C**  clears the crosshair from the screen. 

## Software for monitoring a CCD. ##
The program follows the Model-View-Controller design structure. This allows a rapid exchange of different parts of the code.


### Structure of the folders: ###
UUTrap: Main folder. Important executables should be placed here.

* _Controller_ : Houses the files related to periferals, such as python wrappers for cameras. They are organized inside of folders according to the brand. The idea is to copy/paste wrappers already available, without worrying for specific implementations.

* _Model_: Houses the intermediate steps between model and View. It handles the conditioning of data before being presented to the user. A model has to be defined for each different camera and for each different experiment. The skeleton should house all the used functions exposed to the user, in this way, if an implementation has the same functions with the same outputs, nothing will break downstream. Each class here inherits directly from the Controller device; this allows to access lower-level functionality without explicitly importing the Controller modules.

* _View_: Houses everything related to visualization of data. View should communicate only through models to devices and should get the input from the user. Acquisition tasks should be performed in a different thread, in order not to block the GUI. A timer updates the GUI at constant intervals, while the acquisition can happen at a different rate.

## Screenshot ##

![Alt text](View/Icons/screenshot.png?raw=true "Optional Title")

### General Functionalities to achieve ###

* preparation

	1. [x] live video for alignment and exposure settings
	2. [x] selection of ROI
	3. [x] adjustment of mean/range min/max for grayscale viewer
	4. [ ] selecting background correction option

* tracking

	1. [x] waterfall update
	2. [ ] event counter (?)
	3. [ ] timer (?)
	4. [x] selecting particle of interest with cursor
	5. [x] recording track
	6. [ ] saving track (preferably on the screen) with flexible extra parameters (x,y,z,size,angle,intensity, etc vs time)
	7. [x] live update of the track on screen 
	8. [ ] adjusting tracking parameters
	9. [ ] calculating track properties such as D or other computation

* electrophoresis

	1. [x] setting up function generator
	2. [x] programming waveforms such as ramps, etc
	3. [ ] generating specific waveform based on tracking coordinates for feedback control

* review

	1. [ ]  possibility of reviewing a track on a separate screen

