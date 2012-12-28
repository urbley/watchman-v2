#!/usr/bin/python
from __future__ import print_function
import sys
import os
import re
import commands
import datetime
import time
import subprocess
import shlex
import smtplib


class ProcessSearch:
    'Search class to store search details and handle searching for and restarting of processes'
    def __init__( self, search, pattern, start, server, domain, reportEmail ):
        self.search = search
        self.pattern = pattern
        self.start = start
        self.server = server
        self.domain = domain
        self.reportEmail = reportEmail

    def runSearch( self ):
        log = open( "/var/log/watchman_log", "a" )
        print( "%s - Running %s.\n%s - Searching for \"%s\"." % ( time.ctime(), self.search, time.ctime(), self.pattern ), file=log )

        commOutput = commands.getstatusoutput( "pgrep -fl \"" + self.pattern + "\"" )

        # Bummer... The pgrep is in the list of search results causing false positives.  Need to RE them out.
        # I've tried ps and considered querying /proc using glob but they all require as much work as the grep.
        # Most Python resources recommend avoiding RE where possible (hog) but given the size of the project
        # and since I like using RE I'm going to proceed with that.

        commOutputList = commOutput[1].split( '\n' )

        for item in commOutputList:
            if re.search( "^.+pgrep.+", item ):
                commOutputList.remove( item )

        if commOutputList:
            print( time.ctime() + " - %s is currently running.  Nothing to do!\n" % self.pattern, file=log )
        else:
            print( time.ctime() + " - Oh dear! Restarting %s...\n" % self.pattern, file=log )
            self.restartProcess()

        log.close()


    def restartProcess( self ):
        log = open( "/var/log/watchman_log", "a" )
        x = 1
        args = shlex.split( self.start )

        while x < 4:
            print( time.ctime() + " - Trying to start %s: %s" % ( self.search, self.pattern ), file=log )
            output = subprocess.Popen( args, stdout=subprocess.PIPE ).communicate()[0]
            print( time.ctime() + " - Attempt %d output: %s" % ( x, output ), file=log )

            # After having trawled through the Sphinx documentation I can confirm that if Sphinx fails to start for ANY reason
            # it will have "FATAL" in stdout.
            if re.search( "^.+FATAL.", output, re.MULTILINE ):
                if x < 3:
                    print( time.ctime() + " - Attempt %d failed.  Trying again" % x, file=log )
                else:
                    print( time.ctime() + " - Attempt %d failed.  Emailing admin" % x, file=log )
            else:
                print( time.ctime() + " - Success! %s restarted successfully\n" % self.search, file=log )
                break

            x += 1

            # If we've tried 3 times without a successful restart send an email to alert whoever needs to know about this
            if x == 4:
                fromEmail = "watchman@" + self.server + "." + self.domain
                errorMessage = "From: Watchman <" + fromEmail + ">\n" +\
                               "To: Server Admin <" + self.reportEmail + ">\n" +\
                               "MIME-Version: 1.0\n" +\
                               "Content-type: text/html\n" +\
                               "Subject: Watchman Alert on: " + self.server + " with: " + self.search + "\n" +\
                               "\n"+\
                               "Oh dear.  I found an error when checking for your configured processes.<br />" +\
                               "<br />"+\
                               "<strong>" + self.search + "</strong> on server: <strong>" + self.server + "</strong> was not running when I checked and I could not restart it.  The search term was <strong>" + self.pattern + "</strong><br />" +\
                               "<br />"+\
                               "You should probably look into this right away.<br /><br />The output from the last attempt was:<br />------------------------<br /> " + output

                try:
                    errorEmail = smtplib.SMTP( 'localhost' )
                    errorEmail.sendmail( fromEmail, self.reportEmail, errorMessage )
                except Exception, e :
                    print( time.ctime() + " - Could not send email with error: %s" % e, file=log )

        log.close()