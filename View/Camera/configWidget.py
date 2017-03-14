from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

class configWidget(QtGui.QWidget):
    """Widget for configuring the main parameters of the camera.
    """
    def __init__(self,session,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._session = session
        self.t = ParameterTree()
        self.populateTree()
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.t)
        self.p.sigTreeStateChanged.connect(self.change)

    def change(self,param,changes):
        for param, change, data in changes:
            to_update = param.name().replace(' ','_')
            path = self.p.childPath(param)[0]
            print(path)
            print(to_update)
            print(data)
            self._session.params[path][to_update] = data
            self.emit(QtCore.SIGNAL('updateSession'), self._session)

    def populateTree(self):
        params = self._session.getParams()
        print(params)
        self.p = Parameter.create(name='params', type='group', children=params)
        self.t.setParameters(self.p, showTop=False)


