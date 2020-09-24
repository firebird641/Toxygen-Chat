import plugin_super_class
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap
import json
import time
import os

class QRGenerator(plugin_super_class.PluginSuperClass):
    def __init__(self, *args):
        super(QRGenerator, self).__init__('QRCode Generator', 'qr', *args)
        self._tmp = None
    def get_description(self):
        return QtWidgets.QApplication.translate("qr", 'Generates and displays a QR Code of your TOX-ID. Needs qrencode to be installed.')
    def start(self):
        pass
    def stop(self):
        pass
    def get_window(self):
        inst = self
        class Window(QtWidgets.QWidget):
            def __init__(self):
                super(Window, self).__init__()
                self.setGeometry(QtCore.QRect(450, 300, 350, 100))
                self.resize(400,400)
                label = QLabel(self)
                os.system("qrencode "+inst._tox.self_get_address()+" -o /usr/bin/toxygen/images/qrcode.png")
                pixmap = QPixmap('/usr/bin/toxygen/images/qrcode.png')
                scaled = pixmap.scaled(400,400)
                label.setPixmap(scaled)
        return Window()
