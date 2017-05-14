import os
import io
import re
from setuptools import setup, find_packages
from codecs import open
from os import path

# Version number helpers from
# https://packaging.python.org/en/latest/single_source_version.html
def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='celerybeatmongo',

    version=find_version('celerybeatmongo', '__init__.py'),

    description='A very simple Celery Beat Scheduler that stores status information in a MongoDB database.',
    long_description=long_description,

    url='https://github.com/sm11963/celerybeatmongo',

    # Author details
    author='Sam Miller',
    author_email='sm11963@gmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Object Brokering',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ],

    keywords='celery beat scheduler mongo python',

    packages=[
        'celerybeatmongo',
    ],

    install_requires=[
        'setuptools',
        'celery',
        'marshmallow',
        'pymongo',
        'python-dateutil'
    ],

    extras_require={
        'test': ['pytest'],
    },
)
