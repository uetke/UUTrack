"""Best place to store variables that can be shared between different classes.
"""
import yaml
from PyQt4.QtCore import QObject, pyqtSignal, SIGNAL

class _session(QObject):
    """Stores variables and other classes that are common to several UI or instances of the code.
    """
    def __init__(self,file=None):
        """The class is prepared to load values from a Yaml file"""
        super(_session, self).__init__()
        super().__setattr__('params', dict())
        if file != None and type(file) == type('path'):
            with open(file,'r') as f:
                data = yaml.load(f)
                for d in data:
                    self.__setattr__(d,data[d])
        elif file != None and type(file) == type({}):
            data = file
            for d in data:
                self.__setattr__(d, data[d])

    def __setattr__(self, key, value):
        if type(value) != type({}):
            raise Exception('Everything passed to a session has to be a dictionary')
        if key not in self.params:
            self.params[key] = dict()
            self.__setattr__(key,value)
            print('AA')
        else:
            for k in value:
                if k in self.params[key]:
                    val = value[k]
                    self.params[key][k] = value[k] # Update value
                    self.emit(SIGNAL('Updated'))
                else:
                    self.params[key][k] = value[k]
                    self.emit(SIGNAL('New'))

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

    def getParams(self):
        """Special class for setting up the ParamTree from PyQtGraph. It saves the iterating over all the variables directly
        on the GUI."""
        p = []
        for k in self.params:
            c = []
            for m in self.params[k]:
                if type(self.params[k][m]) == type([]):
                    s = {'name': m.replace('_', ' '), 'type': type(self.params[k][m]).__name__,'values': self.params[k][m]}
                else:
                    s = {'name': m.replace('_', ' '), 'type': type(self.params[k][m]).__name__, 'value': self.params[k][m]}
                c.append(s)

            a = {'name': k.replace('_', ' '), 'type': 'group', 'children': c}
            p.append(a)
        return p

    def copy(self):
        """Copies this class"""
        _session.params = {}
        print('Copying')
        return _session(self.params)



if __name__ == '__main__':
    s = _session(file='../Config/Camera_defaults_example.yml')
    print('NEW')
    s.Camera = {'new': 'New'}
    print('OLD')
    s.Camera = {'model': 'Old'}
    #print(s.Camera)
    for k in s.params:
        print(k)
        for m in s.params[k]:
            print('   %s:  %s'%(m,s.params[k][m]))
    print(s)

    for k in s.params['Camera']:
        print(k)

    for m in s.Camera:
        print(m)