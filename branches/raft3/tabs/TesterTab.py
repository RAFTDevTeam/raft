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
import uuid

import PyQt4
from PyQt4.QtCore import Qt, QObject, SIGNAL, QUrl
from PyQt4.QtGui import *
from PyQt4 import Qsci

from core.network.StandardNetworkAccessManager import StandardNetworkAccessManager
from core.web.TesterPageFactory import TesterPageFactory
from core.web.RenderingWebView import RenderingWebView

from core.database.constants import ResponsesTable
# from core.tester.CSRFTester import CSRFTester
from core.tester import CSRFTester
from core.tester.ClickjackingTester import ClickjackingTester
from actions import interface

class TesterTab(QObject):
    def __init__(self, framework, mainWindow):
        QObject.__init__(self, mainWindow)
        self.framework = framework
        self.mainWindow = mainWindow

        self.networkAccessManager = StandardNetworkAccessManager(self.framework, self.framework.get_global_cookie_jar())
        self.pageFactory = TesterPageFactory(self.framework, self.console_log, self.networkAccessManager, self)

        self.framework.subscribe_populate_tester_csrf(self.tester_populate_csrf)
        self.framework.subscribe_populate_tester_click_jacking(self.tester_populate_click_jacking)

        self.Data = None
        self.cursor = None
        self.framework.subscribe_database_events(self.db_attach, self.db_detach)

        self.cjTester = ClickjackingTester(self.framework)
        
        self.setScintillaProperties(self.mainWindow.csrfGenEdit)
        self.mainWindow.testerRegenBtn.clicked.connect(self.regen_csrf)

        self.setScintillaProperties(self.mainWindow.testerClickjackingEditHtml)
        self.mainWindow.testerClickjackingSimulateButton.clicked.connect(self.handle_testerClickjackingSimulateButton_clicked)
        self.mainWindow.testerClickjackingOpenInBrowserButton.clicked.connect(self.handle_testerClickjackingOpenInBrowserButton_clicked)
        self.mainWindow.testerClickjackingGenerateButton.clicked.connect(self.handle_testerClickjackingGenerateButton_clicked)

        self.clickjackingRenderWebView = RenderingWebView(self.framework, self.pageFactory, self.mainWindow.testerClickjackingEmbeddedBrowserPlaceholder)
        self.clickjackingRenderWebView.loadFinished.connect(self.handle_clickjackingRenderWebView_loadFinished)
        self.clickjackingRenderWebView.urlChanged.connect(self.handle_clickjackingRenderWebView_urlChanged)
        self.clickjackingRenderWebView.titleChanged.connect(self.handle_clickjackingRenderWebView_titleChanged)

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
        
        responseItems = interface.data_row_to_response_items(row)
        
        url = responseItems[ResponsesTable.URL]
        # Are reqHeaders necessary?
        reqHeaders = str(responseItems[ResponsesTable.REQ_HEADERS], 'utf-8', 'ignore')
        reqData = str(responseItems[ResponsesTable.REQ_DATA], 'utf-8', 'ignore') # TODO: consider replacement
        
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
    
        row = self.Data.read_responses_by_id(self.cursor, response_id)
        if not row:
            return
        responseItems = interface.data_row_to_response_items(row)
        url = responseItems[ResponsesTable.URL]
        self.setup_clickjacking_url(url)

    def setup_clickjacking_url(self, url):
        self.mainWindow.testerClickjackingUrlEdit.setText('http://attacker.example.com/frame.html')
        self.mainWindow.testerClickjackingConsoleLogTextEdit.setText('')

        self.mainWindow.testerClickjackingTargetURL.setText(url)
        self.mainWindow.testerClickjackingEditHtml.setText(self.cjTester.make_default_frame_html(url))

    def handle_testerClickjackingSimulateButton_clicked(self):
        self.mainWindow.testerClickjackingConsoleLogTextEdit.setText('Starting Clickjacking Simulation')
        url = self.mainWindow.testerClickjackingUrlEdit.text()
        # TODO: better way than to force unique URL to reload content ?
        if '?' in url:
            url = url[0:url.find('?')+1] + uuid.uuid4().hex
        else:
            url = url + '?' + uuid.uuid4().hex
        headers = ''
        body = self.mainWindow.testerClickjackingEditHtml.text()
        content_type = 'text/html'
        self.clickjackingRenderWebView.fill_from_response(url, headers, body, content_type)

    def handle_testerClickjackingGenerateButton_clicked(self):
        entry = self.mainWindow.testerClickjackingTargetURL.text()
        url = QUrl.fromUserInput(entry).toEncoded().data().decode('utf-8')
        self.setup_clickjacking_url(url)

    def handle_testerClickjackingOpenInBrowserButton_clicked(self):
        pass

    def handle_clickjackingRenderWebView_loadFinished(self):
        self.console_log('info', 'Page load finished')

    def handle_clickjackingRenderWebView_urlChanged(self):
        url = self.clickjackingRenderWebView.url().toEncoded().data().decode('utf-8')
        self.mainWindow.testerClickjackingUrlEdit.setText(url)

    def handle_clickjackingRenderWebView_titleChanged(self, title):
        self.console_log('info', 'Page title changed to [%s]' % (title))

    def console_log(self, logtype, logmessage):
        msg = None
        if 'javaScriptConsoleMessage' == logtype:
            (lineNumber, sourceID, message) = logmessage
            msg = 'console log from [%s / %s]: %s' % (lineNumber, sourceID, message)
        elif 'info':
            msg = logmessage

        if msg:
            curtext = self.mainWindow.testerClickjackingConsoleLogTextEdit.toPlainText()
            curtext += '\n' + msg
            self.mainWindow.testerClickjackingConsoleLogTextEdit.setPlainText(curtext)

    # TODO: refactor into common module in framework
    def setScintillaProperties(self, scintillaWidget, contentType = 'html'):
        scintillaWidget.setFont(self.framework.get_font())
        scintillaWidget.setWrapMode(1)
        scintillaWidget.zoomTo(self.framework.get_zoom_size())
        # TOOD: set based on line numbers (size is in pixels)
        scintillaWidget.setMarginWidth(1, '1000')
        lexerInstance = Qsci.QsciLexerHTML(scintillaWidget)
        lexerInstance.setFont(self.framework.get_font())
        scintillaWidget.setLexer(lexerInstance)
        self.framework.subscribe_zoom_in(lambda: scintillaWidget.zoomIn())
        self.framework.subscribe_zoom_out(lambda: scintillaWidget.zoomOut())

