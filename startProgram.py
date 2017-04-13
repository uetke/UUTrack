"""
    Starting point for running the program.
"""

from UUTrack.startCamera import start

confDir = 'Config'
confFile = 'Camera_defaults_example.yml'

start(confDir,confFile)
