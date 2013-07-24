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

from io import StringIO

class ClickjackingTester():

    def __init__(self, framework):
        self.framework = framework


    def make_default_frame_html(self, url):
        html = StringIO()
        html.write('<html>\n')
        html.write('  <head>\n')
        html.write('    <title>Framed Content</title>\n')
        html.write('  </head>\n')
        html.write('  <body>\n')
        html.write('    <iframe src="%s"></iframe>\n' % (url))
        html.write('  </body>\n')
        html.write('</html>\n')

        return html.getvalue()
