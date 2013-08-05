import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "boxsim",
    version = "0.1",
    author = "Fabien Benureau",
    author_email = "fabien.benureau@inria.fr",
    description = ("A java simulation based on JBox2D with a python interface"),
    license = "Not Yet Decided.",
    keywords = "simulation java",
    url = "flowers.inria.fr",
    packages=['boxsim'],
    classifiers=[],
    package_data={'boxsim': ['interact.jar']},
)