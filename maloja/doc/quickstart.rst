..  Titling
    ##++::==~~--''``
    
Quickstart Guide
================

Create an options file
~~~~~~~~~~~~~~~~~~~~~~

Make a text file '`options.private`' containing connection strings to your cloud
Organisation endpoint on two lines like this::

    --url=https://api.vcd.portal.XXXXXXXXX.YYY
    --user=WWWW.XXX.YYYYYY@ZZZZZZZZZZZZZZ

Invoke the Maloja console
~~~~~~~~~~~~~~~~~~~~~~~~~

Launch an interactive session in a fresh window, passing your options file
using the '`@`' syntax, eg:

On Ubuntu 14.04::

    $ ~/py3.4/bin/python -m maloja.main @options.private

On Windows 8.1::

    > start %HOME%\py3.5\Scripts\python -m maloja.main @options.private

The window will open and prompt you for your API password::

    Enter your API password:

Enter the password and press return. After a few moments you should see this
message::

    [1] 1:1 Token received.

If no token is returned, you'll be prompted for the password again.

Use the help command
~~~~~~~~~~~~~~~~~~~~

* Type '`help`' to see what commands are available.
* Type '`help <command>`' to see command-specific information.

Survey and search
~~~~~~~~~~~~~~~~~

Issue a '`survey`' command to get information on the structure of your
cloud. This is achieved recursively and asynchronously to the console. Each
task reports when it has finished. When no more tasks are active, the survey is
complete.

Use the '`search`' command to view assets at every level, filter by attribute and
pick from a list of results, eg:

* View a list of all Windows templates::

    search template name=Windows

* Pick from the list of all Windows templates::

    search template name=Windows 5

Clear the buffer
~~~~~~~~~~~~~~~~

The console stores in memory each object you have identified by search. Refresh
this buffer with the '`clear`' command.
