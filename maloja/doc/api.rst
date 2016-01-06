..  Titling
    ##++::==~~--''``

Implementation details
::::::::::::::::::::::

Common types
============

Maloja defines lightweight types for many things, including
API tokens:

    .. autoclass:: maloja.types.Token

Status messages:

    .. autoclass:: maloja.types.Status

As well as other message types which we'll see later on.
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
   :members:

.. autofunction:: maloja.broker.create_broker

Messages
~~~~~~~~

A broker object will respond to the following messages:

    * :py:class:`maloja.types.Survey`
    * :py:class:`maloja.types.Design`
    * :py:class:`maloja.types.Stop`

.. autofunction:: maloja.broker.handler

Surveyor module
===============

The Surveyor is launched by the Broker whenever a
:py:class:`maloja.types.Survey` message is received.

.. autoclass:: maloja.surveyor.Surveyor
   :members:

Planner module
==============

.. automodule:: maloja.planner

You can test the module using one of the example files which come with
your Maloja installation.

On Ubuntu 14.04::

    $ ~/py3.4/bin/maloja @options.private plan --input=maloja/test/use_case01.yaml

On Windows 8.1::

    > %HOME%\py3.5\Scripts\maloja @options.private plan --input=maloja/test/use_case01.yaml

Builder module
==============

.. autoclass:: maloja.broker.Broker
   :members:

Plugins
=======

.. autofunction:: maloja.plugin.vapplicator.selector

.. autoclass:: maloja.plugin.vapplicator.Workflow
   :members: __init__, __call__
   :special-members:

Maloja uses python `entry points`_ to define an interface for third party plugins.

.. _entry points: http://pythonhosted.org/distribute/setuptools.html#dynamic-discovery-of-services-and-plugins
.. _function objects: http://docs.python.org/3/reference/datamodel.html?highlight=__call__#emulating-callable-objects
