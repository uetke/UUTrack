import h5py
from PyQt4.QtGui import QMainWindow, QFileDialog, QListWidget, QLineEdit, QHBoxLayout, QWidget, QTextEdit, QVBoxLayout, \
    QPushButton
from PyQt4 import QtGui
from PyQt4 import QtCore

# from pyqtgraph.Qt import QtGui
from .Camera import resources


class HDFLoader(QMainWindow):
    def __init__(self):
        super(HDFLoader, self).__init__()
        self.setGeometry(40,40,600,600)

        self.setWindowTitle('Open HDF File')

        self.widget = HDFWidget(self)
        self.setCentralWidget(self.widget)


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
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            '/home/aquiles', "HDF Files (*.hdf *.hdf5)")
        self.widget.add_items(fname)

    def exitSafe(self):
        self.close()


class HDFWidget(QWidget):
    def __init__(self, parent=None):
        super(HDFWidget, self).__init__(parent=parent)
        self.parent = parent

        self.main_layout = QVBoxLayout()

        ### Select Dataset and properties ###
        self.layout = QHBoxLayout()
        self.list = QListWidget()
        self.textBox = QTextEdit()
        self.textBox.resize(200,200)

        ### Add button ###
        self.button = QPushButton("Apply")

        self.main_layout.addLayout(self.layout)
        self.main_layout.addWidget(self.button)
        self.setLayout(self.main_layout)

        self.layout.addWidget(self.list)
        self.layout.addWidget(self.textBox)

        ### Variables ###
        self.settings = None

        self.list.itemClicked.connect(self.item_clicked)
        self.connect(self.button,QtCore.SIGNAL("clicked()"),self.apply_settings)

    def item_clicked(self, item):
        i = self.list.currentRow()
        self.settings = self.all_settings[i]
        self.textBox.clear()
        self.textBox.setText(self.settings)
        # mdd = self.settings.split('\n')
        # for t in mdd:
        #     self.textBox.append(t)

    def add_items(self, name):
        f = h5py.File(name, 'r')
        self.settings = None
        self.all_settings = []
        self.list.clear()
        for g in f:
            self.all_settings.append(f[g+'/metadata'][()].decode('ascii'))
            self.list.addItem(g)

        f.close()

    def apply_settings(self):
        if self.settings is not None:
            self.parent.emit(QtCore.SIGNAL('settings'), self.settings)

if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    app = QApplication(sys.argv)
    h = HDFLoader()
    h.show()
    sys.exit(app.exec_())