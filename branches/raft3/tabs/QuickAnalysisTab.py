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

import os

import PyQt4
from PyQt4.QtCore import Qt, QObject, SIGNAL, QUrl
from PyQt4.QtGui import *
from PyQt4 import Qsci
try:
    from PyQt4.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QString = type("")

from utility import ScintillaHelpers

class QuickAnalysisTab(QObject):
    def __init__(self, framework, mainWindow):
        QObject.__init__(self, mainWindow)
        self.framework = framework
        QObject.connect(self, SIGNAL('destroyed(QObject*)'), self._destroyed)
        self.mainWindow = mainWindow

        self.mainWindow.quickAnalysisLoadFromFile.clicked.connect(self.handle_quickAnalysisLoadFromFile_clicked)
        self.mainWindow.quickAnalysisSaveToFile.clicked.connect(self.handle_quickAnalysisSaveToFile_clicked)
        self.mainWindow.quickAnalysisRunAnalysis.clicked.connect(self.handle_quickAnalysisRunAnalysis_clicked)
        self.mainWindow.quickAnalysisClearResults.clicked.connect(self.handle_quickAnalysisClearResults_clicked)

        # TODO: get python formatting working
        ScintillaHelpers.SetScintillaProperties(self.framework, self.mainWindow.quickAnalysisCodeEntry, 'python')
        self.mainWindow.quickAnalysisCodeEntry.setAutoIndent(True)

    def set_quick_analysis_thread(self, quickAnalysisThread):
        QObject.connect(self, SIGNAL('runQuickAnalysisFinished(QString)'), self.handle_quickAnalysisFinished)
        
    def _destroyed(self):
        pass

    def handle_quickAnalysisLoadFromFile_clicked(self):
        filename = QFileDialog.getOpenFileName(None, 'Open Python Script File', '', 'Python file (*.py)')

        if filename and os.path.exists(filename):
            fh = open(filename, 'r')
            python_code = fh.read()
            fh.close()
            self.mainWindow.quickAnalysisCodeEntry.setText(python_code)

    def handle_quickAnalysisSaveToFile_clicked(self):
        python_code = self.mainWindow.quickAnalysisCodeEntry.text()
        filename = QFileDialog.getSaveFileName(None, 'Save to file', '', '')
        if filename:
            fh = open(filename, 'w')
            fh.write(python_code)
            fh.close()

    def handle_quickAnalysisRunAnalysis_clicked(self):
        python_code = self.mainWindow.quickAnalysisCodeEntry.text()
        self.mainWindow.quickAnalysisThread.runQuickAnalysis(python_code, self)

    def handle_quickAnalysisClearResults_clicked(self):
        self.mainWindow.quickAnalysisOutputResults.setPlainText('')        

    def handle_quickAnalysisFinished(self, results):
        self.mainWindow.quickAnalysisOutputResults.setPlainText(results)


