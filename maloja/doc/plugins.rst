..  Titling
    ##++::==~~--''``

Plugins
:::::::

You can write and maintain your own scripts and still invoke them from
Maloja. The advantage of that is to make use of `survey` data
which you can search for in the Maloja console and pass to your scripts
interactively.

Your script must contain three things:

    * a `selector function`_
    * a `Workflow class`_
    * a `plugin declaration`_

For reference, see the example in `maloja.plugin.vapplicator`.

Selector function
=================

.. autofunction:: maloja.plugin.vapplicator.selector

Workflow class
==============

Your Workflow should be implemented as a `callable object`_.

.. autoclass:: maloja.plugin.vapplicator.Workflow
   :members: __init__, __call__
   :member-order: bysource

Plugin declaration
==================

Maloja uses Python `entry points`_ to define an interface for third
party plugins. The interface is called `maloja.plugin`.

In order for Maloja to detect your plugin, you must package your
scripts as an installable Python distibution, and make an entry point
declaration in your `setup.py`.

Here's what that would look like for a script called `myscript` in a
package `mypackage`::

    entry_points={
        "maloja.plugin": [
            "myplugin = mypackage.myscript:plugin",
        ],
    },

The target for the entry point is a module-level variable of type
:py:class:`maloja.types.Plugin`.

.. _entry points: https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins
.. _callable object: http://docs.python.org/3/reference/datamodel.html?highlight=__call__#emulating-callable-objects
