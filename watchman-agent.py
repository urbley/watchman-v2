#!/usr/bin/python
from __future__ import print_function
import sys
import os
import re
import commands
import time
import subprocess
import shlex
import smtplib
import processSearch
import daemonize


# Global variables
searches = {} # dictionary to store all searches found in the conf
pwd = os.path.dirname( os.path.realpath( __file__ ) ) # I'm running from here

# The below vars are read in from watchman.conf
server = ""
reportEmail = ""
domain = ""

# Check for a config file and load the contents
def loadConfig():
    log = open( "/var/log/watchman_log", "a" )
    try:
        f = open( pwd + "/watchman.conf", "r" )
    except IOError, e:
        print( time.ctime() + " - I could not find watchman.conf in the working directory (" + pwd + "). Error: %s" % e, file=log )

        try:
            f = open( pwd + "/watchman.conf", "w" )
            print( "[General]\n#These 3 vars MUST be set correctly for the script to work\n\n#server can get retrieved from hostname linux command\nserver=server1\n\n#this is the email where errors will be sent\nreportEmail=you@yourdomain.com\n\n#any domain that has send permissions in sendmail\ndomain=yourdomain.com\n\n[Searches]\n#You can add multiple search patterns in the key=value formation e.g.\n#Search1=searchd\n#Search2=searche", file=f )

            print( time.ctime() + " - It's ok.  I created a blank for you but you'll need to configure it or there's nothing for me to do!", file=log )

            f = open( pwd + "/watchman.conf", "r" )
        except IOError, e:
            print( time.ctime() + " - I tried to create a blank template for you but unfortunately I couldn't.  You're on your own muchacho." )
            print( time.ctime() + " - Error was: %s " % e, file=log )

    for line in f:
        # Skipping the rubbish
        if re.search( "^\[", line ):
            continue # Lets ignore section headers. the conf isn't complicated enough yet...

        if re.search( "^#", line ):
            continue # Lets ignore comments of course

        if line == '\n':
            continue # We don't care about blank lines do we?

        # Reading in the useful info from General section
        if re.search( "^server=.+", line ):
            global server
            server = re.search( "^server=(.+)", line ).group(1)

        if re.search( "^domain=.+", line ):
            global domain
            domain = re.search( "^domain=(.+)", line ).group(1)

        if re.search( "^reportEmail=.+", line ):
            global reportEmail
            reportEmail = re.search( "^reportEmail=(.+)", line ).group(1)

        # Read in all defined searches
        matches = re.search( "^(Search\d+)=(.+)::(.+)", line )

        if matches:
            # We want the search name and the search string.
            searches[matches.group(1)] = processSearch.ProcessSearch( matches.group(1), matches.group(2), matches.group(3), server, domain, reportEmail )

    log.close()


# Run the searches
def runSearches():
    if searches:
        # Log readability separator
        log = open( "/var/log/watchman_log", "a" )
        print( "\n------------------------ Search starting - %s ------------------------" % time.ctime(), file=log )
        log.close()

        for searchKey, searchObj in searches.iteritems():
            searches[searchKey].runSearch()
    else:
        log = open( "/var/log/watchman_log", "a" )
        print( time.ctime() + " - There were no searches in the config (" + pwd + "/watchman.conf).", file=log )
        log.close()
        sys.exit()


# Run the script
loadConfig()

runSearches()