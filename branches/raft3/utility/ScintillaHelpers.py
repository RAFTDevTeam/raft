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

from PyQt4 import Qsci

def SetScintillaProperties(framework, scintillaWidget, contentType = 'html'):
    scintillaWidget.setFont(framework.get_font())
    scintillaWidget.setWrapMode(1)
    scintillaWidget.zoomTo(framework.get_zoom_size())
    # TOOD: set based on line numbers (size is in pixels)
    scintillaWidget.setMarginWidth(1, '1000')
    if 'html' == contentType:
        lexerInstance = Qsci.QsciLexerHTML(scintillaWidget)
    elif 'javascript' == contentType:
        lexerInstance = Qsci.QsciLexerJavaScript(scintillaWidget)
    elif 'python' == contentType:
        lexerInstance = Qsci.QsciLexerPython(scintillaWidget)
    else:
        lexerInstance = Qsci.QsciLexer(scintillaWidget)
    lexerInstance.setFont(framework.get_font())
    scintillaWidget.setLexer(lexerInstance)
