#!/usr/bin/env pythonw

import sys, os
from SpotlightMain import mtApp
import SpotlightGui

def main(args):
    app = mtApp(0)
    if len(args) == 2:  # check command line for a file name to open
        SpotlightGui.gui.openImageFile(sys.argv[1])
    app.MainLoop()

if __name__=="__main__":
    main(sys.argv)
