..  Titling
    ##++::==~~--''``

Installation
::::::::::::

Maloja is currently available only as a preview. During this phase, we
recommend running it from the working directory of your git repository.

It is necessary however to install dependencies. These instructions show you
how.

The version of Python you use depends on your Operating System. You should
run Maloja in the most recent Python available for your OS. Two examples
are shown below:

* Operation under `Ubuntu Linux 14.04 LTS`_ with Python version 3.4
  from the package repository.
* Operation under `Microsoft Windows 8.1`_ with Python version 3.5.1
  downloaded from the Python website.

Ubuntu Linux 14.04 LTS
======================

#. Install `python3-dev` from the package repository of your OS::

    $ sudo apt-get install -y python3-dev

#. Install `python-virtualenv` from the package repository of your OS::

    $ sudo apt-get install python-virtualenv

#. Create a new Python virtual environment::

    $ virtualenv --python=python3.4 ~/py3.4

#. Upgrade your version of `pip`::

    $ ~/py3.4/bin/pip install --upgrade pip

#. Install Maloja dependencies::

    $ ~/py3.4/bin/pip install chameleon
    Running setup.py install for chameleon
    Successfully installed chameleon-2.24

    $ ~/py3.4/bin/pip install requests-futures
    Installing collected packages: requests, requests-futures
    Running setup.py install for requests-futures
    Successfully installed requests-2.8.1 requests-futures-0.9.5

    $ ~/py3.4/bin/pip install ruamel.yaml
    Installing collected packages: ruamel.base, ruamel.yaml
    Running setup.py install for ruamel.yaml
    Successfully installed ruamel.base-1.0.0 ruamel.yaml-0.10.12

Microsoft Windows 8.1
=====================

#.  Ensure the environment variable '`%HOME%`' points to your user directory.
#.  Download and install `Python 3.5.1 for Windows`_.
#.  Create a new Python virtual environment::

    > C:\Program Files (x86)\Python 3.5\python.exe -m venv %HOME%\py3.5

#.  Upgrade your version of `pip`::

    > %HOME%\py3.5\Scripts\pip install --upgrade pip

#. Use `pip` to install the following packages:

    * chameleon
    * requests-futures
    * ruamel.yaml

Install Maloja into the Python environment
==========================================

On Linux::

    $ ~/py3.4/bin/pip install .[dev,docbuild]

On Windows::

    > %HOME%\py3.5\Scripts\pip install .[dev,docbuild]

Building documentation
======================

Maloja's documentation is best when compiled to HTML on your local machine.

Install sphinx::

    $ pip install sphinx

Build the docs from source::

    $ sphinx-build maloja/doc maloja/doc/html

Read the documentation::

    $ firefox maloja/doc/html/index.html

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
