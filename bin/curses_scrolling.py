#!/usr/bin/env python

"""
Lyle Scott, III
lyle@digitalfoo.net

A simple demo that uses curses to scroll the terminal.
"""
import curses
import sys
import random
import time
import signal, os
import gnomekeyring
import sys
import pygtk
pygtk.require('2.0')
# import gtk # sets app name
import gnomekeyring
import curses
from pprint import pprint
from types import *
import signal, os



def handler(signum, frame):
    endCursesSession()
    sys.exit(-1);

# arm the INT handler
signal.signal(signal.SIGINT, handler)

class MenuDemo:
    DOWN = 1
    UP = -1
    SPACE_KEY = 32
    ESC_KEY = 27
    Q_KEY = 113

    PREFIX_SELECTED = '_X_'
    PREFIX_DESELECTED = '___'

    outputLines = []
    columns = None

    def __init__(self):
        self.screen = curses.initscr()
        self.columns = self.screen.getmaxyx()[1]
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)
        self.screen.border(0)
        self.topLineNum = 0
        self.highlightLineNum = 0
        self.markedLineNums = []
        if ( len(sys.argv) > 1 ): # there is something to search for
            self.puke(sys.argv[1])
        else:
            self.puke('')
        self.getOutputLines()
        self.run()

    def run(self):
        while True:
            self.displayScreen()
            # get user command
            c = self.screen.getch()
            if c == curses.KEY_UP:
                self.updown(self.UP)
            elif c == curses.KEY_DOWN:
                self.updown(self.DOWN)
            elif c == self.SPACE_KEY:
                self.markLine()
            elif c == self.ESC_KEY or c == self.Q_KEY:
                self.exit(-1)

    def markLine(self):
        linenum = self.topLineNum + self.highlightLineNum
        if linenum in self.markedLineNums:
            self.markedLineNums.remove(linenum)
        else:
            self.markedLineNums.append(linenum)

    def getOutputLines(self):
        self.nOutputLines = len(self.outputLines)

    def displayScreen(self):
        # clear screen
        self.screen.erase()

        # now paint the rows
        top = self.topLineNum
        bottom = self.topLineNum+curses.LINES
        for (index,line,) in enumerate(self.outputLines[top:bottom]):
            linenum = self.topLineNum + index
            if linenum in self.markedLineNums:
                prefix = self.PREFIX_SELECTED
            else:
                prefix = self.PREFIX_DESELECTED

            line = '%s %s' % (prefix, line)
            line = line[0:self.columns-1]

            # highlight current line
            if index != self.highlightLineNum:
                self.screen.addstr(index, 0, line)
            else:
                self.screen.addstr(index, 0, line, curses.A_BOLD)
        self.screen.refresh()

    # move highlight up/down one line
    def updown(self, increment):
        nextLineNum = self.highlightLineNum + increment

        # paging
        if increment == self.UP and self.highlightLineNum == 0 and self.topLineNum != 0:
            self.topLineNum += self.UP
            return
        elif increment == self.DOWN and nextLineNum == curses.LINES and (self.topLineNum+curses.LINES) != self.nOutputLines:
            self.topLineNum += self.DOWN
            return

        # scroll highlight line
        if increment == self.UP and (self.topLineNum != 0 or self.highlightLineNum != 0):
            self.highlightLineNum = nextLineNum
        elif increment == self.DOWN and (self.topLineNum+self.highlightLineNum+1) != self.nOutputLines and self.highlightLineNum != curses.LINES:
            self.highlightLineNum = nextLineNum

    def restoreScreen(self):
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    # catch any weird termination situations
    def __del__(self):
        self.restoreScreen()

    def displayItem(self, r,n,s,a):
        line1 =  '[%s] %s = %s' % ( r, n, s if len(s) > 0 else 'blank' )
        line2 =  '%s' % ( str(a) )
        line3 = ""
        self.outputLines.append(line1)
        self.outputLines.append(line2)
        self.outputLines.append(line3)

    def puke(self, search_term):
        for keyring in gnomekeyring.list_keyring_names_sync():
            for id in gnomekeyring.list_item_ids_sync(keyring):
                item = gnomekeyring.item_get_info_sync(keyring, id)
                attr = gnomekeyring.item_get_attributes_sync(keyring, id)
                display_name = item.get_display_name()
                secret = item.get_secret()

                if ( len(search_term) > 0 ):
                    i = attr.iterkeys()
                    try:
                        while ( True ):
                            k = i.next()
                            if ( type(attr[k]) == StringType and attr[k].lower().find(search_term.lower()) >= 0 ):
                                self.displayItem(keyring, display_name, secret, attr)
                                break
                    except StopIteration:
                        pass


if __name__ == '__main__':
    ih = MenuDemo()
