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

Example
=======

.. literalinclude:: ../test/issue_025-03.yaml
   :language: yaml

Plan command
============

Build command
=============

