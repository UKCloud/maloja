..  Titling
    ##++::==~~--''``

Implementation details
::::::::::::::::::::::

Common types
============

Maloja defines lightweight types for many things, including
user credentials:

    .. autoclass:: maloja.types.Credentials

Status messages:

    .. autoclass:: maloja.types.Status

There's also a class to represent user plugins.

.. autoclass:: maloja.types.Plugin

Common utilities
================

A small number of functions are used frequently for parsing, sorting
and storing data.

.. autofunction:: maloja.workflow.utils.find_xpath

.. autofunction:: maloja.workflow.utils.group_by_type

Broker module
=============

.. autoclass:: maloja.broker.Broker

.. autofunction:: maloja.broker.create_broker

.. autofunction:: maloja.broker.handler

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
