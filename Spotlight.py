## #!/usr/bin/env python

import os
import sys
import string
import copy
import pickle
import math
import struct
import time
import SpotlightCommand
import SpotlightGui
import Image
import PilProcess
try:
    from commands import *
    # some application builders require all plugins to be imported
    # in order to correctly resolve module dependencies
    import encodings.string_escape
    import JpegImagePlugin
    import TiffImagePlugin
    import ArgImagePlugin
    import BmpImagePlugin
    import CurImagePlugin
    import DcxImagePlugin
    import EpsImagePlugin
    import FliImagePlugin
    import FpxImagePlugin
    import GbrImagePlugin
    import GifImagePlugin
    import IcoImagePlugin
    import ImImagePlugin
    import ImtImagePlugin

    #import IptcImagePlugin ####<<<<-- causes deprication warning

    import JpegImagePlugin
    import McIdasImagePlugin
    import MicImagePlugin
    import MpegImagePlugin
    import MspImagePlugin
    import PalmImagePlugin
    import PcdImagePlugin
    import PcxImagePlugin
    import PdfImagePlugin
    import PixarImagePlugin
    import PngImagePlugin
    import PpmImagePlugin
    import PsdImagePlugin
    import SgiImagePlugin
    import SunImagePlugin
    import TgaImagePlugin
    import WmfImagePlugin
    import XVThumbImagePlugin
    import XbmImagePlugin
    import XpmImagePlugin
except:
    pass
if sys.platform == 'darwin':
    import VideoReaderMac

# define globals
currentfile = ""
nextfile = ""      # next numbered file
previousfile = ""  # previous numbered file
lastfile = ""      # previously loaded file
resultsfile = ''
imageLoaded = False
moving = False
stepsize = 1
tracking = False
frameCounter = 0
framesToTrack = 100000
scaleTool = None
scaleUserUnits = 1.0
scalePixelUnits = 1.0
pixelScale = 1.0
timeScale = 1.0
ctrlKeyDown = False
stopImmediately = False
lastAviFrame = 0
fileType = 'IMG'
stepMode = 0 # 0=frames (both fields), 1=fields (odd first), 2=fields (even first)
currentField = 0
originalMode = 'RGB'
dontAskAgain = False
skipBrokenFiles = False

workingImage = None # all image processing manipulates the workingImage
dirtyWorkingImage = 0 # set whenever working image changes
forceEveryOperationToRedisplay = 0 # 0 for speed, 1 for debugging

"return the directory where this program is installed"
def installDirectory():
    return os.path.abspath(sys.path[0])

def createUserDirectory():
    """
    On win32 creates a user directory following windows standards. It is
    usually located in 'H:\Documents and Settings\klimek\Application Data'
    directory.
    """
    if sys.platform != "win32":
        return
    home = os.path.expanduser('~')
    datadir = os.path.abspath(os.path.join(home, "Application Data"))
    if os.path.exists(datadir):
        userdir = os.path.abspath(os.path.join(datadir, "Spotlight-8"))
        if os.path.exists(userdir):
            pass  # Spotlight-8 dir already exists - do nothing
        else:
            os.mkdir(userdir) # create dir
    else:
        # Application Data dir doesn't exist so can't append to it a new
        # directory so do nothing
        pass

def userDirectory():
    """ Return the directory where the current user can write files. """
    if sys.platform == "win32":
        home = os.path.expanduser('~')
        datadir = os.path.abspath(os.path.join(home, "Application Data"))
        userdir = os.path.abspath(os.path.join(datadir, "Spotlight-8"))
        if os.path.exists(userdir):
            return userdir
        else:
            return home
    else:
        return os.path.expanduser('~')

### define set functions for globals

def setDontAskAgain(flag):
    global dontAskAgain
    dontAskAgain = flag

def setOriginalMode(d):
    'preserves the depth of the file right after it was loaded in'
    global originalMode
    originalMode = d
def setCurrentField(field):
    'sets the field currently being displayed'
    global currentField
    currentField = field
def setStepMode(mode):
    global stepMode
    stepMode = mode
def setImageType(type):
    global fileType
    fileType = type
def setLastAviFrame(n):
    global lastAviFrame
    lastAviFrame = n
def setStopImmediately(s):
    global stopImmediately
    stopImmediately = s
def setCtrlKeyDown(key):
    global ctrlKeyDown
    ctrlKeyDown = key
def setResultsfile(r):
    global resultsfile
    resultsfile = r
def setPixelScale(s):
    global pixelScale
    pixelScale = s
def setTimeScale(s):
    global timeScale
    timeScale = s
def setScaleUserUnits(s):
    global scaleUserUnits
    scaleUserUnits = s
def setScalePixelUnits(s):
    global scalePixelUnits
    scalePixelUnits = s
def setTracking(flag):
    global tracking
    tracking = flag
def setFramesToTrack(f):
    global framesToTrack
    framesToTrack = f
def setFrameCounter(c):
    global frameCounter
    frameCounter = c
def setScaleTool(s):
    global scaleTool
    scaleTool = s
def setImageLoadedFlag(flag):
    global imageLoaded
    imageLoaded = flag
def setLastFile(file):
    'called by openImageFile in frame'
    global lastfile
    lastfile = file
def setCurrentFile(file):
    'called by openImageFile() in frame as well as openImageFile() in Spotlight'
    global currentfile
    currentfile = file
def setNextFile(file):
    global nextfile
    nextfile = file
def setPreviousFile(file):
    global previousfile
    previousfile = file
def setMoving(flag):
    global moving
    moving = flag
def setStepSize(s):
    global stepsize
    stepsize = s

def mark(aCharacter):
    """ print a mark on the terminal window immediately, for debugging """
    sys.stdout.write(aCharacter)
    sys.stdout.flush()

def setWorkingImage(img):
    """ save the workingImage in a global variable, and schedule display for update"""
    global workingImage, dirtyWorkingImage
    if workingImage == None:
        oldWidth, oldHeight = 0,0
    else:
        oldWidth, oldHeight = getWorkingImageSize()
    workingImage = img
    dirtyWorkingImage = 1 # this is the only place this should be set
    workingImageWidth, workingImageHeight = getWorkingImageSize()
    if oldWidth-workingImageWidth != 0 or oldHeight-workingImageHeight != 0:
        SpotlightGui.gui.iPanel.Zoom() # recalculate scroll bars due to image size change
    # force the image on the screen to be updated because the workingImage has changed
    if forceEveryOperationToRedisplay: # redraws after every processing operation
        SpotlightGui.gui.iPanel.updateDisplay()
    SpotlightGui.gui.iPanel.Refresh()

def clearDirtyWorkingImageFlag():
    global dirtyWorkingImage
    dirtyWorkingImage = 0

def setForceEveryOperationToRedisplay(flag):
    global forceEveryOperationToRedisplay
    forceEveryOperationToRedisplay = flag

def getWorkingImageSize():
    """ return the width and height of the working image """
    if workingImage == None:
        return (0, 0)
    else:
        width, height = workingImage.size[0], workingImage.size[1]  # PIL dependency
        return (width, height)

