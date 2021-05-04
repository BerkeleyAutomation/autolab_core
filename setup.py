"""
Setup of core python codebase
Author: Jeff Mahler
"""
import os
from setuptools import setup

requirements = [
    "numpy",
    "scipy",
    "scikit-image",
    "scikit-learn",
    "ruamel.yaml",
    "matplotlib",
    "multiprocess",
    "setproctitle",
    "opencv-python",
    "Pillow",
    "joblib",
    "colorlog",
    "pyreadline; platform_system=='Windows'",
]

# load __version__ without importing anything
version_file = os.path.join(
    os.path.dirname(__file__), "autolab_core/version.py"
)
with open(version_file, "r") as f:
    # use eval to get a clean string of version from file
    __version__ = eval(f.read().strip().split("=")[-1])

setup(
    name="autolab_core",
    version=__version__,
    description="Core utilities for the Berkeley AutoLab",
    long_description=(
        "Core utilities for the Berkeley AutoLab. "
        "Includes rigid transformations, loggers, and 3D data wrappers."
    ),
    author="Jeff Mahler",
    author_email="jmahler@berkeley.edu",
    maintainer="Mike Danielczuk",
    maintainer_email="mdanielczuk@berkeley.edu",
    license="Apache Software License",
    url="https://github.com/BerkeleyAutomation/autolab_core",
    keywords="robotics grasping transformations",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
    ],
    packages=["autolab_core"],
    install_requires=requirements,
    extras_require={
        "docs": ["sphinx", "sphinxcontrib-napoleon", "sphinx_rtd_theme"],
        "ros": ["rospkg", "catkin_pkg", "empy"],
    },
)
