from pyqtgraph.Qt import QtCore

class clearQueueThread(QtCore.QThread):
    """Clears the Queue.
    """
    def __init__(self,q):
        QtCore.QThread.__init__(self)
        self.q = q
    def __del__(self):
        self.wait()
    def run(self):
        """Clears the queue.
        """
        while self.q.qsize()>0:
            self.q.get()
