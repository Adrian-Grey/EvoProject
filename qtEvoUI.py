import sys
import numpy as np
from scipy.stats import norm
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from PyQt5 import QtCore, QtWidgets, QtWebSockets, QtNetwork, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QPlainTextEdit, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit
from PyQt5.QtCore import *
from evoBackend import snapshot

import json

#implement graphs
    # continue standardizing inter-program messages re: metadata
    # figure out next steps


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
            mainWin.handleData(data)
        elif "Simulation incremented" in msg:
            self.send_message("getPop")
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
        self.population_graph = rectarea

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

    def handleData(self, data):
        if "success" in data and data["success"]:
            if data["type"] == "save_file_list":
                print("recieved save file data:")
                print(data)
                self.loadselector.clear()
                for file in data["data"]:
                    self.loadselector.addItem(file)
            elif data["type"] == "population_list": 
                print("recieved population data")
                self.population_graph.updatePoints(data["data"])
            elif data["type"] in ["load_result", "new_start", "reset"]:
                self.population_graph.updatePoints(data["data"])
                self.updateResults(data["status_text"])
        else:
            print(f"Not success? {data}")
            self.updateResults(data["status_text"])



class GraphicsWidget(QWidget):
    def __init__(self):
        super().__init__()
        # self.setFixedSize(300, 300)

        self.pointsX = []
        self.pointsY = []

        self.view = FigureCanvas(Figure(figsize=(3, 3)))
        self.axes = self.view.figure.subplots()
        
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.view)
        self.setLayout(vlayout)

    def updatePoints(self, input_data):
        self.pointsX.clear()
        self.pointsY.clear()
        for pair in input_data:
            self.pointsX.append(pair["time"])
            self.pointsY.append(pair["count"])

        self.axes.clear()
        self.axes.plot(self.pointsX, self.pointsY)
        self.view.draw()

if __name__ == "__main__":
    global mainWin
    app = QtWidgets.QApplication(sys.argv)
    client = Client(app)
    mainWin = MainWindow(client)
    mainWin.show()

    sys.exit( app.exec_() )