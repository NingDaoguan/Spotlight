"""
A very simple setup script to create an executable.

Run the build process by entering:
'python setupWin.py py2exe' in a console prompt.

It is assumed that py2exe is installed and environment variables like path
and PYTHONPATH are set.

It is also assumed that a subdirectory was created which contains all
the app .py files, the .ico file, and this 'setupWin.py' file.

"""

import sys
if sys.platform != 'win32':
    print 'setupWin.py can only build Win32 packages'
    sys.exit(1)

from distutils.core import setup
import py2exe

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "",
    description = "Spotlight installation script",
    name = "Spotlight program",

    # targets to build
    windows = [
            {
                "script": "SpotlightStart.py",
                "icon_resources": [(1, "spotlight.ico")]
            }
        ],

    )