class AoiList:
    def __init__(self):
        self.currentAoi = -1
        self.aoiList = [] # contains selected aoi's
        self.urList = []  # undo-redo list - contains latest commands
        self.lastExecuted = -1
        self.allowRedo = True

    def __del__(self):
        self = None

    def previousAoi(self):
        'make the previous aoi current'
        self.currentAoi = self.currentAoi - 1
        if self.currentAoi <= -1:
            self.currentAoi = self.getAoiListLength()-1
        self.updateStatusBar0Text()
        SpotlightGui.gui.iPanel.Refresh()

    def nextAoi(self):
        'make the next aoi current'
        self.currentAoi = self.currentAoi + 1
        if self.currentAoi >= self.getAoiListLength():
            self.currentAoi = 0
        self.updateStatusBar0Text()
        SpotlightGui.gui.iPanel.Refresh()

    def setNewAoi(self, aoi):
        'add a new aoi to the aoi list'
        self.aoiList.append(aoi)  # append to end of list
        self.currentAoi = self.getAoiListLength() - 1
        self.updateStatusBar0Text()
        SpotlightGui.gui.iPanel.Refresh()

    def updateWholeImageAoi(self, aoi):
        'replace first aoi with another aoi'
        del self.aoiList[0]
        self.aoiList.insert(0, aoi)

    def deleteCurrentAoi(self):
        'delete the current aoi'
        del self.aoiList[self.currentAoi]
        # check if the 'last' Aoi was deleted
        if self.getAoiListLength() == self.currentAoi:
            self.currentAoi = self.currentAoi - 1
        self.updateStatusBar0Text()
        SpotlightGui.gui.iPanel.Refresh()

    def deleteSelectedAoi(self, aoi):
        'delete the aoi thats passed in'
        if not aoi.isWholeImageAoi():
            self.aoiList.remove(aoi)
            # check if the 'last' Aoi was deleted
            if self.getAoiListLength() == self.currentAoi:
                self.currentAoi = self.currentAoi - 1
            self.updateStatusBar0Text()
            SpotlightGui.gui.iPanel.Refresh()

    def deleteAllAois(self):
        'delete all aois in the list'
        self.currentAoi = self.getAoiListLength() - 1
        for i in range(self.currentAoi+1):
            aoi = self.getCurrentAoi()
            aoi.deinitialize()
            if not aoi.isWholeImageAoi():
                self.deleteCurrentAoi()
            self.currentAoi = self.currentAoi -1
        self.currentAoi = 0
        SpotlightGui.gui.iPanel.Refresh()

    def getAoiListLength(self):
        'returns how many aois are in the list'
        return len(self.aoiList)

    def getCurrentAoi(self):
        'returns reference to the current aoi'
        if self.getAoiListLength() > 0:
            return self.aoiList[self.currentAoi]
        else:
            return None

    def setWholeImageAoiAsCurrent(self):
        'sets the WholeImageAoi as the current aoi'
        self.currentAoi = 0
        SpotlightGui.gui.iPanel.Refresh()

    def getWholeImageAoi(self):
        'returns reference to the WholeImage aoi'
        if self.getAoiListLength() > 0:
            return self.aoiList[0]
        else:
            return None

    def getCurrentAoiCoords(self):
        'get coords of the current aoi'
        if self.getAoiListLength() > 0:
            aoi = self.aoiList[self.currentAoi]
            x1 = aoi.x1
            y1 = aoi.y1
            x2 = aoi.x2
            y2 = aoi.y2
            return (x1, y1, x2, y2)

    def updateModelessAois(self, refreshAxes=False):
        'updates Histogram and Line Profile dialog boxes'
        for aoi in self.aoiList:
            aoi.updateModeless(refreshAxes)

    def redrawAll(self, dc=None):
        """ Redraw AOIs and any other graphic.  """
        if dc==None:
            raise 'dc is None'
        self.redrawAois(dc)
        if scaleTool:
            scaleTool.drawScale(dc)

    def redrawAois(self, dc=None):
        """Redraw AOIs - current aoi with a thick line, all others will thin line"""
        for aoi in self.aoiList:
            if aoi == self.getCurrentAoi():
                aoi.drawAoi(True, dc)
            else:
                aoi.drawAoi(False, dc)

    def updateStatusBar0Text(self):
        aoi = self.getCurrentAoi()
        if aoi:
            aoi.updateStatusBar0()

    def OnMouseRightDown(self, pos):
        'called by OnMouseRightDown()in mtImagePanel class'
        aoi = self.getCurrentAoi()
        if aoi:
            aoi.OnMouseRightDown(pos)

    def OnMouseRightDClick(self, pos):
        'called by OnMouseRightDClick()in mtImagePanel class'
        aoi = self.getCurrentAoi()
        if aoi:
            aoi.OnMouseRightDClick(pos)

    def OnMouseLeftDown(self, pos):
        'called by OnMouseLeftDown()in mtImagePanel class'
        if scaleTool:
            scaleTool.OnMouseLeftDown(pos)
        else:
            aoi = self.getCurrentAoi()
            if aoi:
                aoi.OnMouseLeftDown(pos)

    def OnMouseLeftUp(self, pos):
        'called by OnMouseLeftUp()in mtImagePanel class'
        if scaleTool:
            scaleTool.OnMouseLeftUp(pos)
        else:
            aoi = self.getCurrentAoi()
            if aoi:
                aoi.OnMouseLeftUp(pos)

    def OnMouseMove(self, pos):
        'called by OnMouseMove()in mtImagePanel class'
        if scaleTool:
            scaleTool.OnMouseMove(pos)
        else:
            aoi = self.getCurrentAoi()
            if aoi:
                aoi.OnMouseMove(pos)

    #-------- UndoRedo and processing stuff --------

    def do(self, command):
        aoi = self.getCurrentAoi()
        if self.lastExecuted < len(self.urList) - 1:
            self.deleteAllAfterCurrentPosition()
        self.urList.append(command)
        self.lastExecuted = len(self.urList) - 1
        command.initialize(aoi)
        command.do(aoi)
        self.allowRedo = command.isRedoable()

    def undo(self):
        if self.lastExecuted >= 0:
            c = self.urList[self.lastExecuted]
            c.undo()
            self.allowRedo = True
            self.lastExecuted = self.lastExecuted - 1

    def redo(self):
        if len(self.urList) == 0:
            return
        aoi = self.getCurrentAoi()
        if self.lastExecuted < len(self.urList) - 1:  # middle or beginning of list
            self.lastExecuted = self.lastExecuted + 1
            c = self.urList[self.lastExecuted]
            c.do(aoi)
            if self.lastExecuted < len(self.urList) - 1: # still in the middle
                self.allowRedo = True
            else:
                self.allowRedo = c.isRedoable()
        else:  # last executed command is at end of list
            c = self.urList[self.lastExecuted]
            self.allowRedo = c.isRedoable()
            if self.allowRedo:
                #cCopy = copy.deepcopy(c)
                cCopy = copy.copy(c)
                cCopy.initialize(aoi)
                cCopy.do(aoi)
                self.urList.append(cCopy)
                self.lastExecuted = len(self.urList) - 1

    def deleteAllAfterCurrentPosition(self):
        urlen = len(self.urList)
        n = urlen - self.lastExecuted
        deletePosition = self.lastExecuted + 1
        for i in range(1, n):
            del self.urList[deletePosition]
        self.lastExecuted = len(self.urList) - 1

    def clearURList(self):
        n = len(self.urList)
        deletePosition = 0
        for i in range(n):
            del self.urList[deletePosition]
        self.lastExecuted = len(self.urList) - 1

##-------------------- ScaleTool class ----------------------------------------

class ScaleTool:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.lastPoint = (0,0)
        self.leftdown = False
        self.closest = 0

    def initialize(self, userUnits, pixelUnits, timeUnits):
        params = {}
        self.dd = SpotlightGui.gui.createModelessDialog('ScaleTool', params)
        self.dd.GetUserUnits().SetValue(str(userUnits))
        self.dd.GetPixelUnits().SetValue(str(pixelUnits))
        self.dd.GetTimeUnits().SetValue(str(timeUnits))
        sh = self.dd.Show(True)
        SpotlightGui.gui.iPanel.Refresh()  # calls OnPaint in iPanel

    def deinitialize(self):
        self.dd.Destroy()

    def setParams(self):
        userUnits = self.dd.GetUserUnits().GetValue()
        pixelUnits = self.dd.GetPixelUnits().GetValue()
        timeUnits = self.dd.GetTimeUnits().GetValue()
        # user units
        if self.isFloat(userUnits):
            setScaleUserUnits(float(userUnits))
        else:
            SpotlightGui.gui.messageDialog('invalid user units value')
        # pixel units
        if self.isFloat(pixelUnits):
             setScalePixelUnits(float(pixelUnits))
        else:
            SpotlightGui.gui.messageDialog('invalid pixel units value')
        # time units
        if self.isFloat(timeUnits):
             setTimeScale(float(timeUnits))
        else:
            SpotlightGui.gui.messageDialog('invalid time units value')
        setPixelScale(scaleUserUnits / scalePixelUnits)
        aList.updateStatusBar0Text()
        aList.updateModelessAois()

    def isFloat(self, sn):
        retCode = True
        try:
            n = float(sn)
        except ValueError:
            retCode = False
        return retCode

    def updateStatusBar0(self):
        message = 'Scale: (%3d, %3d) (%3d, %3d)' % (self.x1,self.y1,self.x2,self.y2)
        SpotlightGui.gui.updateStatusBar(message, 0)

    def drawScale(self, dc=None):
        params = {}
        pointList = []
        points = []
        points.append((self.x1, self.y1))
        points.append((self.x2, self.y2))
        pointList.append(points)
        params['pointList'] = pointList
        params['highlight'] = True
        params['thickness'] = 1
        params['lineHandles'] = True
        SpotlightGui.gui.iPanel.drawAoi(params, dc)

    def OnMouseMove(self, pos):
        if self.leftdown:
            px = pos[0]
            py = pos[1]
            offsetWidth = px - self.lastPoint[0]
            offsetHeight = py - self.lastPoint[1]

            if self.closest == 0:   # move Aoi
                self.x1 = self.x1 + offsetWidth
                self.y1 = self.y1 + offsetHeight
                self.x2 = self.x2 + offsetWidth
                self.y2 = self.y2 + offsetHeight
            else:               # move control point
                if self.closest == 1:      # top left corner
                    if self.dist(px, py, self.x2, self.y2) > 5: # limit line length to 5 pix
                        self.x1 = px
                        self.y1 = py
                elif self.closest == 3:    # bottom right corner
                    if self.dist(self.x1, self.y1, px, py) > 5:
                        self.x2 = px
                        self.y2 = py

            r = self.limitLineMovement(self.x1, self.y1, self.x2, self.y2)
            self.x1 = r[0]
            self.y1 = r[1]
            self.x2 = r[2]
            self.y2 = r[3]

            self.lastPoint = (px, py)
            self.updateStatusBar0()
            self.updatePixelUnits()
            SpotlightGui.gui.iPanel.Refresh()  # calls OnPaint in iPanel

    def OnMouseLeftDown(self, pos):
        self.closest = self.Closest(pos)
        self.leftdown = True
        self.lastPoint = pos

    def OnMouseLeftUp(self, event):
        self.leftdown = False

    def updatePixelUnits(self):
        d = self.dist(self.x1, self.y1, self.x2, self.y2)
        s = '%.2f' % d
        self.dd.GetPixelUnits().SetValue(s)

    def Closest(self, c):
        clos = 0
        d = 0.0
        dmin = 10e10
        d = self.dist(self.x1, self.y1, c[0], c[1])
        if (d<dmin and d<10):  # "near" is within 10 pixels
            dmin = d
            clos = 1
        d = self.dist(self.x2, self.y2, c[0], c[1])
        if (d<dmin and d<10):
            dmin = d
            clos = 3
        return clos

    def dist(self, x1, y1, x2, y2):
        t1 = t2 = 0.0
        t1 = x1 - x2
        t2 = y1 - y2
        return math.sqrt(t1*t1 + t2*t2)

    def limitLineMovement(self, x1, y1, x2, y2):
        imX, imY = getWorkingImageSize()
        lenx = min(imX, x2-x1)
        leny = min(imY, y2-y1)
        minXY = 0       # left or top edge of where line can go
        maxX = imX    # right edge of where line can go
        maxY = imY   # bottom edge of where line can go
        if x1 <= minXY:
            x1 = minXY
            if y1 == y2:
                x2 = x1 + lenx
            if abs(y1 - y2) == 1 and x2 < 2:
                x2 = 2
        if x1 > maxX-1:
            x1 = maxX-1
            if y1 == y2:
                x2 = x1 + lenx
            if abs(y1-y2) == 1 and x2 > (maxX-3):
                x2 = maxX-3
        if x2 < minXY:
            x2 = minXY
            if y1 == y2:
                x1 = x2 - lenx
            if abs(y1-y2) == 1 and x1 < 2:
                x1 = 2
        if x2 > maxX-1:
            x2 = maxX-1
            if y1 == y2:
                x1 = x2 - lenx
            if abs(y1-y2) == 1 and x1 > maxX-3:
                x1 = maxX - 3
        if y1 < minXY:
            y1 = minXY
            if x1 == x2:
                y2 = y1 + leny
            if abs(x1-x2) == 1 and y2 < 2:
                y2 = 2
        if y1 > maxY-1:
            y1 = maxY-1
            if x1 == x2:
                y2 = y1 + leny
            if abs(x1-x2) == 1 and y2 > maxY -3:
                y2 = maxY - 3
        if y2 < minXY:
            y2 = minXY
            if x1 == x2:
                y1 = y2 - leny
            if abs(x1-x2) == 1 and y1 < 2:
                y1 = 2
        if y2 > maxY-1:
            y2 = maxY - 1
            if x1 == x2:
                y1 = y2 - leny
            if abs(x1-x2) == 1 and y1 > maxY-3:
                y1 = maxY-3
        if x1 < minXY: x1 = minXY
        if x1 > maxX-1: x1 = maxX-1
        if x2 < minXY: x2 = minXY
        if x2 > maxX-1: x2 = maxX-1
        if y1 < minXY: y1 = minXY
        if y1 > maxY-1: y1 = maxY-1
        if y2 < minXY: y2 = minXY
        if y2 > maxY-1: y2 = maxY-1
        return (x1, y1, x2, y2)


