#
# Author: Gregory Fleischer (gfleischer@gmail.com)
#
# Copyright (c) 2013 RAFT Team
#
# This file is part of RAFT.
#
# RAFT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# RAFT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RAFT.  If not, see <http://www.gnu.org/licenses/>.
#

import PyQt4
from PyQt4.QtCore import Qt, QObject, SIGNAL, QDateTime, QSize
from PyQt4.QtGui import *

from actions import encoderlib
from utility.HexDump import HexDump

class EncoderTab(QObject):
    def __init__(self, framework, mainWindow):
        QObject.__init__(self, mainWindow)
        self.framework = framework
        self.mainWindow = mainWindow

        self.hexDump = HexDump()

        self.mainWindow.encodeButton.clicked.connect(self.encode_data)
        self.mainWindow.encodeWrapButton.clicked.connect(self.encode_wrap)
        self.mainWindow.decodeButton.clicked.connect(self.decode_data)
        self.mainWindow.decodeWrapButton.clicked.connect(self.decode_wrap)

        self.mainTab = QWidget(self.mainWindow.encoderTabWidget)
        self.make_encoder_decoder_display_tab(self.mainTab)
        self.mainWindow.encoderTabWidget.addTab(self.mainTab, 'Encoding/Decoding')

    def make_encoder_decoder_display_tab(self, parentWidget):
        currentWidget = parentWidget
        vbox_layout = QVBoxLayout(currentWidget)

        encoderTabWidget = QTabWidget(currentWidget)
        decoderTabWidget = QTabWidget(currentWidget)

        self.encoderTextEdit, self.encoderHexEdit = self.make_text_hex_tab(encoderTabWidget)
        self.decoderTextEdit, self.decoderHexEdit = self.make_text_hex_tab(decoderTabWidget)

        vbox_layout.addWidget(encoderTabWidget)
        vbox_layout.addWidget(decoderTabWidget)

    def make_text_hex_tab(self, currentWidget):

        thisTabWidget = currentWidget

        textTab = QWidget(thisTabWidget)
        thisTabWidget.addTab(textTab, 'Text')
        hexTab = QWidget(thisTabWidget)
        thisTabWidget.addTab(hexTab, 'Hex')

        vlayout_text = QVBoxLayout(textTab)
        thisTextEdit = QTextEdit(textTab)
        vlayout_text.addWidget(thisTextEdit)

        vlayout_hex = QVBoxLayout(hexTab)
        thisHexEdit = QTextEdit(hexTab)
        vlayout_hex.addWidget(thisHexEdit)

        return (thisTextEdit, thisHexEdit)

    def encode_data(self):
        """ Encode the specified value """
        
        encode_value = str(self.encoderTextEdit.toPlainText())
        encode_method = self.mainWindow.encodingMethodCombo.currentText()
        value = encoderlib.encode_values(encode_value, encode_method)
        self.decoderTextEdit.setPlainText(value)
        
    def encode_wrap(self):
        """ Wrap the specified values in the encode window """
        
        encode_value = str(self.encoderTextEdit.toPlainText())
        wrap_value = self.mainWindow.encodingWrapCombo.currentText()
        value = encoderlib.wrap_encode(encode_value, wrap_value)
        self.encoderTextEdit.setPlainText(value)
        
    def decode_data(self):
        """ Decode the specified value from the decoder interface """
        
        decode_value = str(self.decoderTextEdit.toPlainText())
        decode_method = self.mainWindow.decodeMethodCombo.currentText()
        value = encoderlib.decode_values(decode_value, decode_method)
        self.encoderTextEdit.setPlainText(value)
        
    def decode_wrap(self):
        """ Wrap the specified values in the decode window """
        
        decode_value = str(self.decoderTextEdit.toPlainText())
        wrap_value = self.mainWindow.decodeWrapCombo.currentText()
        value = encoderlib.wrap_decode(decode_value, wrap_value)
        self.decoderTextEdit.setPlainText(value)
                                                             
        
