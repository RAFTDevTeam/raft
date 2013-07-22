#
# Author: Nathan Hamiel
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

import os

class Payloads(object):
    """ Class that handles the identification and loading of payloads """
    
    def __init__(self, framework):
        self.framework = framework
        self.payloads_dir = os.path.join(self.framework.get_data_dir(), 'payloads')
        self.functions_dir = os.path.join(self.framework.get_data_dir(), 'functions')
    
    def list_files(self):
        
        payload_listing = os.listdir(self.payloads_dir)
        
        return payload_listing
        
    def read_data(self, payload_file):
        
        f = open(os.path.join(self.payloads_dir, payload_file), "rb")
        vals = list()
        
        for item in f.readlines():
            if item.startswith(b"# "):
                pass
            else:
                vals.append(item.rstrip().decode())
                
        f.close()
        
        return vals
    
    def list_function_files(self):
        
        function_listing = os.listdir(self.functions_dir)
        
        return function_listing
    
    def read_function(self, function_file):
        
        #ToDo: Check to make sure this properly displays Python files
        f = open(os.path.join(self.functions_dir, function_file), "rb")
        vals = list()
        
        for item in f.readlines():
            vals.append(item)
            
        f.close()
        
        return vals
        
    
    
    