##---------- Program Options class ---------------

class ProgramOptions:
    def __init__(self):
        if sys.platform == 'win32':
            prefix = ''
        else:
            prefix = '.spotlight-'
        self.optionsFile = os.path.abspath(os.path.join(userDirectory(), prefix + 'programOptions.txt'))
        self.programOptions = self.getProgramOptions()
        self.setPaletteDisplay(0)      # set initially to off
        self.setDVCorrectionType(0)   # 0=force square pixels if its DV
        self.setArbitraryWidth(640)  # height will remain same (480 probably)
        self.setPixelDisplayValues(1)     # display initially as actual values
        self.setDialogBoxTab(0) # initially set to display general options

    def getProgramOptions(self):
        'returns the latest path stored in the programOptions.txt file'
        if os.path.isfile(self.optionsFile):
            f = open(self.optionsFile, 'rb')
            opt = pickle.load(f)
            f.close()
            return opt
        else:
            return {'backgroundColor': 'gray',
                    'paletteDisplay': 0,   # 0=apply palette directly to image
                    'dvCorrectionType': 0,       # 1=True, force square pixels
                    'arbitraryWidth': 640,
                    'latestLoadPath': '',
                    'latestSavePath': '',
                    'latestLUTPath': '',
                    'latestResultsPath': '',
                    'pixelValues': 1,
                    'expandRange': 0,
                    'dialogBoxTab': 0}

    def setPaletteDisplay(self, paletteType):
        """Don't save the programOptions here because we want to set
        the paletteDisplay to 0 on startup, i.e. the checkbox labeled
        Apply Palette To Display will always come up not checked each
        time the program is started up."""
        self.programOptions['paletteDisplay'] = paletteType

    def setDVCorrectionType(self, flag):
        """
        Don't save because we want to initialize to TRUE.
        NOTE: the two check boxes are converted to a single variable (named
        "dvCorrectionType") in the dialog box. Essentially they are made to
        act like a radio box with three fields. This simplifies the code and logic.
        """
        self.programOptions['dvCorrectionType'] = flag

    def setArbitraryWidth(self, flag):
        """Don't save because we want to initialize to FALSE """
        self.programOptions['arbitraryWidth'] = flag

    def setPixelDisplayValues(self, v):
        """Sets how pixel intensities will be displayed. 0=display normalized,
        range of (0.0-1.0) and 1=display actual values, range of (0-255).
        """
        self.programOptions['pixelValues'] = v

    def setDialogBoxTab(self, v):
        """Don't save the programOptions here because we want the dialog box
        to always come up with tab 0 each time the program is started up."""
        self.programOptions['dialogBoxTab'] = v

    def setBackgroundColor(self, color):
        self.programOptions['backgroundColor'] = color
        self.saveProgramOptions()

    def setLatestLoadPath(self, p):
        'Keeps track of latest directory and file for load image operation.'
        self.programOptions['latestLoadPath'] = p
        self.saveProgramOptions()

    def setLatestSavePath(self, p):
        'Keeps track of latest directory and file for save image operation.'
        self.programOptions['latestSavePath'] = p
        self.saveProgramOptions()

    def setLatestLUTPath(self, p):
        'Keeps track of latest directory and file for LUT operation.'
        self.programOptions['latestLUTPath'] = p
        self.saveProgramOptions()

    def setLatestResultsPath(self, p):
        'Keeps track of latest directory and file for LUT operation.'
        self.programOptions['latestResultsPath'] = p
        self.saveProgramOptions()

    def saveProgramOptions(self):
        'save back to disk'
        f = open(self.optionsFile, 'wb')
        pickle.dump(self.programOptions, f)
        f.close()

##------------- Results class ----------------------------------------

class Results:
    """
    This class holds and saves the output data generated by the tracking
    process. The main parameter self.data is a list and each item in it is
    another list, which may contain only a single item (like x trackpoint)
    or may contain many items (like a histogram). Here is a sample
    representing a framenumber, x, y, and a very short lineprofile (3 pts):
    [['  1   '], [' 123  '], ['  21  '], ['  12 ', ' 34 ', ' 124 ']]
    """
    def __init__(self):
        self.data = []

    def clearData(self):
        self.data = []

    def clearHeader(self):
        self.header = []
        self.aoiHeader = []
        if timeScale == 1.0:
            self.header.append('|  Frame  |')
        else:
            self.header.append('|     Time     |')

    def addScaleHeader(self):
        """adds the scale header"""
        u = scaleUserUnits
        p = scalePixelUnits
        s = "Scale Factor - user units: %.5f  image units: %.5f" % (u, p)
        self.aoiHeader.append(s)

    def addAoiHeader(self, header, aoicount = -1):
        'adds image name and aoi type'
        s = 'Aoi ' + str(aoicount+1) + ': ' + header
        self.aoiHeader.append(s)

    def addFilenameHeader(self):
        path, file = os.path.split(nextfile)
        name, ext = os.path.splitext(file)
        # add the full path of first file
        imgname, numb = splitExtendedFilename(os.path.abspath(nextfile))
        imgPath = 'Starting Image: ' + imgname
        self.aoiHeader.append(imgPath)
        # add the word fileaname (next to Frame) in the header of various widths
        if len(name) <= 8:
            self.header.append('   filename   |')
        elif len(name) > 8 and len(name) <= 13:
            self.header.append('     filename     |')
        elif len(name) > 13 and len(name) <= 19:
            self.header.append('       filename       |')
        elif len(name) > 19 and len(name) <= 29:
            self.header.append('             filename             |')
        else:
            self.header.append('                 filename                 |')

    def addFrameNumber(self, d):
        """
        Adds the frame number to first column.
        """
        if timeScale == 1.0:
            sn = str(d)
            if stepMode == 0:
                sframe = sn.rjust(5) # right justified in a string 5 wide
                s = '  ' + sframe + '    '
            else:
                sframe = sn.rjust(5)
                f = getFieldName()
                if f == '':
                    field = ' '  # blank space
                else:
                    field = f[13] # 13th char is either an 'o' or an 'e'
                s = ' ' + sframe + ' ' + field + '   '
            f = []
            f.append(s)
            self.data.append(f)
        else:
            d = d / timeScale
            sn = '%.5f' % d
            if stepMode == 0:
                sframe = sn.rjust(12) # right justified in a string 5 wide
                s = ' ' + sframe + '   '
            else:
                sframe = sn.rjust(12)
                f = getFieldName()
                if f == '':
                    field = ' '  # blank space
                else:
                    field = f[13] # 13th char is either an 'o' or an 'e'
                s = ' ' + sframe + ' ' + field + ' '
            f = []
            f.append(s)
            self.data.append(f)

    def addFilename(self):
        """
        Adds the image filename to second column.
        """
        path, file = os.path.split(currentfile)
        name, ext = os.path.splitext(file)
        sname = str(name)
        # make width relative to the header
        w = len(self.header[1]) # width of filename header
        sn = sname.rjust(w-4) + '    '
        f = []
        f.append(sn)
        self.data.append(f)

    def addHeader(self, header, aoicount):
        """
        Adds a one line header to the data file. The header is just a string.
        """
        c = str(aoicount+1)
        for i in range(len(header)):
            h = header[i]
            for j in range(len(h)):
                s = ' ' + h[j] + ' (aoi ' + c + ')' + ' ' + '|'
                self.header.append(s)

    def addTrackData(self, trackPointLabel):
        if trackPointLabel != (): # skip if empty
            n = len(trackPointLabel)
            for i in range(n):
                field = trackPointLabel[i]
                self.data.append(field)

    def addData(self, d):
        """
        Formats the self.data list. The data (d) that's passed in is a
        list containing other lists.
        """
        if len(d) > 0:
            for item in d:
                self.data.append(item)

    def writeHeaderToDisk(self, file, writeAoiHeader = True):
        """
        Write out the header info contained in self.aoiHeader and self.header.
        The writeAoiHeader flag is for specifying when and when not to write
        out the aoiHeader.
        """
        f = open(file, 'a')
        # write image name and aoi type
        f.write('\n')
        if writeAoiHeader: # needed only the first time
            for i in range(len(self.aoiHeader)):
                h = self.aoiHeader[i]
                f.write(h + '\n')
        # write a solid line
        n = 0
        for d in self.header:
            n = n + len(d)
        blanks = '_' * n
        f.write(blanks + '\n')
        # write the main header (processing operations)
        h = ''
        for i in range(len(self.header)):
            h = h + self.header[i]
        f.write(h + '\n' + '\n')
        f.close()

    def writeDataToDisk(self, file):
        """
        Write out the data to disk each frame. The data has accumulated in
        self.data from multiple aois and/or from multiple operations that have
        an data output. The data is formatted by adding blanks where needed so
        that long output data (such as histogram) line up in columns.
        """
        longest = self.getLongest()

        # generate an output list in which blanks are added.
        outList = []
        for x in range(len(self.header)):
            d = self.data[x]

            col = []  # one column (vertical) which will contain data and blanks
            for i in range(longest):
                if len(d) > i:
                    col.append(d[i])
                else:
                    n = len(self.header[x])
                    sgap = ' ' * n
                    col.append(sgap)
            outList.append(col)

        # add a new header if frame number is not 1 (we're in continuous tracking)
        # and we have a long data type (such as histogram)
        if self.data[0][0] != '      1    ' and longest > 1:
            self.writeHeaderToDisk(file, False)

        # write out the formatted data contained in the outList
        f = open(file, 'a')
        for y in range(longest):
            out = ''
            for d in outList:
                item = d[y]
                out = out + item
            f.write(out + '\n')

        f.close()
        self.clearData()  # clear out the data buffer after each frame

    def getLongest(self):
        """
        Get longest data element (list) in self.data - some are single data
        point and others could be line profiles or histograms which have
        many data points.
        """
        longest = 0
        for i in range(len(self.data)):
            if len(self.data[i]) > longest:
                longest = len(self.data[i])
        return longest

