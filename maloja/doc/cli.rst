..  Titling
    ##++::==~~--''``

.. _commands:

Commands
::::::::

Command Line Interface
======================

.. automodule:: maloja.cli

.. argparse::
   :ref: maloja.cli.cli
   :prog: maloja
   :nodefault:

Console
=======

The console launches when you invoke Maloja without a subcommand.
It provides an interactive environment and a help facility::

    Type 'help' for commands > help

    Documented commands (type help <topic>):
    ========================================
    clear  help  plugin  quit  search  survey

    Type 'help' for commands > help plugin

            'Plugin' lists plugins and their availability. Supply
            a number from that menu to invoke the plugin.

                > plugin
                (a list will be shown)

                > plugin 2

Use the console for long-running tasks which require your attention
or intervention.

The commands available from the console are:

    * help
    * survey
    * search
    * clear
    * plugin
    * quit

