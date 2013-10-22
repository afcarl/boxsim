#!/usr/bin/env python
# encoding: utf-8
"""
color.py

Created by Paul Fudal on 2013-10-22.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os

class Color(object):
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue
    
    def __str__(self):
        return "R:" + str(self.red) + " G:" + str(self.green) + " B:" + str(self.blue)
        
    def __repr__(self):
        return "R:" + str(self.red) + " G:" + str(self.green) + " B:" + str(self.blue)

