"""
UUTrack.Model.config 
====================
.. deprecated:: 0.1

loads configuration files.
It is a relic file and not used anymore.
"""

import logging
import os.path
import xml.etree.cElementTree as ET

from .lib.logger import get_all_caller
from .lib.xml2dict import xmltodict


class DeviceConfig():
    def __init__(self,name=None, type='NI', filename='config/config_devices.xml'):
        self.logger = logging.getLogger(get_all_caller())
        tree = ET.ElementTree(file=filename)
        root = tree.getroot()
        if root.find(".//*[@Name='%s']"%name)!= None:
            self.logger.info('Loaded the data for %s in %s' %(name,filename))
            self.properties = xmltodict(root.find(".%s//*[@Name='%s']" %(type,name)))
        elif name==None:
            self.properties = []
            self.logger.info('Loaded all the data from %s' %(filename))
            for tags in root.find(".%s" %type):
                name = tags.get('Name')
                self.properties.append(name)
        else:
            self.logger.error("Name of Device is not in XML-file")

# Load the variable definition file
def open_configfile(basename):
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_dir = os.path.join(project_root, 'config')
    full_name = os.path.join(config_dir, basename)
    return open(full_name)
