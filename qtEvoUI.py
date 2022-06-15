import sys
from PyQt5 import QtCore, QtWidgets, QtWebSockets, QtNetwork, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QPlainTextEdit, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit
from PyQt5.QtCore import QSize, QUrl
from evoBackend import snapshot

import json

#implement graphs
    #pass population data points from dict in backend
    #use points to draw graph line using PolyLine

class Client(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)

        self.connected = False
        self.messageBuffer = []

        self.wsClient = QtWebSockets.QWebSocket("",QtWebSockets.QWebSocketProtocol.Version13,None)
        self.wsClient.error.connect(self.error)

        self.wsClient.open(QUrl("ws://127.0.0.1:8765"))
        self.wsClient.textMessageReceived.connect(self.onMessage)
        self.wsClient.connected.connect(self.onConnected)


    def send_message(self, msg):
        if (self.connected):
            print(f"client: send_message: {msg}")
            self.wsClient.sendTextMessage(msg)
        else:
            self.messageBuffer.append(msg)

    def onConnected(self):
        self.connected = True
        for msg in self.messageBuffer:
            self.send_message(msg)
        self.messageBuffer.clear()

    def onMessage(self, msg):
        print("onMessage: {}".format(msg))
        # check what type or kind of message this is
        # send type=results messages to updateResults
        # and send other types to the appropriate handler
        if msg[0] == "{":
            data = json.loads(msg)
            mainWin.updateData(data)
        else:
            mainWin.updateResults(msg)

    def error(self, error_code):
        print("error code: {}".format(error_code))
        print(self.wsClient.errorString())

    def close(self):
        self.wsClient.close()

class MainWindow(QMainWindow):
    def __init__(self, client):
        QMainWindow.__init__(self)
        self.client = client
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
        self.loadselector = loadselector
        # fetch the list of saved files
        self.getSaveFiles()

        loadbutton = QPushButton('Load',self)
        loadbutton.clicked.connect(self.onLoadClick)

        saveselector = QLineEdit(self)
        self.savefile = saveselector

        rectarea = GraphicsWidget()

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
        layout.addWidget(rectarea)

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

    def getSaveFiles(self):
        print("sent get save file req")
        self.client.send_message("save_files")

    def onLoadClick(self):
        self.onButtonPush(f"start,{self.loadselector.currentText()}")
    
    def updateResults(self, text):
        self.resultsText.clear()
        self.resultsText.appendPlainText(text)

    def updateData(self, data):
        if data["type"] == "save_file_list":
            print("recieved save file data:")
            print(data)
            self.loadselector.clear()
            for file in data["data"]:
                self.loadselector.addItem(file)

class GraphicsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 300)

    def setPoints(pointsList):
        self.points = pointsList

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        height = 300
        #                      left, top,                    width, height
        ourRect = QtCore.QRect(0, 0, self.width(), height)
        painter.fillRect(ourRect, QtGui.QBrush(QtCore.Qt.blue))
        #pen = QtGui.QPen(QtGui.QColor("red"), 10)
        #painter.setPen(pen)
        painter.drawRect(self.rect())

if __name__ == "__main__":
    global mainWin
    app = QtWidgets.QApplication(sys.argv)
    client = Client(app)
    mainWin = MainWindow(client)
    mainWin.show()

    sys.exit( app.exec_() )