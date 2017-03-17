from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import copy
class configWidget(QtGui.QWidget):
    """Widget for configuring the main parameters of the camera.
    """
    def __init__(self, session, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._session = session.copy()
        session.Camera = {'roi_x1': 20}
        self._session_new = session.copy()  # To store the changes until applied
        self.t = ParameterTree()
        self.populateTree()
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.t)

        self.apply = QtGui.QPushButton('Apply')
        self.cancel = QtGui.QPushButton('Cancel')

        self.apply.clicked.connect(self.updateSession)
        self.cancel.clicked.connect(self.populateTree)

        self.layout.addWidget(self.apply)
        self.layout.addWidget(self.cancel)

    def change(self,param,changes):
        """Updates the values while being updated"""
        for param, change, data in changes:
            to_update = param.name().replace(' ','_')
            path = self.p.childPath(param)[0]
            self._session_new.params[path][to_update] = data
            print('Old session: ')
            print(self._session)
            print('New session:')
            print(self._session_new)

    def updateSession(self):
        """ Updates the session and sends a signal"""
        self._session = self._session_new.copy()
        self.emit(QtCore.SIGNAL('updateSession'), self._session)

    def populateTree(self):
        """Fills the tree with the values from the Session"""
        params = self._session.getParams()
        self.p = Parameter.create(name='params', type='group', children=params)
        self.p.sigTreeStateChanged.connect(self.change)
        self.t.setParameters(self.p, showTop=False)


