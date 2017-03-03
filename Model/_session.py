"""Best place to store variables that can be shared between different classes.
"""
import yaml
from PyQt4.QtCore import QObject, pyqtSignal

class _session(QObject):
    """Stores variables and other classes that are common to several UI or instances of the code.
    """
    UPDATESIGNAL = pyqtSignal()
    NEWSIGNAL = pyqtSignal()
    params = {}
    def __init__(self,file=None):
        """The class is prepared to load values from a Yaml file"""
        super(_session, self).__init__()
        if file != None:
            with open(file,'r') as f:
                data = yaml.load(f)
                for d in data:
                    self.__setattr__(d,data[d])

    def __setattr__(self, key, value):
        if key not in self.params:
            self.params[key] = dict()
            self.__setattr__(key,value)
        else:
            for k in value:
                if k in self.params[key]:
                    val = value[k]
                    self.params[key][k] = value[k] # Update value
                    self.UPDATESIGNAL.emit()
                    print('Update')

                else:
                    self.params[key][k] = value[k]
                    self.NEWSIGNAL.emit()
                    print('New new')
                    print(key)
            super(_session, self).__setattr__(k, value[k])

    def __getattr__(self, item):
        if item not in self.params:
            return None
        else:
            return self.params[item]

    def __str__(self):
        s = ''
        for key in self.params:
            s += '%s\n'%key
            for kkey in self.params[key]:
                s+= '\t%s: %s\n'%(kkey,self.params[key][kkey])
        return s



if __name__ == '__main__':
    s = _session(file='../Config/Camera_defaults_example.yml')
    print(s.Camera)
    print(s)
