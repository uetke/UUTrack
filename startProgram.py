"""
    Starting point for running the program.
"""

from UUTrack.startMonitor import start
from multiprocessing import Process

if __name__ == '__main__':

    confDir = 'Config'
    confFile = 'Config_Sanli.yml'

    p = Process(target = start, args=(confDir,confFile))
    p.start()
    p.join()