##-------------- Instantiate classes ---------------------------------------

createUserDirectory()
aList = AoiList()  # after AoiList class has been defined
pOptions = ProgramOptions()
results = Results()    # hold and formats tracking results
resultsfile = pOptions.programOptions['latestResultsPath']
if resultsfile == '':
    resultsfile = os.path.abspath(os.path.join(userDirectory(), 'results.txt'))

##-------------- Image functions --------------------------

def getPixel(x, y, img = None):
    """ Return pixel value from the main image as int """
    if img:
        p = PilProcess.getPixel(img, x, y)
    else:
        p = PilProcess.getPixel(workingImage, x, y)
    return p

def getPixelNorm(x, y, img = None):
    """ Return pixel value from the main image as normalized values """
    if img:
        return PilProcess.getPixelNorm(img, x, y)
    else:
        return PilProcess.getPixelNorm(workingImage, x, y)

def getWorkingImageMode():
    return workingImage.mode

def getWorkingImageDepth():
    # formerly getImDepth()
    return workingImage.depth

def getAoiImage(r):
    'extracts an Aoi from the main image'
    return workingImage.crop(r)

def setAoiImage(aoiImage, r):
    'copies the aoiImage into the main image and sets the imDirty flag'
    x1 = r[0]
    y1 = r[1]
    workingImage.paste(aoiImage, (x1, y1))
    setWorkingImage(workingImage)

def scaleCoordinates(x, y):
    """
    Take care of pixel scaling when ScaleTool was used.
    """
    if scaleUserUnits == 1.0 and scalePixelUnits == 1.0:
        pass
    else:
        x = x * pixelScale
        y = y * pixelScale
    return (x, y)

def scaleArea(area):
    """
    Take care of pixel scaling when ScaleTool was used.
    """
    if scaleUserUnits == 1.0 and scalePixelUnits == 1.0:
        sArea = '%3d' % area
    else:
        sArea = '%.4f' % (area * pixelScale * pixelScale)
    return sArea

def getPercent(threshold=128):
    """
    This works for thresholded images as well as non-thresholded.
    """
    histo = PilProcess.histogram1
    if not histo:
        return ''

    # sum of whole histogram
    h = 0
    for i in range(0, 256):
        h = h + histo[i]

    # sum for pixels above threshold
    c = 0
    for i in range(threshold+1, 256):
        c = c + histo[i]

    p = float(c)*100.0/float(h)
    p = '%.3f' % p
    return p

##-------------- File functions ------------------------------

def saveImage(image, path):
    """
    Since Spotlight converts all images to RGB, it would save all images
    as RGB even though the original image might have been grayscale.
    Called from SpotlightMain and SpotlightCommand.
    """
    img = image.copy()
    name, ext = os.path.splitext(path)
    if ext == '':
        path = name + '.tif'  # PIL craps out if it doesn't get an extension
    if originalMode == 'L':
        img = image.convert('L')

    # Save "JPEGs" with the best quality, all else with default options
    name, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext == '.jpg':
        img.save(path, quality=96) # high quality but smaller file than q=100
    else:
        img.save(path)

def getExtendedFilename(path, frame=0):
    if fileType == 'AVI':
        if isExtended(path):
            # already is extended so just update the frame number
            actualFile, sf = splitExtendedFilename(path)
            sframe = str(frame)
            name, ext = os.path.splitext(actualFile)
            newName = name + ' -> ' + sframe + ext
            return newName
        else:
            # is not extended, so extend it
            sframe = str(frame)
            name, ext = os.path.splitext(path)
            newName = name + ' -> ' + sframe + ext
            return newName
    else:
        return path

def isExtended(path):
    if fileType == 'AVI':
        name, ext = os.path.splitext(path)
        n = name.find(' -> ')
        if n == -1:  # the string '->' does not exist, so file is not extended
            return False
        else:
            return True

def splitExtendedFilename(path):
    'splits the extended avi file which includes -> string'
    actualFile = ''
    sframe = ''
    if fileType == 'IMG':
        return (path, sframe)
    else:
        name, ext = os.path.splitext(path)
        n = name.find(' -> ')
        if n == -1:  # the string '->' does not exist, so file is not extended
            return (path, sframe)
        else:
            actualName = name[0:n]
            actualFile = actualName + ext
            n = n + 4
            sframe = name[n:len(name)]
            return (actualFile, sframe)

def fileExists(file):
    exists  = True
    actualFile, sframe = splitExtendedFilename(file)
    if not os.path.isfile(actualFile):
        exists = False
    return exists

def loadImage(file):
    """
    Load image from disk and set parameters. Note: most of the errors
    are intercepted in convertTowxImage() rather than here (see the
    note there).
    """
    global skipBrokenFiles
    goodFile = currentfile
    if not fileExists(file):
        return False # errors

    previousSize = (0, 0)
    if workingImage:
        previousSize = getWorkingImageSize()

    try:
        openImageFile(file)
        noErrors = updateSpotlightParameters(file, previousSize)
        return True # no errors
    except Exception, e:
        if str(e) == 'cannot identify image file':
            # write log
            logFile = os.path.abspath(os.path.join(userDirectory(), 'spotlightErrors.txt'))
            f=open(logFile, "a")
            f.write(time.asctime(time.localtime()) + '  ')
            f.write(str(e) + ':  ' + file + '\n')
            f.close()

            if dontAskAgain and not skipBrokenFiles:
                return False

            if not dontAskAgain:
                params = {}
                params['dontAskAgain'] = dontAskAgain
                params['unreadableFilePath'] = file
                params['logFilePath'] = logFile
                params = SpotlightGui.gui.showModalDialog('TrackingFailed', params)
                setDontAskAgain(params['dontAskAgain'])
                skipBrokenFiles = not params['stop']

                if params['stop']:
                    return False

            # advance frame without processing this image
            setCurrentFile(file)
            # If stepping thru fields (not frames) then the number image frames will
            # double-up therefore must skip updating the nextfile and previousfile.
            if currentField != 1:
                setNextFile(getNextFilename(stepsize))
                setPreviousFile(getNextFilename(-stepsize))
            if moving == "forward" or tracking:
                if EnableFrameForward():
                    return loadImage(nextfile)
                else:
                    # reset currentFile
                    setCurrentFile(goodFile)
                    setNextFile("")
                    setPreviousFile(getNextFilename(-stepsize))
                    return False
            elif moving == "backward":
                if EnableFrameBack():
                    return loadImage(previousfile)
                else:
                    # reset currentFile
                    setCurrentFile(goodFile)
                    setNextFile(getNextFilename(stepsize))
                    setPreviousFile("")
                    return False
            else:
                return False
        SpotlightGui.gui.messageDialog('problems opening file: %s' % e)
        return False # errors

def openImageFile(file):
    if fileType == 'AVI':
        framenumber = 0
        actualFile, sframe = splitExtendedFilename(file)
        if sframe != '':
            framenumber = int(sframe)
        img = getAviFileFrame(actualFile, framenumber)
    else:
        img = Image.open(file)
    if img:
        setOriginalMode(img.mode)
        if img.mode == 'L':
            img = img.convert("RGB")

        img = CorrectAspectRatio(img)
        img = checkFields(img)
        setWorkingImage(img)

