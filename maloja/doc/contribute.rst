..  Titling
    ##++::==~~--''``

Notes for developers
::::::::::::::::::::

Git workflow
============

Challenges
~~~~~~~~~~

*   The Maloja software is stored in an online git repository
*   Project partners have different aspirations and intentions for the codebase
*   Some code implements the site-specific behaviour of a project partner

Best practice
~~~~~~~~~~~~~

There are several documented processes for working with git in a collaborative
environment. Each of them recommends strategies for branching, adding features,
and merging.

Of these, the Branch Per Feature (BPF) model represents a well-evolved good fit
for our purposes, based on the challenges stated above.

`BPF explained here`_.

Your responsibility as a developer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The code you write for your own project is your own affair. Your responsibility
to others begins when you contribute it to a shared repository.

Git is hard to use in this environment without making mistakes. The attitudes
we recommend are:

* humble in the face of complexity
* respectful of the intentions of others
* meticulous in testing your product 

The very first thing you should do now is `read this description of the
workflow`_ so that you can start to familiarise yourself with the process.
It may take a while to assimilate.

Summary of workflow
~~~~~~~~~~~~~~~~~~~

*   The master branch contains the last known good release.
*   Create a single Git ticket to represent your feature release.
*   Create a git feature branch in the repository.
    Name the branch after the ticket, eg: issue_0123_short_description_follows.
*   Developers regularly create an `integration` branch from master to check that
    upcoming features can be merged cleanly from their branches.
*   We capture integration issues in the Git ticket for each feature.
    Discussion between partners goes here.
*   Optionally: record any merge conflict resolution using `git rerere` and
    commit to ``maloja/git/rerere`` cache.
*   When a feature set is agreed for release, a `qa` branch is created from
    master and has features merged into it.
*   QA team tests the `qa` branch in Reference environment.
*   When `qa` branch is good it is merged into master and deployed to Production.

Uninstalling Maloja
===================

To eliminate the install process from your development cycle,
it's preferable to perform these tasks with maloja *uninstalled*:

    * `Running unit tests`_
    * `Building documentation`_
    * `Running PEP8`_

On Ubuntu Linux 14.04::

    $ ~/py3.4/bin/pip uninstall -y maloja

On Windows 8.1::

    > %HOME%\py3.5\Scripts\pip uninstall -y maloja

Running unit tests
==================

On Ubuntu Linux 14.04::

    $ ~/py3.4/bin/python -m unittest discover maloja

On Windows 8.1::

    > %HOME%\py3.5\Scripts\python -m unittest discover maloja

Building documentation
======================

Maloja's documentation is maintained in reStructuredText_. You can
compile it to HTML using the Sphinx tools.

On Ubuntu Linux 14.04::

    $ ~/py3.4/bin/sphinx-build maloja/doc maloja/doc/html

On Windows 8.1::

    > %HOME%\py3.5\Scripts\sphinx-build maloja\doc maloja\doc\html

Read the documentation in your browser::

    firefox maloja/doc/html/index.html

Running PEP8
============

On Ubuntu Linux 14.04::

    $ ~/py3.4/bin/pep8 .

On Windows 8.1::

    > %HOME%\py3.5\Scripts\pep8 .

.. _BPF explained here: https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow
.. _read this description of the workflow: https://www.acquia.com/blog/pragmatic-guide-branch-feature-git-branching-strategy
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
