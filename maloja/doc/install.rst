..  Titling
    ##++::==~~--''``

Installation
::::::::::::

Maloja can be installed from either;

    * a self-contained package or, 
    * from a working directory of our git repository.

At this early stage of the project we recommend the second option. These instructions show you how.

The version of Python you use depends on your Operating System. You should
run Maloja in the most recent Python available for your OS. Two examples
are shown below:

* Virtual environment on `Ubuntu Linux 14.04 LTS`_ with Python version
  3.4 from the package repository.
* Virtual environment on `Microsoft Windows 8.1`_ with Python version
  3.5.1 downloaded from the Python website.

Create a Python virtual environment
===================================

Ubuntu Linux 14.04 LTS
~~~~~~~~~~~~~~~~~~~~~~

#. Install any necessary development libraries from the package repository of your OS::

    $ sudo apt-get install -y zlib1g-dev libjpeg8-dev python3-dev

#. Install `python-virtualenv` from the package repository of your OS::

    $ sudo apt-get install python-virtualenv

#. Create a new Python virtual environment::

    $ virtualenv --python=python3.4 ~/py3.4

#. Upgrade your version of `pip`::

    $ ~/py3.4/bin/pip install --upgrade pip

Microsoft Windows 8.1
~~~~~~~~~~~~~~~~~~~~~

#.  Ensure the environment variable '`%HOME%`' points to your user directory.
#.  Download and install `Python 3.5.1 for Windows`_.
#.  Create a new Python virtual environment::

    > C:\Program Files (x86)\Python 3.5\python.exe -m venv %HOME%\py3.5

#.  Upgrade your version of `pip`::

    > %HOME%\py3.5\Scripts\pip install --upgrade pip

.. _install Maloja:

Check out the Maloja repository
===============================

::

    git clone git@github.com:skyscape-cloud-services/maloja.git
    cd maloja

Install Maloja into the Python environment
==========================================

On Ubuntu Linux 14.04::

    $ ~/py3.4/bin/pip install .[dev,docbuild]

On Windows 8.1::

    > %HOME%\py3.5\Scripts\pip install .[dev,docbuild]

.. #.  Install `Maloja`::
..
..        > %HOME%\py3.5\Scripts\pip install maloja-0.0.0.zip
..
..    This step should automatically install the following dependencies from PyPI_:
..
..    * requests-futures
..    * ruamel.yaml

.. _PyPI: https://pypi.python.org/pypi
.. _Python 3.5 for Windows: https://www.python.org/ftp/python/3.5.0/python-3.5.0.exe
.. _Python 3.5.1 for Windows: https://www.python.org/ftp/python/3.5.1/python-3.5.1.exe
