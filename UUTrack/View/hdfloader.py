import h5py
from PyQt4.QtGui import QMainWindow, QFileDialog, QListWidget
from PyQt4 import QtGui

# from pyqtgraph.Qt import QtGui
from Camera import resources


class HDFLoader(QMainWindow):
    def __init__(self):
        super(HDFLoader, self).__init__()
        self.setWindowTitle('Open HDF File')

        self.list = QListWidget()
        self.setCentralWidget(self.list)
        self.list.addItem('Test')
        self.list.addItem('Test')
        self.list.addItem('Test')
        self.list.addItem('Test')
        

        self.setup_actions()
        self.setupToolbar()
        self.setupMenubar()

    def setup_actions(self):
        self.exitAction = QtGui.QAction(QtGui.QIcon(':Icons/power-icon.png'), '&Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.exitSafe)

        self.openAction = QtGui.QAction(QtGui.QIcon(':Icons/Zoom-In-icon.png'), '&Open', self)
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip('Open File')
        self.openAction.triggered.connect(self.open_file)

    def setupToolbar(self):
        """Setups the toolbar with the desired icons. It's placed into a function
        to make it easier to reuse in other windows.
        """
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addAction(self.openAction)

    def setupMenubar(self):
        """Setups the menubar.
        """
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.exitAction)
        self.fileMenu.addAction(self.openAction)

    def open_file(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            '/home/aquiles', "HDF Files (*.hdf *.hdf5)")

        f = h5py.File(self.fname,'r')

        self.groups = []
        for g in f:
            self.groups.append(g)

        print(self.groups)

    def exitSafe(self):
        self.close()

if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    app = QApplication(sys.argv)
    h = HDFLoader()
    h.show()
    sys.exit(app.exec_())