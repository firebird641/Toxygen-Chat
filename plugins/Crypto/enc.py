import plugin_super_class
from PyQt5 import QtGui, QtWidgets, QtCore
import json
import time
import os
import waterfall

class Message:
    def __init__(self, message_type, owner, time):
        self._time = time
        self._type = message_type
        self._owner = owner
    def get_type(self):
        return self._type
    def get_owner(self):
        return self._owner
    def mark_as_sent(self):
        self._owner = 0

class TextMessage(Message):
    def __init__(self, message, owner, time, message_type):
        super(TextMessage, self).__init__(message_type, owner, time)
        self._message = message
    def get_data(self):
        return self._message, self._owner, self._time, self._type

class CryptMessage(plugin_super_class.PluginSuperClass):
    def __init__(self, *args):
        super(CryptMessage, self).__init__('Message Overlay Encryption', 'enc', *args)
        self._data = json.loads(self.load_settings())
        self._tmp = None
    def get_description(self):
        return QtWidgets.QApplication.translate("enc", 'Encrypts text messages with specific users.')
    def start(self):
        self._tmp_send = self._profile.send_message
        self._tmp_recv = self._profile.new_message
        def send_func(text, friend_num=None):
            if len(text)==0:
                return
            if not self._profile.is_active_a_friend():
                self._profile.send_gc_message(text)
                return
            if friend_num is None:
                friend_num = self._profile.get_active_number()
            if self._profile.get_friend_by_number(friend_num).tox_id in self._data and len(text) != 0:
                encrypted = waterfall.encrypt_text(text, self._data[self._profile.get_friend_by_number(friend_num).tox_id])
            message_type = 0
            friend = self._profile.get_friend_by_number(friend_num)
            friend.inc_receipts()
            if friend.status is not None:
                if self._profile.get_friend_by_number(friend_num).tox_id in self._data:
                    self._profile.split_and_send(friend.number, message_type, encrypted.encode('utf-8'))
                else:
                    self._profile.split_and_send(friend.number, message_type, text.encode('utf-8'))
            t = time.time()
            if friend.number == self._profile.get_active_number() and self._profile.is_active_a_friend():
                if self._profile.get_friend_by_number(friend_num).tox_id in self._data:
                    self._profile.create_message_item(text+" [ENCRYPTED]", t, 2, message_type)
                    self._profile._screen.messageEdit.clear()
                    self._profile._messages.scrollToBottom()
                else:
                    self._profile.create_message_item(text, t, 2, message_type)
                    self._profile._screen.messageEdit.clear()
                    self._profile._messages.scrollToBottom()
            friend.append_message(TextMessage(text+" [ENCRYPTED]", 2, t, message_type))
        def recv_func(friend_num, message_type, message):
            if self._profile.get_friend_by_number(friend_num).tox_id in self._data:
                try:
                    message = waterfall.decrypt_text(message, self._data[self._profile.get_friend_by_number(friend_num).tox_id])+" [ENCRYPTED]"
                except:
                    message = message
            if friend_num == self._profile.get_active_number() and self._profile.is_active_a_friend():
                t = time.time()
                self._profile.create_message_item(message, t, 1, message_type)
                self._profile._messages.scrollToBottom()
                self._profile.get_curr_friend().append_message(TextMessage(message, 1, t, message_type))
            else:
                friend = self._profile.get_friend_by_number(friend_num)
                friend.inc_messages()
                friend.append_message(TextMessage(message, 1, time.time(), message_type))
                if not friend.visibility:
                    self._profile.update_filtration()
        self._profile.send_message = send_func
        self._profile.new_message = recv_func
    def stop(self):
        self._profile.send_message = self._tmp_send
        self._profile.new_message = self._tmp_recv
    def readjs(self):
        js = self.load_settings()
        return js
    def writejs(self,data):
        if len(data)<2:
            data = "{ }"
        self.save_settings(data)
    def get_window(self):
        inst = self
        class Window(QtWidgets.QWidget):
            def __init__(self):
                super(Window, self).__init__()
                self.setGeometry(QtCore.QRect(450, 300, 350, 100))
                self.resize(814, 509)
                self.plainTextEdit = QtWidgets.QPlainTextEdit(self)
                self.plainTextEdit.setGeometry(QtCore.QRect(0, 10, 811, 371))
                self.lineEdit = QtWidgets.QLineEdit(self)
                self.lineEdit.setGeometry(QtCore.QRect(0, 390, 811, 41))
                self.lineEdit.setReadOnly(True)
                self.pushButton = QtWidgets.QPushButton("Save JSON", self)
                self.pushButton.setGeometry(QtCore.QRect(0, 440, 404, 61))
                self.pushButton_2 = QtWidgets.QPushButton("Generate Key", self)
                self.pushButton_2.setGeometry(QtCore.QRect(410, 440, 401, 61))
                self.pushButton.clicked.connect(lambda data: inst.writejs(self.plainTextEdit.toPlainText()))
                self.pushButton_2.clicked.connect(self.genkey)
                js = inst.readjs()
                self.plainTextEdit.insertPlainText(js)
            def genkey(self):
                key = waterfall.random_key()
                self.lineEdit.setText(key)
        return Window()
