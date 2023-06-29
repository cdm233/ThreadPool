from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'A simple threadpool library for python that does three things: distribute work, start work, sync'

# Setting up
setup(
    name="threadpool",
    version=VERSION,
    author="Derek Chen",
    author_email="demeng.chen@mail.utoronto.ca",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/cdm233/ThreadPool",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'multithreading', 'IO Blocking', "threadpool"],
    license="MIT",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)