..  Titling
    ##++::==~~--''``

API Guide
:::::::::

Common types
============

.. autoclass:: maloja.types.Plugin

Common utilities
================

Broker module
=============

Surveyor module
===============

.. automodule:: maloja.surveyor

Planner module
==============

Builder module
==============

.. automodule:: maloja.builder

Plugins
=======

.. autofunction:: maloja.plugin.vapplicator.selector

.. autoclass:: maloja.plugin.vapplicator.Workflow
   :members: __init__, __call__
   :special-members:

Maloja uses python `entry points`_ to define an interface for third party plugins.

.. _entry points: http://pythonhosted.org/distribute/setuptools.html#dynamic-discovery-of-services-and-plugins
.. _function objects: http://docs.python.org/3/reference/datamodel.html?highlight=__call__#emulating-callable-objects
