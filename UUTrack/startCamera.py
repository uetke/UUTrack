"""
    UUTrack.startCamera
    ===================
    Main starting point of the program. It imports the base classes and defines the :meth:`~UUTrack.startCamera.start` function.
    To start the program you can run either from the command prompt or embedded into your own code.
    
        >>> from UUTrack import startCamera
        >>> config_dir = 'Path/To/Config_Dir'
        >>> config_file = 'config.yml'
        >>> startCamera.start(config_dir,config_file)
    
    The config file is passed to a :class:`~UUTrack.Model._session` variable. That will be shared with the rest of the program. The session variable idea comes from programming websites, but is useful in other kind of programs as well.
        
    :copyright: 2017
    
    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""
import os
import sys
from datetime import datetime

from PyQt4.Qt import QApplication

from .Model._session import _session
from .View.Camera.cameraMain import cameraMain


def start(configDir='',configFile=''):
    """
    Starts the main window of the program and loads the appropirate configuration file.

    :param str configDir: Folder where the config file is stored
    :param str configFile: Name of the config file
    :return: Window for the camera
    """
    global session

    if configDir != '':
        base_dir = os.getcwd()
    else:
        base_dir = os.path.dirname(os.path.realpath(__file__))

    if configFile == '':
        from . import config_dir

    print(base_dir)
    camera_config = os.path.join(base_dir, configDir, configFile)
    session = _session(camera_config)

    if session.Saving['directory'] == '':
        savedir =os.path.join(base_dir, str(datetime.now().date()))
    else:
        savedir = os.path.join(session.Saving['directory'], str(datetime.now().date()))

    if not os.path.exists(savedir):
        os.makedirs(savedir)

    session.Saving = {'directory': savedir}

    if session.Camera['camera'] == 'dummyCamera':
        from .Model.Cameras.dummyCamera import camera
        cam = camera(0)
    elif session.Camera['camera'] == 'Hamamatsu':
        from .Model.Cameras.Hamamatsu import camera
        cam = camera(0)
    elif session.Camera['camera'] == 'PSI':
        from .Model.Cameras.PSI import camera
        cam = camera('C:\\Users\\Experimentor\\Programs\\UUTrack\\Controller\\devices\\PhotonicScience')
    else:
        raise Exception('That particular camera has not been implemented yet.\n Please check your config file')

    cam.initializeCamera()
    cam.setExposure(session.Camera['exposure_time'])
    app = QApplication(sys.argv)
    win = cameraMain(session,cam)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start()
