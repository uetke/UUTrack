from distutils.core import setup

setup(
    name='UUtracking',
    version='0.1',
    packages=['View', 'View.Camera', 'Model', 'Model.lib', 'Model.Cameras', 'Controller', 'Controller.devices',
              'Controller.devices.keysight', 'Controller.devices.hamamatsu', 'Controller.devices.PhotonicScience'],
    url='https://github.com/aquilesC/UUTrack',
    license='MIT',
    author='aquiles',
    author_email='aquiles@uetke.com',
    description='GUI for tracking particles in a capillary'
)
