Python Installation
~~~~~~~~~~~~~~~~~~~

Note that the `core` module is known to work for Python 2.7 and has not been tested for Python 3.

1. Clone the repository
"""""""""""""""""""""""
Clone or download our source code from `Github`_. ::

    $ git clone https://github.com/BerkeleyAutomation/core.git

.. _Github: https://github.com/BerkeleyAutomation/core

2. Run installation script
""""""""""""""""""""""""""
Change directories into the `core` repository and run ::

    $ python setup.py install

or ::

    $ pip install -r requirements.txt

Alternatively, you can run ::

    $ pip install /path/to/core

to install `core` from anywhere.
This will install `core` in your current Python environment.

3. Test the installation
""""""""""""""""""""""""
Change directories into the `core` repository and run ::

    $ python setup.py test

ROS Installation
~~~~~~~~~~~~~~~~

The `core` library can also be used with ROS, as our `RigidTransform`_ class can be used to wrap rigid transformations accessed through `tf`_.
This provides a convenient override of multiplication operator ::

    T_b_a = RigidTransform.rigid_transform_from_ros(from_frame='a', to_frame='b')
    T_c_b = RigidTransform.rigid_transform_from_ros(from_frame='b', to_frame='c')
    T_c_a = T_c_b * T_b_a

The `RigidTransform`_ class  also does automatic checking of frame name compatibility to help prevent bugs.

See the static methods `publish_to_ros`_, `delete_from_ros`_, and `rigid_transform_from_ros`_ of `RigidTransform`_ for more information.

.. _RigidTransform: ../api/rigid_transform.html
.. _tf: http://wiki.ros.org/tf
.. _publish_to_ros: ../api/rigid_transform.html#core.RigidTransform.publish_to_ros
.. _delete_from_ros: ../api/rigid_transform.html#core.RigidTransform.delete_from_ros
.. _rigid_transform_from_ros: ../api/rigid_transform.html#core.RigidTransform.rigid_transform_from_ros

1. Clone the repository
"""""""""""""""""""""""
Clone or download our source code from `Github`_. ::

    $ cd {PATH_TO_YOUR_CATKIN_WORKSPACE}/src
    $ git clone https://github.com/BerkeleyAutomation/core.git

.. _Github: https://github.com/BerkeleyAutomation/core

2. Build the catkin package
"""""""""""""""""""""""""""
Build the catkin pacakge by running ::

    $ cd {PATH_TO_YOUR_CATKIN_WORKSPACE}
    $ catkin_make

Then re-source devel/setup.bash for the module to be available through Python.

Dependencies
~~~~~~~~~~~~
The `core` module's only dependencies are on `numpy`_, `scipy`_,
`matplotlib`_, and `pyyaml` and should be installed automatically.
You can install these manually if you wish with
pip. ::

    $ pip install numpy
    $ pip install scipy
    $ pip install matplotlib
    $ pip install pyyaml

However, installing our repo using `pip` will install these automatically.

.. _numpy: http://www.numpy.org/
.. _scipy: https://www.scipy/org/
.. _matplotlib: http://www.matplotlib.org/

Documentation
~~~~~~~~~~~~~

Building
""""""""
Building `core`'s documentation requires a few extra dependencies --
specifically, `sphinx`_ and a few plugins.

.. _sphinx: http://www.sphinx-doc.org/en/1.4.8/

To install the dependencies required, simply run ::

    $ pip install -r docs_requirements.txt

Then, go to the `docs` directory and run ``make`` with the appropriate target.
For example, ::

    $ cd docs/
    $ make html

will generate a set of web pages. Any documentation files
generated in this manner can be found in `docs/build`.

Deploying
"""""""""
To deploy documentation to the Github Pages site for the repository,
simply push any changes to the documentation source to master
and then run ::

    $ . gh_deploy.sh

from the `docs` folder. This script will automatically checkout the
``gh-pages`` branch, build the documentation from source, and push it
to Github.

