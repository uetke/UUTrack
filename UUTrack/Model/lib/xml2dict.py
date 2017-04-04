import logging
import os
import xml.etree.cElementTree as ET

from config_dir import base_dir
from .logger import get_all_caller


def xmltodict(element):
    """converts the XML-file to a dictionary"""
    def xmltodict_handler(parent_element,result={}):
        for element in parent_element:
            if len(element):
                obj = xmltodict_handler(element)
            else:
                obj = element.attrib
                for i, j in obj.items():
                    try:
                        obj[i]=float(j)
                    except:
                        pass
            if result.get(element.tag):
                if hasattr(result[element.tag], "append"):
                    result[element.tag].append(obj)
                else:
                    result[element.tag] = [result[element.tag], obj]
            else:
                result[element.tag] = obj
        return result

    result=element.attrib
    return xmltodict_handler(element,result)

class device():
    def __init__(self,name=None,type='NI',filename=os.path.join(base_dir,'config','config_devices.xml')):
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


class variables():
    def __init__(self,name=None, filename=os.path.join(base_dir,'config/config_variables.xml')):
        var=device(name,'',filename)
        self.properties=var.properties
        for i in self.properties.keys():
            try:
                self.properties[i]=int(self.properties[i])
            except:
                pass

if __name__ == '__main__':
    fifo=variables('Fifo')
    #print(fifo.properties)
    counter = device()
    print(counter.properties)
