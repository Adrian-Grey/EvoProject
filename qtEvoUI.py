import sys
from PyQt5 import QtCore, QtWidgets, QtWebSockets, QtNetwork
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QPlainTextEdit
from PyQt5.QtCore import QSize, QUrl

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

        pybutton = QPushButton('Get population', self)
        pybutton.clicked.connect(self.clickMethod)
        pybutton.resize(200,32)
        pybutton.move(5, 5)

        textinput = QPlainTextEdit(self)
        textinput.setReadOnly(True)
        textinput.resize(200,32)
        textinput.move(5, 44)
        self.resultsText = textinput
        # textinput.setPlaceholderText("Results go here")
        textinput.appendPlainText("Results go here")

    def clickMethod(self):
        print('Clicked Pyqt button.')
        client.send_message("getPop")
    
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