import os
import sys
from distutils.sysconfig import get_python_lib
import shutil

def _get_installation_dir():
    """Returns installation location. Works also with easy_install."""
    try:
        import rdb
    except ImportError:
        # Workaround for Windows installer problem with Python 2.6.1
        # http://code.google.com/p/robotframework/issues/detail?id=196
        class FakeModule:
            def __getattr__(self, name):
                raise RuntimeError('Fake module set by rdb_postinstall.py')
        sys.modules['urllib'] = FakeModule()
        import rdb
    return os.path.dirname(os.path.abspath(rdb.__file__))

def windows_binary_install():
    data_path = os.path.join(sys.prefix, 'rdb', 'settings.rdb',)
    install_rdb_path = _get_installation_dir()
    rdb_path = os.path.join(install_rdb_path, 'settings.rdb',)
    try:      
        shutil.move(data_path, rdb_path)
        print '\ndata_path:%s' % data_path
        print '\nrdb_path:%s' % rdb_path
        print '\nInstallation was successful. !'
    except Exception, err:
        print '\nRunning post-install script failed: %s' % err

def windows_binary_uninstall():
    print '\nRunning post-install script...'

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == '-install':
        windows_binary_install()
    elif sys.argv[1] == '-remove':
        windows_binary_uninstall()
        
