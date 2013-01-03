watchman-v2
===========

Now that v1 is working I decided to leave it as is (as I need a working version!) and start a new project to
continue on the path of python.

I want to drop the need for creating a cron job to run the script regularly by daemonizing the process.  Big 
thanks to Chad J. Schroeder for his daemonize tutorial 
(http://code.activestate.com/recipes/278731-creating-a-daemon-the-python-way/)

I've also broken the search details out into a new class that will contain reuseable functions such as 
the search and restart functions.  