def updateSpotlightParameters(file, previousSize):
    """
    Take care of some of ancillary stuff.
    """
    setCurrentFile(file)

    # If stepping thru fields (not frames) then the number image frames will
    # double-up therefore must skip updating the nextfile and previousfile.
    if currentField != 1:
        setNextFile(getNextFilename(stepsize))
        setPreviousFile(getNextFilename(-stepsize))

    SpotlightGui.gui.setWindowTitle(getTitleMessage())
    aList.updateModelessAois()
    setImageLoadedFlag(True)
    aList.clearURList()
    # instantiate new whole image aoi
    if aList.getAoiListLength() <= 0:
        command = SpotlightCommand.cmdNewAoiWholeImage()
        aList.do(command)
        aList.clearURList()
    # update the size if it changed
    if previousSize != getWorkingImageSize():
        updateWholeImageAoiSize()
    return True

def CorrectAspectRatio(img):
    """
    Convert the image to square pixels if the 'correct DV aspect ratio'
    option is selected in the Program Options dialog box.
    """
    if pOptions.programOptions['dvCorrectionType'] == 0:
        width, height = img.size
        if width == 720 and height == 480:
            newWidth = int(4.0/3.0 * height)
            return img.resize((newWidth, height))
        else:
            return img
    elif pOptions.programOptions['dvCorrectionType'] == 1:
        width, height = img.size
        newWidth = int(pOptions.programOptions['arbitraryWidth'])
        return img.resize((newWidth, height))
    else:
        return img

def checkFields(img):
    """
    This function returns the appropriate field (or frame) and sets the
    firstField flag which prevents the updating of nextfile and previous
    file.
    """
    if stepMode == 0:   # return full frame
        setCurrentField(0)
        return img
    elif stepMode == 1: # return odd field first
        if currentField != 1:
            setCurrentField(1)
            return PilProcess.extractField(img, 'odd')
        else:
            setCurrentField(2)
            return PilProcess.extractField(img, 'even')
    elif stepMode == 2:  # return even field first
        if currentField != 1:
            setCurrentField(1)
            return PilProcess.extractField(img, 'even')
        else:
            setCurrentField(2)
            return PilProcess.extractField(img, 'odd')

def getFieldName():
    if stepMode == 0:
        return ''

    if stepMode == 1:
        if currentField == 1:
            return '  field:  1 (odd)'
        elif currentField == 2:
            return '  field:  2 (even)'
        else:
            print currentField
            SpotlightGui.gui.messageDialog('error - stepMode=1, no such field')
            return ''
    elif stepMode == 2:
        if currentField == 1:
            return '  field:  2 (even)'
        elif currentField == 2:
            return '  field:  1 (odd)'
        else:
            SpotlightGui.gui.messageDialog('error - stepMode=2, no such field')
            return ''
    else:
        SpotlightGui.gui.messageDialog('error - no such stepMode')
        return ''

def getTitleMessage():
    actualFile, sframe = splitExtendedFilename(currentfile)

    programName = 'Spotlight - '
    if tracking:
        programName = str(frameCounter) + '    Spotlight - '

    if stepMode == 0:   # return full frame
        titleMessage = programName + actualFile
        if fileType == 'AVI':
            titleMessage = titleMessage + '    frame: ' + sframe
        return titleMessage
    else:   # include field information in the title
        titleMessage = programName + actualFile + getFieldName()
        if fileType == 'AVI':
            titleMessage = programName + actualFile
            t = '    frame: ' + sframe + getFieldName()
            titleMessage = titleMessage + t
        return titleMessage

def getAviFileFrame(avifile, framenumber):
    """
    This function pulls out a specific frame out of an AVI file and converts
    it to a PIL image. Returns the PIL image reference.
    """
    if sys.platform == 'win32':
        # Call the C-program to pull the frame out of the AVI file and save it to disk
        avireader = 'AviReader'
        savefile = 'AviTransferFile'
        frame = str(framenumber)
        # Note: popen(2) works on Win2000 and XP (but not win98, no pipes)
        cmd = avireader +  ' ' + avifile + ' ' +  savefile + ' ' + frame
        os.popen2(cmd)
    elif sys.platform == 'darwin':
        # Call the Python language QuickTime reader directly
        savefile = os.path.abspath(os.path.join(userDirectory(), 'AviTransferFile'))
        VideoReaderMac.readFrame(avifile, savefile, framenumber)
    else: # Linux
        # Call the C-program to pull the frame out of the AVI file and save it to disk
        # (most likely not working)
        savefile = os.path.abspath(os.path.join(userDirectory(), 'AviTransferFile'))
        avireader = 'AviReaderLinux'
        cmd = avireader +  ' "' + avifile + '" "' +  savefile + '" ' + str(framenumber)
        os.system(cmd)

    # Read back the image from disk
    data, w, h, colorPlanes, bitsPerPlane = readAviTransferFile(savefile)

    if data == None:
        m = 'Problems opening AVI file \nraw byte data could not be read'
        SpotlightGui.gui.messageDialog(m)
        return None

    # Create an image
    if bitsPerPlane != 8:
        return None

    #img = mProcess.convertRawToImage(data, colorPlanes, w, h)
    img = PilProcess.convertRawToPIL(data, colorPlanes, w, h)
    return img

def readAviTransferFile(inFile):
    'Read the extracted Avi frame - returns raw bytes'
    data, w, h, colorPlanes, bitsPerPlane = None, 0, 0, 0, 0
    if not os.path.isfile(inFile):
        SpotlightGui.gui.messageDialog(inFile + ' does not exist')
        return (data, w, h, colorPlanes, bitsPerPlane)

    try:
        f = open(inFile, 'rb')
    except IOError:
        SpotlightGui.gui.messageDialog('crapped out')
        return (data, w, h, colorPlanes, bitsPerPlane)

    header = f.read(4)
    errorCode = struct.unpack("i", header)[0]
    if errorCode == 0:  # no errors - read rest of the data
        header = f.read(20)  # 5 numbers, each is 4 bytes
        frames, w, h, colorPlanes, bitsPerPlane = struct.unpack("iiiii", header)
        data = f.read()
        setLastAviFrame(frames-1)
    else:
        errorMessage = f.read()
        SpotlightGui.gui.messageDialog(errorMessage, 'AVI Error')
    f.close()
    return (data, w, h, colorPlanes, bitsPerPlane)

def getNextAviFrameName(stepSize):
    outPath = ''
    actualFile, sframe = splitExtendedFilename(currentfile)
    if sframe == '':
        return ''
    num = int(sframe)
    num = num + stepSize
    if num >= 0 and num <= lastAviFrame:
        outPath = getExtendedFilename(actualFile, num)
    return  outPath

def getNextFilename(stepSize):
    """In generating the next (and previous) numeric, a special case is
    supported which is the CM-2 file naming convention. CM-2 files are
    named as follows: basenameNNNaa.tif where NNN is the numeric and
    aa are ASCII letters. The standard names are of the following format:
    basenameNNN.ext where the numeric is located just before the extension.
    """
    if fileType == 'AVI':
        return getNextAviFrameName(stepSize)

    outPath = ''
    path, file = os.path.split(currentfile)
    name, ext = os.path.splitext(file)
    basename, oldNumeric = splitNumeric(name)
    if oldNumeric == '':
        return ''

    numeric1, numeric2 = getNewNumeric(name, stepSize)
    # if numeric2 (above) is null, that means there is only one possible number
    # that it could be. If numeric2 is returned with some value, then there are two
    # possible numbers that the next file name can have and further testing
    # must be done to figure which is correct.
    if numeric2 == '':
        newName = basename + numeric1 + ext
        outPath = os.path.abspath(os.path.join(path, newName))
        if os.path.isfile(outPath):
            return outPath
        else:
            return ''
    else:  # could be either numeric1 or numeric2 - see if either exists
        newPath1 = basename + numeric1 + ext
        newPathName1 = os.path.abspath(os.path.join(path, newPath1))
        newPath2 = basename + numeric2 + ext
        newPathName2 = os.path.abspath(os.path.join(path, newPath2))

        # check which of the two possibilities exists
        path1Exists = False
        path2Exists = False
        if os.path.isfile(newPathName1):
            path1Exists = True
        if os.path.isfile(newPathName2):
            path2Exists = True

        if path1Exists == True and path2Exists == False:
            outPath = newPathName1
        elif path1Exists == False and path2Exists == True:
            outPath = newPathName2
        elif path1Exists == False and path2Exists == False:
            outPath = ''
        else: # both files exist in the same directory
            path, file1 = os.path.split(newPathName1)
            path, file2 = os.path.split(newPathName2)
            m1 = 'Which is the proper filename in the sequence?'
            m2 = 'select --Yes-- if ' + file1 + ' is the correct file.'
            m3 = 'select --No-- if ' + file2 + ' is the correct file.'
            m = m1 + '\n' + m2 + '\n' + m3
            whichFile = SpotlightGui.gui.YesNoDialog(m)
            if whichFile == True:
                outPath = newPathName1
            else:
                outPath = newPathName2

        return outPath

