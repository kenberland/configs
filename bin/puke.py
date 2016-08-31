#!/usr/bin/env python

import sys
import pygtk
pygtk.require('2.0')
# import gtk # sets app name
import gnomekeyring
import curses
from pprint import pprint
from types import *
import signal, os

stdscr = curses.initscr() # Global for the curses session

def endCursesSession():
    curses.cbreak()
    stdscr.keypad(1)
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()



def handler(signum, frame):
    endCursesSession()
    sys.exit(-1);

# arm the INT handler
signal.signal(signal.SIGINT, handler)

def displayItem(r,n,s,a):
    line1 =  '[%s] %s = %s' % ( r, n, s if len(s) > 0 else 'blank' )
    line2 =  '%s' % ( a if len(a) > 0 else 'blank')
    stdscr.addstr( line1 )
    stdscr.addstr( "\n" )
    stdscr.addstr( line2 )
    stdscr.addstr( "\n" )
    stdscr.addstr( "\n" )

def puke(term):

    for keyring in gnomekeyring.list_keyring_names_sync():
        for id in gnomekeyring.list_item_ids_sync(keyring):
            item = gnomekeyring.item_get_info_sync(keyring, id)
            attr = gnomekeyring.item_get_attributes_sync(keyring, id)
            display_name = item.get_display_name()
            secret = item.get_secret()
         
            attrmatch = False
            if ( len(term) > 0 ):
                i = attr.iterkeys()
                try:
                    while ( True ):
                        k = i.next()
                        if ( type(attr[k]) == StringType and attr[k].lower().find(term.lower()) >= 0 ):
                            attrmatch = True
                            break
                except StopIteration:
                    pass


            if ( len(term) == 0 or attrmatch or display_name.lower().find(term.lower()) >= 0 or secret.find(term) > 0 ):
                displayItem(keyring, display_name, secret, attr)

        else:
            if len(gnomekeyring.list_item_ids_sync(keyring)) == 0:
                print '[%s] --empty--' % keyring
 
if __name__ == '__main__':
    stdscr.erase();
    if ( len(sys.argv) > 1 ): # there is something to search for
        puke(sys.argv[1])
    else:
        puke('')
    stdscr.refresh()
    c = stdscr.getch()   # read a keypress
    endCursesSession();

