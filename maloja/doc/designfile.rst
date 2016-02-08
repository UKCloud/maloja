..  Titling
    ##++::==~~--''``

Design file
:::::::::::

After you run a Maloja survey, you'll find a representation of your virtual infrastructure
in your output directory (typically named `.maloja`).

These files keep all the attributes of your Organisations, Templates, Vms etc in YAML
format.

You can paste the contents of these files together to describe to Maloja what
infrastructure you want it to build. When you save these scraps of YAML together it's
called a `design file`.

In order to build a new VApp, a design file contains:

    * One Vdc
    * One or more Networks
    * A Template for the VApp
    * Optionally, one or more Vms to add into the VApp
    * Optionally, a configuration for a Gateway

You need to present these items as a YAML list, which means that each is indented once and
preceded by a '-' character.

Example
=======

.. literalinclude:: ../test/issue_025-03.yaml
   :language: yaml

Plan command
============

You can check your design file with Maloja's `plan` command::

    maloja @options.private plan --input=mydesign.yaml
    
The output will verify the objects in the file::

    2016-02-08 13:53:09,640 INFO    maloja|Using project proj_55i3s4ug.
    2016-02-08 13:53:09,687 INFO    maloja.planner|Modify <Org> 1-1-1-xxxxxx
    2016-02-08 13:53:09,687 INFO    maloja.planner|Modify <Vdc> Skyscape (PROD-STANDARD)
    2016-02-08 13:53:09,687 INFO    maloja.planner|Modify <Network> USER_NET
    2016-02-08 13:53:09,687 INFO    maloja.planner|Create <Network> Data network
    2016-02-08 13:53:09,702 INFO    maloja.planner|Modify <Template> Public Website
    2016-02-08 13:53:09,702 INFO    maloja.planner|Modify <Vm> Web
    2016-02-08 13:53:09,702 INFO    maloja.planner|Modify <Vm> App
    2016-02-08 13:53:09,702 INFO    maloja.planner|Modify <Vm> DB
    2016-02-08 13:53:09,718 INFO    maloja.planner|Modify <Gateway> ext0001
    2016-02-08 13:53:09,718 INFO    maloja.planner|Approved 9 objects of 9

Build command
=============

