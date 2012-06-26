#!/usr/bin/env python

import sys, os

# check for wrong interpreter on Mac
if sys.platform == 'darwin':
    try:
        runningAsFrozenApp = sys.frozen
    except AttributeError:
        # running from command line, not as frozen application
        if sys.executable.split('/')[-1] == 'python':
            # restart with 'pythonw' interpreter
            arguments = ['/usr/bin/pythonw', os.getcwd() + '/SpotlightStart.py'] + sys.argv[1:]
            os.execvp('/usr/bin/pythonw', arguments )

from SpotlightMain import mtApp
import SpotlightGui

def main(args):
    app = mtApp(0)
    if len(args) == 2:  # check command line for a file name to open
        SpotlightGui.gui.openImageFile(sys.argv[1])
    app.MainLoop()

if __name__=="__main__":
    main(sys.argv)
