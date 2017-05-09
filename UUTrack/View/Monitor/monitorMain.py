"""
    UUTrack.View.Monitor.monitorMain.py
    ========================================

    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""

import os
import sys
import time
from datetime import datetime
from multiprocessing import Process, Queue

import h5py
import numpy as np
import psutil
from PyQt4.Qt import QApplication
from pyqtgraph import ProgressDialog
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import *

from UUTrack.Model._session import _session
from UUTrack.View.hdfloader import HDFLoader
from .monitorMainWidget import monitorMainWidget
from .cameraViewer import cameraViewer
from .clearQueueThread import clearQueueThread
from .configWidget import configWidget
from .crossCut import crossCutWindow
from .messageWidget import messageWidget
from .specialTaskWorker import specialTaskWorker
from .workerThread import workThread
from .trajectoryWidget import trajectoryWidget
from ...Model.workerSaver import workerSaver, clearQueue
from . import resources

class monitorMain(QtGui.QMainWindow):
    """
    Main control window for showing the live captured images and initiating special tasks
    """
    def __init__(self, session, cam):
        """
        Inits the camera window

        :param: session: session
        :param: cam: camera
        """
        super(monitorMain,self).__init__()
        self.setWindowTitle('nano-EPics Flow Setup Monitoring (UUTrack)')
        self.setMouseTracking(True)
        self._session = session

        self.camera = cam
        # Queue of images. multiprocessing takes care of handling the data in and out
        # and the sharing between parent and child processes.
        self.q = Queue(0)

        self.area = DockArea()
        self.setCentralWidget(self.area)
        self.resize(800, 800)
        self.area.setMouseTracking(True)

        # Main widget
        self.camWidget = monitorMainWidget()
        self.camWidget.setup_cross_cut(self.camera.maxHeight)
        self.camWidget.setup_cross_hair([self.camera.maxWidth, self.camera.maxHeight])
        self.camWidget.setup_roi_lines([self.camera.maxWidth, self.camera.maxHeight])
        self.camWidget.setup_overlay()
        self.camWidget.setup_mouse_tracking()
        # Widget for displaying information to the user
        self.messageWidget = messageWidget()
        # Small window to display the results of the special task
        self.trajectoryWidget = trajectoryWidget()
        # Window for the camera viewer
        self.camViewer = cameraViewer(self._session, self.camera, parent=self)
        # Configuration widget with a parameter tree
        self.config = configWidget(self._session)
        # Line cut widget
        self.crossCut = crossCutWindow(parent=self)
        # Select settings Window
        self.selectSettings = HDFLoader()

        self.refreshTimer = QtCore.QTimer()
        self.connect(self.refreshTimer, QtCore.SIGNAL('timeout()'), self.updateGUI)
        self.connect(self.refreshTimer, QtCore.SIGNAL('timeout()'), self.crossCut.update)

        self.refreshTimer.start(self._session.GUI['refresh_time'])



        self.acquiring = False
        self.logMessage = []

        ''' Initialize the camera and the camera related things '''
        self.maxSizex = self.camera.GetCCDWidth()
        self.maxSizey = self.camera.GetCCDHeight()
        self.current_width = self.maxSizex
        self.current_height = self.maxSizey

        if self._session.Camera['roi_x1'] == 0:
            self._session.Camera = {'roi_x1': 1}
        if self._session.Camera['roi_x2'] == 0 or self._session.Camera['roi_x2'] > self.maxSizex:
            self._session.Camera = {'roi_x2': self.maxSizex}
        if self._session.Camera['roi_y1'] == 0:
            self._session.Camera = {'roi_y1': 1}
        if self._session.Camera['roi_y2'] == 0 or self._session.Camera['roi_y2'] > self.maxSizey:
            self._session.Camera = {'roi_y2': self.maxSizey}

        self.config.populateTree(self._session)
        self.lastBuffer = time.time()
        self.lastRefresh = time.time()

        # Program variables
        self.tempImage = []
        self.trajectories = []
        self.fps = 0
        self.bufferTime = 0
        self.bufferTimes = []
        self.refreshTimes = []
        self.totalFrames = 0
        self.droppedFrames = 0
        self.buffer_memory = 0
        self.centroidX = np.array([])
        self.centroidY = np.array([])
        self.watData = []
        self.watIndex = 0 # Waterfall index
        self.corner_roi = [] # Real coordinates of the coorner of the ROI region. (Min_x and Min_y).

        self.docks = []

        self.corner_roi.append(self._session.Camera['roi_x1'])
        self.corner_roi.append(self._session.Camera['roi_y1'])

        # Program status
        self.continuousSaving = False
        self.showWaterfall = False
        self.saveRunning = False
        self.accumulateBuffer = False
        self.specialTaskRunning = False
        self.dock_state = None

        self.setupActions()
        self.setupToolbar()
        self.setupMenubar()
        self.setupDocks()
        self.setupSignals()

        ### This block can be erased if one relies exclusively on Session variables.
        self.fileDir = self._session.Saving['directory']
        self.fileName = self._session.Saving['filename_photo']
        self.movieName = self._session.Saving['filename_video']
        ###
        self.messageWidget.appendLog('i', 'Program started by %s' % self._session.User['name'])

    def snap(self):
        """Function for acquiring a single frame from the camera. It is triggered by the user.
        It gets the data the GUI will be updated at a fixed framerate.
        """
        if self.acquiring: #If it is itself acquiring a message is displayed to the user warning him
            msgBox = QtGui.QMessageBox()
            msgBox.setIcon(QtGui.QMessageBox.Critical)
            msgBox.setText("You cant snap a photo while in free run")
            msgBox.setInformativeText("The program is already acquiring data")
            msgBox.setWindowTitle("Already acquiring")
            msgBox.setDetailedText("""When in free run, you can\'t trigger another acquisition. \n
                You should stop the free run acquisition and then snap a photo.""")
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            retval = msgBox.exec_()
            self.messageWidget.appendLog('e', 'Tried to snap while in free run')
        else:
            self.workerThread = workThread(self._session, self.camera)
            self.connect(self.workerThread,QtCore.SIGNAL('Image'),self.getData)
            self.workerThread.origin = 'snap'
            self.workerThread.start()
            self.acquiring = True
            self.messageWidget.appendLog('i', 'Snapped photo')

    def saveImage(self):
        """Saves the image that is being displayed to the user.
        """
        if len(self.tempImage) >= 1:
            # Data will be appended to existing file
            fn = self._session.Saving['filename_photo']
            filename = '%s.hdf5' % (fn)
            fileDir = self._session.Saving['directory']
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)

            f = h5py.File(os.path.join(fileDir,filename), "a")
            now = str(datetime.now())
            g = f.create_group(now)
            dset = g.create_dataset('image', data=self.tempImage)
            meta = g.create_dataset('metadata',data=self._session.serialize())
            f.flush()
            f.close()
            self.messageWidget.appendLog('i', 'Saved photo')

    def startMovie(self):
        if self._session.Debug['to_screen']:
            print('Start Movie')
        if self.specialTaskRunning:
            self.messageWidget.appendLog('w', 'Special task is running')
        else:
            if self.acquiring:
                self.stopMovie()
            else:
                self.emit(QtCore.SIGNAL('stopChildMovie'))
                self.messageWidget.appendLog('i', 'Started free run movie')
                # Worker thread to acquire images. Specially useful for long exposure time images
                self.workerThread = workThread(self._session,self.camera)
                self.connect(self.workerThread, QtCore.SIGNAL('Image'), self.getData)
                self.connect(self.workerThread, QtCore.SIGNAL("finished()"), self.done)
                self.workerThread.start()
                self.acquiring = True

    def stopMovie(self):
        if self.acquiring:
            self.workerThread.keep_acquiring = False
            while self.workerThread.isRunning():
                pass
            self.acquiring = False
            self.camera.stopAcq()
            self.messageWidget.appendLog('i', 'Stopped free run movie')
            if self.continuousSaving:
                self.movieSaveStop()

    def movieData(self):
        """Function just to trigger and read the camera in the separate thread.
        """
        self.workerThread.start()

    def movieSave(self):
        """Saves the data accumulated in the queue continuously.
        """
        if not self.continuousSaving:
            # Child process to save the data. It runs continuously until and exit flag
            # is passed through the Queue. (self.q.put('exit'))
            self.accumulateBuffer = True
            if len(self.tempImage) > 1:
                im_size = self.tempImage.nbytes
                max_element = int(self._session.Saving['max_memory']/im_size)
                #self.q = Queue(0)
            fn = self._session.Saving['filename_video']
            filename = '%s.hdf5' % (fn)
            fileDir = self._session.Saving['directory']
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)
            to_save = os.path.join(fileDir, filename)
            metaData = self._session.serialize() # This prints a YAML-ready version of the session.
            self.p = Process(target=workerSaver, args=(to_save, metaData, self.q,))  #
            self.p.start()
            self.continuousSaving = True
            self.messageWidget.appendLog('i', 'Started the Continuous savings')
        else:
            self.messageWidget.appendLog('w', 'Continuous savings already triggered')

    def movieSaveStop(self):
        """Stops the saving to disk. It will however flush the queue.
        """
        if self.continuousSaving:
            self.q.put('Stop')
            self.accumulateBuffer = False
            #self.p.join()
            self.messageWidget.appendLog('i', 'Stopped the Continuous savings')
            self.continuousSaving = False

    def emptyQueue(self):
        """Clears the queue.
        """
        # Worker thread for clearing the queue.
        self.clearWorker = Process(target = clearQueue, args = (self.q,))
        self.clearWorker.start()

    def startWaterfall(self):
        """Starts the waterfall. The waterfall can be accelerated if camera supports hardware binning in the appropriate
        direction. If not, has to be done via software but the acquisition time cannot be improved.
        TODO: Fast waterfall should have separate window, since the acquisition of the full CCD will be stopped.
        """
        if not self.showWaterfall:
            self.watWidget = monitorMainWidget()
            self.area.addDock(self.dwaterfall, 'bottom', self.dmainImage)
            self.dwaterfall.addWidget(self.watWidget)
            self.showWaterfall = True
            Sx, Sy = self.camera.getSize()
            self.watData = np.zeros((self._session.GUI['length_waterfall'],Sx))
            self.watWidget.img.setImage(np.transpose(self.watData))
            self.messageWidget.appendLog('i', 'Waterfall opened')
        else:
            self.closeWaterfall()

    def stopWaterfall(self):
        """Stops the acquisition of the waterfall.
        """
        pass

    def closeWaterfall(self):
        """Closes the waterfall widget.
        """
        if self.showWaterfall:
            self.watWidget.close()
            self.dwaterfall.close()
            self.showWaterfall = False
            del self.watData
            self.messageWidget.appendLog('i', 'Waterfall closed')

    def setROI(self, X, Y):
        """
        Gets the ROI from the lines on the image. It also updates the GUI to accommodate the changes.
        :param X:
        :param Y:
        :return:
        """
        if not self.acquiring:
            self.corner_roi[0] = X[0]
            self.corner_roi[1] = Y[0]
            if self._session.Debug['to_screen']:
                print('Corner: %s, %s' % (self.corner_roi[0],self.corner_roi[1]))
            self._session.Camera = {'roi_x1': int(X[0])}
            self._session.Camera = {'roi_x2': int(X[1])}
            self._session.Camera = {'roi_y1': int(Y[0])}
            self._session.Camera = {'roi_y2': int(Y[1])}
            self.messageWidget.appendLog('i', 'Updated roi_x1: %s' % int(X[0]))
            self.messageWidget.appendLog('i', 'Updated roi_x2: %s' % int(X[1]))
            self.messageWidget.appendLog('i', 'Updated roi_y1: %s' % int(Y[0]))
            self.messageWidget.appendLog('i', 'Updated roi_y2: %s' % int(Y[1]))

            Nx, Ny = self.camera.setROI(X, Y)
            Sx, Sy = self.camera.getSize()
            self.current_width = Sx
            self.current_height = Sy

            self.tempImage = np.zeros((Nx, Ny))
            self.camWidget.hline1.setValue(1)
            self.camWidget.hline2.setValue(Ny)
            self.camWidget.vline1.setValue(1)
            self.camWidget.vline2.setValue(Nx)
            self.centroidX = np.array([])
            self.centroidY = np.array([])
            self.trajectories = []
            self.camWidget.img2.clear()
            if self.showWaterfall:
                self.watData = np.zeros((self._session.GUI['length_waterfall'],self.current_width))
                self.watWidget.img.setImage(np.transpose(self.watData))

            self.config.populateTree(self._session)
            self.messageWidget.appendLog('i', 'Updated the ROI')
        else:
            self.messageWidget.appendLog('e', 'Cannot change ROI while acquiring.')

    def getROI(self):
        """Gets the ROI coordinates from the GUI and updates the values."""
        y1 = np.int(self.camWidget.hline1.value())
        y2 = np.int(self.camWidget.hline2.value())
        x1 = np.int(self.camWidget.vline1.value())
        x2 = np.int(self.camWidget.vline2.value())
        X = np.sort((x1, x2))
        Y = np.sort((y1, y2))
        # Updates to the real values
        X += self.corner_roi[0] - 1
        Y += self.corner_roi[1] - 1
        self.setROI(X, Y)

    def clearROI(self):
        """Resets the roi to the full image.
        """
        if not self.acquiring:
            self.camWidget.hline1.setValue(1)
            self.camWidget.vline1.setValue(1)
            self.camWidget.vline2.setValue(self.maxSizex)
            self.camWidget.hline2.setValue(self.maxSizey)
            self.corner_roi = [1, 1]
            self.getROI()
        else:
            self.messageWidget.appendLog('e', 'Cannot change ROI while acquiring.')

    def setupActions(self):
        """Setups the actions that the program will have. It is placed into a function
        to make it easier to reuse in other windows.

        :rtype: None
        """
        self.exitAction = QtGui.QAction(QtGui.QIcon(':Icons/power-icon.png'), '&Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.exitSafe)

        self.saveAction = QtGui.QAction(QtGui.QIcon(':Icons/floppy-icon.png'),'&Save image',self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip('Save Image')
        self.saveAction.triggered.connect(self.saveImage)

        self.saveWaterfallAction = QtGui.QAction("Save Waterfall", self)
        self.saveWaterfallAction.setShortcut('Ctrl+Shift+W')
        self.saveWaterfallAction.setStatusTip('Save waterfall data to new file')
        self.saveWaterfallAction.triggered.connect(self.saveWaterfall)

        self.saveTrajectoryAction = QtGui.QAction("Save Trajectory", self)
        self.saveTrajectoryAction.setShortcut('Ctrl+Shift+T')
        self.saveTrajectoryAction.setStatusTip('Save trajectory data to new file')
        self.saveTrajectoryAction.triggered.connect(self.saveTrajectory)

        self.snapAction = QtGui.QAction(QtGui.QIcon(':Icons/snap.png'),'S&nap photo',self)
        self.snapAction.setShortcut(QtCore.Qt.Key_F5)
        self.snapAction.setStatusTip('Snap Image')
        self.snapAction.triggered.connect(self.snap)

        self.movieAction = QtGui.QAction(QtGui.QIcon(':Icons/video-icon.png'),'Start &movie',self)
        self.movieAction.setShortcut('Ctrl+R')
        self.movieAction.setStatusTip('Start Movie')
        self.movieAction.triggered.connect(self.startMovie)

        self.movieSaveStartAction = QtGui.QAction(QtGui.QIcon(':Icons/Download-Database-icon.png'),'Continuous saves',self)
        self.movieSaveStartAction.setShortcut('Ctrl+M')
        self.movieSaveStartAction.setStatusTip('Continuous save to disk')
        self.movieSaveStartAction.triggered.connect(self.movieSave)

        self.movieSaveStopAction = QtGui.QAction(QtGui.QIcon(':Icons/Delete-Database-icon.png'),'Stop continuous saves',self)
        self.movieSaveStopAction.setShortcut('Ctrl+N')
        self.movieSaveStopAction.setStatusTip('Stop continuous save to disk')
        self.movieSaveStopAction.triggered.connect(self.movieSaveStop)

        self.startWaterfallAction = QtGui.QAction(QtGui.QIcon(':Icons/Blue-Waterfall-icon.png'),'Start &Waterfall',self)
        self.startWaterfallAction.setShortcut('Ctrl+W')
        self.startWaterfallAction.setStatusTip('Start Waterfall')
        self.startWaterfallAction.triggered.connect(self.startWaterfall)

        self.setROIAction = QtGui.QAction(QtGui.QIcon(':Icons/Zoom-In-icon.png'),'Set &ROI',self)
        self.setROIAction.setShortcut('Ctrl+T')
        self.setROIAction.setStatusTip('Set ROI')
        self.setROIAction.triggered.connect(self.getROI)

        self.clearROIAction = QtGui.QAction(QtGui.QIcon(':Icons/Zoom-Out-icon.png'),'Set R&OI',self)
        self.clearROIAction.setShortcut('Ctrl+T')
        self.clearROIAction.setStatusTip('Clear ROI')
        self.clearROIAction.triggered.connect(self.clearROI)

        self.accumulateBufferAction = QtGui.QAction(QtGui.QIcon(':Icons/disk-save.png'),'Accumulate buffer',self)
        self.accumulateBufferAction.setShortcut('Ctrl+B')
        self.accumulateBufferAction.setStatusTip('Start or stop buffer accumulation')
        self.accumulateBufferAction.triggered.connect(self.bufferStatus)

        self.clearBufferAction = QtGui.QAction('Clear Buffer',self)
        self.clearBufferAction.setShortcut('Ctrl+F')
        self.clearBufferAction.setStatusTip('Clears the buffer')
        self.clearBufferAction.triggered.connect(self.emptyQueue)

        self.viewerAction = QtGui.QAction('Start Viewer',self)
        self.viewerAction.triggered.connect(self.camViewer.show)

        self.configAction = QtGui.QAction('Config Window',self)
        self.configAction.triggered.connect(self.config.show)

        self.dockAction = QtGui.QAction('Restore Docks', self)
        self.dockAction.triggered.connect(self.setupDocks)

        self.crossCutAction = QtGui.QAction(QtGui.QIcon(':Icons/Ruler-icon.png'),'Show cross cut', self)
        self.crossCutAction.triggered.connect(self.crossCut.show)

        self.settingsAction = QtGui.QAction('Load config', self)
        self.settingsAction.triggered.connect(self.selectSettings.show)

    def setupToolbar(self):
        """Setups the toolbar with the desired icons. It's placed into a function
        to make it easier to reuse in other windows.
        """
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(self.exitAction)
        self.toolbar2 = self.addToolBar('Image')
        self.toolbar2.addAction(self.saveAction)
        self.toolbar2.addAction(self.snapAction)
        self.toolbar2.addAction(self.crossCutAction)
        self.toolbar3 = self.addToolBar('Movie')
        self.toolbar3.addAction(self.movieAction)
        self.toolbar3.addAction(self.movieSaveStartAction)
        self.toolbar3.addAction(self.movieSaveStopAction)
        self.toolbar4 = self.addToolBar('Waterfall')
        self.toolbar4.addAction(self.startWaterfallAction)
        self.toolbar4.addAction(self.setROIAction)
        self.toolbar4.addAction(self.clearROIAction)

    def setupMenubar(self):
        """Setups the menubar.
        """
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.settingsAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.exitAction)
        self.snapMenu = menubar.addMenu('&Snap')
        self.snapMenu.addAction(self.snapAction)
        self.snapMenu.addAction(self.saveAction)
        self.movieMenu = menubar.addMenu('&Movie')
        self.movieMenu.addAction(self.movieAction)
        self.movieMenu.addAction(self.movieSaveStartAction)
        self.movieMenu.addAction(self.movieSaveStopAction)
        self.movieMenu.addAction(self.startWaterfallAction)
        self.configMenu = menubar.addMenu('&Configure')
        self.configMenu.addAction(self.setROIAction)
        self.configMenu.addAction(self.clearROIAction)
        self.configMenu.addAction(self.accumulateBufferAction)
        self.configMenu.addAction(self.clearBufferAction)
        self.configMenu.addAction(self.viewerAction)
        self.configMenu.addAction(self.configAction)
        self.configMenu.addAction(self.dockAction)

        self.saveMenu = menubar.addMenu('S&ave')
        self.saveMenu.addAction(self.saveWaterfallAction)
        self.saveMenu.addAction(self.saveTrajectoryAction)

    def setupDocks(self):
        """Setups the docks in order to recover the initial configuration if one gets closed."""

        for d in self.docks:
            try:
                d.close()
            except:
                pass

        self.docks = []

        self.dmainImage = Dock("Main Image", size=(500, 250))
        self.dwaterfall = Dock("Waterfall", size=(500, 125))

        self.dparams = Dock("Parameters", size=(100, 3))
        self.dtraj = Dock("Trajectory", size=(200, 2))
        self.dmessage = Dock("Messages", size=(200, 2))
        # self.dstatus = Dock("Status", size=(100, 3))

        self.area.addDock(self.dmainImage, 'right')
        self.area.addDock(self.dtraj, 'bottom')
        self.area.addDock(self.dmessage, 'right', self.dtraj)
        self.area.addDock(self.dparams, 'left', self.dtraj)

        self.docks.append(self.dmainImage)
        self.docks.append(self.dtraj)
        self.docks.append(self.dmessage)
        self.docks.append(self.dparams)
        self.docks.append(self.dwaterfall)
        # self.area.addDock(self.dstatus, 'bottom', self.dparams)

        self.dmainImage.addWidget(self.camWidget)
        self.dmessage.addWidget(self.messageWidget)
        self.dparams.addWidget(self.config)
        self.dtraj.addWidget(self.trajectoryWidget)

        self.dock_state = self.area.saveState()

    def setupSignals(self):
        """Setups all the signals that are going to be handled during the excution of the program."""
        self.connect(self._session, QtCore.SIGNAL('Updated'), self.config.populateTree)
        self.connect(self.config, QtCore.SIGNAL('updateSession'), self.updateSession)
        self.connect(self.camWidget, QtCore.SIGNAL('specialTask'), self.startSpecialTask)
        self.connect(self.camWidget, QtCore.SIGNAL('stopSpecialTask'), self.stopSpecialTask)
        self.connect(self.camViewer, QtCore.SIGNAL('Stop_MainAcquisition'), self.stopMovie)
        self.connect(self, QtCore.SIGNAL('stopChildMovie'), self.camViewer.stopCamera)
        self.connect(self, QtCore.SIGNAL('CloseAll'), self.camViewer.closeViewer)
        self.connect(self.selectSettings, QtCore.SIGNAL("settings"), self.update_settings)
        self.connect(self, QtCore.SIGNAL('CloseAll'), self.selectSettings.close)

    def bufferStatus(self):
        """Starts or stops the buffer accumulation.
        """
        if self.accumulateBuffer:
            self.accumulateBuffer = False
            self.messageWidget.appendLog('i', 'Stopped the buffer accumulation')
        else:
            self.accumulateBuffer = True
            self.messageWidget.appendLog('i', 'Stopped the buffer accumulation')

    def getData(self, data, origin):
        """Gets the data that is being gathered by the working thread.

        .. _getData:
        """
        s = 0
        if origin == 'snap': #Single snap.
            self.acquiring=False
            self.workerThread.origin = None
            self.workerThread.keep_acquiring = False  # This already happens in the worker thread itself.
            self.camera.stopAcq()

        if isinstance(data, list):
            for d in data:
                if self.accumulateBuffer:
                    s = float(self.q.qsize())*int(d.nbytes)/1024/1024
                    if s<self._session.Saving['max_memory']:
                        self.q.put(d)
                    else:
                        self.droppedFrames+=1

                if self.showWaterfall:
                    if self.watIndex == self._session.GUI['length_waterfall']:
                        if self._session.Saving['auto_save_waterfall']:
                            self.saveWaterfall()

                        self.watData = np.zeros((self._session.GUI['length_waterfall'],self.current_width))
                        self.watIndex = 0

                    wf = np.array([np.sum(d,1)])
                    self.watData[self.watIndex,:] = wf
                    self.watIndex +=1

                self.totalFrames+=1
            self.tempImage = d
        else:
            self.tempImage = data
            if self.accumulateBuffer:
                s = float(self.q.qsize())*int(d.nbytes)/1024/1024

                if s<self._session.Saving['max_memory']:
                    self.q.put(data)
                else:
                    self.droppedFrames+=1

            if self.showWaterfall:
                if self.watIndex == self._session.GUI['length_waterfall']:
                    if self._session.Saving['auto_save_waterfall']:
                        self.saveWaterfall()

                    self.watData = np.zeros((self._session.GUI['length_waterfall'],self.current_width))
                    self.watIndex = 0

                wf = np.array([np.sum(d,1)])
                self.watData[self.watIndex,:] = wf
                self.watIndex +=1

            self.totalFrames += 1

        new_time = time.time()
        self.bufferTime = new_time - self.lastBuffer
        self.lastBuffer = new_time
        self.buffer_memory = s
        if self._session.Debug['queue_memory']:
            print('Queue Memory: %3.2f MB' % self.buffer_memory)

    def getCoordinates(self, X):
        """Gets the coordinates emitted by the special task worker and stores them in an array"""
        self.centroidX = np.append(self.centroidX,X[0,:])
        self.centroidY = np.append(self.centroidY,X[1,:])
        self.trajectories[int(X[0,0]), int(X[1,0]),1] = 50000

    def updateGUI(self):
        """Updates the image displayed to the user.
        """
        if len(self.tempImage) >= 1:
            self.camWidget.img.setImage(self.tempImage, autoLevels=False, autoRange=False, autoHistogramRange=False)
            self.buffer_memory = float(self.q.qsize())*int(self.tempImage.nbytes)/1024/1024

        if len(self.centroidX) >= 1:
            self.camWidget.img2.setImage(self.trajectories)
            # self.trajectoryWidget.plot.clear()
            self.trajectoryWidget.plot.setData(self.centroidX,self.centroidY)

        if self.showWaterfall:
            self.watData  = self.watData[:self._session.GUI['length_waterfall'],:]
            self.watWidget.img.setImage(np.transpose(self.watData))


        new_time = time.time()
        self.fps = new_time-self.lastRefresh
        self.lastRefresh = new_time

        self.messageWidget.updateMemory(self.buffer_memory/self._session.Saving['max_memory']*100)
        self.messageWidget.updateProcessor(psutil.cpu_percent())

        msg = '''<b>Buffer time:</b> %0.2f ms <br />
             <b>Refresh time:</b> %0.2f ms <br />
             <b>Acquired Frames</b> %i <br />
             <b>Dropped Frames</b> %i <br />
             <b>Frames in buffer</b> %i'''%(self.bufferTime*1000,self.fps*1000,self.totalFrames,self.droppedFrames,self.q.qsize())
        self.messageWidget.updateMessage(msg)
        #self.messageWidget.updateLog(self.logMessage)
        self.logMessage = []

    def saveWaterfall(self):
        """Saves the waterfall data, if any.
        """
        if len(self.watData) > 1:
            fn = self._session.Saving['filename_waterfall']
            filename = '%s.hdf5' % (fn)
            fileDir = self._session.Saving['directory']
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)

            f = h5py.File(os.path.join(fileDir,filename), "a")
            now = str(datetime.now())
            g = f.create_group(now)
            dset = g.create_dataset('waterfall', data=self.watData)
            meta = g.create_dataset('metadata', data=self._session.serialize().encode("ascii","ignore"))
            f.flush()
            f.close()
            self.messageWidget.appendLog('i','Saved Waterfall')

    def saveTrajectory(self):
        """Saves the trajectory data, if any.
        """
        if len(self.centroidX) > 1:
            fn = self._session.Saving['filename_trajectory']
            filename = '%s.hdf5' % (fn)
            fileDir = self._session.Saving['directory']
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)

            f = h5py.File(os.path.join(fileDir,filename), "a")
            now = str(datetime.now())
            g = f.create_group(now)
            dset = g.create_dataset('trajectory', data=[self.centroidX, self.centroidY])
            meta = g.create_dataset('metadata',data=self._session.serialize().encode("ascii","ignore"))
            f.flush()
            f.close()
            self.messageWidget.appendLog('i', 'Saved Trajectory')


    def update_settings(self, settings):
        new_session = _session(settings)
        self.updateSession(new_session)
        self.config.populateTree(self._session)

    def updateSession(self, session):
        """Updates the session variables passed by the config window.
        """
        update_cam = False
        update_roi = False
        update_exposure = False
        update_binning = True
        for k in session.params['Camera']:
            new_prop = session.params['Camera'][k]
            old_prop = self._session.params['Camera'][k]
            if new_prop != old_prop:
                update_cam = True
                if k in ['roi_x1', 'roi_x2', 'roi_y1', 'roi_y2']:
                    update_roi = True
                    if self._session.Debug['to_screen']:
                        print('Update ROI')
                elif k == 'exposure_time':
                    update_exposure = True
                elif k in ['binning_x', 'binning_y']:
                    update_binning = True

        if session.GUI['length_waterfall'] != self._session.GUI['length_waterfall']:
            if self.showWaterfall:
                self.closeWaterfall()
                self.restart_waterfall = True

        self.messageWidget.appendLog('i', 'Updated the parameters')
        self._session = session.copy()

        if update_cam:
            if self.acquiring:
                self.stopMovie()

            if update_roi:
                X = np.sort([session.Camera['roi_x1'], session.Camera['roi_x2']])
                Y = np.sort([session.Camera['roi_y1'], session.Camera['roi_y2']])
                self.setROI(X, Y)

            if update_exposure:
                new_exp = self.camera.setExposure(session.Camera['exposure_time'])
                self._session.Camera = {'exposure_time': new_exp}
                self.messageWidget.appendLog('i', 'Updated exposure: %s' % new_exp)
                if self._session.Debug['to_screen']:
                    print("New Exposure: %s" % new_exp)
                    print(self._session)

            if update_binning:
                self.camera.setBinning(session.Camera['binning_x'],session.Camera['binning_y'])

        self.refreshTimer.stop()
        self.refreshTimer.start(session.GUI['refresh_time'])


    def startSpecialTask(self):
        """Starts a special task. This is triggered by the user with a special combination of actions, for example clicking
        with the mouse on a plot, draggin a crosshair, etc."""
        if not self.specialTaskRunning:
            if self.acquiring:
                self.stopMovie()
                self.acquiring = False

            X = self.camWidget.crosshair[0].getPos()
            Y = self.camWidget.crosshair[1].getPos()
            self.centroidX = np.array([])
            self.centroidY = np.array([])
            self.trajectories = np.zeros((self.tempImage.shape[0],self.tempImage.shape[1],3))
            self.specialTaskWorker = specialTaskWorker(self._session,self.camera,X,Y)
            self.connect(self.specialTaskWorker,QtCore.SIGNAL('Image'),self.getData)
            self.connect(self.specialTaskWorker,QtCore.SIGNAL('Coordinates'),self.getCoordinates)
            self.specialTaskWorker.start()
            self.specialTaskRunning = True
            self.messageWidget.appendLog('i', 'Started special task')
        else:
            print('special task already running')

    def stopSpecialTask(self):
        """Stops the special task"""
        if self.specialTaskRunning:
            self.specialTaskWorker.keep_running = False
            self.specialTaskRunning = False
            self.messageWidget.appendLog('i', 'Stopped special task')

    def done(self):
        #self.saveRunning = False
        self.acquiring = False

    def exitSafe(self):
        self.close()


    def closeEvent(self,evnt):
        """Triggered at closing. Checks that the save is complete and closes the dataFile
        """
        self.messageWidget.appendLog('i', 'Closing the program')
        if self.acquiring:
            self.stopMovie()
        if self.specialTaskRunning:
            self.stopSpecialTask()
            while self.specialTaskWorker.isRunning():
                pass
        self.emit(QtCore.SIGNAL('CloseAll'))
        self.camera.stopCamera()
        self.movieSaveStop()
        try:
            # Checks if the process P exists and tries to close it.
            if self.p.is_alive():
                qs = self.q.qsize()
                with ProgressDialog("Finish saving data...", 0, qs) as dlg:
                    while self.q.qsize() > 1:
                        dlg.setValue(qs - self.q.qsize())
                        time.sleep(0.5)
            self.p.join()
        except AttributeError:
            pass
        if self.q.qsize() > 0:
            self.messageWidget.appendLog('i', 'The queue was not empty')
            print('Freeing up memory...')
            self.emptyQueue()

        # Save LOG.
        fn = self._session.Saving['filename_log']
        timestamp = datetime.now().strftime('%H%M%S')
        filename = '%s%s.log' % (fn, timestamp)
        fileDir = self._session.Saving['directory']
        if not os.path.exists(fileDir):
            os.makedirs(fileDir)

        f = open(os.path.join(fileDir,filename), "a")
        for line in self.messageWidget.logText:
            f.write(line+'\n')
        f.flush()
        f.close()
        print('Saved LOG')
        super(monitorMain, self).closeEvent(evnt)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    cam = monitorMain()
    cam.show()
    sys.exit(app.exec_())
