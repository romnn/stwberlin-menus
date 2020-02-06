===============================
stwberlin menus
===============================

.. image:: https://travis-ci.com/romnnn/stwberlin_menus.svg?branch=master
        :target: https://travis-ci.com/romnnn/stwberlin_menus
        :alt: Build Status

.. image:: https://img.shields.io/pypi/v/stwberlin_menus.svg
        :target: https://pypi.python.org/pypi/stwberlin_menus
        :alt: PyPI version

.. image:: https://img.shields.io/github/license/romnnn/stwberlin_menus
        :target: https://github.com/romnnn/stwberlin_menus
        :alt: License

.. image:: https://readthedocs.org/projects/stwberlin-menus/badge/?version=latest
        :target: https://stwberlin-menus.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://codecov.io/gh/romnnn/stwberlin_menus/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/romnnn/stwberlin_menus
        :alt: Test Coverage

""""""""

Your short description here. `romnnn.github.io/stwberlin_menus <https://romnnn.github.io/stwberlin_menus>`_

.. code-block:: console

    $ pip install stwberlin_menus

See the `official documentation`_ for more information.

.. _official documentation: https://stwberlin-menus.readthedocs.io

.. code-block:: python

    import stwberlin_menus

Development
-----------

For detailed instructions see `CONTRIBUTING <CONTRIBUTING.rst>`_.

Tests
~~~~~~~
You can run tests with

.. code-block:: console

    $ invoke test
    $ invoke test --min-coverage=90     # Fail when code coverage is below 90%
    $ invoke type-check                 # Run mypy type checks

Linting and formatting
~~~~~~~~~~~~~~~~~~~~~~~~
Lint and format the code with

.. code-block:: console

    $ invoke format
    $ invoke lint

All of this happens when you run ``invoke pre-commit``.

Note
-----

This project is still in the alpha stage and should not be considered production ready.