def getNewNumeric(name, stepSize):
    'generate new numeric'
    basename, oldNumeric = splitNumeric(name)

    nn = len(oldNumeric)
    leadzeros = getLeadingZeros(oldNumeric)

    numeric2 = ''

    if stepSize == 0:
        return (oldNumeric, numeric2)

    if leadzeros == 0:
        num = int(oldNumeric)
        num = num + stepSize
        numeric = str(num)
        numeric2 = "0" + numeric
    else:
        num = int(oldNumeric)
        num = num + stepSize
        numeric = str(num)
        for i in range(leadzeros):
            numeric = "0" + numeric

    # add or subtract a 0 (when going from say, 009 to 010)
    if len(numeric) != nn and leadzeros > 0:
        if stepSize >= 0:  # positive stepSize (nextfilename)
            numeric = numeric[1 : len(numeric)]
        else:
            numeric = "0" + numeric # negative stepSize (previousfile)

    # this condition must have happened at some point (because its here)
    # although in further testing I couldn't find any case (number sequence)
    # when this would help.
    if stepSize < 0:
        if leadzeros == 0: # could be numeric  or  numeric2
            pass
        else:
            numeric2 = ''

    return (numeric, numeric2)

def splitNumeric(name):
    'returns a numeric part of a filename'
    lname = list(name) # convert to list (list has a reverse function)
    lname.reverse()    # reverse order - so numbers are at beginning
    numb = []
    for c in lname:
        if c in '0123456789':
            numb.append(c)
        else:
            break
    numb.reverse()   # put them back in the right order
    numeric = ''

    numeric = string.join(numb, '')  # convert back to string

    n = len(name) - len(numeric)
    basename = name[0:n]
    return (basename, numeric)

def getLeadingZeros(numeric):
    'returns number of leading zeros in the numberic'
    count = 0
    if numeric == '':   # numeric is empty - return 0
        return 0
    for c in numeric:   # count number of leading 0's
        if c == '0':
            count = count + 1
        else:
            break
    if count == len(numeric): # numeric is 0 or all 0's
        count = len(numeric) - 1
    return count

def getImageFileFilter(type):
    f2 = '|TIFF file (*.tif)|*.tif;*.TIF'
    f3 = '|BMP file (*.bmp)|*.bmp;*.BMP'
    f4 = '|JPG file (*.jpg)|*.jpg;*.JPG'
    f5 = '|PNG file (*.png)|*.png;*.PNG'
    f6 = '|GIF file (*.gif)|*.gif;*.GIF'
    if type == 'wxOPEN':
        # OPEN can read tga,  but not save
        label = 'All supported image files|'
        ext1 = '*.tif;*.TIF;*.jpg;*.JPG;*.bmp;*.BMP;*.png;*.PNG;*.gif;*.GIF'
        ext2 = ';*.tga;*.TGA;*.avi;*.AVI;*.mov;*.MOV'
        ext3 = ';*.tiff;*.TIFF;*.jpeg;*.JPEG'
        f1 = label + ext1 + ext2 + ext3
        f7 = '|TGA file (*.tga)|*.tga;*.TGA'
        f8 = '|AVI file (*.avi)|*.avi;*.AVI'
        f9 = '|MOV file (*.mov)|*.mov;*.MOV'
        fileTypes = f1 + f2 + f3 + f4 + f5 + f6 + f7 + f8 + f9
    else:
        label = 'All supported image files|'
        ext = '*.tif;*.TIF;*.jpg;*.JPG;*.bmp;*.BMP;*.png;*.PNG'
        f1 = label + ext
        fileTypes = f1 + f2 + f3 + f4 + f5
    return fileTypes

#-------------------------- View functions ------------------------------------------

def OnImageInfo():
    if workingImage:
        info = PilProcess.imageInfo(workingImage, originalMode)
        SpotlightGui.gui.messageDialog(info, 'image info')
        aoi = aList.getCurrentAoi()
        aoi.updateStatusBar0()

def OnScale():
    """brings up a modeless ScaleTool dialog box"""
    if scaleTool == None:
        scTool = ScaleTool(30,30,70,70)
        setScaleTool(scTool)
        scaleTool.initialize(scaleUserUnits, scalePixelUnits, timeScale)
        scaleTool.updateStatusBar0()

def ScaleOk():
    """called when OK button in the Scale dialog box is clicked"""
    scaleTool.setParams()
    scaleTool.deinitialize()
    setScaleTool(None)
    aList.updateStatusBar0Text()
    SpotlightGui.gui.iPanel.Refresh()

def ScaleCancel():
    """called when CANCEL button in the Scale dialog box is clicked"""
    scaleTool.deinitialize()
    setScaleTool(None)
    aList.updateStatusBar0Text()
    SpotlightGui.gui.iPanel.Refresh()

def OnProgramOptions():
    """brings up a dialog box to select Program Options"""
    params = {}
    params['backgroundColor'] = pOptions.programOptions['backgroundColor']
    params['paletteDisplay'] = pOptions.programOptions['paletteDisplay']
    params['latestLUTPath'] = pOptions.programOptions['latestLUTPath']
    params['dvCorrectionType'] = pOptions.programOptions['dvCorrectionType']
    params['arbitraryWidth'] = pOptions.programOptions['arbitraryWidth']
    params['pixelValues'] = pOptions.programOptions['pixelValues']
    params['dialogBoxTab'] = pOptions.programOptions['dialogBoxTab']

    params = SpotlightGui.gui.showModalDialog('ProgramOptions', params)
    if params:
        SpotlightGui.gui.iPanel.setBackgroundColor(params['backgroundColor'])
        pOptions.setBackgroundColor(params['backgroundColor'])
        pOptions.setPaletteDisplay(params['paletteDisplay'])
        pOptions.setLatestLUTPath(params['latestLUTPath'])
        pOptions.setDVCorrectionType(params['dvCorrectionType'])
        pOptions.setArbitraryWidth(params['arbitraryWidth'])
        pOptions.setPixelDisplayValues(params['pixelValues'])
        pOptions.setDialogBoxTab(params['dialogBoxTab'])

        setPalette()

        # reload the image - checks the status of palette and arbitraryWidth
        if workingImage:
            noproblem = loadImage(currentfile)
            SpotlightGui.gui.iPanel.Refresh()
            aList.updateModelessAois(True) # refresh axes

def setPalette():
    paletteDisplay = pOptions.programOptions['paletteDisplay']
    if paletteDisplay == False:
        SpotlightGui.gui.iPanel.setPalette(None)
    else:
        path = pOptions.programOptions['latestLUTPath']
        if path == '':
            SpotlightGui.gui.messageDialog('No palette was specified - Select a Palette!')
            pOptions.setPaletteDisplay(False)  # remove check from the checkbox
            return
        command = SpotlightCommand.cmdPseudocolor()
        palette = command.loadPalette(os.path.abspath(path))
        if palette:
            SpotlightGui.gui.iPanel.setPalette(palette)


#-------------------------- Transport functions --------------------------------------

def EnableFrameForward():
    """check if nextfile exists"""
    if nextfile == "":
        return False
    else:
        return True

def EnableFrameBack():
    """check if a previousfile exists"""
    if previousfile == "":
        return False
    else:
        return True

def OnGotoSpecificFrame():
    """brings up a dialog box to specify goto frame"""
    params = {}
    params['lastframe'] = lastAviFrame
    params = SpotlightGui.gui.showModalDialog('GotoSpecificFrame', params)
    if params:
        file = getExtendedFilename(currentfile, params['framenumber'])
        setCurrentFile(file)
        loadImage(currentfile)
        setNextFile(getNextFilename(stepsize))
        setPreviousFile(getNextFilename(-stepsize))

def Rewind():
    """advances backward in the image sequence as fast as possible"""
    if moving != False:  # prevents lock-up when clicked while moving
        return
    setMoving("backward")
    while(moving != False and EnableFrameBack()):
        if loadImage(previousfile):
            setMoving("backward")
        else:
            setMoving(False)
        SpotlightGui.gui.Yield()
    setMoving(False)

def Stepback():
    """load previous image"""
    if EnableFrameBack():
        setMoving("backward")
        loadImage(previousfile)
        setMoving(False)

def Pause():
    """stops tracking or frames advancing"""
    setMoving(False)

def Stepforward():
    """load next image"""
    if EnableFrameForward():
        setMoving("forward")
        loadImage(nextfile)
        setMoving(False)

def Fastforward():
    """advances forward in the image sequence as fast as possible"""
    if moving != False:  # prevents lock-up when clicked while moving
        return
    setMoving("forward")
    while(moving != False and EnableFrameForward()):
        if loadImage(nextfile):
            setMoving("forward")
        else:
            setMoving(False)
        SpotlightGui.gui.Yield()
    setMoving(False)

def OnNextStepOptions():
    """
    Brings up a dialog box to select field/frame, step size, and frames
    to track.
    """
    params = {}
    params['stepsize'] = stepsize
    params['framesToTrack'] = framesToTrack
    params['stepMode'] = stepMode
    params = SpotlightGui.gui.showModalDialog('NextStepOptions', params)
    if params:
        setStepMode(params['stepMode'])
        setFramesToTrack(params['framesToTrack'])
        setStepSize(params['stepsize'])
        # next two statements enable single stepping with the new stepsize
        setNextFile(getNextFilename(stepsize))
        setPreviousFile(getNextFilename(-stepsize))

#-------------------- AOI functions ----------------------------------

def OnNewRectangle():
    command = SpotlightCommand.cmdNewAoiRectangle()
    aList.do(command)

def OnNewLineProfile():
    command = SpotlightCommand.cmdNewAoiLineProfile()
    aList.do(command)
    SpotlightGui.gui.updateWidgets() # forces enable/disable of menus

def OnNewHistogram():
    command = SpotlightCommand.cmdNewAoiHistogram()
    aList.do(command)
    SpotlightGui.gui.updateWidgets() # forces enable/disable of menus

def OnNewAngleTool():
    command = SpotlightCommand.cmdNewAoiAngleTool()
    aList.do(command)

def OnNewAbelTool():
    command = SpotlightCommand.cmdNewAoiAbelTool()
    aList.do(command)
    SpotlightGui.gui.updateWidgets() # forces enable/disable of menus

