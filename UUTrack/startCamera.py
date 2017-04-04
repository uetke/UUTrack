import os
import sys
from datetime import datetime

from PyQt4.Qt import QApplication

from .Model._session import _session
from .View.Camera.cameraMain import cameraMain


def start(configDir='Config',configFile='Camera_defaults_example.yml'):
    """
    Starts the main window of the program and loads the appropirate configuration file.
    :param str configDir: Folder where the config file is stored
    :param str configFile: Name of the config file
    :return: Window for the camera
    """
    global session

    base_dir = os.getcwd()
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
    elif session.Camera['camera'] == 'Hamamatsu':
        from .Model.Cameras.Hamamatsu import camera
    elif session.Camera['camera'] == 'PSI':
        from .Model.Cameras.PSI import camera
    else:
        raise Exception('That particular camera has not been implemented yet.\n Please check your config file')

    cam = camera(0)
    cam.initializeCamera()
    cam.setExposure(session.Camera['exposure_time'])
    app = QApplication(sys.argv)
    win = cameraMain(session,cam)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start()