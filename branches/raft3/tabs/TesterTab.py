#
# Author: Nathan Hamiel
#         Gregory Fleischer (gfleischer@gmail.com)
#
# Copyright (c) 2011 RAFT Team
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

import re

import PyQt4
from PyQt4.QtCore import Qt, QObject, SIGNAL, QUrl
from PyQt4.QtGui import *
from PyQt4 import Qsci

from core.database.constants import ResponsesTable
# from core.tester.CSRFTester import CSRFTester
from core.tester import CSRFTester

class TesterTab(QObject):
    def __init__(self, framework, mainWindow):
        QObject.__init__(self, mainWindow)
        self.framework = framework
        self.mainWindow = mainWindow

        self.framework.subscribe_populate_tester_csrf(self.tester_populate_csrf)
        self.framework.subscribe_populate_tester_click_jacking(self.tester_populate_click_jacking)

        self.Data = None
        self.cursor = None
        self.framework.subscribe_database_events(self.db_attach, self.db_detach)
        
        lexer = Qsci.QsciLexerHTML()
        self.mainWindow.csrfGenEdit.setLexer(lexer)
        
        self.mainWindow.testerRegenBtn.clicked.connect(self.regen_csrf)

    def db_attach(self):
        self.Data = self.framework.getDB()
        self.cursor = self.Data.allocate_thread_cursor()

    def db_detach(self):
        self.close_cursor()
        self.Data = None

    def close_cursor(self):
        if self.cursor and self.Data:
            self.cursor.close()
            self.Data.release_thread_cursor(self.cursor)
            self.cursor = None

    def tester_populate_csrf(self, response_id):
        
        row = self.Data.read_responses_by_id(self.cursor, response_id)
        
        if not row:
            return
        
        responseItems = [m or '' for m in list(row)]
        
        url = str(responseItems[ResponsesTable.URL])
        # Are reqHeaders necessary?
        reqHeaders = str(responseItems[ResponsesTable.REQ_HEADERS])
        reqData = str(responseItems[ResponsesTable.REQ_DATA])
        
        data = reqHeaders + "\n" + reqData
        
        # Check to ensure that either a GET or a POST is being used.
        check = re.compile("^(GET|POST)", re.I)
        result = check.match(reqHeaders)
        if not result:
            return()
        
        # htmlresult = CSRFTester.generate_csrf_html(self, url, reqHeaders, reqData)
        
        htmlresult = CSRFTester.generate_csrf_html(url, reqData)
        
        self.mainWindow.testerCSRFURLEdit.setText(url)
        self.mainWindow.csrfGenEdit.setText(htmlresult)
        self.mainWindow.csrfReqEdit.setPlainText(data)
        
    def regen_csrf(self):
        if self.mainWindow.testerFormGen.isChecked():
            print("Form")
        if self.mainWindow.testerImgGen.isChecked():
            url = self.mainWindow.testerCSRFURLEdit.text()
            htmlresult = CSRFTester.generate_csrf_img(url, self.mainWindow.csrfGenEdit.text())
            self.mainWindow.csrfGenEdit.setText(htmlresult)
    
        

    def tester_populate_click_jacking(self, response_id):
        print(('IMPLEMENT ME: tester click jacking', response_id))

