'''
Created on Feb 24, 2018

@author: brian
'''

#!/usr/bin/env python3.4
# coding: latin-1

# (c) Massachusetts Institute of Technology 2015-2016
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages, Extension
import io, os, re

here = os.path.abspath(os.path.dirname(__file__))

def read_rst(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

# cf https://packaging.python.org/en/latest/single_source_version.html

def read_file(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()
    
def find_version(*file_paths):
    version_file = read_file(*file_paths)
    version_match = re.search(r"__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

long_description = read_rst('README.rst')

setup(
    name = "dptrp1",
    version = find_version("dptrp1", "__init__.py"),
    packages = find_packages(),
    
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['Crypto',
                        'pbkdf2',
                        'requests',
                        'httpsig',
                        'urllib3',
                        'traits',
                        'pyface',
                        'traitsui',
                        'envisage'], 
                        
                        # ALSO requires PyQt4 >= 4.10, but it's not available
                        # via pypi and distutils.  Install it locally!
    
    package_data = { 'dptrp1.gui' : ['preferences.ini',
                                      'images/*.png']},

    # metadata for upload to PyPI
    author = "Brian Teague",
    author_email = "bpteague@gmail.edu",
    description = "Python package to manage data on the Sony DPT-RP1",
    long_description = long_description,
    license = "GPLv2",
    keywords = "Sony Digital Paper DPT-RP1",
#     url = "https://github.com/bpteague/cytoflow", 
    classifiers=[
                 'Development Status :: 3 - Alpha',
                 'Environment :: Console',
                 'Environment :: MacOS X',
                 'Environment :: Win32 (MS Windows)',
                 'Environment :: X11 Applications :: Qt',
                 'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
                 'Natural Language :: English',
                 'Operating System :: MacOS',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: Implementation :: CPython'],
    
    entry_points={'console_scripts' : ['dptrp1-cli = dptrp1.cli:main'],
                  'gui_scripts' : ['dptrp1 = dptrp1.gui:run_gui']}
)
