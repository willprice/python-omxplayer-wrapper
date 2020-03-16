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

1. Set up a virtual environment 

   .. code:: console

       $ python3 -m venv .venv
       $ .venv/bin/activate

2. Install package in editable mode with dependencies

   .. code:: console

       $ pip install ".[test,docs]" -e . 

3. Run unit tests

   .. code:: console

       $ make test              # run under current python version

       $ pip install tox pyenv tox-pyenv  # Install pyenv tox to run under all python versions
       $ git clone https://github.com/momo-lab/xxenv-latest.git "$(pyenv root)"/plugins/xxenv-latest
       $ for v in 2.7 3.4 3.5 3.6 3.7; do pyenv la test install "$v"; done
       $ pyenv versions --base > .python-version
       $ make test-all          # run under tox for all supported python versions

4. Run integration tests (on Raspberry Pi)

   .. code:: console

       $ make test-integration


5. Build docs

   .. code:: console

       $ make doc
       $ make doc-serve   # run HTTP server to view docs

6. Run examples

   .. code:: console

       $ cd examples
       $ PYTHONPATH=.. python3 video_file.py
       $ PYTHONPATH=.. python3 advanced_usage.py


On a Raspberry Pi
~~~~~~~~~~~~~~~~~

There's also an Ansible playbook in ``devenv`` which will set up a
raspberry pi with ``omxplayer-wrapper`` in develop mode (located at
``/usr/src/omxplayer-wrapper``) which can be used by running
``./devenv/deploy.sh``

This will install via symlinks so that you can continue to work on it
locally but import it from other python packages
