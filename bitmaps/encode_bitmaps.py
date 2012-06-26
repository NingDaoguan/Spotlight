import sys, os, glob
from wx.tools import img2py

output = 'images.py'

# get the list of XPM files
files = glob.glob('*.xpm')

# Truncate the images module
open(output, 'w')

# call img2py on each file
for file in files:

    # extract the basename to be used as the image name
    name = os.path.splitext(os.path.basename(file))[0]
    name = name[0].upper() + name[1:]

    # encode it
    if file == files[0]:
        cmd = "   -c -u -i -n %s %s %s" % (name, file, output)
    else:
        cmd = "-a -c -u -i -n %s %s %s" % (name, file, output)
    img2py.main(cmd.split())