def OnNewManualTracking():
    command = SpotlightCommand.cmdNewAoiManualTracking()
    aList.do(command)
    SpotlightGui.gui.updateWidgets() # forces enable/disable of menus

def OnNewThresholdTracking():
    command = SpotlightCommand.cmdNewAoiThresholdTracking()
    aList.do(command)
    SpotlightGui.gui.updateWidgets() # forces enable/disable of menus

def OnNewCenterTracking():
    command = SpotlightCommand.cmdNewAoiCenterTracking()
    aList.do(command)

def OnNewMaximumTracking():
    command = SpotlightCommand.cmdNewAoiMaximumTracking()
    aList.do(command)

def OnNewSnakeTracking():
    command = SpotlightCommand.cmdNewAoiSnake()
    aList.do(command)
    SpotlightGui.gui.updateWidgets() # forces enable/disable of menus

def OnNewLineFollowing():
    command = SpotlightCommand.cmdNewAoiLineFollowing()
    aList.do(command)
    SpotlightGui.gui.updateWidgets() # forces enable/disable of menus

def DeleteCurrentAoi():
    command = SpotlightCommand.cmdDeleteCurrentAoi()
    aList.do(command)

def DeleteAll():
    command = SpotlightCommand.cmdDeleteAllAois()
    aList.do(command)

def NextAoi():
    command = SpotlightCommand.cmdNextAoi()
    aList.do(command)

def PreviousAoi():
    command = SpotlightCommand.cmdPreviousAoi()
    aList.do(command)

def updateWholeImageAoiSize():
    aoi = aList.getWholeImageAoi()
    imX, imY = getWorkingImageSize()
    aoi.setAoiPosition(0, 0, imX, imY)

def deleteAoiFromOnCancel():
    """
    Called when modeless dialog is closed using a cancel button.
    Now find out which aoi is the right one to close.
    """
    for aoi in aList.aoiList:
        if aoi.isCloseExecuted():
            break
    command = SpotlightCommand.cmdDeleteSelectedAoi(aoi)
    aList.do(command)

def redrawAll(dc=None):
    aList.redrawAll(dc)

def OnAoiSetPosition():
    """
    Brings up a dialog box to manually specify position/size of the aoi.
    """
    command = SpotlightCommand.cmdAoiSetPosition()
    aoi = aList.getCurrentAoi()
    ok = command.showDialog(aoi)
    if ok:
        aList.do(command)
    else:
        aoi.updateStatusBar0()

def OnAoiOptions():
    """
    Brings up a dialog box to set up aoi options. Used for Tracking and
    AngleTool aois only.
    """
    aoi = aList.getCurrentAoi()
    if aoi:
        aoi.showAoiOptions()
    aoi.updateStatusBar0()

def OnProcSequence():
    """
    Brings up a dialog box to set up sequence of imaging operations.
    """
    aoi = aList.getCurrentAoi()
    if aoi:
        params = {}
        params['ipSequenceList'] = aoi.ipSequenceList
        params['isThresholdTrackingAoi'] = aoi.isThresholdTrackingAoi()
        # update name -- currently only cmdThreshold supports this
        for ip in params['ipSequenceList']: # list of ip commands
            ip.updateName()

        params = SpotlightGui.gui.showModalDialog('IpSequence', params)
        if params:
            aoi.setSeqList(params['ipSequenceList'])
        aoi.updateStatusBar0()

def OnUpdate():
    """
    The showStopButton and removeStopButton are really only needed when the
    aoi is ManualTracking or LineFollowing. Those AOIs expect a mouse click
    on the image before you can click buttons of menus. Putting up a Stop
    button forces people to either click the image or click the Stop button.
    """
    aoi = aList.getCurrentAoi()
    if aoi.isManualAoi():
        SpotlightGui.gui.showStopButton()

    command = SpotlightCommand.cmdUpdate()
    aList.do(command)

    if aoi.isManualAoi():
        SpotlightGui.gui.removeStopButton()
        setStopImmediately(False)

def instantiateIpCommand(params):
    'instantiates an ip operation (command) from the parameters passed in'
    cmdname = 'SpotlightCommand.cmd' + params['name'] + '()'
    ip = eval(cmdname)  # evaluate the string - returns the instance of the ip class
    return ip

#--------------------- Process functions -------------------------------------

def OnTest():
    command = SpotlightCommand.cmdTest()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnThreshold():
    command = SpotlightCommand.cmdThreshold()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnFilter():
    command = SpotlightCommand.cmdFilter()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnArithmetic():
    command = SpotlightCommand.cmdArithmetic()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnContrast():
    command = SpotlightCommand.cmdContrast()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnMorphological():
    command = SpotlightCommand.cmdMorphological()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnExtractPlane():
    command = SpotlightCommand.cmdExtractPlane()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnExtractField():
    command = SpotlightCommand.cmdExtractField()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnGeometric():
    command = SpotlightCommand.cmdGeometric()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnStatistics():
    command = SpotlightCommand.cmdStatistics()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnProcessSaveAoi():
    command = SpotlightCommand.cmdSaveAoi()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnPseudocolor():
    """
    Perform a pseudocolor operation on an image -- if image is grayscale
    it will be changed to color -- color images remain color
    """
    command = SpotlightCommand.cmdPseudocolor()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnConvertImage():
    command = SpotlightCommand.cmdConvertImage()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()

def OnResizeImage():
    command = SpotlightCommand.cmdResizeImage()
    ok = command.showDialog()
    if ok:
        aList.do(command)
    aoi = aList.getCurrentAoi()
    aoi.updateStatusBar0()


##----------------------- Track functions ---------------------

def trackOne(fCount):
    """
    Perform complete tracking/processing operation.
    """
    # move to next frame
    if False == loadImage(nextfile):
        return False
    # add frame and filename to results
    results.addFrameNumber(fCount)
    results.addFilename()

    # do tracking
    tempCurrentAoi = aList.currentAoi
    aoiCount = 0
    oldCenter = (0, 0)
    for aoi in aList.aoiList:
        aList.currentAoi = aoiCount
        if aoi.useVelocity():
            oldCenter = aoi.getAoiCenter() # old center
            vx, vy = aoi.getVelocity()
            aoi.moveAoi(vx, vy)
        SpotlightGui.gui.iPanel.Refresh()
        command = SpotlightCommand.cmdUpdate()
        command.do(aoi)
        # get data (results) from the ip sequence
        data = command.getData()
        results.addData(data)
        # get trackpoint (obtained from the Aoi class, via command class)
        if aoi.useVelocity():
            trackPoint = command.getTrackPoint() # new center
            vx = trackPoint[0] - oldCenter[0]
            vy = trackPoint[1] - oldCenter[1]
            aoi.setVelocity((vx, vy))
        trackPointLabel = command.getTrackDataLabel() # formatted trackPoint
        results.addTrackData(trackPointLabel)
        aoiCount = aoiCount + 1

    m = 'Frame tracked: ' + str(fCount)
    SpotlightGui.gui.updateStatusBar(m, 2)
    aList.currentAoi = tempCurrentAoi
    SpotlightGui.gui.iPanel.Refresh()
    return True

def OnTrackOne():
    """track one frame"""
    if moving != False:  # prevents lock-up when clicked while moving
        message = 'Fastforward or Rewind is in progress. Stop it before tracking'
        SpotlightGui.gui.messageDialog(message)
        return
    preTrackingOperations()
    if trackOne(1):
        results.writeDataToDisk(resultsfile)
    setTracking(False)
    postTrackingOperations()

def OnTrackContinuous():
    """gets in a tracking loop"""
    if tracking: # this is just double-check, normally OnStop() should do it
        setTracking(False)
        return

    if moving != False:  # prevents lock-up when clicked while moving
        message = 'Fastforward or Rewind is in progress. Stop it before tracking'
        SpotlightGui.gui.messageDialog(message)
        return

    preTrackingOperations()
    while(tracking and EnableFrameForward()):
        SpotlightGui.gui.Yield()
        if tracking == False:
            break
        updateFrameCounter()
        if trackOne(frameCounter):
            results.writeDataToDisk(resultsfile)
        else:
            setTracking(False)
        if frameCounter >= framesToTrack:
            setTracking(False)
        if tracking == False:
            break
    setTracking(False)
    postTrackingOperations()


def updateFrameCounter():
    if currentField != 1:
        setFrameCounter(frameCounter + 1)

def preTrackingOperations():
    'common operations done before tracking is started'
    # set constrain line(s) to which all constrained trackpoints will be mapped to
    for aoi in aList.aoiList:
        if aoi.getConstrain():
            aoi.setImageConstrainLine()

    results.clearData()  # clear out the data buffer
    results.clearHeader()  # clear out the header buffer

    setTracking(True)
    writeHeader()
    SpotlightGui.gui.showStopButton()

def postTrackingOperations():
    'common operations done after tracking is completed'
    results.clearData()  # clear out the data buffer
    results.clearHeader()  # clear out the header buffer
    setFrameCounter(0)
    SpotlightGui.gui.removeStopButton()
    setStopImmediately(False)

def OnStop():
    """
    The Stop button is used for two things, to stop snake slithering
    and to stop tracking.
    """
    if aList.getAoiListLength() <= 0:
        return
    setStopImmediately(True)
    for aoi in aList.aoiList:
        aoi.Stop()
        aoi.leftdown = False # some weirdness with manual aoi

    # stop tracking
    if tracking:
        setTracking(False)

