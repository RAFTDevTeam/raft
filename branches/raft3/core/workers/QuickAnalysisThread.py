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

import sys

from io import StringIO
from core.responses import RequestResponseFactory

from utility.ScriptLoader import ScriptLoader

from PyQt4.QtCore import Qt, QObject, SIGNAL, QThread, QTimer, QMutex
try:
    from PyQt4.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QString = type("")

class QuickAnalysisThread(QThread):
    def __init__(self, framework, parent = None):
        QThread.__init__(self, parent)
        self.framework = framework

        self.callback_object = None
        self.qtimer = QTimer()
        self.qlock = QMutex()
        QObject.connect(self, SIGNAL('quit()'), self.handle_quit)
        QObject.connect(self, SIGNAL('started()'), self.handle_started)

        self.Data = None
        self.read_cursor = None
        self.cursor = None

    def db_attach(self):
        self.Data = self.framework.getDB()
        self.read_cursor = self.Data.allocate_thread_cursor()

    def db_detach(self):
        self.close_cursor()
        self.Data = None

    def close_cursor(self):
        if self.read_cursor:
            self.read_cursor.close()
            self.Data.release_thread_cursor(self.read_cursor)
            self.read_cursor = None

    def run(self):
        QObject.connect(self, SIGNAL('do_runQuickAnalysis()'), self.handle_runQuickAnalysis, Qt.DirectConnection)
        self.exec_()

    def runQuickAnalysis(self, python_code, callback_object):
        self.python_code = python_code
        self.callback_object = callback_object
        print('run called')
        QTimer.singleShot(50, self, SIGNAL('do_runQuickAnalysis()'))

    def handle_quit(self):
        self.framework.debug_log('QuickAnalysisThread quit...')
        self.close_cursor()
        self.exit(0)

    def handle_started(self):
        self.framework.debug_log('QuickAnalysisThread started...')
        self.framework.subscribe_database_events(self.db_attach, self.db_detach)

    def handle_runQuickAnalysis(self):
        results = ''
        stdout_io = StringIO()
        if not self.qlock.tryLock():
            self.framework.debug_log('failed to acquire lock for quick analysis')
        else:
            original_stdout = sys.stdout
            sys.stdout = stdout_io
            try:
                python_code = str(self.python_code)
                scriptLoader = ScriptLoader()
                global_ns = local_ns = {}
                script_env = scriptLoader.load_from_string(python_code, global_ns, local_ns)
                 
                begin_method = script_env.functions.get('begin')
                if begin_method:
                    begin_method()

                process_request_method = script_env.functions['process_request']
                factory = RequestResponseFactory.RequestResponseFactory(self.framework, None)
                for row in self.Data.read_all_responses(self.read_cursor):
                    try:
                        rr = factory.fill_by_row(row)
                        process_request_method(rr)
                    except Exception as e:
                        results += '\nEncountered processing error: %s' % (e)

                end_method = script_env.functions.get('end')
                if end_method:
                    end_method()
                
            except Exception as error:
                self.framework.report_exception(error)
                results += '\nEncountered processing error: %s' % (error)
            finally:
                sys.stdout = original_stdout
                self.qlock.unlock()
                
        if self.callback_object:
            if results:
                results += '\n'
            results += stdout_io.getvalue()
            self.callback_object.emit(SIGNAL('runQuickAnalysisFinished(QString)'), results)
        
        
