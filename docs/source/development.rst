.. _development:

=============
Development
=============


.. _get the code:

Get the code
================

Please see the Source code checkouts section of the :ref:`Installation <installation>` page for details on how to obtain Elevator's source code.


.. _contributing:

Contributing
============

There are a number of ways to get involved with Elevator:

* Send us **feedback!** This is both the easiest and arguably the most important way to improve the project.

* **Report bugs**. Pretty much a special case of the previous item: if you think you’ve found a bug in Elevator, check on the `ticket tracker <http://github.com/oleiade/Elevator/issues>`_ to see if anyone’s reported it yet, and if not - fill a bug report. If possible, try to make sure you can replicate it repeatedly, and let us know the circumstances (what version of Elevator you’re using, what platform you’re on, and what exactly you were doing when the bug cropped up.)

* Submit **patches or new features**. Make a Github account, create a fork of the main Elevator repository, and submit a pull request. Every contributions will be inspected with attention, if it respects some simple conventions:

    * A new feature **HAS** to ship with tests and documentation.
    * A bug fix has to be explained and detailled
    * An optimisation, refactoring, has to be totally atomical and transparent with Elevator's 'public' behavior.


.. _coding style:

Coding Style
===============

Elevator tries hard to keep up to ``go fmt`` norm. So anytime, use ``go fmt`` to help you code keep clean and following the go creators coding style.


.. _releases:

Releases
============

Fabric tries to follow open-source standards and conventions in its release tagging, including typical version numbers such as 2.0, 1.2.5, or 1.2b1. Each release will be marked as a tag in the Git repositories, and are broken down as follows:

Major
~~~~~~~~~~

Major releases update the first number, e.g. going from 0.9 to 1.0, and indicate that the software has reached some very large milestone.

For example, the 1.0 release signified a commitment to a medium to long term protocol and some significant backwards incompatible (compared to the 0.9 series) features. Version 2.0 might indicate a rewrite using a new underlying network technology.

Major releases will often be backwards-incompatible with the previous line of development, though this is not a requirement, just a usual happenstance. Clients maintainers should expect to have to make at least some changes to their clients when switching between major versions.

Minor
~~~~~~~~~~~

Minor releases, such as moving from 0.1 to 0.2, typically mean that one or more new, large features has been added. They are also sometimes used to mark off the fact that a lot of bug fixes or small feature modifications have occurred since the previous minor release. (And, naturally, some of them will involve both at the same time.)

These releases are guaranteed to be backwards-compatible with all other releases containing the same major version number, so a fabfile that works with 1.0 should also work fine with 1.1 or even 1.9.

Bugfixes
~~~~~~~~~~~~~

The third and final part of version numbers, such as the ‘d’ in 0.3d, generally indicate a release containing one or more bugfixes, although minor feature modifications may (rarely) occur.

