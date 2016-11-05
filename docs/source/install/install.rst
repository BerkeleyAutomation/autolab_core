Installation Instructions
=========================

Dependencies
~~~~~~~~~~~~
The `core` module's only dependencies are on `numpy`_, `scipy`_,
`matplotlib`_, and `pyyaml`. You can install these manually if you wish with
pip. ::

    $ pip install numpy
    $ pip install scipy
    $ pip install matplotlib
    $ pip install pyyaml

However, installing our repo using `pip` will install these automatically.

.. _numpy: http://www.numpy.org/
.. _scipy: https://www.scipy/org/
.. _matplotlib: http://www.matplotlib.org/

Cloning the Repository
~~~~~~~~~~~~~~~~~~~~~~
You can clone or download our source code from `Github`_. ::

    $ git clone git@github.com:mmatl/core.git

.. _Github: https://github.com/mmatl/core

Installation
~~~~~~~~~~~~
To install `core` in your current Python environment, simply
change directories into the `core` repository and run ::

    $ pip install -e .

or ::

    $ pip install -r requirements.txt

Alternatively, you can run ::

    $ pip install /path/to/core

to install `core` from anywhere.

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~
Building `core`'s documentation requires a few extra dependencies --
specifically, `sphinx`_ and a few plugins.

.. _sphinx: http://www.sphinx-doc.org/en/1.4.8/

To install the dependencies required, simply run ::

    $ pip install -r docs_requirements.txt

Then, go to the `docs` directory and run `make` with the appropriate target.
For example, ::

    $ cd docs/
    $ make html

will generate a set of web pages. Any documentation files
generated in this manner can be found in `docs/build`.

