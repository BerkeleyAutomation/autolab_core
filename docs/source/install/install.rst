Python Installation
~~~~~~~~~~~~~~~~~~~

Option 1: Pip
"""""""""""""
This package is now installable via `pip` ::

    $ pip install autolab_core

Use this option if you aren't interested in using our ROS nodes.

Option 2: Install from Source for ROS
"""""""""""""""""""""""""""""""""""""
The `autolab_core` library can also be used with ROS, as our `RigidTransform`_ class can be used to wrap rigid transformations accessed through `tf`_.
This provides a convenient override of multiplication operator ::

    T_b_a = RigidTransform.rigid_transform_from_ros(from_frame='a', to_frame='b')
    T_c_b = RigidTransform.rigid_transform_from_ros(from_frame='b', to_frame='c')
    T_c_a = T_c_b * T_b_a

The `RigidTransform`_ class  also does automatic checking of frame name compatibility to help prevent bugs.

See the static methods `publish_to_ros`_, `delete_from_ros`_, and `rigid_transform_from_ros`_ of `RigidTransform`_ for more information.

.. _RigidTransform: ../api/rigid_transform.html
.. _tf: http://wiki.ros.org/tf
.. _publish_to_ros: ../api/rigid_transform.html#autolab_core.RigidTransform.publish_to_ros
.. _delete_from_ros: ../api/rigid_transform.html#autolab_core.RigidTransform.delete_from_ros
.. _rigid_transform_from_ros: ../api/rigid_transform.html#autolab_core.RigidTransform.rigid_transform_from_ros

Start by cloning or downloading our source code from `Github`_. ::

    $ cd {PATH_TO_YOUR_CATKIN_WORKSPACE}/src
    $ git clone https://github.com/BerkeleyAutomation/autolab_core.git

.. _Github: https://github.com/BerkeleyAutomation/autolab_core


Change directories into the `autolab_core` repository and run ::

    $ python setup.py install

Finally, run `catkin_make` ::

    $ cd {PATH_TO_YOUR_CATKIN_WORKSPACE}
    $ catkin_make

Then re-source devel/setup.bash for the module to be available through Python.

Documentation
~~~~~~~~~~~~~

Building
""""""""
Building `autolab_core`'s documentation requires a few extra dependencies --
specifically, `sphinx`_ and a few plugins.

.. _sphinx: http://www.sphinx-doc.org/en/1.4.8/

To install the dependencies required, simply change directories into the `autolab_core` source and run ::

    $ pip install .[docs]

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

