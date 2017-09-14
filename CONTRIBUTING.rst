Contributing
============

Rules
-----

-  **Thou shalt not break the build**.
-  **Thou shalt not break the tests**.
-  **Thou shalt write tests for new functionality**.
-  **Thou shalt rebase onto ``develop`` instead of merging**.
-  Don't reduce test coverage, ideally improve it.
-  Add doc comments if your code is to be used by client code.

Thou shalt receive cookies for your welcomed contribution.

Development
-----------

Locally
~~~~~~~

Ensure you have all the development dependencies:

.. code:: bash

    $ pipenv install --dev

Install the library in *development* mode so you can test it out whilst
developing features.

.. code:: bash

    $ python setup.py develop

On a raspberry pi
~~~~~~~~~~~~~~~~~

There's also an Ansible playbook in ``devenv`` which will set up a
raspberry pi with ``omxplayer-wrapper`` in develop mode (located at
``/usr/src/omxplayer-wrapper``) which can be used by running
``./devenv/deploy.sh``

This will install via symlinks so that you can continue to work on it
locally but import it from other python packages
