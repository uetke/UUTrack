""" messageWidget
created by: AJ Carattino
"""
from pyqtgraph.Qt import QtGui

class messageWidget(QtGui.QWidget):
    """Widget that holds text boxes for displaying information to the user."""
    messageTitle = "Status"
    logTitle = "Log"
    logMaxLength = 20 # maximum length of the log to be displayed to the user.

    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)

        # General layout of the widget
        self.layout = QtGui.QVBoxLayout(self)

        # Status bars to display memory and CPU usage to the user
        self.statusBars = QtGui.QHBoxLayout()
        self.memory = QtGui.QProgressBar(self)
        self.processor = QtGui.QProgressBar(self)
        self.statusBars.addWidget(self.memory)
        self.statusBars.addWidget(self.processor)

        # Displays a textbox to the user with either information or a simple log.
        self.message = QtGui.QTextEdit()
        self.log = QtGui.QTextEdit()


        self.layout.addLayout(self.statusBars)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.log)

        self.setupStyles()

        self.setupMessage()
        self.setupLog()

    def setupStyles(self):
        """ Setups three styles for the bars: Red, Yellow and Default. It is meant to be more graphical to the user regarding
        the availability of resources."""
        self.RED_STYLE = """
                QProgressBar{
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center
                }

                QProgressBar::chunk {
                    background-color: red;
                    width: 10px;
                    margin: 1px;
                }
                """

        self.DEFAULT_STYLE = """
                QProgressBar{
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center
                }

                QProgressBar::chunk {
                    background-color: green;
                    width: 10px;
                    margin: 1px;
                }
                """

        self.YELLOW_STYLE = """
                QProgressBar{
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center
                }

                QProgressBar::chunk {
                    background-color: yellow;
                    width: 10px;
                    margin: 1px;
                }
                """

    def setupMessage(self):
        """Starts the message box with a title that will always be displayed."""
        self.message.setHtml('<h1>%s</h1>'%self.messageTitle)

    def updateMessage(self,msg):
        """Updates the message displayed to the user.
        msg -- string or array, in which case every item will be displayed in a new line."""
        message = '<h1>%s</h1>'%self.messageTitle
        if type(msg) == type([]):
            for m in msg:
                message += '<br/>%s'%m
        else:
            message += '<br/>%s'%msg

        self.message.setHtml(message)

    def setupLog(self):
        """Startes the log box with a title that will always be displayed on top."""
        self.log.setHtml('<h1>%s</h1>' % self.logTitle)
        self.logText = []

    def updateLog(self,msg):
        """Updates the log displayed to the user by prepending the desired message to the available messages.
        msg -- string or array, in which case every item will be displayed in a new line."""
        message = '<h1>%s</h1>'%self.logTitle

        if type(msg) == type([]):
            for m in msg:
                self.logText.append(m)
        else:
            self.logText.append(msg)

        if len(self.logText)>self.logMaxLength:
            until = self.logMaxLength
        else:
            until = len(self.logText)
        for m in self.logText[-until::-1]:
            message += "<br />%s"%m
        self.log.setHtml(message)