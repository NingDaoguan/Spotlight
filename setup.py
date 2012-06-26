"""
Build a self contained application on Mac, run with:
% python setup.py py2app

For the list of available commands, see:
% python setup.py py2app --help

"""
import sys
if sys.platform != 'darwin':
    print 'setup.py can only build Mac packages when run on a Mac'
    sys.exit(1)

from distutils.core import setup
import py2app, os

# Note that you must replace hypens '-' with underscores '_'
# when converting option names from the command line to a script.
# For example, the --argv-emulation option is passed as
# argv_emulation in an options dict.
py2app_options = dict(
    # argv_emulation maps "open document" events to sys.argv.
    # Scripts that expect files as command line arguments
    # can be trivially used as "droplets" using this option.
    # Without this option, sys.argv should not be used at all
    # as it will contain only Mac OS X specific stuff.
    argv_emulation=True,
    semi_standalone=True,
    strip=True,
)

NAME = 'Spotlight-8'
SCRIPT = 'SpotlightStart.py'
ICON = 'spotlightIcon.icns'
ID = 'pth'
VERSION = os.popen('date +%Y.%m.%d').readline()[:-1]
print 'Building', NAME, VERSION

try:
    # path for Tiger
    os.stat('/usr/lib/libwx_macud-2.5.3.rsrc')
    wxPath='/usr/lib/libwx_macud-2.5.3.rsrc'
except OSError:
    # path for Panther
    os.stat('/usr/local/lib/libwx_mac-2.4.0.rsrc')
    wxPath='/usr/local/lib/libwx_mac-2.4.0.rsrc'

DATA_FILES = [ ICON, 'spotlight.pdf', ('../Frameworks', [wxPath] ) ]

plist = dict(
    CFBundleIconFile            = ICON,
    CFBundleName                = NAME,
    CFBundleShortVersionString  = ' '.join([NAME, VERSION]),
    CFBundleGetInfoString       = NAME,
    CFBundleExecutable          = NAME,
    CFBundleIdentifier          = 'gov.nasa.grc.%s' % ID,
)

app_data = dict(script=SCRIPT, plist=plist)

setup(
  data_files = DATA_FILES,
  app = [app_data],
  options = dict(py2app=py2app_options,),
)