def writeHeader():
    ' set up the aoi header'
    results.addFilenameHeader()
    results.addScaleHeader()
    count = 0
    for aoi in aList.aoiList:
        # add aoi type info
        className = aoi.__class__.__name__
        className = className[3:]  # all but the 1st 3 chars - removes 'Aoi' from the name
        results.addAoiHeader(className, count)
        # add processing operation
        command = SpotlightCommand.cmdUpdate()
        header = command.getHeader(aoi)
        results.addHeader(header, count)
        count = count + 1
    results.writeHeaderToDisk(resultsfile)

def OnResultsFile():
    'brings up a dialog box to select results file'
    params = {}
    params['resultsfile'] = resultsfile
    params = SpotlightGui.gui.showModalDialog('TrackingResultsDialog', params)
    if params:
        setResultsfile(params['resultsfile'])
        pOptions.setLatestResultsPath(resultsfile) # persitent path

#-------------------------- Help functions -----------------------------------------------

def OnAboutSpotlight():
    aboutString = """
    Spotlight-8 (8-bit)  ver. 2005.11.23

    written by:
    robert.klimek@grc.nasa.gov
    ted.wright@grc.nasa.gov
    NASA Glenn Research Center
    Microgravity Science Division

    Spotlight uses functions provided by:

    wxPython and wxWindows
    Copyright 2005 by
    Robin Dunn for wxPython and
    Julian Smart, Robert Roebling, Vadim Zeitlin
    and other members of the wxWindows team

    Python Imaging Library (PIL)
    Copyright 1997-2005 by Secret Labs AB
    Copyright 1995-2005 by Fredrik Lundh
    """

    title = 'About Spotlight'
    SpotlightGui.gui.infoBox(aboutString, 320, 380, title)

def OnViewDocumentation():
    SpotlightManual = os.path.abspath(os.path.join(installDirectory(), 'spotlight.pdf'))
    if 'library.zip' in SpotlightManual:
        # a work around for py2exe sticking all Spotlight files into a library.zip
        # and thus the path of install directory is bound up in this zip file
        import re
        newPath = re.sub('library.zip', '', SpotlightManual)
        SpotlightManual = os.path.abspath(newPath)

    fileExists = os.path.isfile(SpotlightManual)
    if not fileExists:
        m = 'Unable to find Spotlight.PDF file in path: ' + SpotlightManual
        SpotlightGui.gui.messageDialog(m)
        return

    if sys.platform == 'win32':
        os.startfile(SpotlightManual)
    elif sys.platform == 'darwin':
        cmd = 'open /Applications/Preview.app ' + SpotlightManual
        os.system(cmd)
    else:
        pdfViewers = ['acroread', 'gpdf', 'kghostview', 'xpdf']
        for viewer in pdfViewers:
            existCheck = getoutput('which %s' % viewer)
            if ':' in existCheck:
                continue
            # viewer is on path, do Unix style fork and exec to run it
            if 0 == os.fork():
                os.execv(existCheck, [existCheck, SpotlightManual])
            return
        m1 = 'No known PDF reader is installed. '
        m2 = 'If you have a means to display a .PDF file, you'
        m3 = 'can read the the Spotlight documentation at:'
        m4 = '%s' % SpotlightManual
        m = m1 + '\n' + '\n' + m2 + '\n' + m3 + '\n' + m4
        SpotlightGui.gui.messageDialog(m)

def OnNewSinceLastRelease():
    newReleaseString = """
    --- New in Spotlight-8 ver 2005.11.23 ---

    - Added an option to ignore corrupt files when
      tracking or operating the transport controls.

    --- New in Spotlight-8 ver 2005.10.08 ---

    - Fixed a few things in Abel Transform such as
      the header of saved data now saves the value of
      "separation distance" when Intensity is selected.
      Also, the line profile is now saved as floating
      point values which will make it compatible with
      the new AbelGen2.

    --- New in Spotlight-8 ver 2005.09.12 ---

    - Converted Spotlight to wxPython 2.6+ convention.
    - Improved the look and feel on Mac OS X as well as
      fixed a number of Mac related bugs.
    - Completely rewrote Line Profile, Histogram and
      Abel Transform dialog boxes as well as much of
      the supporting code. In the process fixed a flicker
      when the line profile was redrawn.
    - Fixed a bug in Pseudocolor portion of the Program
      Options dialog box requiring that a path to a
      palette file be set before the dialog could be used.
    - Added Spotlight icons to the desktop (when
      installed on win23 using an installer) and to title
      bar.
    - Switched to py2exe (from McMillan Installer) for
      generating standalone windows executibles.
    - On win32 the program preferences are now saved
      to x:\Documents and Settings\user\Application-
      Data following a MSWin standard convention.

    --- New in Spotlight-8 ver 2005.04.28 ---

    - Rewrote the image panel to support double
      buffering. This eliminates the problem of leftover
      graphics artifacts, especially on a Mac, and
      eliminates flicker when scrolling.
    - Added command line image load. This can be used
      as a limited drag-n-drop support. Image file
      can now be dropped onto the Spotlight icon on
      the desktop and the program will open with the
      image loaded.
    - Fixed a bug in pseudocolor palette dialog box
      showing only lower case extensions.
    - Improved how pseudocolor palettes are selected
      from the Program Options dialog box.

    --- New in Spotlight-8 ver 2005.02.17 ---

    - Added support for reading QuickTime video on Mac.
    - Added "Frames tracked" counter to title bar, visible
      during tracking when the program is minimized.

    --- New in Spotlight-8 ver 2004.11.09 ---

    - Fixed AviReader.cpp, which for some AVI files
      reported that a requested frame was less than 0.
    - Modified the code to allow a step size of 0.
      This is useful for manually tracking many points
      on a single frame.

    --- New in Spotlight-8 ver 2004.09.15 ---

    - Converted toolbar button images to python
      code. This eliminates a need for a separate
      bitmaps folder.
    - Fixed a problem with filenames not lining up properly
      when they were certain lenghts.
    - Fixed a problem with the program freezing up when
      fast-forwarding through an AVI file and Track-
      Continuous is hit. Not sure why anybody would ever
      want to do this, but they did.
    - Fixed a bug in the Morphological,Reconstruct routine.
    - Added capability to scale the image width to an
      arbitrary value. This is to compensate for non-square
      pixels.

    --- New in Spotlight-8 ver 2004.03.24 ---

    - Fixed columns alignment in results file. The AVI
      frame numbers were not right justified.

    --- New in Spotlight-8 ver 2004.03.12 ---

    - Fixed a couple bugs related to closing profile
      dialog box and switching color modes while
      fast-forwarding through an AVI.
    - Fixed a bug related to changing angle in Threshold
      Tracking dialog box.
    - Fixed threshold operation updating of AOI. Now
      when you undo, move the AOI, and redo, the new
      AOI will be operated on.
    - Added a few minor improvements to smooth out
      the UI. This includes:
            - Delete key deletes current AOI.
            - TAB key shifts focus to next AOI.
            - Improved line profile data formatting.
    - Added the option to display pixel values as actual or
      normalized.
    - Improved the functionality of ScaleTool. Now the
      scaled pixel coordinates are saved to a results file
      as well as displayed to the screen. Also added time
      scale units.
    - Added area measurement.

    --- New in Spotlight 1.2.1 ---

    - Added resize handles to AOIs (Area of Interest).
    - Fixed a bug in reading a pixel value under the
      cursor when zoomed up.
    - Fixed ScaleTool drawAoi function so that its
      compatible with the new way of drawing AOIs.

    --- New in Spotlight 1.2 ---

    - Added Zoom and Scroll capability.
    - Improved/simplified drawAoi functions to transfer
      the graphics using list of polylines.

    --- New in Spotlight 1.1 ---

    - Added capability to extract a field from a frame.
    - Added Line Following AOI.

    --- New in Spotlight 1.0 ---

    - Finally selected a new permanent name: Spotlight;
      miniTracker was always intended to be a temporary
      name.
    - Added two new tracking AOIs: Center Tracking AOI
      and Local Maximum Tracking AOI.
    - Added constraint of AOI movement to a line during
      tracking.
    - Added Morphological functions.
    - Added AVI file reading under Linux.
    - Added an option to correct DV aspect ratio.
    - Added Resize Image operation.

    --- New in miniTracker 1.7 ---

    - Added AVI file reading (Windows only).
    - Fixed a bug when filename was written as second
      column in the results file, which hung the program
      in some situations.
    - Fixed line profile and histogram columns not lining
      up in results file.

    --- New in miniTracker 1.6 ---

    - Added Manual Tracking Aoi.
    - Added filename to the Results file. The second column
      will now show each filename being tracked.

    --- New in miniTracker 1.5 ---

    - Added Snake Aoi.
    - Uses a velocity vector to move Aoi during tracking
      (predicts where the object might be in the next frame).
    - Uses toolbar button bitmaps with transparent background.
      (Improves the look on both Windows and Linux.)
    - Fixed a problem with FileOpen dialog on Linux.
    - Fixed a bug which prevented decrementing CM-2 files
      from 100 to 99.
    - Stopping of tracking or snake slithering is now stopped
      by clicking on a Stop sign button.

    --- New in miniTracker 1.4 ---

    - Started using wxDesigner (dialog editor).
    - Changed threshold processing dialog box to be
      interactive and added new features.
    - Added coordinate scaling.

    --- New in miniTracker 1.3 ---

    - Added Abel Transform Aoi.
    - Added Angle Tool Aoi.

    --- New in miniTracker 1.2 ---

    - Added Pseudocoloring option.
    - Added CM-2 "type" TIFF file support.

    """
    title = 'What is new since last release'
    SpotlightGui.gui.infoBox(newReleaseString, 384, 450, title)


# self tests
if __name__ == '__main__':
    OnImageInfo()
    print '-----------'
    loadImage('tiger3.jpg')
    print '-----------'
    OnImageInfo()
    print '-----------'
    filter()
