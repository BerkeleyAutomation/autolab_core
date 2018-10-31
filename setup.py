"""
Setup of core python codebase
Author: Jeff Mahler
"""
from setuptools import setup

requirements = [
    'numpy',
    'scipy',
    'scikit-learn',
    'ruamel.yaml',
    'matplotlib',
    'multiprocess',
    'setproctitle',
    'joblib',
    'colorlog'
]

exec(open('autolab_core/version.py').read())


setup(
    name='autolab_core',
    version = __version__,
    description = 'Core utilities for the Berkeley AutoLab',
    long_description = 'Core utilities for the Berkeley AutoLab. Includes rigid transformations, loggers, and 3D data wrappers.',
    author = 'Jeff Mahler',
    author_email = 'jmahler@berkeley.edu',
    license = 'Apache Software License',
    url = 'https://github.com/BerkeleyAutomation/autolab_core',
    keywords = 'robotics grasping transformations',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering'
    ],
    packages = ['autolab_core'],
    install_requires = requirements,
    extras_require = { 'docs' : [
                            'sphinx',
                            'sphinxcontrib-napoleon',
                            'sphinx_rtd_theme'
                        ],
                       'ros' : [
                           'rospkg',
                           'catkin_pkg',
                           'empy'
                        ],
    }
)
