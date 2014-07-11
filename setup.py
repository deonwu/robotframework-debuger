#from setuptools import setup
from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
import os
import sys

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
cur_dir = os.path.abspath(os.getcwd())
#if root_dir != '':
os.chdir("src")

for dirpath, dirnames, filenames in os.walk("."):
    if ".egg" in dirpath: continue
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join("src", dirpath, f) for f in filenames]])

os.chdir(cur_dir)
# Small hack for working with bdist_wininst.
# See http://mail.python.org/pipermail/distutils-sig/2004-August/004134.html
if len(sys.argv) > 1 and sys.argv[1] == 'bdist_wininst':
    for file_info in data_files:
        file_info[0] = '\\PURELIB\\%s' % file_info[0]

version = "1 0 0"

setup(name='RDB',
      version='1.0',
      description='robot framework debug',
      author='IPATA',
      author_email='deonwu@gmail.com',
      url='',      
      package_dir={'': 'src'},
      packages = packages,
      #cmdclass = cmdclasses,
      #data_files = data_files,
      py_modules=[],
      platforms    = 'any',
      data_files=[('rdb', ['src/rdb/settings.rdb', ]), ],
      
      scripts  = ['rdb_postinstall.py', ],
      )

