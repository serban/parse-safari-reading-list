#!/usr/bin/env python
# vim:set ts=8 sw=4 sts=4 et:

# Copyright (c) 2012 Serban Giuroiu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# ------------------------------------------------------------------------------

import os
import pdb
import plistlib
import pprint
import subprocess
import time

# ------------------------------------------------------------------------------

EXIT_SUCCESS    = 0
EXIT_FAILURE    = 1
EXIT_CMDFAILURE = 2

# TTY Colors
NOCOLOR     = '\033[0m'
RED         = '\033[01;31m'
GREEN       = '\033[01;32m'
YELLOW      = '\033[01;33m'
BLUE        = '\033[01;34m'
MAGENTA     = '\033[01;35m'
CYAN        = '\033[01;36m'
WHITE       = '\033[01;37m'

def msg(s):
    print(GREEN + "*", s, NOCOLOR)

def err(s):
    print(RED + "!", s, NOCOLOR)

def dbg(s):
    if not __debug__:
        return

    if isinstance(s, dict) or isinstance(s, list):
        print(YELLOW + "%", pprint.pformat(s, indent=2), NOCOLOR)
    else:
        print(YELLOW + "%", s, NOCOLOR)

def sep():
    try:
        num_columns = int(subprocess.getoutput('stty size').split()[1])
    except IndexError:
        num_columns = 80

    s = "".join(["-" for i in range(num_columns)])

    print(WHITE + s + NOCOLOR)

def run_process(s):
    if __debug__:
        print(CYAN + ">", s, NOCOLOR)

    subprocess.call(s, shell=True)

class Timer(object):
    def start(self):
        self.start_time = int(time.time())

    def stop(self):
        self.end_time = int(time.time())

    def time_delta(self):
        return self.end_time - self.start_time

    def string_delta(self):
        total = self.time_delta()

        days    = total     // 86400
        remain  = total     %  86400
        hours   = remain    //  3600
        remain  = remain    %   3600
        minutes = remain    //    60
        seconds = remain    %     60

        return str(days) + "d " + str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s"

# ------------------------------------------------------------------------------

binary_plist_path = os.path.expanduser('~/Library/Safari/Bookmarks.plist')

def read_plist():
    plutil_args = ['plutil', '-convert', 'xml1', '-o', '-', binary_plist_path]
    xml_plist_bytes = subprocess.check_output(plutil_args)

    return plistlib.readPlistFromBytes(xml_plist_bytes)

def parse_reading_list():
    plist = read_plist()

    reading_list = list()

    for child in plist.get('Children', []):
        if child.get('Title') == 'com.apple.ReadingList':
            reading_list = child.get('Children', [])

    reading_list_items = list()

    for item in reading_list:
        assert item.get('WebBookmarkType') == 'WebBookmarkTypeLeaf'
        assert item.get('URLString') is not None

        reading_list_item = {
            'url':          item.get('URLString'),
            'title':        item.get('URIDictionary', {}).get('title'),
            'preview_text': item.get('ReadingList', {}).get('PreviewText'),
        }

        reading_list_items.append(reading_list_item)

    return reading_list_items

def main():
    for item in parse_reading_list():
        print(item['title'])

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
