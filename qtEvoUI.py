import sys
from PyQt5 import QtCore, QtWidgets, QtWebSockets, QtNetwork
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QPlainTextEdit, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit
from PyQt5.QtCore import QSize, QUrl

from evoBackend import snapshot

#make backend command to pass through all save files
#implement graphs

class Client(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)

        self.client =  QtWebSockets.QWebSocket("",QtWebSockets.QWebSocketProtocol.Version13,None)
        self.client.error.connect(self.error)

        self.client.open(QUrl("ws://127.0.0.1:8765"))
        self.client.textMessageReceived.connect(self.onMessage)

    def send_message(self, msg):
        print(f"client: send_message: {msg}")
        self.client.sendTextMessage(msg)

    def onMessage(self, msg):
        print("onMessage: {}".format(msg))
        mainWin.updateResults(msg)

    def error(self, error_code):
        print("error code: {}".format(error_code))
        print(self.client.errorString())

    def close(self):
        self.client.close()

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(300, 200))    
        self.setWindowTitle("PyQt button example - pythonprogramminglanguage.com") 

        layout = QVBoxLayout()

        loadlayout = QHBoxLayout()

        savelayout = QHBoxLayout()

        getpopbutton = QPushButton('Get population', self)
        getpopbutton.clicked.connect(self.onGetPopClick)
        
        startbutton = QPushButton('Start', self)
        startbutton.clicked.connect(self.onStartClick)

        runsimbutton1 = QPushButton('Advance simulation by 1 tick', self)
        runsimbutton1.clicked.connect(self.onRunSimClick1)

        runsimbutton5 = QPushButton('Advance simulation by 5 ticks', self)
        runsimbutton5.clicked.connect(self.onRunSimClick5)

        runsimbutton10 = QPushButton('Advance simulation by 10 ticks', self)
        runsimbutton10.clicked.connect(self.onRunSimClick10)

        resetbutton = QPushButton('Reset simulation',self)
        resetbutton.clicked.connect(self.onResetClick)

        snapshotbutton = QPushButton('Save',self)
        snapshotbutton.clicked.connect(self.onSnapshotClick)

        textoutput = QPlainTextEdit(self)
        textoutput.setReadOnly(True)
        self.resultsText = textoutput
        textoutput.appendPlainText("Results go here")

        loadselector = QComboBox(self)
        loadselector.addItems(["default.json","save1.json","save2.json"])
        self.loadselector = loadselector

        loadbutton = QPushButton('Load',self)
        loadbutton.clicked.connect(self.onLoadClick)

        saveselector = QLineEdit(self)
        self.savefile = saveselector

        loadlayout.addWidget(loadselector)
        loadlayout.addWidget(loadbutton)

        savelayout.addWidget(snapshotbutton)
        savelayout.addWidget(saveselector)

        layout.addWidget(startbutton)
        layout.addLayout(savelayout)
        layout.addLayout(loadlayout)
        layout.addWidget(runsimbutton1)
        layout.addWidget(runsimbutton5)
        layout.addWidget(runsimbutton10)
        layout.addWidget(getpopbutton)
        layout.addWidget(resetbutton)
        layout.addWidget(textoutput)

        mainWidget = QWidget()
        mainWidget.setLayout(layout)
        self.setCentralWidget(mainWidget)

    def onButtonPush(self, input):
        print('Clicked Pyqt button.')
        client.send_message(input)

    def onGetPopClick(self):
        self.onButtonPush("getPop")

    def onStartClick(self):
        self.onButtonPush("start")

    def onRunSimClick1(self):
        self.onButtonPush("runSim,1")

    def onRunSimClick5(self):
        self.onButtonPush("runSim,5")

    def onRunSimClick10(self):
        self.onButtonPush("runSim,10")

    def onResetClick(self):
        self.onButtonPush("reset")
    
    def onSnapshotClick(self):
        self.onButtonPush(f"snapshot,{self.savefile.text()}")

    def onLoadClick(self):
        self.onButtonPush(f"start,{self.loadselector.currentText()}")
    
    def updateResults(self, text):
        self.resultsText.clear()
        self.resultsText.appendPlainText(text)

if __name__ == "__main__":
    global client
    global mainWin
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    client = Client(app)

    sys.exit( app.exec_() )