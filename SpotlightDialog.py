import wx
import wx.lib.dialogs  # for wxScrolledMessageDialog
import math, os, pickle, string, sys
import Spotlight
from DialogBoxes_wdr import *

frame = None

RED = 0
GREEN = 1
BLUE = 2
HUE = 3
SATURATION = 4
LUMINANCE = 5
RGB = 6

#---------------------------------------------------------------------------

def setFrame(f):
    global frame
    frame = f

#--------------

def scaledToNormalized(value):
    """
    Input value is either normalized or actual and output is always normalized.
    """
    if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
        v = value  # stays normalized
    else:
        v = value / 255.0  # convert to normalized
    return v

def scaledToActual(value):
    """
    Input value is either normalized or actual and output is always actual.
    """
    if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
        v = value * 255.0
    else:
        v = value
    return v

def actualToScaled(value):
    """
    Input value is always actual and output is either normalized or actual.
    """
    if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
        v = value / 255.0
    else:
        v = value
    return v

def normalizedToScaled(value):
    """
    Input value is always normalized and output is either normalized or actual.
    """
    if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
        v = value
    else:
        v = int(value * 255.0)
    return v

def infoBox(message, xsize=400, ysize=380, title=""):
    'display a resizable InfoBox message dialog'
    pos = (-1, -1)
    size = (xsize, ysize)
    dlg = wx.lib.dialogs.ScrolledMessageDialog(frame, message, title, pos, size)
    dlg.ShowModal()

def messageDialog(message, title="", displayWindow=None):
    'display a Message message dialog--'
    displayTo = displayWindow
    if displayTo == None:
        displayTo = frame
    dlg = wx.MessageDialog(displayTo, message, title, wx.OK|wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()

def showWxFileDialog(params, displayWindow=None):
    """Display general File Selection dialog box."""
    displayTo = displayWindow
    if displayTo == None:
        displayTo = frame
    title = params['title']
    f1 = params['field1']
    f2 = params['field2']
    f3 = params['field3']
    if params['opType'] == "open":
        fd = wx.FileDialog(displayTo, title, f1, f2, f3, wx.OPEN)
    else:
        fd = wx.FileDialog(displayTo, title, f1, f2, f3, wx.SAVE)
    val = fd.ShowModal()
    if val == wx.ID_OK:
        params = {'path': fd.GetPath()}
    fd.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def YesNoDialog(message, title=""):
    'display a Yes/No dialog - returns YES=True, NO=False'
    returnFlag = False
    dlg = wx.MessageDialog(frame, message, title, wx.YES_NO | wx.ICON_INFORMATION)
    if dlg.ShowModal() == wx.ID_YES:
        returnFlag = True
    else:
        returnFlag = False
    dlg.Destroy()
    return returnFlag

def isValid(sn, min = 0, max = 255, isFloat = False):
    """
    Check the string if it is a number and between min and max -
    returns True if it is
    """
    retCode = True
    try:
        if isFloat:
            n = float(sn)
        else:
            n = int(sn)
        if n >= min and n <= max:
            pass
        else:
            retCode = False
    except ValueError:
        retCode = False
    return retCode

def convertStringToInteger(sn):
    """
    Try to convert the string to a number. The string can be a int or float.
    If the string is non-numeric, thus can't be converted then return None.
    """
    if sn.isdigit():  # integer
        n = int(sn)
    else:
        try: # try to see if its a float
            fn = float(sn)
            n = int(fn)
        except ValueError:
            #n = None
            n = ''
    return n

def showRectangleAoiOptionsDialog(params):
    #~ d = RectangleAoiOptionsDialog('Rectangle Aoi Options')
    d = RectAoiOptionsDialog('Rectangle Aoi Options')

    d.Centre()
    d.setWidth(params['newWidth'])
    d.setHeight(params['newHeight'])
    d.setAspectFlag(params['fixedAspect'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        paramsOut = d.getParams() # validation included in dialog
    d.Destroy()
    if val == wx.ID_OK:
        return paramsOut
    else:
        return {}

def showTestDialog(params, command):
    d = TestDialog(command, -1, "Interactive Test" )
    threshold = params['test']
    v = str(threshold)
    d.GetTestSlider().SetValue(threshold) # set first
    d.GetThreshold().SetValue(v)  # set second
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = d.getParams()
    else:
        command.undo()
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showConvertImageDialog(params):
    d = convertImageDialog("Convert Image Options")
    d.Centre()
    # Note: set only the notebood tab here. The type or depth (radioboxes)
    # are selected inside the dialog box.
    d.setNotebookTab(params['operation'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = d.getParams()
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showEnhanceDialog(params, command):
    d = EnhanceDialog(command, -1, "Interactive Enhancement" )
    brightness = int(params['brightness'])
    d.GetBrightnessSlider().SetValue(brightness) # set first
    bright = str(brightness-100)
    d.GetBrightness().SetValue(bright)  # set second

    contrast = int(params['contrast'])
    d.GetContrastSlider().SetValue(contrast) # set first
    cont = str(contrast-100)
    d.GetContrast().SetValue(cont)  # set second

    val = d.ShowModal()
    if val == wx.ID_OK:
        params = d.getParams()
    else:
        command.undo()
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showStatisticsDialog(params):
    d = statisticsDialog("Image Statistics selection")
    d.Centre()
    d.setStatistic(params['type'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = {'name': 'Statistics', 'type': d.getStatistic()}
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showStandardAoiPositionDialog(params):
    """Used by all Aois other than Snake and Abel, which use their own."""
    d = StandardAoiPositionDialog('Set Aoi Position')
    d.setX1(str(params['x1']))
    d.setY1(str(params['y1']))
    d.setX2(str(params['x2']))
    d.setY2(str(params['y2']))
    val = d.ShowModal()
    if val == wx.ID_OK:
        paramsOut = d.getPositionParams() # validation included in dialog
    d.Destroy()
    if val == wx.ID_OK:
        return paramsOut
    else:
        return {}

def showSnakeAoiPositionDialog(params):
    d = SnakeAoiPositionDialog("Set Aoi Position")
    d.Centre()
    d.setParams(params)
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = d.getParams()
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showAbelToolAoiPositionDialog(params, parent):
    d = AbelToolAoiPositionDialog("Set Aoi Position", parent)
    d.Centre()
    xx1 = params['x1']
    yy1 = params['y1']
    xx2 = params['x2']
    yy2 = params['y2']
    # convert line endpoints to centerpoint and length
    cx = (xx1 + xx2)/2
    cy = (yy1 + yy2)/2
    sx = "%s" % cx
    sy = "%s" % cy
    slength = "%s" % (xx2 - xx1 + 1)
    x = y = length = 0
    d.setX(sx)
    d.setY(sy)
    d.setLength(slength)
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = {}
        if d.areAoiPositionsValid(d.getX(), d.getY(), d.getLength()):
            x = int(d.getX())
            y = int(d.getY())
            length = int(d.getLength())
            # convert centerpoint and length to line endpoints
            if length > 1:
                half = length / 2
                xx1 = x - half
                yy1 = y
                xx2 = x + half
                yy2 = y
                params['x1'] = xx1
                params['y1'] = yy1
                params['x2'] = xx2
                params['y2'] = yy2
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showAngleToolOptionsDialog(params, parentAoi):
    d = AngleToolOptionsDialog(parentAoi, "AngleTool Options")
    d.Centre()
    d.setRelativeTo(params['relativeTo'])
    d.setDisplayMode(params['displayMode'])
    d.setRotateNow(params['rotateNow'])
    d.setAngle(params['angle'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = {'relativeTo': d.getRelativeTo(),
                        'displayMode': d.getDisplayMode(),
                        'rotateNow': d.getRotateNow()}
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showSnakeOptionsDialog(params, parent):
    d = SnakeOptionsDialog("Snake Options", parent)
    d.Centre()
    d.setIntensityWeight(params['intensityWeight'])
    d.setGradientWeight(params['gradientWeight'])
    d.setSecondDerivativeWeight(params['derivativeWeight'])
    d.setEvenSpacingWeight(params['evenSpacingWeight'])
    d.setTotalLengthWeight(params['totalLengthWeight'])
    d.setResultFormatSelection(params['resultFormat'])
    d.setSnakePointsFormatSelection(params['snakePointsFormat'])
    d.setFixedNumberOfPoints(params['fixedNumber'])
    d.setPercent(params['percent'])
    vx, vy = params['velocity']
    d.setVelocityX(vx)
    d.setVelocityY(vy)
    d.setUseVelocityCheckbox(params['useVelocity'])
    d.setPixelsToSearch(params['pixelsToSearch'])
    value = str(actualToScaled(params['idealIntensity']))
    d.setIdealIntensity(value)
    d.setProcessingRadius(params['processingRadius'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        outParams = d.getSnakeParams() # validation included in dialog
    d.Destroy()
    if val == wx.ID_OK:
        return outParams
    else:
        return params   # sends back the original parameters

def showMaximumTrackingOptionsDialog(params):
    d = MaximumTrackingOptions('Local Max Tracking Options')
    d.Centre()
    a = "%.3f" % params['angle'] # 3 digits to right of decimal pt
    d.setAngle(a)
    vx, vy = params['velocity']
    d.setVelocityX(vx)
    d.setVelocityY(vy)
    d.setUseVelocity(params['useVelocity'])
    d.setConstrainToLine(params['constrain'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        paramsOut = d.getLocalMaxTrackingParams() # validation included in dialog
    d.Destroy()
    if val == wx.ID_OK:
        return paramsOut
    else:
        return {}

def showCenterTrackingOptionsDialog(params):
    d = CenterTrackingOptions('Center Tracking Options')
    d.Centre()
    vx, vy = params['velocity']
    d.setVelocityX(vx)
    d.setVelocityY(vy)
    d.setUseVelocityCheckbox(params['useVelocity'])
    d.setTrackingType(params['trackingType'])
    d.setSaveToResultsFile(params['saveResults'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        paramsOut = d.getParams() # validation included in dialog
    d.Destroy()
    if val == wx.ID_OK:
        return paramsOut
    else:
        return {}

def showTrackingResultsDialog(params):
    d = ResultsDialog("Select file for tracking results")
    d.Centre()
    d.setFilePath(params['resultsfile'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = {'resultsfile': d.getFilePath()}
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showThresholdTrackingOptionsDialog(params):
    d = ThresholdTrackingOptions('Threshold Tracking Options')
    d.Centre()
    # Note: direction is set inside the dialog
    a = "%.3f" % params['angle'] # 3 digits to right of decimal pt
    d.setAngle(a)
    vx, vy = params['velocity']
    d.setVelocityX(vx)
    d.setVelocityY(vy)
    d.setUseVelocityCheckbox(params['useVelocity'])
    d.setConstrainToLine(params['constrain'])
    d.setSearchType(params['searchType'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        paramsOut = d.getThresholdTrackingParams() # validation included in dialog
    d.Destroy()
    if val == wx.ID_OK:
        return paramsOut
    else:
        return {}

def showIpSequenceDialog(params):
    d = ipSequenceDialog('Image Processing Sequence', params)
    d.Centre()
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = {'name': 'ipSequence', 'ipSequenceList': d.getSeqList()}
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showResizeImageDialog(params):
    d = ResizeImageDialog("Resize Image")
    d.setWidth(params['newWidth'])
    d.setHeight(params['newHeight'])
    d.setRatio(float(params['newWidth']) / float(params['newHeight']))
    w, h = Spotlight.getWorkingImageSize()
    d.setImageSize((w, h))
    d.setConstrainAspectFlag(params['constrain'])
    d.setType(params['type'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        paramsOut = d.getResizeImageParams()
    d.Destroy()
    if val == wx.ID_OK:
        return paramsOut
    else:
        return {}

def showExtractFieldDialog(params):
    d = ExtractFieldDialog('Field Operation')
    d.setFieldSelection(params['field'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = d.getParams()
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showSaveAoiDialog(params):
    d = saveAoiDialog("Save Aoi to disk")
    d.setAppNumFlag(params['appNumFlag'])
    d.setSaveAsGrayscaleFlag(params['saveAsGrayscaleFlag'])
    d.setPath(params['path'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = d.getParams()
        dir, file = os.path.split(params['path'])
        if os.path.isdir(dir):
            pass
        else:
            messageDialog('specified directory does not exist')
            val = wx.ID_CANCEL # makes this function return False
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showGeometricDialog(params):
    d = geometricDialog('Geometric Options Selection')
    d.Centre()
    d.setNotebookTab(params['operation'])
    d.setAngle(params['angle'])
    d.setAngleSelection(params['angleselection'])
    d.setDistance(params['distance'])
    d.setDirection(params['direction'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = {'name': 'Geometric',
                   'operation': d.getNotebookTab(),
                   'angle': d.getAngle(),
                   'angleselection': d.getAngleSelection(),
                   'direction': d.getDirection(),
                   'distance': d.getDistance()}
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showGotoSpecificFrameDialog(params):
    d = GotoSpecificFrameDialog("Goto Frame")
    #~ d.Centre()
    d.setLastFrame(params['lastframe'])
    d.setFirstFrame(0)
    d.setFrameSelection(2)
    d.setSpecificFrame(0)
    val = d.ShowModal()
    if val == wx.ID_OK:
        paramsOut = d.getSpecificFrameParams() # validation included in dialog
    d.Destroy()
    if val == wx.ID_OK:
        return paramsOut
    else:
        return {}

def showMorphologicalDialog(params):
    d = MorphologicalDialog("Morphological Types")
    d.setType(params['type'])
    d.setIterations(params['iterations'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        paramsOut = d.getMorphologicalParams()
    d.Destroy()
    if val == wx.ID_OK:
        return paramsOut
    else:
        return {}

def showArithmeticDialog(params):
    d = arithmeticDialog("Arithmetic Operations")
    d.Centre()
    d.setOperation(params['operation'])
    d.setSource1(params['source1'])
    d.setSource2(params['source2'])

    const1 = actualToScaled(params['constant1'])
    const2 = actualToScaled(params['constant2'])
    d.setConstant1(str(const1))
    d.setConstant2(str(const2))

    d.setFile1(params['file1'])
    d.setFile2(params['file2'])
    allValid = True
    val = d.ShowModal()
    if val == wx.ID_OK:
        if allValid and d.getSource1() == 2: #if Source1 is file
            allValid = os.path.isfile(d.getFile1())
            if allValid == False:
                messageDialog('Source1 file is invalid')
        if allValid and d.getSource2() == 2: #if Source2 is file
            allValid = os.path.isfile(d.getFile2())
            if allValid == False:
                messageDialog('Source2 file is invalid')
        if allValid:

            value = float(d.getConstant1())
            if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
                allValid = isValid(value, 0.0, 1.0, True)
                if allValid == False:
                    m1 = 'Normalized coordinates in use!\n'
                    m2 = 'Source1 constant is not between 0.0 and 1.0'
                    messageDialog(m1+m2)
            else:
                allValid = isValid(value, 0.0, 255.0, True)
                if allValid == False:
                    messageDialog('Source1 constant is not between 0.0 and 255.0')

        if allValid:
            value = float(d.getConstant2())
            if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
                allValid = isValid(value, 0.0, 1.0, True)
                if allValid == False:
                    m1 = 'Normalized coordinates in use!\n'
                    m2 = 'Source2 constant is not between 0.0 and 1.0'
                    messageDialog(m1+m2)
            else:
                allValid = isValid(value, 0.0, 255.0, True)
                if allValid == False:
                    messageDialog('Source2 constant is not between 0.0 and 255.0')

        if allValid:  # do only if all values are valid
            params = {'name': 'Arithmetic',
                        'operation': d.getOperation(),
                        'constant1': scaledToActual(float(d.getConstant1())),
                        'constant2': scaledToActual(float(d.getConstant2())),
                        'source1': d.getSource1(),
                        'source2': d.getSource2(),
                        'file1': d.getFile1(),
                        'file2': d.getFile2()}
        else:
            val = wx.ID_CANCEL # makes this function return False

    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showNextStepOptionsDialog(params):
    d = NextStepOptionsDialog("Next Step Options")
    d.Centre()
    d.setStepsize(str(params['stepsize']))
    d.setNumberToTrack(str(params['framesToTrack']))
    d.setStepMode(params['stepMode'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = d.getParams()
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showExtractPlaneDialog(params):
    d = extractPlaneDialog("Extract Plane Selection")
    d.Centre()
    d.setColorPlane(params['type'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = {'name': 'ExtractPlane', 'type': d.getColorPlane()}
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showThresholdDialog(params, command):
    d = ThresholdDialog(command, -1, "Interactive threshold" )
    d.GetThresholdType().SetSelection(params['type'])
    d.GetThresholdMode().SetSelection(params['mode'])
    threshold = params['threshold']
    v = str(actualToScaled(threshold))
    d.GetThresholdSlider().SetValue(threshold) # set first
    d.GetThreshold().SetValue(v)  # set second
    #d.GetPercent().SetValue(str(command.getPercent()))
    d.GetPercent().SetValue(str(Spotlight.getPercent()))
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = d.getParams()
    else:
        command.undo()
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showFilterDialog(params):
    d = filterDialog("Filter Type Selection")
    d.Centre()
    d.setFilter(params['type'])
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = {'name': 'Filter', 'type': d.getFilter()}
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showContrastDialog(params):
    d = contrastDialog("Contrast Stretching Selection")
    d.Centre()
    d.setContrastSelection(params['type'])
    s = "%s" % params['subAoiSize']
    d.setSubAoiSize(s)
    val = d.ShowModal()
    if val == wx.ID_OK:
        s = d.getSubAoiSize()  # returns string
        if isSizeValid(s):
            params = {'name': 'Contrast',
                          'type': d.getContrastSelection(),
                          'subAoiSize': int(s)}
        else:
            messageDialog('subAoiSize is not a valid number')
            val = wx.ID_CANCEL # makes this function return False
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def isSizeValid(s):
    'checks subAoiSize'
    try:
        #i = string.atoi(s)
        i = int(s)
        if i < 4 or i > 256:
            return False
        else:
            return True
    except ValueError:
        return False

def showPseudocolorDialog(params):
    path = params['latestLUTPath']
    lutDir, lutFile = os.path.split(path)
    fd = wx.FileDialog(frame, "Open palette", lutDir, lutFile,
            "Palette file (*.dat; *.DAT)|*.dat; *.DAT", wx.OPEN)
    val = fd.ShowModal()
    if val == wx.ID_OK:
        path = os.path.abspath(fd.GetPath())
        params = {'name': 'Pseudocolor', 'palettePath': path}
    fd.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showProgramOptionsDialog(params):
    d = OptionsDialog("Program Options")
    d.Centre()
    d.setNotebookTab(params['dialogBoxTab'])
    d.setColor(params['backgroundColor'])
    d.setPaletteDisplaySelection(params['paletteDisplay'])
    #d.setPalettePath(params['latestLUTPath'])
    d.setPaletteFilePath(params['latestLUTPath'])
    d.setPixelDisplayValues(params['pixelValues'])
    d.setDVCorrectionType(params['dvCorrectionType'])
    d.setArbitraryWidth(str(params['arbitraryWidth']))
    val = d.ShowModal()
    if val == wx.ID_OK:
        params = d.getParams()
    d.Destroy()
    if val == wx.ID_OK:
        return params
    else:
        return {}

def showTrackingFailedDialog(params):
    d = TrackingFailedDialog("Cannot Identify Image File")
    d.setDontAskAgainCheckbox(params['dontAskAgain'])
    d.setLogFilePath(params['logFilePath'])
    d.setUnreadableFilePath(params['unreadableFilePath'])
    val = d.ShowModal()

    params = d.getParams()
    if val == wx.ID_OK:
        params['stop'] = False
    else:
        params['stop'] = True

    d.Destroy()
    return params


#------------------ TrackingFailed dialog box -----------------------------

class TrackingFailedDialog(wx.Dialog):
    #~ def __init__(self, title):
        #~ wx.Dialog.__init__(self, frame, -1, title)
    ### The following makes the dialog resizable with the minimum size set
    ### in the wxDesigner in the TextCtrl widget (set to width=410 pixels)
    def __init__(self, title,
        pos = wx.DefaultPosition, size = wx.DefaultSize,
        style = wx.RESIZE_BORDER|wx.CAPTION):
        wx.Dialog.__init__(self, frame, -1, title, pos, size, style)

        TrackingFailedDialogFunc(self, True)
        self.CentreOnParent()
        #~ a = self.FindWindowById(ID_UNREADABLE_FILES)
        #~ a.Enable(False)

    def getDontAskAgainCheckbox(self):
        a = self.FindWindowById(ID_DONT_ASK)
        return a.GetValue()
    def setDontAskAgainCheckbox(self, flag):
        a = self.FindWindowById(ID_DONT_ASK)
        a.SetValue(flag)

    def setLogFilePath(self, path):
        a = self.FindWindowById(ID_LOG_FILE)
        a.SetValue(str(path))

    def setUnreadableFilePath(self, path):
        a = self.FindWindowById(ID_UNREADABLE_FILE)
        a.SetValue(str(path))

    def getParams(self):
        params = {}
        params['dontAskAgain'] = self.getDontAskAgainCheckbox()
        return params


#---------------
#-------------------- Dialog boxes ------------------------------------
#---------------


class ThresholdDialog(wx.Dialog):
    def __init__(self, command, id, title,
        pos = wx.DefaultPosition, size = wx.DefaultSize,
        style = wx.DEFAULT_DIALOG_STYLE ):
        wx.Dialog.__init__(self, frame, id, title, pos, size, style)
        self.command = command

        ThresholdDialogFunc( self, True )
        self.CentreOnParent()

        # WDR: handler declarations for ThresholdDialog
        self.Bind(wx.EVT_RADIOBOX, self.OnMode, id=ID_THRESHOLD_MODE)
        self.Bind(wx.EVT_RADIOBOX, self.OnType, id=ID_THRESHOLD_TYPE)
        self.Bind(wx.EVT_SLIDER, self.OnSlider, id=ID_THRESHOLD_SLIDER)

    # WDR: methods for ThresholdDialog
    def GetThresholdMode(self):
        return self.FindWindowById(ID_THRESHOLD_MODE)

    def GetPercent(self):
        return self.FindWindowById(ID_PERCENT)

    def GetThresholdType(self):
        return self.FindWindowById(ID_THRESHOLD_TYPE)

    def GetThresholdSlider(self):
        return self.FindWindowById(ID_THRESHOLD_SLIDER)

    def GetThreshold(self):
        return self.FindWindowById(ID_THRESHOLD)

    # WDR: handler implementations for ThresholdDialog

    def OnMode(self, event):
        self.execute()

    def OnType(self, event):
        self.execute()

    def OnSlider(self, event):
        sliderValue = self.GetThresholdSlider().GetValue()
        v = str(actualToScaled(sliderValue))
        self.GetThreshold().SetValue(v)
        if sys.platform == 'darwin': # wx.CallAfter is weird on Mac
            self.execute()
        else:
            wx.CallAfter(self.execute)

    def execute(self):
        type = self.GetThresholdType().GetSelection()
        mode = self.GetThresholdMode().GetSelection()
        threshold = float(self.GetThreshold().GetValue())
        threshold = scaledToActual(threshold) # output is always 0-255
        self.command.executeThreshold(threshold, type, mode)
        self.GetPercent().SetValue(str(Spotlight.getPercent()))

    def getParams(self):
        params = {}
        params['type'] = self.GetThresholdType().GetSelection()
        params['mode'] = self.GetThresholdMode().GetSelection()
        threshold = float(self.GetThreshold().GetValue())
        threshold = scaledToActual(threshold) # output is always 0 - 255
        params['threshold'] = int(threshold)
        return params

#--------------------------------------------------------------

class filterDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)
        pos = wx.DefaultPosition
        size = wx.DefaultSize

        box = wx.BoxSizer(wx.VERTICAL)

        sampleList = ['smooth', 'smooth more', 'blur', 'contour',
            'sharpen', 'sharpen more', 'edge enhance', 'edge detect', 'invert']
        numberOfColumns = 1
        self.rb = wx.RadioBox(self, 10, "Filters", pos, wx.DefaultSize,
                        sampleList, numberOfColumns, wx.RA_SPECIFY_COLS)

        # This expands radio box into the sizer left/right and separately
        # controls top space. Probably most visually pleasing.
        boxTop = wx.BoxSizer(wx.VERTICAL)
        boxTop.Add(self.rb, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 16)
        box.Add(boxTop, 0, wx.EXPAND|wx.TOP, 10) # add space on top

        boxX = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self,wx.ID_OK,"OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self,wx.ID_CANCEL,"Cancel")
        boxX.Add(okButton)
        boxX.Add(cancelButton)
        boxButtons = wx.BoxSizer(wx.VERTICAL)
        boxButtons.Add(boxX, 0, wx.EXPAND|wx.ALL, 10)
        box.Add(boxButtons)

        ### Commented out based on what is in DialogBoxes_wdr.py
        #self.SetAutoLayout(True)
        self.SetSizer(box)
        #box.Fit(self)
        box.SetSizeHints(self)

    def getFilter(self):
        return self.rb.GetSelection()
    def setFilter(self, type):
        self.rb.SetSelection(type)

#-------------------- Arithmetic dialog box -------------------------------------------

class arithmeticDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        defpos = wx.DefaultPosition
        defsize = wx.DefaultSize

        #self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)) # for testing

        # create vertical sizer to hold everything
        box = wx.BoxSizer(wx.VERTICAL)

        # -- Source 1 --
        # Source1 sizers
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box3 = wx.BoxSizer(wx.HORIZONTAL)
        staticBox1 = wx.StaticBox(self, -1, "Source1", defpos, defsize)
        boxSource1 = wx.StaticBoxSizer(staticBox1, wx.VERTICAL)

        # Source1 controls
        self.b1 = wx.RadioButton(self, -1, "this AOI", defpos, defsize, wx.RB_GROUP)
        self.b2 = wx.RadioButton(self, -1, "constant:")
        self.b3 = wx.RadioButton(self, -1, "file:")
        self.constantSource1 = wx.TextCtrl(self, -1, "", defpos, wx.Size(45,-1))
        self.fileSource1 = wx.TextCtrl(self, -1, "", defpos, wx.Size(160,-1))
        self.buttonSource1 = wx.Button(self,-1, "Select", defpos, wx.Size(50,-1))

        # Add Source1 controls to sizers
        box1.Add(self.b1, 0, wx.EXPAND|wx.BOTTOM, 7)
        box2.Add(self.b2)
        box2.Add(self.constantSource1, 0, wx.EXPAND|wx.LEFT|wx.BOTTOM, 1)
        box3.Add(self.b3)
        box3.Add(self.fileSource1, 0, wx.EXPAND|wx.LEFT, 1)
        box3.Add(self.buttonSource1)
        boxSource1.Add(box1)
        boxSource1.Add(box2)
        boxSource1.Add(box3)

        # -- Source 2 --
        # Source2 sizers
        box4 = wx.BoxSizer(wx.HORIZONTAL)
        box5 = wx.BoxSizer(wx.HORIZONTAL)
        box6 = wx.BoxSizer(wx.HORIZONTAL)
        staticBox2 = wx.StaticBox(self, -1, "Source2", defpos, defsize)
        boxSource2 = wx.StaticBoxSizer(staticBox2, wx.VERTICAL)

        # Source2 controls
        self.b4 = wx.RadioButton(self, -1, "this AOI",  defpos, defsize, wx.RB_GROUP)
        self.b5 = wx.RadioButton(self, -1, "constant:")
        self.b6 = wx.RadioButton(self, -1, "file:")
        self.constantSource2 = wx.TextCtrl(self, -1, "", defpos, wx.Size(45,-1))
        self.fileSource2 = wx.TextCtrl(self, -1, "", defpos, wx.Size(160,-1))
        self.buttonSource2 = wx.Button(self,-1, "Select", defpos, wx.Size(50,-1))

        # Add Source2 controls to sizers
        box4.Add(self.b4, 0, wx.EXPAND|wx.BOTTOM, 7)
        box5.Add(self.b5)
        box5.Add(self.constantSource2, 0, wx.EXPAND|wx.LEFT|wx.BOTTOM, 1)
        box6.Add(self.b6)
        box6.Add(self.fileSource2, 0, wx.EXPAND|wx.LEFT, 1)
        box6.Add(self.buttonSource2)
        boxSource2.Add(box4)
        boxSource2.Add(box5)
        boxSource2.Add(box6)

        # now create vertical sizer for left side
        boxLeftSide = wx.BoxSizer(wx.VERTICAL)
        boxLeftSide.Add(boxSource1, 0, wx.EXPAND|wx.BOTTOM, 5)
        boxLeftSide.Add(boxSource2)

        # Arithmetic operation radio buttons
        boxOperation = wx.BoxSizer(wx.VERTICAL)
        optionsList = ['add','subtract','multiply','divide','difference','lighter','darker','blend']
        numberOfColumns = 1
        self.selectOperation = wx.RadioBox(self, 15, "Operation", defpos, defsize,
                        optionsList, numberOfColumns, wx.RA_SPECIFY_COLS)
        boxOperation.Add(self.selectOperation)

        # create a horizontal sizer for all controls except OK and Cancel buttons
        boxAllControls = wx.BoxSizer(wx.HORIZONTAL)
        boxAllControls.Add(boxLeftSide, 0, wx.EXPAND|wx.RIGHT, 5)
        boxAllControls.Add(boxOperation, 0, wx.EXPAND|wx.LEFT, 5)

        # Add all controls except Ok and Cancel buttons
        box.Add(boxAllControls, 0, wx.EXPAND|wx.ALL, 10)

        boxX = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self,wx.ID_OK,"OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self,wx.ID_CANCEL,"Cancel")
        boxX.Add(okButton,0, wx.EXPAND|wx.BOTTOM|wx.RIGHT, 10) # pad only bottom with 15
        boxX.Add(cancelButton,0, wx.EXPAND|wx.BOTTOM|wx.LEFT, 10) # pad only bottom with 15

        box.Add(boxX,0,wx.CENTER)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        box.Fit(self)
        box.SetSizeHints(self)

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateUI)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, self.b1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, self.b2)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, self.b3)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, self.b4)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, self.b5)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, self.b6)
        self.Bind(wx.EVT_BUTTON, self.OnFileSource1, self.buttonSource1)
        self.Bind(wx.EVT_BUTTON, self.OnFileSource2, self.buttonSource2)

    def OnUpdateUI(self, event):
        'enable/disable controls'
        s1 = self.getSource1()
        if s1 == 1:  # if Source1 is a constant
            self.constantSource1.Enable(True)
        else:
            self.constantSource1.Enable(False)
        if s1 == 2:  # if Source1 is a file
            self.fileSource1.Enable(True)
            self.buttonSource1.Enable(True)
        else:
            self.fileSource1.Enable(False)
            self.buttonSource1.Enable(False)
        s2 = self.getSource2()
        if s2 == 1:  # if Source2 is a constant
            self.constantSource2.Enable(True)
        else:
            self.constantSource2.Enable(False)
        if s2 == 2:  # if Source2 is a file
            self.fileSource2.Enable(True)
            self.buttonSource2.Enable(True)
        else:
            self.fileSource2.Enable(False)
            self.buttonSource2.Enable(False)

    def OnFileSource1(self, event):
        homedir = os.path.expanduser('~')  # home dir
        imagedir = os.path.abspath(os.path.join(homedir, 'Images'))
        fileTypes = Spotlight.getImageFileFilter('wxOPEN')
        fd = wx.FileDialog(self, "Open Image", imagedir, "", fileTypes, wx.OPEN)
        if fd.ShowModal() == wx.ID_OK:
            currentfile = fd.GetPath()
            self.setFile1(currentfile)
        fd.Destroy()

    def OnFileSource2(self, event):
        homedir = os.path.expanduser('~')  # home dir
        imagedir = os.path.abspath(os.path.join(homedir, 'Images'))
        fileTypes = Spotlight.getImageFileFilter('wxOPEN')
        fd = wx.FileDialog(self, "Open Image", "", "", fileTypes, wx.OPEN)
        if fd.ShowModal() == wx.ID_OK:
            currentfile = fd.GetPath()
            self.setFile2(currentfile)
        fd.Destroy()

    def getFile1(self):
        return self.fileSource1.GetValue()
    def setFile1(self, val):
        self.fileSource1.SetValue(val)
    def getFile2(self):
        return self.fileSource2.GetValue()
    def setFile2(self, val):
        self.fileSource2.SetValue(val)

    def getSource1(self):
        #return self.selectSource1.GetSelection()
        if self.b1.GetValue():
            return 0
        elif self.b2.GetValue():
            return 1
        else:
            return 2

    def setSource1(self, s):
        if s == 0:
            self.b1.SetValue(True)
            self.b2.SetValue(False)
            self.b3.SetValue(False)
        elif s == 1:
            self.b1.SetValue(False)
            self.b2.SetValue(True)
            self.b3.SetValue(False)
        else:
            self.b1.SetValue(False)
            self.b2.SetValue(False)
            self.b3.SetValue(True)

    def getConstant1(self):
        return self.constantSource1.GetValue()
    def setConstant1(self, val):
        self.constantSource1.SetValue(val)

    def getSource2(self):
        if self.b4.GetValue():
            return 0
        elif self.b5.GetValue():
            return 1
        else:
            return 2

    def setSource2(self, s):
        if s == 0:
            self.b4.SetValue(True)
            self.b5.SetValue(False)
            self.b6.SetValue(False)
        elif s == 1:
            self.b4.SetValue(False)
            self.b5.SetValue(True)
            self.b6.SetValue(False)
        else:
            self.b4.SetValue(False)
            self.b5.SetValue(False)
            self.b6.SetValue(True)

    def getConstant2(self):
        return self.constantSource2.GetValue()
    def setConstant2(self, val):
        self.constantSource2.SetValue(val)

    def getOperation(self):
        return self.selectOperation.GetSelection()
    def setOperation(self, type):
        self.selectOperation.SetSelection(type)

#---------------- Contrast dialog ----------------------

class contrastDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        # --- radio buttons on the left ---
        sampleList = ['Linear Contrast Stretch', 'Histogram Equalization',
            'Adaptive Contrast Stretch']
        numberOfColumns = 1
        self.rb = wx.RadioBox(self, -1, "Type", wx.DefaultPosition, wx.DefaultSize,
                        sampleList, numberOfColumns, wx.RA_SPECIFY_COLS)

        # --- text box and label on the right ---
        self.st = wx.StaticText(self, -1, "SubAoi Size:", wx.DefaultPosition)
        self.t = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(55,-1))

        box1 = wx.BoxSizer(wx.VERTICAL)  # for radio buttons
        box1.Add(self.rb, 0, wx.EXPAND|wx.RIGHT, 10)

        box2 = wx.BoxSizer(wx.HORIZONTAL) # holds text box and label
        box2.Add(self.st, 0, wx.EXPAND|wx.RIGHT, 6)
        box2.Add(self.t)

        box3 = wx.BoxSizer(wx.VERTICAL)  # used for positioning box2 vertically
        box3.Add(box2, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 30)

        box4 = wx.BoxSizer(wx.HORIZONTAL) # holds radio buttons (left) and text box (right)
        box4.Add(box1)  # radio buttons
        box4.Add(box3) # text box

        boxX = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self,wx.ID_OK,"OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self,wx.ID_CANCEL,"Cancel")
        boxX.Add(okButton,0, wx.EXPAND|wx.BOTTOM|wx.RIGHT, 10) # pad only bottom with 15
        boxX.Add(cancelButton,0, wx.EXPAND|wx.BOTTOM|wx.LEFT, 10) # pad only bottom with 15

        # create vertical sizer to hold everything
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(box4, 0, wx.EXPAND|wx.ALL, 10)
        box.Add(boxX,0,wx.CENTER)  # Ok and Cancel buttons
        self.SetAutoLayout(True)
        self.SetSizer(box)
        box.Fit(self)
        box.SetSizeHints(self)

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateUI) # when dialog is created
        self.Bind(wx.EVT_RADIOBOX, self.OnUpdateUI, self.rb)

    def OnUpdateUI(self, event):
        'enable/disable controls'
        if self.getContrastSelection() == 2:  # adaptive contrast stretch
            self.st.Enable(True)
            self.t.Enable(True)
        else:
            self.st.Enable(False)
            self.t.Enable(False)

    def getContrastSelection(self):
        return self.rb.GetSelection()
    def setContrastSelection(self, type):
        self.rb.SetSelection(type)

    def getSubAoiSize(self):
        return self.t.GetValue()
    def setSubAoiSize(self, s):
        self.t.SetValue(s)


#------------------ Extract Plane dialog box ---------------------------------------

class extractPlaneDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)
        pos = wx.DefaultPosition
        size = wx.DefaultSize

        box = wx.BoxSizer(wx.VERTICAL)

        sampleList = ['red', 'green', 'blue', 'luminance']
        numberOfColumns = 1
        self.rb = wx.RadioBox(self, 10, "Color Plane", pos, wx.DefaultSize,
                        sampleList, numberOfColumns, wx.RA_SPECIFY_COLS)

        boxTop = wx.BoxSizer(wx.VERTICAL)
        # expand radio box into the sizer
        boxTop.Add(self.rb, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 20)
        box.Add(boxTop, 0, wx.EXPAND|wx.TOP, 10) # add space on top

        boxX = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self,wx.ID_OK,"OK", size=(60, 22))
        okButton.SetDefault()
        cancelButton = wx.Button(self,wx.ID_CANCEL,"Cancel", size=(60, 22))
        boxX.Add(okButton)
        boxX.Add(cancelButton)
        boxButtons = wx.BoxSizer(wx.VERTICAL)
        boxButtons.Add(boxX, 0, wx.EXPAND|wx.ALL, 10)
        box.Add(boxButtons)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        box.Fit(self)
        box.SetSizeHints(self)

    def getColorPlane(self):
        return self.rb.GetSelection()
    def setColorPlane(self, type):
        self.rb.SetSelection(type)

#-------------- Next Step Options dialog box --------------------------------

class NextStepOptionsDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        NextStepOptionsDialogFunc(self, True)

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateUI) # called when dialog is created
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_BOTH_FIELDS)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_ODD_FIRST)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_EVEN_FIRST)

    def OnUpdateUI(self, event):
        'enable/disable controls'
        stepMode = self.getStepMode()
        if stepMode == 1 or stepMode == 2:
            a = self.FindWindowById(ID_STEP_SIZE)
            a.SetValue(str(1))
            a.Enable(False)
        else:
            a = self.FindWindowById(ID_STEP_SIZE)
            a.Enable(True)

    def getStepsize(self):
        a = self.FindWindowById(ID_STEP_SIZE)
        return a.GetValue()
    def setStepsize(self, step):
        a = self.FindWindowById(ID_STEP_SIZE)
        a.SetValue(str(step))

    def getNumberToTrack(self):
        a = self.FindWindowById(ID_FRAMESTOTRACK)
        return a.GetValue()
    def setNumberToTrack(self, n):
        a = self.FindWindowById(ID_FRAMESTOTRACK)
        a.SetValue(str(n))

    #- NOTE: the reason for using separate radio buttons instead of a single
    #- radio box is so that  each radio button can have its own tooltip.

    def getStepMode(self):
        b0 = self.FindWindowById(ID_BOTH_FIELDS)
        if b0.GetValue():
            return 0
        b1 = self.FindWindowById(ID_ODD_FIRST)
        if b1.GetValue():
            return 1
        b2 = self.FindWindowById(ID_EVEN_FIRST)
        if b2.GetValue():
            return 2

    def setStepMode(self, s):
        b0 = self.FindWindowById(ID_BOTH_FIELDS)
        b1 = self.FindWindowById(ID_ODD_FIRST)
        b2 = self.FindWindowById(ID_EVEN_FIRST)
        if s == 0:
            b0.SetValue(True)
            b1.SetValue(False)
            b2.SetValue(False)
        elif s == 1:
            b0.SetValue(False)
            b1.SetValue(True)
            b2.SetValue(False)
        elif s == 2:
            b0.SetValue(False)
            b1.SetValue(False)
            b2.SetValue(True)

    def getParams(self):
        stepsize = self.getStepsize()
        framesToTrack = self.getNumberToTrack()
        stepMode = self.getStepMode()

        valid = True
        #~ if not isValid(stepsize, 0, 1000):
            #~ m = 'Stepsize is out of range of (0 - 1000)'
            #~ messageDialog(m)
            #~ valid = False
        if not isValid(framesToTrack, 0, 1000000):
            m = 'Frame number is out of range of (0 - 1000000'
            messageDialog(m)
            valid = False

        params = {}
        if valid:
            params['stepsize'] = int(stepsize)
            params['framesToTrack'] = int(framesToTrack)
            params['stepMode'] = stepMode
        return params

#---------------- Morphological dialog box -----------------------------

class MorphologicalDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        MorphologicalDialogFunc(self, True)
        self.CentreOnParent()

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateUI) # called when dialog is created
        self.Bind(wx.EVT_RADIOBOX, self.OnUpdateUI, id=ID_MORPHO_TYPE)

    def OnUpdateUI(self, event):
        'enable/disable controls'
        if self.getType() == 0 or self.getType() == 1 or self.getType() == 2:
            self.enableIterations(True)
        else:
            self.enableIterations(False)

    def enableIterations(self, flag):
        a = self.FindWindowById(ID_ITERATIONS)
        b = self.FindWindowById(ID_TEXT_ITERATIONS)
        a.Enable(flag)
        b.Enable(flag)

    def getType(self):
        a = self.FindWindowById(ID_MORPHO_TYPE)
        return a.GetSelection()
    def setType(self, type):
        a = self.FindWindowById(ID_MORPHO_TYPE)
        a.SetSelection(type)

    def getIterations(self):
        a = self.FindWindowById(ID_ITERATIONS)
        return a.GetValue()
    def setIterations(self, i):
        a = self.FindWindowById(ID_ITERATIONS)
        a.SetValue(str(i))

    def getMorphologicalParams(self):
        params = {}
        params['name'] = 'Morphological'
        params['type'] = self.getType()
        params['iterations'] = int(self.getIterations())
        return params

#---------------- GotoSpecificFrameDialog dialog box -----------------------------

class GotoSpecificFrameDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        GotoFrameDialogFunc(self, True)
        self.CentreOnParent()

        self.setPermanentGray()

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateUI) # called when dialog is created
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_RADIO_FIRST)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_RADIO_LAST)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_RADIO_SPECIFIC)

    def OnUpdateUI(self, event):
        'enable/disable controls'
        selection = self.getFrameSelection()
        if selection == 0 or selection == 1:
            a = self.FindWindowById(ID_GOTO_SPECIFIC)
            a.Enable(False)
        else:
            a = self.FindWindowById(ID_GOTO_SPECIFIC)
            a.Enable(True)
            # SetFocus and SetSelection together highlight the wx.TextCtrl
            a.SetFocus()
            a.SetSelection(-1, -1)

    def setPermanentGray(self):
        'this disables the Goto First and Goto Last fields'
        a = self.FindWindowById(ID_GOTO_FIRST)
        b = self.FindWindowById(ID_GOTO_LAST)
        a.Enable(False)
        b.Enable(False)

    def setFirstFrame(self, firstframe):
        a = self.FindWindowById(ID_GOTO_FIRST)
        a.SetValue(str(firstframe))

    def setLastFrame(self, lastframe):
        self.lastframe = lastframe
        a = self.FindWindowById(ID_GOTO_LAST)
        a.SetValue(str(lastframe))

    def setSpecificFrame(self, f):
        a = self.FindWindowById(ID_GOTO_SPECIFIC)
        a.SetValue(str(f))

    def getSpecificFrame(self):
        a = self.FindWindowById(ID_GOTO_SPECIFIC)
        return a.GetValue()

    def getFrameSelection(self):
        b0 = self.FindWindowById(ID_RADIO_FIRST)
        if b0.GetValue():
            return 0
        b1 = self.FindWindowById(ID_RADIO_LAST)
        if b1.GetValue():
            return 1
        b2 = self.FindWindowById(ID_RADIO_SPECIFIC)
        if b2.GetValue():
            return 2
    def setFrameSelection(self, s):
        b0 = self.FindWindowById(ID_RADIO_FIRST)
        b1 = self.FindWindowById(ID_RADIO_LAST)
        b2 = self.FindWindowById(ID_RADIO_SPECIFIC)
        if s == 0:
            b0.SetValue(True)
            b1.SetValue(False)
            b2.SetValue(False)
        elif s == 1:
            b0.SetValue(False)
            b1.SetValue(True)
            b2.SetValue(False)
        elif s == 2:
            b0.SetValue(False)
            b1.SetValue(False)
            b2.SetValue(True)

    def getSpecificFrameParams(self):
        selection = self.getFrameSelection()
        if selection == 0:
            frame = 0
        elif selection == 1:
            frame = self.lastframe
        else:
            frame = self.getSpecificFrame()

        valid = True
        if not isValid(frame, 0, self.lastframe):
            m = 'Frame number is out of range of (0 - ' + str(self.lastframe) + ')'
            messageDialog(m)
            valid = False

        params = {}
        if valid:
            params['framenumber'] = int(frame)
        return params

#------------------- Geometric dialog ------------------------------------

class geometricDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        GeometricDialogFunc(self, True)

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateUI) # called when dialog is created
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_ANGLE90)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_ANGLE180)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_ANGLE270)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_ANGLEOTHER)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_ANGLEFLIP)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_ANGLEFLOP)

    def OnUpdateUI(self, event):
        'enable/disable controls'
        s = self.getAngleSelection()
        if s == 0:  # 90 degrees
            self.setAngle(90.0)
        elif s == 1:  # 180 degrees
            self.setAngle(180.0)
        elif s == 2:  # 270 degrees
            self.setAngle(270.0)

        if s == 3:  # manually setting angle
            self.setAngleEnable(True)
        else:
            self.setAngleEnable(False)

    def getNotebookTab(self):
        t = self.FindWindowById(ID_GEOMETRIC_DIALOG)
        return t.GetSelection()
    def setNotebookTab(self, tab):
        ntab = int(tab)
        t = self.FindWindowById(ID_GEOMETRIC_DIALOG)
        t.SetSelection(ntab)

    def getAngle(self):
        a = self.FindWindowById(ID_ANGLE)
        return a.GetValue()
    def setAngle(self, angle):
        s = str(angle)
        a = self.FindWindowById(ID_ANGLE)
        a.SetValue(s)

    def setAngleEnable(self, flag):
        a = self.FindWindowById(ID_ANGLE)
        a.Enable(flag)

    def getAngleSelection(self):
        b1 = self.FindWindowById(ID_ANGLE90)
        if b1.GetValue():
            return 0
        b2 = self.FindWindowById(ID_ANGLE180)
        if b2.GetValue():
            return 1
        b3 = self.FindWindowById(ID_ANGLE270)
        if b3.GetValue():
            return 2
        b4 = self.FindWindowById(ID_ANGLEOTHER)
        if b4.GetValue():
            return 3
        b5 = self.FindWindowById(ID_ANGLEFLIP)
        if b5.GetValue():
            return 4
        b6 = self.FindWindowById(ID_ANGLEFLOP)
        if b6.GetValue():
            return 5

    def setAngleSelection(self, s):
        b1 = self.FindWindowById(ID_ANGLE90)
        b2 = self.FindWindowById(ID_ANGLE180)
        b3 = self.FindWindowById(ID_ANGLE270)
        b4 = self.FindWindowById(ID_ANGLEOTHER)
        b5 = self.FindWindowById(ID_ANGLEFLIP)
        b6 = self.FindWindowById(ID_ANGLEFLOP)
        if s == 0:
            b1.SetValue(True)
            b2.SetValue(False)
            b3.SetValue(False)
            b4.SetValue(False)
            b5.SetValue(False)
            b6.SetValue(False)
        elif s == 1:
            b1.SetValue(False)
            b2.SetValue(True)
            b3.SetValue(False)
            b4.SetValue(False)
            b5.SetValue(False)
            b6.SetValue(False)
        elif s == 2:
            b1.SetValue(False)
            b2.SetValue(False)
            b3.SetValue(True)
            b4.SetValue(False)
            b5.SetValue(False)
            b6.SetValue(False)
        elif s == 3:
            b1.SetValue(False)
            b2.SetValue(False)
            b3.SetValue(False)
            b4.SetValue(True)
            b5.SetValue(False)
            b6.SetValue(False)
        elif s == 4:
            b1.SetValue(False)
            b2.SetValue(False)
            b3.SetValue(False)
            b4.SetValue(False)
            b5.SetValue(True)
            b6.SetValue(False)
        else:
            b1.SetValue(False)
            b2.SetValue(False)
            b3.SetValue(False)
            b4.SetValue(False)
            b5.SetValue(False)
            b6.SetValue(True)

    def getDistance(self):
        d = self.FindWindowById(ID_TRANS_DISTANCE)
        return d.GetValue()
    def setDistance(self, dist):
        d = self.FindWindowById(ID_TRANS_DISTANCE)
        s = str(dist)
        d.SetValue(s)

    def getDirection(self):
        d = self.FindWindowById(ID_RADIOBOX2)
        return d.GetSelection()
    def setDirection(self, type):
        d = self.FindWindowById(ID_RADIOBOX2)
        d.SetSelection(type)

#------------------ Save Aoi dialog -------------------------

class saveAoiDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        SaveAoiDialogFunc(self, True)
        self.CentreOnParent()

        self.Bind(wx.EVT_BUTTON, self.OnSelect, id=ID_BASEFILE_SEL)
        self.Bind(wx.EVT_CHECKBOX, self.OnAppendNumber, id=ID_CHECK_APPNUMB)

    def setPath(self, path):
        dir, file = os.path.split(path)
        base, ext = os.path.splitext(file)

        basename, numeric = Spotlight.splitNumeric(base)

        basepath = os.path.abspath(os.path.join(dir, basename))
        self.setBasePath(basepath)
        self.setExt(ext)

        if numeric == '':
            self.setAppendNumber(0)
        else:
            self.setAppendNumber(int(numeric))

        if self.getAppNumFlag(): # enable/disable a wxTextCtrl
            self.enableAppendNumb(True)
        else:
            self.enableAppendNumb(False)

    def getBasePath(self):
        d = self.FindWindowById(ID_BASEFILE)
        return d.GetValue()
    def setBasePath(self, path):
        d = self.FindWindowById(ID_BASEFILE)
        d.SetValue(str(path))

    def getExt(self):
        a = self.FindWindowById(ID_FILE_EXT)
        return a.GetValue()
    def setExt(self, ext):
        a = self.FindWindowById(ID_FILE_EXT)
        a.SetValue(str(ext))

    def getAppendNumber(self):
        d = self.FindWindowById(ID_APPEND_NUMB)
        return d.GetValue()
    def setAppendNumber(self, n):
        d = self.FindWindowById(ID_APPEND_NUMB)
        d.SetValue(str(n))

    def OnAppendNumber(self, event):
        self.enableAppendNumb(event.Checked()) # enable/disable

    def enableAppendNumb(self, flag):
        a = self.FindWindowById(ID_APPEND_NUMB)
        a.Enable(flag)

    def OnSelect(self, event):
        fileTypes = Spotlight.getImageFileFilter('wxSAVE')
        dir, file = os.path.split(self.getBasePath())
        fd = wx.FileDialog(self, "Save Image", dir, "", fileTypes, wx.SAVE)
        val = fd.ShowModal()
        if val == wx.ID_OK:
            path = fd.GetPath()
            dir, file = os.path.split(path)
            base, ext = os.path.splitext(file)
            ext = self.getExt()
            basename, numeric = Spotlight.splitNumeric(base)
            basePath = os.path.abspath(os.path.join(dir, basename))
            self.setBasePath(basePath)
            self.setExt(ext)
        fd.Destroy()

    def getAppNumFlag(self):
        a = self.FindWindowById(ID_CHECK_APPNUMB)
        return a.GetValue()
    def setAppNumFlag(self, flag):
        a = self.FindWindowById(ID_CHECK_APPNUMB)
        a.SetValue(flag)

    def getSaveAsGrayscaleFlag(self):
        a = self.FindWindowById(ID_SAVEAS_GRAY)
        return a.GetValue()
    def setSaveAsGrayscaleFlag(self, flag):
        a = self.FindWindowById(ID_SAVEAS_GRAY)
        a.SetValue(flag)

    def getParams(self):
        params = {}
        params['name'] = 'SaveAoi'
        params['appNumFlag'] = self.getAppNumFlag()
        params['saveAsGrayscaleFlag'] = self.getSaveAsGrayscaleFlag()

        # now combine parts to generate the full path
        basepath = self.getBasePath()
        numb = self.getAppendNumber()
        ext = self.getExt()

        # split off any numbers that might be part of the basepath and use
        # the "appendnumber" from the combo box
        dir, file = os.path.split(basepath)
        basename, numeric = Spotlight.splitNumeric(file)
        basePath = os.path.abspath(os.path.join(dir, basename))

        if self.getAppNumFlag():
            path = basePath + numb + ext
        else:
            path = basePath + ext
        params['path'] = path
        return params

#---------------- ExtractFieldDialog ------------------------------------

class ExtractFieldDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        ExtractFieldDialogFunc(self, True)
        self.CentreOnParent()

    def getFieldSelection(self):
        a = self.FindWindowById(ID_EXTRACT_FIELD)
        return a.GetSelection()
    def setFieldSelection(self, type):
        a = self.FindWindowById(ID_EXTRACT_FIELD)
        a.SetSelection(type)

    def getParams(self):
        params = {}
        params['name'] = 'ExtractField'
        params['field'] = self.getFieldSelection()
        return params

#------------------ ResizeImage dialog box -----------------------------


class ResizeImageDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        ResizeImageDialogFunc(self, True)
        self.CentreOnParent()
        self.ratio = 0.0
        self.constrainAspectFlag = False
        self.update = True
        self.imageSize = (0, 0)  # original size

        self.Bind(wx.EVT_TEXT, self.OnGetWidthText, id=ID_RESIZE_WIDTH)
        self.Bind(wx.EVT_TEXT, self.OnGetHeightText, id=ID_RESIZE_HEIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.OnUpdateConstrainAspect, id=ID_CONSTRAIN_ASPECT)
        self.Bind(wx.EVT_COMBOBOX, self.OnUpdateType, id=ID_DIM_TYPE)

    def OnGetWidthText(self, event):
        s = event.GetString()
        if not self.allowToContinue(s):
            return

        # if Width is blank if Height is blank also
        if s == '':
            if self.getConstrainAspectFlag():
                self.setH(s)
            return

        if self.getType() == "pixels":
            if isValid(s, 0, 10001):
                self.updateHeight(s)
                self.updateColor(ID_RESIZE_WIDTH)
            else:
                self.updateColor(ID_RESIZE_WIDTH, "red")
        else:
            if isValid(s, 0.0, 1000.1, isFloat=True):
                self.updateHeight(s)
                self.updateColor(ID_RESIZE_WIDTH)
            else:
                self.updateColor(ID_RESIZE_WIDTH, "red")


    def OnGetHeightText(self, event):
        s = event.GetString()
        if not self.allowToContinue(s):
            return

        # if Height is blank if Width is blank also
        if s == '':
            if self.getConstrainAspectFlag():
                self.setW(s)
            return

        if self.getType() == "pixels":
            if isValid(s, 0, 10001):
                self.updateWidth(s)
                self.updateColor(ID_RESIZE_HEIGHT)
            else:
                self.updateColor(ID_RESIZE_HEIGHT, "red")
        else:
            if isValid(s, 0.0, 1000.1, isFloat=True):
                self.updateWidth(s)
                self.updateColor(ID_RESIZE_HEIGHT)
            else:
                self.updateColor(ID_RESIZE_HEIGHT, "red")

    def updateHeight(self, s):
        if self.getConstrainAspectFlag():
            w = float(s)
            h = self.calcNewHeight(w)
            self.setH(h)
            self.updateColor(ID_RESIZE_HEIGHT) # set to white

    def updateWidth(self, s):
        if self.getConstrainAspectFlag():
            h = float(s)
            w = self.calcNewWidth(h)
            self.setW(w)
            self.updateColor(ID_RESIZE_WIDTH) # set to white

    def setH(self, h):
        self.update = False
        self.setHeight(h)

    def setW(self, w):
        self.update = False
        self.setWidth(w)

    def calcNewWidth(self, h):
        if self.getType() == "pixels":
            w = int(round(h * self.ratio))
        else:
            w = float(h * self.ratio)
        return w

    def calcNewHeight(self, w):
        if self.getType() == "pixels":
            h = int(round(w / self.ratio))
        else:
            h = float(w / self.ratio)
        return h

    def setRatio(self, r):
        """
        The ratio is used to calculate new image size when aspect ratio
        is constrained.
        """
        self.ratio = r

    def OnUpdateConstrainAspect(self, event):
        """
        Called when the checkbox is clicked to update the height to match
        the width.
        """
        self.updateHeight(self.getWidth())
        # bring the focus back to the Width TextControl
        textCtrl = self.FindWindowById(ID_RESIZE_WIDTH)
        textCtrl.SetFocus()
        textCtrl.SetInsertionPointEnd()

    def OnUpdateType(self, event):
        if self.getType() == "pixels":
            self.setW(self.imageSize[0])
            self.setH(self.imageSize[1])
            self.setRatio(float(self.imageSize[0]) / float(self.imageSize[1]))
        else:
            self.setW('100.0')
            self.setH('100.0')
            self.setRatio(1.0)

    def getConstrainAspectFlag(self):
        a = self.FindWindowById(ID_CONSTRAIN_ASPECT)
        return a.GetValue()
    def setConstrainAspectFlag(self, flag):
        a = self.FindWindowById(ID_CONSTRAIN_ASPECT)
        a.SetValue(flag)
        self.constrainAspectFlag = flag

    def getType(self):
        a = self.FindWindowById(ID_DIM_TYPE)
        return a.GetValue()
    def setType(self, value):
        a = self.FindWindowById(ID_DIM_TYPE)
        a.SetValue(str(value))

    def getWidth(self):
        a = self.FindWindowById(ID_RESIZE_WIDTH)
        return a.GetValue()
    def setWidth(self, value):
        a = self.FindWindowById(ID_RESIZE_WIDTH)
        a.SetValue(str(value))

    def getHeight(self):
        a = self.FindWindowById(ID_RESIZE_HEIGHT)
        return a.GetValue()
    def setHeight(self, value):
        a = self.FindWindowById(ID_RESIZE_HEIGHT)
        a.SetValue(str(value))

    def setImageSize(self, size):
        """ The actual image size. """
        self.imageSize = size

    def updateColor(self, id, color="system"):
        """
        This code changes the color of TextControl to Red or back to system color.
        """
        textCtrl = self.FindWindowById(id)
        if color == "system":
            textCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
        else:
            textCtrl.SetBackgroundColour("red")
            textCtrl.Refresh()

    def allowToContinue(self, s):
        """
        Tests various conditions whether to allow the program to finish
        executing the current function or to exit.
        """
        # the following if-statement is here because when height (or width) is set
        # it triggers an extra event to update this function which screws things up
        continueFlag = True
        if self.update == False:
            self.update = True
            continueFlag = False
        # prevents execution of this function before ratio is set
        if self.ratio == 0.0:
            continueFlag = False
        return continueFlag

    def getResizeImageParams(self):
        params = {}
        params['constrain'] = self.getConstrainAspectFlag()
        params['type'] = self.getType()

        # test for error condition before sending params back
        noError = False
        s = self.getWidth()
        if self.getType() == "pixels":
            if isValid(s, 0, 10000):
                newWidth = int(s)
                noError = True
        else:
            if isValid(s, 0.0, 1000.0, isFloat=True):
                newWidth = float(s)
                noError = True

        s = self.getHeight()
        if self.getType() == "pixels":
            if isValid(s, 0, 10000):
                newHeight = int(s)
                noError = True
        else:
            if isValid(s, 0.0, 1000.0, isFloat=True):
                newHeight = float(s)
                noError = True

        params['newWidth'] = newWidth
        params['newHeight'] = newHeight

        if noError:
            return params
        else:
            return {}

#---------------- IP Sequence dialog box -----------------------------

class ipSequenceDialog(wx.Dialog):
    """
    Note: self.t holds only the name (string) of the operation whereas
    the self.ipSequenceList holds the entire reference to the operation
    """
    def __init__(self, title, params):
        wx.Dialog.__init__(self, frame, -1, title)

        self.update(params)

        box = wx.BoxSizer(wx.VERTICAL)
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        # Add the panel to which widgets will be added
        panel = wx.Panel(self,-1,size=(298,234)) # panel must big enough to hold all widgets
        box1.Add(panel,0,wx.ALL,5)
        box.Add(box1,0,wx.ALL,2)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        box.Fit(self)
        box.SetSizeHints(self)
        # Add stuff to the panel here

        # initialize list box as blank unless some operations have already been selected
        startOp = []
        n = len(self.ipSequenceList)
        for pos in range(n):
            ip = self.ipSequenceList[pos]
            name = ip.name
            startOp.append(name)
        self.t = wx.ListBox(panel, 10, wx.Point(0,0), wx.Size(200,230), startOp, wx.LB_SINGLE)

        if n > 0:
            self.t.SetSelection(n-1) # hightlight the last item in the list

        w = 86 # button width
        h = 25  # button height
        g = 1   # gap between buttons
        x = 208 # x button start

        self.buttonAdd = wx.Button(panel,13, "Add",wx.Point(x,0),wx.Size(w,h))
        wx.EVT_BUTTON(panel,13,self.OnAdd)
        y = h+g  # next button start
        self.buttonDelete = wx.Button(panel,14, "Delete",wx.Point(x, y),wx.Size(w,h))
        wx.EVT_BUTTON(panel,14,self.OnDelete)
        y = y + h + g + 6
        self.buttonEdit = wx.Button(panel,15, "Edit",wx.Point(x, y),wx.Size(w,h))
        wx.EVT_BUTTON(panel,15,self.OnEdit)
        y = y + h + g + 6
        self.buttonMoveUp = wx.Button(panel,16, "Move Up",wx.Point(x, y),wx.Size(w,h))
        wx.EVT_BUTTON(panel,16,self.OnMoveUp)
        y = y + h + g
        self.buttonMoveDown = wx.Button(panel,17, "Move Down",wx.Point(x, y),wx.Size(w,h))
        wx.EVT_BUTTON(panel,17,self.OnMoveDown)
        y = y + h + g + 6
        self.buttonLoad = wx.Button(panel,18, "Load",wx.Point(x, y),wx.Size(w,h))
        wx.EVT_BUTTON(panel,18,self.OnLoad)
        y = y + h + g
        self.buttonSave = wx.Button(panel,19, "Save",wx.Point(x, y),wx.Size(w,h))
        wx.EVT_BUTTON(panel,19,self.OnSave)
        y = y + h + g + 6
        okButton = wx.Button(panel,wx.ID_OK,"OK",wx.Point(x, y),wx.Size(w,h))
        okButton.SetDefault()

        wx.EVT_LISTBOX(self, 10, self.EvtListBox)

        self.updateDialogParameters()

###### Sequence List functions

    def getSeqList(self):
        return self.ipSequenceList

    def ipSeqInsert(self, pos, op):
        'insert item into the ipSequenceList'
        self.ipSequenceList.insert(pos, op)

    def getSeqItem(self, pos):
        return self.ipSequenceList[pos]

    def ipSeqDelete(self, pos):
        del self.ipSequenceList[pos]

    def getSeqListLength(self):
        return len(self.ipSequenceList)

##### end of Sequence List functions

    def update(self, params):
        self.ipSequenceList = params['ipSequenceList']
        self.isThresholdTrackingAoi = params['isThresholdTrackingAoi']

    def EvtListBox(self, event):
        'executed when selected ip-operation is changed be clicking on it'
        self.updateDialogParameters() # gray out some buttons

    def updateDialogParameters(self):
        'gray-out appropriate buttons'
        totalNumber = self.t.GetCount() # previously was self.t.Number()
        currSelected = self.t.GetSelection()
        thTrackingAoi = self.isThresholdTrackingAoi
        if totalNumber == 0:
            self.buttonDelete.Enable(False)
            self.buttonEdit.Enable(False)
            self.buttonMoveUp.Enable(False)
            self.buttonMoveDown.Enable(False)
            self.buttonSave.Enable(False)
        else:
            self.buttonSave.Enable(True)
            self.buttonEdit.Enable(True)
            if currSelected == totalNumber-1 and thTrackingAoi:
                self.buttonDelete.Enable(False)
            else:
                self.buttonDelete.Enable(True)

            if currSelected == 0 or (thTrackingAoi and currSelected == totalNumber-1):
                self.buttonMoveUp.Enable(False)
            else:
                self.buttonMoveUp.Enable(True)

            if currSelected == totalNumber-1:
                self.buttonMoveDown.Enable(False)
            else:
                if currSelected < totalNumber-1:
                    if currSelected == totalNumber-2 and thTrackingAoi:
                        self.buttonMoveDown.Enable(False)
                    else:
                        self.buttonMoveDown.Enable(True)
                else:
                    self.buttonMoveDown.Enable(True)

    def OnAdd(self, event):
        d = AddIpOperation('Add Ip Operation')
        d.Centre()
        val = d.ShowModal()
        if val == wx.ID_OK:
            op = d.getIpOperation()
            if self.isThresholdTrackingAoi:
                #totalNumber = self.t.Number()
                totalNumber = self.t.GetCount()
                currSelected = self.t.GetSelection()
                if currSelected == totalNumber-1:
                    self.addBeforeSelected(op)
                else:
                    self.addAfterSelected(op)
            else:
                self.addAfterSelected(op)
        d.Destroy()
        self.updateDialogParameters()

    def addAfterSelected(self, op):
        """called from OnAdd - adds the selection after the
        currently selected operation
        """
        pos = self.t.GetSelection()
        # update dipSeqList
        self.ipSeqInsert(pos+1, op) # update ipSequenceList
        # update the list box
        ip = self.getSeqItem(pos+1)
        self.insertIntoListBox(pos+1, ip.name)

    def addBeforeSelected(self, op):
        """called from OnAdd - adds the selection after the currently
        selected operation
        """
        pos = self.t.GetSelection()
        # update dipSeqList
        self.ipSeqInsert(pos, op) # update ipSequenceList
        # update the list box
        ip = self.getSeqItem(pos)
        self.insertIntoListBox(pos, ip.name)

    def OnDelete(self, event):
        'remove the selected operation'
        pos = self.t.GetSelection() # position of highlighted item
        self.deleteItem(pos)
        self.updateDialogParameters()

    def OnEdit(self, event):
        pos = self.t.GetSelection()
        if pos >= 0:
            ip = self.getSeqItem(pos)
            ok = ip.showDialog()
            if ok:
                # update the list box (ipSequenceList does not change)
                ip = self.getSeqItem(pos)
                self.t.Delete(pos)
                self.insertIntoListBox(pos, ip.name)
                self.updateDialogParameters()

    def OnMoveUp(self, event):
        'moves the selected operation up'
        pos = self.t.GetSelection()
        # update the list box
        s = self.t.GetString(pos)
        self.t.Delete(pos)
        self.insertIntoListBox(pos-1, s)
        # update ipSequenceList
        ip = self.getSeqItem(pos)
        self.ipSeqDelete(pos)
        self.ipSeqInsert(pos-1, ip)
        self.updateDialogParameters()

    def OnMoveDown(self, event):
        'moves the selected operation down'
        pos = self.t.GetSelection()
        # update the list box
        s = self.t.GetString(pos)
        self.t.Delete(pos)
        self.insertIntoListBox(pos+1, s)
        # update ipSequenceList
        ip = self.getSeqItem(pos)
        self.ipSeqDelete(pos)
        self.ipSeqInsert(pos+1, ip)
        self.updateDialogParameters()

    def insertIntoListBox(self, pos, s):
        opName = []
        opName.append(s)
        self.t.InsertItems(opName, pos)
        self.t.SetSelection(pos) # hightlight

    def OnSave(self, event):
        'saves the list of operations to a file'
        fd = wx.FileDialog(self, "Save IP Sequence", "", "*.seq",
                "Seq files (*.seq)|*.seq", wx.SAVE)
        if fd.ShowModal() == wx.ID_OK:
            if os.path.isfile(fd.GetPath()):
                message = 'The file already exists - do you want to overwrite it?'
                overwriteFlag = YesNoDialog(message)
                if overwriteFlag:
                    self.saveIpSequenceFile(fd.GetPath())
            else:
                self.saveIpSequenceFile(fd.GetPath())
        fd.Destroy()

    def saveIpSequenceFile(self, filename):
        'save ip sequence to disk - use pickle to save it'
        seqParams = []
        n = self.getSeqListLength()
        for pos in range(n):
            ip = self.getSeqItem(pos)
            opSpecs = ip.getParams()
            seqParams.append(opSpecs)

        f = open(filename, 'wb')
        pickle.dump(seqParams, f)
        f.close()

    def OnLoad(self, event):
        'Load the list of image processing operations from a file'
        fd = wx.FileDialog(self, "Load IP Sequence", "", "*.seq",
                "Seq files (*.seq)|*.seq", wx.OPEN)
        if fd.ShowModal() == wx.ID_OK:
            if os.path.isfile(fd.GetPath()):
                seqParams = self.loadIpSequenceFile(fd.GetPath())   # load sequence parameters
                self.deleteAll()                                    # delete previous sequence
                self.instantiateSequenceItems(seqParams)            # instantiate new sequence
                self.updateDialogParameters()                       # enable/disable buttons
            else:
                messageDialog('file does not exist')
        fd.Destroy()

    def instantiateSequenceItems(self, seqParams):
        """Takes the list of params passed in (each being a dictionary) and
        from it instantiates the command class and then sets the parameters
        as they were.
        """
        n = len(seqParams)
        for i in range(n):
            params = seqParams[i]
            ip = Spotlight.instantiateIpCommand(params)
            ip.setParams(params)  # set up the class's parameters
            self.addAfterSelected(ip)  # insert into sequence box

    def loadIpSequenceFile(self, filename):
        'load from disk - use pickle to load it'
        f = open(filename, 'rb')
        seqParams = pickle.load(f)
        f.close()
        return seqParams

    def deleteAll(self):
        'delete the whole ip sequence'
        n = self.t.GetCount()
        if n > 0:
            for i in range(n):
                self.deleteItem(0)

    def deleteItem(self, pos):
        """
        delete the item from both the list box (displays only names)
        and ipSequenceList (instances)
        """
        # update the list box
        self.t.Delete(pos)
        n = self.t.GetCount()
        if n > 0:
            if n-1 >= pos:
                self.t.SetSelection(pos)
            else:
                self.t.SetSelection(pos-1)

        # update ipSequenceList
        self.ipSeqDelete(pos)

#---------------- AddIpOperation dialog box -----------------------------

class AddIpOperation(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)
        box = wx.BoxSizer(wx.VERTICAL)
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        # Add the panel to which widgets will be added
        #panel = wx.Panel(self,-1,size=(132, 346)) # panel must big enough
        panel = wx.Panel(self,-1,size=(132, 375)) # panel must big enough
        box1.Add(panel,0,wx.ALL,5)
        box.Add(box1,0,wx.ALL,2)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        box.Fit(self)
        box.SetSizeHints(self)
        # Add stuff to the panel here

        h = 26  # button height
        w = 130 # button width
        g = 3   # gap between buttons

        wx.Button(panel,13, "Threshold",wx.Point(1,0),wx.Size(w,h))
        wx.EVT_BUTTON(panel,13,self.OnThreshold)
        wx.Button(panel,14, "Filtering",wx.Point(1, h+g),wx.Size(w,h))
        wx.EVT_BUTTON(panel,14,self.OnFiltering)
        wx.Button(panel,15, "Arithmetic",wx.Point(1, 2*h+2*g),wx.Size(w,h))
        wx.EVT_BUTTON(panel,15,self.OnArithmetic)
        wx.Button(panel,16, "Contrast",wx.Point(1, 3*h+3*g),wx.Size(w,h))
        wx.EVT_BUTTON(panel,16,self.OnContrast)
        wx.Button(panel,17, "Morphological",wx.Point(1, 4*h+4*g),wx.Size(w,h))
        wx.EVT_BUTTON(panel,17,self.OnMorphological)
        wx.Button(panel,18, "Extract Plane",wx.Point(1, 5*h+5*g),wx.Size(w,h))
        wx.EVT_BUTTON(panel,18,self.OnExtractPlane)
        wx.Button(panel,19, "Geometric",wx.Point(1, 6*h+6*g),wx.Size(w,h))
        wx.EVT_BUTTON(panel,19,self.OnGeometric)
        wx.Button(panel,20, "Statistics",wx.Point(1, 7*h+7*g),wx.Size(w,h))
        wx.EVT_BUTTON(panel,20,self.OnStatistics)
        wx.Button(panel,21, "Save Aoi",wx.Point(1, 8*h+8*g),wx.Size(w,h))
        wx.EVT_BUTTON(panel,21,self.OnSaveAoi)
        wx.Button(panel,22, "Extract Field",wx.Point(1, 9*h+9*g),wx.Size(w,h))
        wx.EVT_BUTTON(panel,22,self.OnExtractField)
        wx.Button(panel,23, "Pseudocolor",wx.Point(1, 10*h+10*g),wx.Size(w,h))
        wx.EVT_BUTTON(panel,23,self.OnPseudocolor)
        wx.Button(panel,24, "Convert Image",wx.Point(1, 11*h+11*g),wx.Size(w,h))
        wx.EVT_BUTTON(panel,24,self.OnConvertImage)
        wx.Button(panel,25, "Resize Image",wx.Point(1, 12*h+12*g),wx.Size(w,h))
        wx.EVT_BUTTON(panel,25,self.OnResizeImage)
        self.ipOperation = None

    def getIpOperation(self):
        return self.ipOperation

    def OnThreshold(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'Threshold'})
        self.EndModal(wx.ID_OK)

    def OnFiltering(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'Filter'})
        self.EndModal(wx.ID_OK)

    def OnArithmetic(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'Arithmetic'})
        self.EndModal(wx.ID_OK)

    def OnContrast(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'Contrast'})
        self.EndModal(wx.ID_OK)

    def OnMorphological(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'Morphological'})
        self.EndModal(wx.ID_OK)

    def OnExtractPlane(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'ExtractPlane'})
        self.EndModal(wx.ID_OK)

    def OnGeometric(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'Geometric'})
        self.EndModal(wx.ID_OK)

    def OnSaveAoi(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'SaveAoi'})
        self.EndModal(wx.ID_OK)

    def OnPseudocolor(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'Pseudocolor'})
        self.EndModal(wx.ID_OK)

    def OnResizeImage(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'ResizeImage'})
        self.EndModal(wx.ID_OK)

    def OnExtractField(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'ExtractField'})
        self.EndModal(wx.ID_OK)

    def OnStatistics(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'Statistics'})
        self.EndModal(wx.ID_OK)

    def OnConvertImage(self, event):
        self.ipOperation = Spotlight.instantiateIpCommand({'name': 'ConvertImage'})
        self.EndModal(wx.ID_OK)

##--------------------- Class LineProfileDialog ---------------------------

class LineProfileDialog(wx.Dialog):
    def __init__(self, parentAoi, frame, title):
        wx.Dialog.__init__(self, frame, -1, title, size=(370, 340))
        self.parentAoi = parentAoi
        self.frame = frame

        ####-- Using wxDesigner

        #LineProfileTestDialogFunc(self, True)
        LineProfileDialogFunc(self, True)
        self.CentreOnParent()

        self.graphPanel = self.FindWindowById(ID_GRAPH_PANEL)
        self.graphPanel.SetBackgroundColour(wx.WHITE)
        self.spin = self.FindWindowById(ID_L_THICKNESS)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.OnRed, id=ID_RED_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnGreen, id=ID_GREEN_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnBlue, id=ID_BLUE_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnLuminance, id=ID_LUMINANCE_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnRgb, id=ID_RGB_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnHue, id=ID_HUE_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnSaveProfile, id=ID_SAVE_BUTTON)
        self.Bind(wx.EVT_SPINCTRL, self.OnLineThickness, id=ID_L_THICKNESS)
        self.Bind(wx.EVT_TEXT, self.OnLineThickness, id=ID_L_THICKNESS)

        self.finishedPainting = True
        self.drawPen = wx.Pen(wx.NamedColour('BLACK'))
        self.colorPlaneSelect = LUMINANCE
        self.profile = None
        self.plotWidth = 320
        self.plotHeight = 200
        self.xoffset = 40  # distance between left side of panel and y-axis
        self.yoffset = 0   # distance between top side of panel and top of y-axis

        # use the Red button to get the font
        button = self.FindWindowById(ID_RED_BUTTON)
        self.font = button.GetFont()

        # gray out the text controls
        self.FindWindowById(ID_PIXEL_NUMBER).Enable(False)
        self.FindWindowById(ID_LINE_LENGTH).Enable(False)

    def OnLineThickness(self, event):
        """ Updates the thickness value when spin control is clicked or when
        the text is manually typed in.
        """
        t = self.spin.GetValue()
        if t < self.spin.GetMin():
            self.spin.SetValue(self.spin.GetMin()) # min of allowable range
        if t > self.spin.GetMax():
            self.spin.SetValue(self.spin.GetMax()) # max of allowable range
        self.parentAoi.changeLineThickness(self.spin.GetValue())

    def getLineLengthPixels(self):
        a = self.FindWindowById(ID_PIXEL_NUMBER)
        return a.GetValue()
    def setLineLengthPixels(self, v):
        a = self.FindWindowById(ID_PIXEL_NUMBER)
        a.SetValue(str(v))

    def getLineLengthEuclidean(self):
        a = self.FindWindowById(ID_LINE_LENGTH)
        return a.GetValue()
    def setLineLengthEuclidean(self, v):
        a = self.FindWindowById(ID_LINE_LENGTH)
        d = v * Spotlight.pixelScale   #- Euclidian distance
        s = '%.2f' % d
        a.SetValue(s)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)  #- must get wx.PaintDC (on MSW)
        self.postProfile()

    def postProfile(self):
        """ Post the event (request to repaint) and return to updateLineProfile (in the
        LineAoi class). The if statement tests whether the OnPaint method is done
        repainting before posting another request. This will call refreshProfile below.
        """
        if self.finishedPainting == True:
            wx.CallAfter(self.refreshProfile)

    def refreshProfile(self):
        if self.finishedPainting == True:
            self.finishedPainting = False
            self.profile = self.parentAoi.getP(self.colorPlaneSelect)
            self.plotProfile = self.calcPlotProfile()

            # draw to a double-buffered dc
            if sys.platform == 'darwin':
                dc = wx.ClientDC(self.graphPanel)
            else:
                w, h = self.graphPanel.GetSizeTuple()
                dc = wx.BufferedDC(wx.ClientDC(self.graphPanel), wx.EmptyBitmap(w, h))
            dc.SetFont(self.font)
            dc.Clear()
            self.drawProfile(dc)
            dc.SetPen(wx.Pen(wx.NamedColour('BLACK'))) # draw axis info in black
            self.drawAxes(dc)
            self.drawMinMaxLabels(dc)
            self.drawAxisLabels(dc)

            self.setLineLengthPixels(len(self.plotProfile))  # number of pixels
            lineLength = self.parentAoi.getLineLength()
            self.setLineLengthEuclidean(lineLength)

            while wx.GetApp().Pending():
                wx.GetApp().Dispatch()

            self.finishedPainting = True

    def drawProfile(self, dc):
        'Draws the line in the graphPanel'
        if self.colorPlaneSelect != RGB:
            dc.SetPen(self.drawPen)
            dc.DrawLines(self.plotProfile)    # draw polyline
        else:
            r, g, b = self.plotProfile
            dc.SetPen(wx.Pen(wx.NamedColour('RED')))
            dc.DrawLines(r)
            dc.SetPen(wx.Pen(wx.NamedColour('GREEN')))
            dc.DrawLines(g)
            dc.SetPen(wx.Pen(wx.NamedColour('BLUE')))
            dc.DrawLines(b)

    def drawAxes(self, dc):
        x1 = self.xoffset
        y1 = self.yoffset
        x2 = self.xoffset + self.plotWidth  # right side of graph area
        y2 = self.yoffset + self.plotHeight  # bottom of graph area (location of x-axis)
        dc.DrawLine(x1, y2-1, x2, y2-1)  # x-axis
        dc.DrawLine(x1, y1, x1, y2-1)  # y-axis

    def drawMinMaxLabels(self, dc):
        minp, maxp, meanp = self.getProfileStatistics()
        txt1 = "min: " + minp
        txt2 = "max: " + maxp
        txt3 = "mean: " + meanp

        if sys.platform == 'win32':
            dc.DrawText(txt1, 80, 204)
            dc.DrawText(txt2, 170, 204)
            dc.DrawText(txt3, 265, 204)
        else:  ## tentative on Mac - double check
            dc.DrawText(txt1, 60, 204)
            dc.DrawText(txt2, 155, 204)
            dc.DrawText(txt3, 250, 204)

    def drawAxisLabels(self, dc):
        o = wx.Point(self.xoffset, self.plotHeight)  # axes origin
        ystep = self.plotHeight / 8  # 8 tick marks

        # draw y-axis tickmarks
        for i in range(1, 9):  # 8 tick marks
            ys = ystep * i
            xstart = o.x-3
            ystart = o.y-ys
            xend = o.x
            yend = o.y-ys
            dc.DrawLine(xstart, ystart, xend, yend)

        # draw labels
        axisText = self.getAxisText()
        for i in range(9):
            te = dc.GetTextExtent(axisText[i])
            x = (self.xoffset-5) - te[0] # make it right justified
            y = o.y - ystep * i
            if i < 8:
                dc.DrawText(axisText[i], x, y-5)
            else:
                dc.DrawText(axisText[i], x, y)  # last label ('255')

    def getAxisText(self):
        isNormalized = Spotlight.pOptions.programOptions['pixelValues']
        axisText = []
        if self.colorPlaneSelect == HUE or isNormalized == 0:
            axisText.append('0.0')
            axisText.append('.125')
            axisText.append('.250')
            axisText.append('.375')
            axisText.append('.500')
            axisText.append('.625')
            axisText.append('.759')
            axisText.append('.875')
            axisText.append('1.0')
        else:
            axisText.append('0')
            axisText.append('32')
            axisText.append('64')
            axisText.append('96')
            axisText.append('128')
            axisText.append('160')
            axisText.append('192')
            axisText.append('224')
            axisText.append('255')
        return axisText

    def calcPlotProfile(self):
        if self.colorPlaneSelect != RGB:
            p = self.scaleProfile(self.profile)
            return p
        else:
            r = []
            g = []
            b = []
            for i in range(len(self.profile)):
                r.append(self.profile[i][0])
                g.append(self.profile[i][1])
                b.append(self.profile[i][2])
            r = self.scaleProfile(r)
            g = self.scaleProfile(g)
            b = self.scaleProfile(b)
            return (r, g, b)

    def scaleProfile(self, prof):
        prof = self.correctProfile(prof)
        num = len(prof)
        hf = float(self.plotHeight)
        xy = []
        p = []
        for i in range(num):
            p.append(int(prof[i] * 256.0))

        for i in range(num):
            if p[i] < 0: p[i] = 0
            if p[i] > 255: p[i] = 255
            x = float(i) / (num-1)*self.plotWidth
            nn = hf * float(p[i]) / 255.0
            y = self.plotHeight - int(nn)
            x = x + 40
            y = y - 2
            c = self.validateCoordinates(x, y)
            xy.append((int(c[0]), int(c[1])))
        return xy

    def correctProfile(self, p):
        """
        This is to prevent crashes when displaying an RGB lines (button in
        Line Profile dialog) while in fast-forward and somebody clicks L button.
        The profile is momentarily an RGB when it should be grayscale and/or
        vice versa.
        """
        num = len(p)
        if self.colorPlaneSelect != RGB:
            # displaying a RGB line while in fastforward and L button is clicked
            try:
                aa = float(p[0]) # for RGB line this value will be a tuple
            except TypeError:
                ptemp = []
                for i in range(num):
                    ptemp.append(p[i][0]) # copy only the red value
                p = []
                p = ptemp[:]
        return p

    def validateCoordinates(self, x, y):
        """Make it fit on the graph. Note: the y is inverted (y=0 is on top)"""
        width, height = self.graphPanel.GetSizeTuple()
        if x < 0: x = 0
        if x > width: x = width
        if y < 0: y = 0
        if y > height-2: y = height-2  # fudge factor to see the line (on bottom)
        return (x,y)

    def getProfileStatistics(self):
        ex = self.calcLineStatistics()
        if self.colorPlaneSelect == HUE: # don't normalize hue
            minp = str(ex[0])
            maxp = str(ex[1])
            meanp = str(ex[2])
        else:
            minp = str(normalizedToScaled(ex[0]))
            maxp = str(normalizedToScaled(ex[1]))
            meanp = str(normalizedToScaled(ex[2]))

        if Spotlight.pOptions.programOptions['pixelValues'] == 0 or self.colorPlaneSelect == HUE:
            minp = string.ljust(minp, 7)
            if len(minp) > 7:
                minp = minp[0:7]  # limit to 7 chars (5 chars right of decimal point)
            maxp = string.ljust(maxp, 7)
            if len(maxp) > 7:
                maxp = maxp[0:7]  # limit to 7 chars
            meanp = string.ljust(meanp, 7)
            if len(meanp) > 7:
                meanp = meanp[0:7]  # limit to 7 chars
        return (minp, maxp, meanp)

    def calcLineStatistics(self):
        """ Returns min and max and mean pixel values under the line."""
        if self.colorPlaneSelect != RGB:
            # Note: the self.profile values go 0-1.0 so must scale (in dialog)
            p = []
            for i in range(len(self.profile)):
                p.append(self.profile[i])
        else:   # RGB line profile (all 3 curves) displays no min,max,mean
            p = []
            for i in range(2):
                p.append(0)

        # calc min, max, and mean of the line profile
        n = len(p)
        minp = min(p)
        maxp = max(p)
        meanp = 0.0

        for i in range(0, n):
            meanp = meanp + p[i]

        nn = max(n, 1)  # prevent division by 0
        meanp = meanp/nn
        return (minp, maxp, meanp)

    def OnCancel(self, event):
        """ Post the event to close dialog and delete aoi. Then get out."""
        self.parentAoi.closeDialog()
        wx.CallAfter(self.frame.deleteAoiFromOnCancel)

    def OnRed(self, event):
        self.colorPlaneSelect = RED
        self.drawPen = wx.Pen(wx.NamedColour('RED'))
        self.SetTitle('Line profile: Red')
        self.refreshProfile()
    def OnGreen(self, event):
        self.colorPlaneSelect = GREEN
        self.drawPen = wx.Pen(wx.NamedColour('GREEN'))
        self.SetTitle('Line profile: Green')
        self.refreshProfile()
    def OnBlue(self, event):
        self.colorPlaneSelect = BLUE
        self.drawPen = wx.Pen(wx.NamedColour('BLUE'))
        self.SetTitle('Line profile: Blue')
        self.refreshProfile()
    def OnLuminance(self, event):
        self.colorPlaneSelect = LUMINANCE
        self.drawPen = wx.Pen(wx.NamedColour('BLACK'))
        self.SetTitle('Line profile: Luminance')
        self.refreshProfile()
    def OnRgb(self, event):
        self.colorPlaneSelect = RGB
        self.drawPen = wx.Pen(wx.NamedColour('BLACK'))
        self.SetTitle('Line profile: RGB')
        self.refreshProfile()
    def OnHue(self, event):
        self.colorPlaneSelect = HUE
        self.drawPen = wx.Pen(wx.NamedColour('PURPLE'))
        self.SetTitle('Line profile: Hue')
        self.refreshProfile()

    def OnSaveProfile(self, event):
        """ Save the line profile to disk. """
        self.profileXY = self.parentAoi.getLineProfileXY()  #### <<<<---------
        thickness = self.spin.GetValue()
        dispType = Spotlight.pOptions.programOptions['pixelValues']
        fd = wx.FileDialog(self, "Save Profile", "", "*.txt",
                    "All files (*.*)|*.*|Data files (*.txt)|*.txt", wx.SAVE)
        if fd.ShowModal() == wx.ID_OK:
            f = open(fd.GetPath(), 'a')
            if self.colorPlaneSelect != RGB: # one line profile (instead RGB line profile)
                p = []
                if self.colorPlaneSelect == RED:
                    s = 'Red Line Profile'
                    colorPix = self.profileXY
                    for i in range(len(colorPix)):
                        colorpxy = colorPix[i]
                        cpix = colorpxy[0]
                        x = colorpxy[1]
                        y = colorpxy[2]
                        p.append((cpix[0],x,y))
                elif self.colorPlaneSelect == GREEN:
                    s = 'Green Line Profile'
                    colorPix = self.profileXY
                    for i in range(len(colorPix)):
                        colorpxy = colorPix[i]
                        cpix = colorpxy[0]
                        x = colorpxy[1]
                        y = colorpxy[2]
                        p.append((cpix[1],x,y))
                elif self.colorPlaneSelect == BLUE:
                    s = 'Blue Line Profile'
                    colorPix = self.profileXY
                    for i in range(len(colorPix)):
                        colorpxy = colorPix[i]
                        cpix = colorpxy[0]
                        x = colorpxy[1]
                        y = colorpxy[2]
                        p.append((cpix[2],x,y))
                elif self.colorPlaneSelect == LUMINANCE:
                    s = 'Luminance Line Profile'
                    colorPix = self.profileXY
                    for i in range(len(colorPix)):
                        colorpxy = colorPix[i]
                        cpix = colorpxy[0]
                        x = colorpxy[1]
                        y = colorpxy[2]
                        lumin = (cpix[0] + cpix[1] + cpix[2]) / 3
                        p.append((lumin,x,y))
                elif self.colorPlaneSelect == HUE:
                    s = 'Hue Line Profile'
                    colorPix = self.profileXY
                    for i in range(len(colorPix)):
                        colorpxy = colorPix[i]
                        cpix = colorpxy[0]
                        x = colorpxy[1]
                        y = colorpxy[2]
                        hue, sat, value = self.parentAoi.Rgb2Hsv((cpix[0], cpix[1], cpix[2]))
                        p.append((hue,x,y))
                else:
                    raise 'in SaveProfile - no such colorPlaneSelect value'

                s2 = 'line thickness:  %s' % thickness
                s3 = 'column format:  index, x, y, value'

                smin, smax, smean = self.getProfileStatistics()

                smin = 'min: ' + smin + '  '
                smax = 'max: ' + smax + '  '
                smean = 'mean: ' + smean

                f.write('\n'+s)
                f.write('\n'+s2)
                f.write('\n' + smin + smax + smean)
                f.write('\n'+s3+'\n'+'\n')

                for i in range(len(p)):
                    pxy = p[i]
                    pix = pxy[0]
                    x = pxy[1]
                    y = pxy[2]
                    if dispType == 0 or self.colorPlaneSelect == HUE:
                        s = '%.6f' % pix  # 4 digits to right of decimal point
                    else:
                        s = '%3d' % int(pix * 255.0)
                    f.write(str(i)+' '+str(x)+' '+str(y)+' '+s+'\n')
            else:  # RGB line profile
                p = self.profileXY
                s = 'RGB Line Profile'
                s2 = 'line thickness:  %s' % thickness
                s3 = 'column format:  index, x, y, r, g, b'
                f.write('\n'+s)
                f.write('\n'+s2)
                f.write('\n' + 'line statistics: not available for RGB line profile')
                f.write('\n'+s3+'\n'+'\n')
                for i in range(len(p)):
                    cpxy = p[i]
                    cpix = cpxy[0]
                    if dispType == 0:
                        r = '%.6f' % cpix[0] # normalized
                        g = '%.6f' % cpix[1]
                        b = '%.6f' % cpix[2]
                    else:
                        r = '%3d' % int(cpix[0] * 255.0) # actual
                        g = '%3d' % int(cpix[1] * 255.0)
                        b = '%3d' % int(cpix[2] * 255.0)
                    x = cpxy[1]
                    y = cpxy[2]
                    f.write(str(i)+' '+str(x)+' '+str(y)+' '+ r +' '+ g +' '+ b +'\n')
            f.close()
        fd.Destroy()

#--------------- Class HistogramDialog ----------------------------------


class HistogramDialog(wx.Dialog):
    def __init__(self, title, params, changeNotificationFunction):
        wx.Dialog.__init__(self, frame, -1, title,size=(400, 340))

        ####-- Using wxDesigner
        HistogramNewDialogFunc(self, True)
        self.CentreOnParent()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

        self.Bind(wx.EVT_BUTTON, self.OnRed, id=ID_RED_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnGreen, id=ID_GREEN_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnBlue, id=ID_BLUE_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.OnLuminance, id=ID_LUMINANCE_BUTTON)
        self.Bind(wx.EVT_BUTTON, self.SaveHistogram, id=ID_SAVE_BUTTON)

        self.graphPanel = self.FindWindowById(ID_GRAPH_PANEL)
        self.graphPanel.SetBackgroundColour(wx.WHITE)

        self.notify = changeNotificationFunction
        self.finishedPainting = True
        self.drawPen = wx.Pen(wx.NamedColour('BLACK'))

        self.plotWidth = 320
        self.plotHeight = 200
        ## Note: the axes can be moved around by changing the offsets
        self.xoffset = 55  # distance between left side of panel and y-axis
        self.yoffset = 8 # distance between top side of panel and top of y-axis

        # get the font off the red button
        button = self.FindWindowById(ID_RED_BUTTON)
        self.font = button.GetFont()

        self.update(params) # after everything else

    def update(self, params):
        'stuff that comes here from the AOI'
        if params != {}:
            if params.has_key('colorPlane'):       # editable parameter
                self.colorPlaneSelect = params['colorPlane']
            if params.has_key('histogram'):
                self.histogram = params['histogram']
            if params.has_key('statistics'):
                self.statistics = params['statistics']

            if self.finishedPainting == True:
                if params.has_key('updateType'):
                    if params['updateType'] == 0:   # only when initializes dialog
                        self.Refresh(True)
                    elif params['updateType'] == 1:  # only histogram during mouse move
                        self.postHistogram()
                    elif params['updateType'] == 2:  # histogram and stats
                        self.postStatistics()
                        self.postHistogram()
                        pass
                    else:       # triggered when left key up
                        self.postStatistics()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.postHistogram()

    def postHistogram(self):
        if self.finishedPainting == True:
            self.finishedPainting = False
            self.notify({'histogram': []})
            wx.CallAfter(self.refreshHistogram)

    def refreshHistogram(self):
        self.plotHistogram = self.calcHistogram()

        # draw to a double-buffered dc
        if sys.platform == 'darwin':
            dc = wx.ClientDC(self.graphPanel)
        else:
            w, h = self.graphPanel.GetSizeTuple()
            dc = wx.BufferedDC(wx.ClientDC(self.graphPanel), wx.EmptyBitmap(w, h))
        dc.SetFont(self.font)
        dc.Clear()
        self.drawHistogram(dc)
        dc.SetPen(wx.Pen(wx.NamedColour('BLACK'))) # draw axis info in black
        self.drawAxes(dc)
        self.drawXAxisLabels(dc)
        self.drawYAxisLabels(dc)

        while wx.GetApp().Pending():
            wx.GetApp().Dispatch()

        self.finishedPainting = True

    def postStatistics(self):
        if self.finishedPainting == True:
            self.finishedPainting = False
            self.notify({'updateStats': True})
            wx.CallAfter(self.refreshHistogram)

    def drawHistogram(self, dc):
        'Draws the histogram in the graphPanel'
        dc.SetPen(self.drawPen)
        dc.DrawLines(self.plotHistogram)    # draw polyline

    def drawAxes(self, dc):
        x1 = self.xoffset
        y1 = self.yoffset
        x2 = self.xoffset + self.plotWidth  # right side of graph area
        y2 = self.yoffset + self.plotHeight  # bottom of graph area (location of x-axis)
        dc.DrawLine(x1, y2, x2, y2)  # x-axis
        dc.DrawLine(x1, y1, x1, y2)  # y-axis

    def calcHistogram(self):
        p = self.histogram

        maxh = 0
        for i in range(0,256):
            if maxh < p[i]: maxh = p[i]
        if maxh == 0:
            maxh = 1
        self.maxHist = maxh

        hf = float(self.plotHeight)
        xy = []
        num = len(p)
        for i in range(num):
            x = float(i) / 256 * self.plotWidth
            nn = hf * float(p[i]) / float(maxh)
            y = self.plotHeight - int(nn)
            x = x + self.xoffset + 1
            y = y + self.yoffset - 1
            c = self.validateCoordinates(x, y)
            xy.append(wx.Point(int(c[0]), int(c[1])))
        return xy

    def drawXAxisLabels(self, dc):
        o = wx.Point(self.xoffset, self.plotHeight+self.yoffset)  # axes origin
        xstep = self.plotWidth / 8  # 8 tick marks

        # draw x-axis tickmarks
        for i in range(1, 9):  # 8 tick marks
            xs = xstep * i
            xstart = o.x+xs
            ystart = o.y
            xend = o.x+xs
            yend = o.y+5
            dc.DrawLine(xstart, ystart, xend, yend)

        # draw x-axis labels
        axisText = self.getXAxisText()
        for i in range(9):
            te = dc.GetTextExtent(axisText[i])
            if i < 8:
                x = o.x + xstep*i - int(te[0]/2)
            else:
                #x = o.x + xstep*i - int(te[0]) # position of last label ('255')
                x = o.x + xstep*i - int(2*te[0]/3)
            dc.DrawText(axisText[i], x, o.y+int(te[1]/2))

        self.refreshStatistics(dc, int(te[1]))

    def refreshStatistics(self, dc, yoffset):
        min_s, max_s, mean_s, stdev_s = self.statistics
        minh = actualToScaled(min_s)
        maxh = actualToScaled(max_s)
        mean = actualToScaled(mean_s)
        stdev = actualToScaled(stdev_s)

        if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
            sminh = '%.3f' % minh
            smaxh = '%.3f' % maxh
            smean = '%.3f' % mean
            sstdev = '%.5f' % stdev
        else:
            sminh = str(minh)
            smaxh = str(maxh)
            smean = str(mean)
            sstdev = '%.4f' % stdev

        o = wx.Point(self.xoffset, self.plotHeight+self.yoffset)  # axes origin
        te = dc.GetTextExtent(sminh)
        y = o.y + int(te[1]) + int(yoffset/2) + 5
        if sys.platform == 'darwin':
            dc.DrawText('min: '+sminh, o.x-30, y)
            dc.DrawText('max: '+smaxh, o.x+50, y)
            dc.DrawText('mean: '+smean, o.x+130, y)
            dc.DrawText('stdev: '+sstdev, o.x+220, y)
        else:
            dc.DrawText('min: '+sminh, o.x-10, y)
            dc.DrawText('max: '+smaxh, o.x+60, y)
            dc.DrawText('mean: '+smean, o.x+130, y)
            dc.DrawText('stdev: '+sstdev, o.x+210, y)

    def getXAxisText(self):
        isNormalized = Spotlight.pOptions.programOptions['pixelValues']
        axisText = []
        if isNormalized == 0:
            axisText.append('0.0')
            axisText.append('.125')
            axisText.append('.250')
            axisText.append('.375')
            axisText.append('.500')
            axisText.append('.625')
            axisText.append('.759')
            axisText.append('.875')
            axisText.append('1.0')
        else:
            axisText.append('0')
            axisText.append('32')
            axisText.append('64')
            axisText.append('96')
            axisText.append('128')
            axisText.append('160')
            axisText.append('192')
            axisText.append('224')
            axisText.append('255')
        return axisText

    def drawYAxisLabels(self, dc):
        o = wx.Point(self.xoffset, self.plotHeight+self.yoffset)  # axes origin
        ystep = self.plotHeight / 4  # 4 tick marks
        axisText = self.getYaxisText()

        # draw y-axis tickmarks
        for i in range(1, 5):
            ys = ystep * i
            xstart = o.x
            ystart = o.y - ys
            xend = o.x-5
            yend = o.y - ys
            dc.DrawLine(xstart, ystart, xend, yend)

            # draw y-axis labels
            te = dc.GetTextExtent(axisText[i-1])
            x = (self.xoffset-6) - te[0]
            y = o.y - ystep * i
            dc.DrawText(axisText[i-1], x, y-5)

    def getYaxisText(self):
        axisText = []
        axisText.append(str(self.maxHist/4)) # bottom y-axis label'
        axisText.append(str(self.maxHist/2)) # third from top
        axisText.append(str(3*self.maxHist/4)) # second from top
        axisText.append(str(self.maxHist)) # top value
        return axisText

    def OnCancel(self, event):
        'Post the event to close dialog and delete aoi. Then get out.'
        self.notify({'closeExecuted': True})
        Spotlight.Pause()
        wx.CallAfter(frame.deleteAoiFromOnCancel)

    def validateCoordinates(self, x, y):
        'Note: the y is inverted (y=0 is on top)'
        width, height = self.graphPanel.GetSizeTuple()
        if x < 0: x = 0
        if x > width: x = width
        if y < 0: y = 0
        if y > height-2: y = height-2  # fudge factor to see the line (on bottom)
        return (x,y)

    def OnRed(self, event):
        self.drawPen = wx.Pen(wx.NamedColour('RED'))
        self.SetTitle('Histogram: Red')
        params = {'colorPlane': RED, 'updateType': 2}
        self.notify(params)
    def OnGreen(self, event):
        self.drawPen = wx.Pen(wx.NamedColour('GREEN'))
        self.SetTitle('Histogram: Green')
        params = {'colorPlane': GREEN, 'updateType': 2}
        self.notify(params)
    def OnBlue(self, event):
        self.drawPen = wx.Pen(wx.NamedColour('BLUE'))
        self.SetTitle('Histogram: Blue')
        params = {'colorPlane': BLUE, 'updateType': 2}
        self.notify(params)
    def OnLuminance(self, event):
        self.drawPen = wx.Pen(wx.NamedColour('BLACK'))
        self.SetTitle('Histogram: Luminance')
        params = {'colorPlane': LUMINANCE, 'updateType': 2}
        self.notify(params)

    def SaveHistogram(self, event):
        self.notify({'histogram': [], 'updateStats': True})
        fd = wx.FileDialog(self, "Save Histogram", "", "*.txt",
                    "All files (*.*)|*.*|Data files (*.txt)|*.txt", wx.SAVE)
        if fd.ShowModal() == wx.ID_OK:
            f = open(fd.GetPath(), 'a')
            p = self.histogram  # histogram of the currently selected color plane
            if self.colorPlaneSelect == RED:
                s = 'Red Histogram'
            elif self.colorPlaneSelect == GREEN:
                s = 'Green Histogram'
            elif self.colorPlaneSelect == BLUE:
                s = 'Blue Histogram'
            elif self.colorPlaneSelect == LUMINANCE:
                s = 'Luminance Histogram'
            f.write('\n'+s)

            #~ ex = self.minmax
            #~ s = self.statistics
            #~ # input value (of min, max, mean, and stdev) is actual, output is
            #~ # either actual or normalized
            #~ min = actualToScaled(ex[0])
            #~ max = actualToScaled(ex[1])
            #~ mean = actualToScaled(s[0])
            #~ stdev = actualToScaled(s[1])

            min_s, max_s, mean_s, stdev_s = self.statistics
            minh = actualToScaled(min_s)
            maxh = actualToScaled(max_s)
            mean = actualToScaled(mean_s)
            stdev = actualToScaled(stdev_s)

            if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
                smin = '%.4f' % minh
                smax = '%.4f' % maxh
                smean = '%.4f' % mean
                sstdev = '%.5f' % stdev
            else:
                smin = str(minh)
                smax = str(maxh)
                smean = str(mean)
                sstdev = '%.4f' % stdev

            smin = 'min: ' + smin + '  '
            smax = 'max: ' + smax + '  '
            smean = 'mean: ' + smean + '  '
            sstdev = 'stdev: ' + sstdev + '  '

            f.write('\n' + smin + smax + smean + sstdev)
            s3 = 'column format:  graylevel, number of pixels'
            f.write('\n'+s3+'\n'+'\n')

            for i in range(256):
                f.write(str(i)+' '+str(p[i])+'\n')
            f.close()
        fd.Destroy()


##---------------- ThresholdTrackingOptions dialog box -----------------------------

class ThresholdTrackingOptions(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        ThresholdTrackingDialogFunc(self, True)
        self.CentreOnParent()

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateInit) # called when dialog is created
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_RIGHT)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_LEFT)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_UP)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_DOWN)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_RADIO_ANGLE)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_THRESH_CONSTRAIN)

    def OnUpdateInit(self, event):
        """The initial enabling/disabling of controls is handled separately
        from stuff done by OnUpdateUI() to take care of the case when user sets
        the angle manually (by dragging arrow) before the dialog is opened.
        """
        a = float(self.getAngle())
        if a == 0.0 or a == 90.0 or a == 180.0 or a == 270.0:
            self.setAngle(a)
            if a == 0:
                self.setTrackDirection(0)
            if a == 90:
                self.setTrackDirection(2)
            if a == 180:
                self.setTrackDirection(1)
            if a == 270:
                self.setTrackDirection(3)
            self.setAngleEnable(False)
        else:
            self.setAngleEnable(True)
            self.setTrackDirection(4)

        if self.getConstrainToLine():
            self.enableSearchType(True)
        else:
            self.enableSearchType(False)

    def OnUpdateUI(self, event):
        'enable/disable controls'
        s = self.getTrackDirection()

        if s == 0:  # right
            self.setAngle(0.0)
        elif s == 1:  # left
            self.setAngle(180.0)
        elif s == 2:  # up
            self.setAngle(90.0)
        elif s == 3:  # down
            self.setAngle(270.0)

        if s == 4:  # angle
            self.setAngleEnable(True)
        else:
            self.setAngleEnable(False)

        if self.getConstrainToLine():
            self.enableSearchType(True)
        else:
            self.enableSearchType(False)

    def enableSearchType(self, flag):
        b1 = self.FindWindowById(ID_SEARCH_TO_LINE)
        b2 = self.FindWindowById(ID_SEARCH_AOI)
        b1.Enable(flag)
        b2.Enable(flag)

    def enableDirection(self, flag):
        b1 = self.FindWindowById(ID_RIGHT)
        b2 = self.FindWindowById(ID_LEFT)
        b3 = self.FindWindowById(ID_UP)
        b4 = self.FindWindowById(ID_DOWN)
        b5 = self.FindWindowById(ID_RADIO_ANGLE)
        b1.Enable(flag)
        b2.Enable(flag)
        b3.Enable(flag)
        b4.Enable(flag)
        b5.Enable(flag)

    def getAngle(self):
        a = self.FindWindowById(ID_ANGLE)
        return a.GetValue()
    def setAngle(self, angle):
        s = str(angle)
        a = self.FindWindowById(ID_ANGLE)
        a.SetValue(s)
    def setAngleEnable(self, flag):
        a = self.FindWindowById(ID_ANGLE)
        a.Enable(flag)

    def getConstrainToLine(self):
        a = self.FindWindowById(ID_THRESH_CONSTRAIN)
        return a.GetValue()
    def setConstrainToLine(self, useVelocityFlag):
        a = self.FindWindowById(ID_THRESH_CONSTRAIN)
        a.SetValue(useVelocityFlag)

    def getUseVelocityCheckbox(self):
        a = self.FindWindowById(ID_USE_VELOCITY)
        return a.GetValue()
    def setUseVelocityCheckbox(self, useVelocityFlag):
        a = self.FindWindowById(ID_USE_VELOCITY)
        a.SetValue(useVelocityFlag)

    def getVelocityX(self):
        a = self.FindWindowById(ID_VELOCITY_X)
        return a.GetValue()
    def setVelocityX(self, v):
        a = self.FindWindowById(ID_VELOCITY_X)
        a.SetValue(str(v))

    def getVelocityY(self):
        a = self.FindWindowById(ID_VELOCITY_Y)
        return a.GetValue()
    def setVelocityY(self, v):
        a = self.FindWindowById(ID_VELOCITY_Y)
        a.SetValue(str(v))

    def getTrackDirection(self):
        b1 = self.FindWindowById(ID_RIGHT)
        if b1.GetValue():
            return 0
        b2 = self.FindWindowById(ID_LEFT)
        if b2.GetValue():
            return 1
        b3 = self.FindWindowById(ID_UP)
        if b3.GetValue():
            return 2
        b4 = self.FindWindowById(ID_DOWN)
        if b4.GetValue():
            return 3
        b5 = self.FindWindowById(ID_RADIO_ANGLE)
        if b5.GetValue():
            return 4

    def setTrackDirection(self, s):
        b1 = self.FindWindowById(ID_RIGHT)
        b2 = self.FindWindowById(ID_LEFT)
        b3 = self.FindWindowById(ID_UP)
        b4 = self.FindWindowById(ID_DOWN)
        b5 = self.FindWindowById(ID_RADIO_ANGLE)
        if s == 0:
            b1.SetValue(True)
            b2.SetValue(False)
            b3.SetValue(False)
            b4.SetValue(False)
            b5.SetValue(False)
        elif s == 1:
            b1.SetValue(False)
            b2.SetValue(True)
            b3.SetValue(False)
            b4.SetValue(False)
            b5.SetValue(False)
        elif s == 2:
            b1.SetValue(False)
            b2.SetValue(False)
            b3.SetValue(True)
            b4.SetValue(False)
            b5.SetValue(False)
        elif s == 3:
            b1.SetValue(False)
            b2.SetValue(False)
            b3.SetValue(False)
            b4.SetValue(True)
            b5.SetValue(False)
        else:
            b1.SetValue(False)
            b2.SetValue(False)
            b3.SetValue(False)
            b4.SetValue(False)
            b5.SetValue(True)

    def getSearchType(self):
        b1 = self.FindWindowById(ID_SEARCH_TO_LINE)
        if b1.GetValue():
            return 0
        b2 = self.FindWindowById(ID_SEARCH_AOI)
        if b2.GetValue():
            return 1

    def setSearchType(self, s):
        b1 = self.FindWindowById(ID_SEARCH_TO_LINE)
        b2 = self.FindWindowById(ID_SEARCH_AOI)
        if s == 0:
            b1.SetValue(True)
            b2.SetValue(False)
        else:
            b1.SetValue(False)
            b2.SetValue(True)

    def getThresholdTrackingParams(self):
        an = self.getAngle()
        vx = self.getVelocityX()
        vy = self.getVelocityY()

        ### The following if-statement is there to correct a bug
        ### in wxPython in which clicking the top radio button
        ### doesn't call the OnUpdateUI (where the angle is set),
        ### but the radiobutton is set correctly so here the angle
        ### is fixed.
        if self.getTrackDirection() == 0:
            an = 0.0

        valid = True
        if not isValid(an, 0.0, 360.0, isFloat=True):
            m = 'Angle is out of range of (0 - 360)'
            messageDialog(m)
            valid = False
        if not (isValid(vx, -400.0, 400.0, isFloat=True) and isValid(vy, -400.0, 400.0, isFloat=True)):
            m = 'Velocity is out of range of (0 - 400)'
            messageDialog(m)
            valid = False

        params = {}
        if valid:
            params['angle'] = float(an)
            params['velocity'] = (int(vx), int(vy))
            params['useVelocity'] = self.getUseVelocityCheckbox()
            params['constrain'] = self.getConstrainToLine()
            params['searchType'] = self.getSearchType()
        return params

#---------------- Save Results dialog ----------------------

class ResultsDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        #self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)) # for testing
        box = wx.BoxSizer(wx.VERTICAL)

        # generate box1top
        box1top = wx.BoxSizer(wx.HORIZONTAL)
        fntext = wx.StaticText(self, -1, "File name:",wx.DefaultPosition)
        box1top.Add(fntext, 0, wx.LEFT|wx.TOP, 10)
        box.Add(box1top, 0, wx.EXPAND|wx.BOTTOM, 5) # put a space of 5 at bottom

        # generate box1
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        self.p = wx.TextCtrl(self, 10, "", wx.DefaultPosition, wx.Size(240, -1))
        bnButton = wx.Button(self, -1, "Select", wx.DefaultPosition, wx.Size(55, -1))
        self.Bind(wx.EVT_BUTTON, self.OnSelectPath, bnButton)

        box1.Add(self.p, 0, wx.EXPAND|wx.LEFT, 10)
        box1.Add(bnButton, 0, wx.EXPAND|wx.LEFT, 5)
        box.Add(box1, 0, wx.EXPAND|wx.RIGHT, 10)

        # generate box2
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        efButton = wx.Button(self, -1, "Empty this file now", wx.DefaultPosition, wx.Size(136, -1))
        vButton = wx.Button(self, -1, "View", wx.DefaultPosition, wx.Size(136, -1))
        self.Bind(wx.EVT_BUTTON, self.OnEmptyFileNow, efButton)
        self.Bind(wx.EVT_BUTTON, self.OnView, vButton)
        box2.Add(efButton, 0, wx.TOP|wx.RIGHT, 10)
        box2.Add(vButton, 0, wx.TOP|wx.LEFT, 10)
        box.Add(box2, 0, wx.CENTER)

        # generate boxx (contains OK and Cancel buttons)
        boxX = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self,wx.ID_OK,"OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self,wx.ID_CANCEL,"Cancel")
        boxX.Add(okButton)
        boxX.Add(cancelButton)
        boxButtons = wx.BoxSizer(wx.VERTICAL) # used to position boxX
        boxButtons.Add(boxX, 0, wx.EXPAND|wx.ALL, 10)
        box.Add(boxButtons, 0, wx.CENTER)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        box.Fit(self)
        box.SetSizeHints(self)

    def OnView(self, event):
        import sys
        if sys.platform == 'win32':
            cmd = 'start notepad.exe ' + self.getFilePath()
            os.system(cmd)
        elif sys.platform == 'darwin':
            cmd = 'open /Applications/Preview.app ' + self.getFilePath()
            os.system(cmd)
        else:
            c = os.system('which kedit')
            if c == 0:
                command = 'kedit "'
                cmd = command + self.getFilePath() + '"' + ' &'
                os.system(cmd)
            else:
                c = os.system('which gedit')
                if c == 0:
                    command = 'gedit "'
                    cmd = command + self.getFilePath() + '"' + ' &'
                    os.system(cmd)
                else:
                    m = 'It appears that neither kedit nor gedit is installed. '
                    messageDialog(m)

    def OnEmptyFileNow(self, event):
        imageExists = os.path.isfile(self.getFilePath())
        if imageExists:
            emptyTheFile = YesNoDialog('Are you sure you want to empty the file?')
            if emptyTheFile:
                f = open(self.getFilePath(), 'w')  # will erase contents
                f.close()
        else:
            message = 'The file specified does not exist'
            messageDialog(message)

    def OnSelectPath(self, event):
        # get file - from this dialog box's file field
        path = self.getFilePath()
        dir, file = os.path.split(path)
        fd = wx.FileDialog(self, "Save As", dir, file,
                "Text files (*.txt)|*.txt|All files (*.*)|*.*", wx.SAVE)
        if fd.ShowModal() == wx.ID_OK:
            path = fd.GetPath()
            self.setFilePath(path)
        fd.Destroy()

    def getFilePath(self):
        return self.p.GetValue()
    def setFilePath(self, path):
        self.p.SetValue(path)

#---------------- CenterTrackingOptions dialog box -----------------------------

class CenterTrackingOptions(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        CenterTrackingDialogFunc(self, True)
        self.CentreOnParent()

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateUI) # called when dialog is created
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_CENTER_OF_MASS)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_CENTER_GRAYSCALE)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_FOUR_SIDE_EDGE)

    def OnUpdateUI(self, event):
        'enable/disable controls'
        if self.getTrackingType() == 0 or self.getTrackingType() == 1:
            self.enableSizeRelated(False)
        else:
            self.enableSizeRelated(True)

    def enableSizeRelated(self, flag):
        b2 = self.FindWindowById(ID_SAVE1)
        b3 = self.FindWindowById(ID_SAVE2)
        b2.Enable(flag)
        b3.Enable(flag)

    def getTrackingType(self):
        b0 = self.FindWindowById(ID_CENTER_OF_MASS)
        if b0.GetValue():
            return 0
        b1 = self.FindWindowById(ID_CENTER_GRAYSCALE)
        if b1.GetValue():
            return 1
        b2 = self.FindWindowById(ID_FOUR_SIDE_EDGE)
        if b2.GetValue():
            return 2

    def setTrackingType(self, s):
        b1 = self.FindWindowById(ID_CENTER_OF_MASS)
        b2 = self.FindWindowById(ID_CENTER_GRAYSCALE)
        b3 = self.FindWindowById(ID_FOUR_SIDE_EDGE)
        if s == 0:
            b1.SetValue(True)
            b2.SetValue(False)
            b3.SetValue(False)
        elif s == 1:
            b1.SetValue(False)
            b2.SetValue(True)
            b3.SetValue(False)
        elif s == 2:
            b1.SetValue(False)
            b2.SetValue(False)
            b3.SetValue(True)

    def getSaveToResultsFile(self):
        b0 = self.FindWindowById(ID_SAVE0)
        if b0.GetValue():
            return 0
        b1 = self.FindWindowById(ID_SAVE1)
        if b1.GetValue():
            return 1
        b2 = self.FindWindowById(ID_SAVE2)
        if b2.GetValue():
            return 2
    def setSaveToResultsFile(self, s):
        b0 = self.FindWindowById(ID_SAVE0)
        b1 = self.FindWindowById(ID_SAVE1)
        b2 = self.FindWindowById(ID_SAVE2)
        if s == 0:
            b0.SetValue(True)
            b1.SetValue(False)
            b2.SetValue(False)
        elif s == 1:
            b0.SetValue(False)
            b1.SetValue(True)
            b2.SetValue(False)
        elif s == 2:
            b0.SetValue(False)
            b1.SetValue(False)
            b2.SetValue(True)

    def getUseVelocityCheckbox(self):
        a = self.FindWindowById(ID_CENTER_USE_VELOCITY)
        return a.GetValue()
    def setUseVelocityCheckbox(self, useVelocityFlag):
        a = self.FindWindowById(ID_CENTER_USE_VELOCITY)
        a.SetValue(useVelocityFlag)

    def getVelocityX(self):
        a = self.FindWindowById(ID_CENTER_VELOCITY_X)
        return a.GetValue()
    def setVelocityX(self, v):
        a = self.FindWindowById(ID_CENTER_VELOCITY_X)
        a.SetValue(str(v))

    def getVelocityY(self):
        a = self.FindWindowById(ID_CENTER_VELOCITY_Y)
        return a.GetValue()
    def setVelocityY(self, v):
        a = self.FindWindowById(ID_CENTER_VELOCITY_Y)
        a.SetValue(str(v))

    def getParams(self):
        vx = self.getVelocityX()
        vy = self.getVelocityY()

        valid = True
        if not (isValid(vx, -400.0, 400.0, isFloat=True) and isValid(vy, -400.0, 400.0, isFloat=True)):
            m = 'Velocity is out of range of (0 - 400)'
            messageDialog(m)
            valid = False

        params = {}
        if valid:
            #~ params['velocity'] = (float(vx), float(vy))
            params['velocity'] = (int(vx), int(vy))
            params['useVelocity'] = self.getUseVelocityCheckbox()
            params['trackingType'] = self.getTrackingType()
            params['saveResults'] = self.getSaveToResultsFile()
        return params

#---------------- MaxTrackingOptions dialog box -----------------------------

class MaximumTrackingOptions(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        LocalMaxDialogFunc(self, True)
        self.CentreOnParent()

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateInit) # called when dialog is created
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_MAX_RIGHT)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_MAX_LEFT)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_MAX_UP)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_MAX_DOWN)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_MAX_RADIO_ANGLE)
        self.Bind(wx.EVT_CHECKBOX, self.OnUpdateUI, id=ID_MAX_CONSTRAIN)

    def OnUpdateInit(self, event):
        a = float(self.getAngle())
        if a == 0.0 or a == 90.0 or a == 180.0 or a == 270.0:
            self.setAngle(a)
            if a == 0:
                self.setTrackDirection(0)
            if a == 90:
                self.setTrackDirection(2)
            if a == 180:
                self.setTrackDirection(1)
            if a == 270:
                self.setTrackDirection(3)
        else:
            self.setTrackDirection(4)

        if self.getConstrainToLine() == True:
            self.enableDirection(True)
            if self.getTrackDirection() == 4:
                self.setAngleEnable(True)
            else:
                self.setAngleEnable(False)
        else:
            self.enableDirection(False)

    def OnUpdateUI(self, event):
        'enable/disable controls'
        s = self.getTrackDirection()
        if s == 0:  # right
            self.setAngle(0.0)
        elif s == 1:  # left
            self.setAngle(180.0)
        elif s == 2:  # up
            self.setAngle(90.0)
        elif s == 3:  # down
            self.setAngle(270.0)

        if self.getConstrainToLine() == True:
            self.enableDirection(True)
            if s == 4:  # angle
                self.setAngleEnable(True)
            else:
                self.setAngleEnable(False)
        else:
            self.enableDirection(False)

    def enableDirection(self, flag):
        b1 = self.FindWindowById(ID_MAX_RIGHT)
        b2 = self.FindWindowById(ID_MAX_LEFT)
        b3 = self.FindWindowById(ID_MAX_UP)
        b4 = self.FindWindowById(ID_MAX_DOWN)
        b5 = self.FindWindowById(ID_MAX_RADIO_ANGLE)
        b1.Enable(flag)
        b2.Enable(flag)
        b3.Enable(flag)
        b4.Enable(flag)
        b5.Enable(flag)
        self.setAngleEnable(flag)

    def getAngle(self):
        a = self.FindWindowById(ID_MAX_ANGLE)
        return a.GetValue()
    def setAngle(self, angle):
        s = str(angle)
        a = self.FindWindowById(ID_MAX_ANGLE)
        a.SetValue(s)

    def setAngleEnable(self, flag):
        a = self.FindWindowById(ID_MAX_ANGLE)
        a.Enable(flag)

    def getUseVelocity(self):
        a = self.FindWindowById(ID_MAX_USE_VELOCITY)
        return a.GetValue()
    def setUseVelocity(self, useVelocityFlag):
        a = self.FindWindowById(ID_MAX_USE_VELOCITY)
        a.SetValue(useVelocityFlag)

    def getVelocityX(self):
        a = self.FindWindowById(ID_MAX_VELOCITY_X)
        return a.GetValue()
    def setVelocityX(self, v):
        a = self.FindWindowById(ID_MAX_VELOCITY_X)
        a.SetValue(str(v))

    def getVelocityY(self):
        a = self.FindWindowById(ID_MAX_VELOCITY_Y)
        return a.GetValue()
    def setVelocityY(self, v):
        a = self.FindWindowById(ID_MAX_VELOCITY_Y)
        a.SetValue(str(v))

    def getTrackDirection(self):
        b1 = self.FindWindowById(ID_MAX_RIGHT)
        if b1.GetValue():
            return 0
        b2 = self.FindWindowById(ID_MAX_LEFT)
        if b2.GetValue():
            return 1
        b3 = self.FindWindowById(ID_MAX_UP)
        if b3.GetValue():
            return 2
        b4 = self.FindWindowById(ID_MAX_DOWN)
        if b4.GetValue():
            return 3
        b5 = self.FindWindowById(ID_MAX_RADIO_ANGLE)
        if b5.GetValue():
            return 4

    def setTrackDirection(self, s):
        b1 = self.FindWindowById(ID_MAX_RIGHT)
        b2 = self.FindWindowById(ID_MAX_LEFT)
        b3 = self.FindWindowById(ID_MAX_UP)
        b4 = self.FindWindowById(ID_MAX_DOWN)
        b5 = self.FindWindowById(ID_MAX_RADIO_ANGLE)
        if s == 0:
            b1.SetValue(True)
            b2.SetValue(False)
            b3.SetValue(False)
            b4.SetValue(False)
            b5.SetValue(False)
        elif s == 1:
            b1.SetValue(False)
            b2.SetValue(True)
            b3.SetValue(False)
            b4.SetValue(False)
            b5.SetValue(False)
        elif s == 2:
            b1.SetValue(False)
            b2.SetValue(False)
            b3.SetValue(True)
            b4.SetValue(False)
            b5.SetValue(False)
        elif s == 3:
            b1.SetValue(False)
            b2.SetValue(False)
            b3.SetValue(False)
            b4.SetValue(True)
            b5.SetValue(False)
        else:
            b1.SetValue(False)
            b2.SetValue(False)
            b3.SetValue(False)
            b4.SetValue(False)
            b5.SetValue(True)

    def getConstrainToLine(self):
        a = self.FindWindowById(ID_MAX_CONSTRAIN)
        return a.GetValue()
    def setConstrainToLine(self, flag):
        a = self.FindWindowById(ID_MAX_CONSTRAIN)
        a.SetValue(flag)

    def getLocalMaxTrackingParams(self):
        an = self.getAngle()
        vx = self.getVelocityX()
        vy = self.getVelocityY()

        valid = True
        if not isValid(an, 0.0, 360.0, isFloat=True):
            m = 'Angle is out of range of (0 - 360)'
            messageDialog(m)
            valid = False
        if not (isValid(vx, -400.0, 400.0, isFloat=True) and isValid(vy, -400.0, 400.0, isFloat=True)):
            m = 'Velocity is out of range of (0 - 400)'
            messageDialog(m)
            valid = False

        params = {}
        if valid:
            params['angle'] = float(an)
            params['velocity'] = (int(vx), int(vy))
            params['direction'] = self.getTrackDirection()
            params['useVelocity'] = self.getUseVelocity()
            params['constrain'] = self.getConstrainToLine()
        return params

#---------------------- Snake Options dialog ----------------------------

class SnakeOptionsDialog(wx.Dialog):
    def __init__(self, title, parent):
        wx.Dialog.__init__(self, frame, -1, title)
        self.parent = parent

        SnakeDialogFunc(self, True)
        self.CentreOnParent()

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateUI) # called when dialog is created
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_VARIABLE)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_FIXED)
        self.Bind(wx.EVT_BUTTON, self.OnReset, id=ID_RESET)
        self.Bind(wx.EVT_BUTTON, self.OnSlither, id=ID_SLITHER)

    def OnUpdateUI(self, event):
        'enable/disable controls'
        s = self.getSnakePointsFormatSelection()
        if s == 0:
            self.setNPointsEnable(True)
            self.setPercentEnable(False)
        else:
            self.setNPointsEnable(False)
            self.setPercentEnable(True)

    def getIntensityWeight(self):
        a = self.FindWindowById(ID_INTENSITY)
        return a.GetValue()
    def setIntensityWeight(self, w):
        a = self.FindWindowById(ID_INTENSITY)
        a.SetValue(str(w))

    def getGradientWeight(self):
        a = self.FindWindowById(ID_GRADIENT)
        return a.GetValue()
    def setGradientWeight(self, w):
        a = self.FindWindowById(ID_GRADIENT)
        a.SetValue(str(w))

    def getSecondDerivativeWeight(self):
        a = self.FindWindowById(ID_SECOND_DERIVATIVE)
        return a.GetValue()
    def setSecondDerivativeWeight(self, w):
        a = self.FindWindowById(ID_SECOND_DERIVATIVE)
        a.SetValue(str(w))

    def getEvenSpacingWeight(self):
        a = self.FindWindowById(ID_EVEN_SPACING)
        return a.GetValue()
    def setEvenSpacingWeight(self, w):
        a = self.FindWindowById(ID_EVEN_SPACING)
        a.SetValue(str(w))

    def getTotalLengthWeight(self):
        a = self.FindWindowById(ID_TOTAL_LENGTH)
        return a.GetValue()
    def setTotalLengthWeight(self, w):
        a = self.FindWindowById(ID_TOTAL_LENGTH)
        a.SetValue(str(w))

    def getResultFormatSelection(self):
        a = self.FindWindowById(ID_RESULT_FORMAT)
        return a.GetSelection()
    def setResultFormatSelection(self, s):
        a = self.FindWindowById(ID_RESULT_FORMAT)
        a.SetSelection(s)

    def getSnakePointsFormatSelection(self):
        b0 = self.FindWindowById(ID_FIXED)
        if b0.GetValue():
            return 0
        b1 = self.FindWindowById(ID_VARIABLE)
        if b1.GetValue():
            return 1
    def setSnakePointsFormatSelection(self, s):
        b0 = self.FindWindowById(ID_FIXED)
        b1 = self.FindWindowById(ID_VARIABLE)
        if s == 0:
            b0.SetValue(True)
            b1.SetValue(False)
        elif s == 1:
            b0.SetValue(False)
            b1.SetValue(True)

    def getFixedNumberOfPoints(self):
        a = self.FindWindowById(ID_NPOINTS)
        return a.GetValue()
    def setFixedNumberOfPoints(self, w):
        a = self.FindWindowById(ID_NPOINTS)
        a.SetValue(str(w))
    def setNPointsEnable(self, flag):
        'this enables/disables the field'
        a = self.FindWindowById(ID_NPOINTS)
        a.Enable(flag)

    def getPercent(self):
        a = self.FindWindowById(ID_PERCENT)
        return a.GetValue()
    def setPercent(self, w):
        a = self.FindWindowById(ID_PERCENT)
        a.SetValue(str(w))
    def setPercentEnable(self, flag):
        'this enables/disables the field'
        a = self.FindWindowById(ID_PERCENT)
        a.Enable(flag)

    def getVelocityX(self):
        a = self.FindWindowById(ID_VELOCITY_X)
        return a.GetValue()
    def setVelocityX(self, v):
        a = self.FindWindowById(ID_VELOCITY_X)
        a.SetValue(str(v))

    def getVelocityY(self):
        a = self.FindWindowById(ID_VELOCITY_Y)
        return a.GetValue()
    def setVelocityY(self, v):
        a = self.FindWindowById(ID_VELOCITY_Y)
        a.SetValue(str(v))

    def getUseVelocityCheckbox(self):
        a = self.FindWindowById(ID_USE_VELOCITY)
        return a.GetValue()
    def setUseVelocityCheckbox(self, useVelocityFlag):
        a = self.FindWindowById(ID_USE_VELOCITY)
        a.SetValue(useVelocityFlag)

    def getPixelsToSearch(self):
        a = self.FindWindowById(ID_PIXELS_TO_SEARCH)
        return a.GetValue()
    def setPixelsToSearch(self, w):
        a = self.FindWindowById(ID_PIXELS_TO_SEARCH)
        a.SetValue(str(w))

    def getIdealIntensity(self):
        a = self.FindWindowById(ID_IDEAL_INTENS)
        return a.GetValue()
    def setIdealIntensity(self, w):
        a = self.FindWindowById(ID_IDEAL_INTENS)
        a.SetValue(str(w))

    def getProcessingRadius(self):
        a = self.FindWindowById(ID_IPR)
        return a.GetValue()
    def setProcessingRadius(self, w):
        a = self.FindWindowById(ID_IPR)
        a.SetValue(str(w))

    def OnReset(self, event):
        self.parent.Reset()

    def OnSlither(self, event):
        if self.parent.slithering:
            self.parent.Stop()
        else:
            a = self.FindWindowById(ID_SLITHER)
            oldFont = a.GetFont()

            # set button label and color
            a.SetLabel("STOP")
            a.SetForegroundColour(wx.RED)
            font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            a.SetFont(font)

            params = self.getSnakeParams()
            if params:
                self.parent.Slither(True, params)

            # set button params back
            a.SetFont(oldFont)
            a.SetLabel("Slither")
            a.SetForegroundColour(wx.BLACK)

    def getSnakeParams(self):
        iw = self.getIntensityWeight()
        gw = self.getGradientWeight()
        dw = self.getSecondDerivativeWeight()
        ew = self.getEvenSpacingWeight()
        tw = self.getTotalLengthWeight()
        rf = self.getResultFormatSelection()
        sp = self.getSnakePointsFormatSelection()
        fp = self.getFixedNumberOfPoints()
        pd = self.getPercent()
        vx = self.getVelocityX()
        vy = self.getVelocityY()
        ps = self.getPixelsToSearch()
        ii = self.getIdealIntensity()
        pr = self.getProcessingRadius()

        imX, imY = Spotlight.workingImage.size
        imX = int(imX / 2)
        imY = int(imY / 2)

        valid = True
        if not (isValid(iw) and isValid(gw) and isValid(dw) and isValid(ew) and isValid(tw)):
            m = 'One of the weights is out of range of (0 - 255)'
            messageDialog(m)
            valid = False

        if valid:
            valid = isValid(fp, 0, 2000)
            if valid == False:
                m = 'Fixed number of points is out of range of (0 - 2000)'
                messageDialog(m)

        if valid:
            vxx = convertStringToInteger(vx)
            valid = isValid(vxx, -imX, imX)
            if valid == False:
                m1 = 'Velocity is out of range of (-%d to %d)' % (imX, imX)
                m2 = 'which is half the size of the image'
                messageDialog(m1 + '\n' + m2)

        if valid:
            vyy = convertStringToInteger(vy)
            valid = isValid(vyy, -imY, imY)
            if valid == False:
                m1 = 'Velocity is out of range of (-%d to %d)' % (imY, imY)
                m2 = 'which is half the size of the image'
                messageDialog(m1 + '\n' + m2)

        if valid:
            valid = isValid(ps, 0, 10)
            if valid == False:
                m = 'Fixed number of points is out of range of (0 - 10)'
                messageDialog(m)

        if valid:
            if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
                valid = isValid(ii, 0.0, 1.0, isFloat=True)
                if valid == False:
                    m = 'Ideal intensity is out of range of 0.0 - 1.0'
                    messageDialog(m)
            else:
                ii = convertStringToInteger(ii)
                valid = isValid(ii, 0, 255)
                if valid == False:
                    m = 'Ideal intensity is out of range of 0 - 255'
                    messageDialog(m)

        if valid:
            minRadius = min(imX, imY)
            valid = isValid(pr, 0, minRadius)
            if valid == False:
                m1 = 'Processing radius is out of range of (0 - %d)' % minRadius
                m2 = 'which is min of half the X and Y size of the image'
                messageDialog(m1 + '\n' + m2)

        if valid:
            valid = isValid(pd, 0, 100)
            if valid == False:
                m = 'Point Density is out of range of (0 - 100)'
                messageDialog(m)

        params = {}
        if valid:
            params['name'] = 'SnakeOptions'
            params['intensityWeight'] = int(iw)
            params['gradientWeight'] = int(gw)
            params['derivativeWeight'] = int(dw)
            params['evenSpacingWeight'] = int(ew)
            params['totalLengthWeight'] = int(tw)
            params['resultFormat'] = rf
            params['snakePointsFormat'] = sp
            params['fixedNumber'] = int(fp)
            params['percent'] = int(pd)
            params['velocity'] = (vxx, vyy)
            params['useVelocity'] = self.getUseVelocityCheckbox()
            params['pixelsToSearch'] = int(ps)
            if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
                params['idealIntensity'] = int(float(ii) * 255.0)
            else:
                params['idealIntensity'] = int(ii)
            params['processingRadius'] = int(pr)
        return params

#--------------------- AngleTool Options dialog box -----------------------------------

class AngleToolOptionsDialog(wx.Dialog):
    def __init__(self, parentAoi, title):
        wx.Dialog.__init__(self, frame, -1, title)
        self.parentAoi = parentAoi
        dpos = wx.DefaultPosition
        dsize = wx.DefaultSize

        box1 = wx.BoxSizer(wx.VERTICAL)
        list1 = ['x-axis', 'y-axis']
        numberOfColumns = 1
        self.rb = wx.RadioBox(self, -1, "Angle relative to:", dpos, dsize,
                    list1, numberOfColumns, wx.RA_SPECIFY_COLS)
        box1.Add(self.rb, 0, wx.TOP, 10)

        box01 = wx.BoxSizer(wx.VERTICAL)
        list2 = ['0  to  360 degrees', '-180  to  180 degrees']
        self.rb01 = wx.RadioBox(self, -1, "Display mode", dpos, dsize, list2,
                             numberOfColumns, wx.RA_SPECIFY_COLS)
        box01.Add(self.rb01, 0, wx.TOP, 10)

        box11 = wx.BoxSizer(wx.VERTICAL)  # used to position box1
        box11.Add(box1, 0, wx.EXPAND|wx.LEFT, 15)
        box11.Add(box01, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 15)

        box2 = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, -1, "angle:",dpos)
        self.t = wx.TextCtrl(self, -1, "", dpos, wx.Size(70,-1),wx.TE_READONLY)
        # Note: the wx.TOP|wx.BOTTOM,4 (below) makes gives it vertically more room
        # and allows the next line (self.t) to be a little bigger vertically
        box2.Add(text, 0, wx.TOP|wx.BOTTOM, 4)
        box2.Add(self.t, 0, wx.EXPAND|wx.LEFT, 5)
        box22 = wx.BoxSizer(wx.VERTICAL)  # used to position box2
        box22.Add(box2, 0, wx.EXPAND|wx.ALL, 10)

        box3 = wx.BoxSizer(wx.VERTICAL)
        self.update = wx.CheckBox(self, 100, "rotate image clockwise by the angle",
                              dpos, dsize, wx.NO_BORDER)
        box3.Add(self.update, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        box33 = wx.BoxSizer(wx.VERTICAL)  # used to position box3
        box33.Add(box3, 0, wx.EXPAND|wx.BOTTOM, 15)

        # add OK and Cancel buttons
        boxX = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self,wx.ID_OK,"OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self,wx.ID_CANCEL,"Cancel")
        boxX.Add(okButton,0, wx.BOTTOM, 10) # pad only bottom with 10
        boxX.Add(cancelButton,0, wx.BOTTOM, 10) # pad only bottom with 10

        # create vertical sizer to hold everything
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(box11, 0, wx.EXPAND|wx.LEFT, 20) # move box11 left by 20
        box.Add(box22, 0, wx.EXPAND|wx.LEFT, 30)
        box.Add(box33, 0, wx.EXPAND|wx.LEFT, 1)
        box.Add(boxX,0,wx.CENTER)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        box.Fit(self)
        box.SetSizeHints(self)

        self.Bind(wx.EVT_RADIOBOX, self.OnUpdateAngle, self.rb)
        self.Bind(wx.EVT_RADIOBOX, self.OnUpdateAngle, self.rb01)

    def OnUpdateAngle(self, event):
        'updates angle display when a radio button is clicked'
        dm = self.getDisplayMode()
        rt = self.getRelativeTo()
        rot = self.getRotateNow()
        self.parentAoi.setOptions(dm, rt, rot)
        self.parentAoi.updateAngle()
        angle = self.parentAoi.getAngle()
        self.setAngle(angle)

    def getRelativeTo(self):
        return self.rb.GetSelection()
    def setRelativeTo(self, d):
        self.rb.SetSelection(d)

    def getDisplayMode(self):
        return self.rb01.GetSelection()
    def setDisplayMode(self, d):
        self.rb01.SetSelection(d)

    def getRotateNow(self):
        return self.update.GetValue()
    def setRotateNow(self, value):
        self.update.SetValue(value)

    def getAngle(self):
        return self.t.GetValue()
    def setAngle(self, a):
        s = "%.4f" % a
        self.t.SetValue(s)

###-------------- Abel Panel --------------------------------

class AbelPanel(wx.Panel):
    dpos = wx.DefaultPosition
    dsize = wx.DefaultSize
    dstyle = wx.TAB_TRAVERSAL
    def __init__(self, parent, id, pos=dpos, size=dsize, style=dstyle):
        wx.Panel.__init__(self, parent, id, pos, size, style)
        self.parent = parent

        ####-- Using wxDesigner
        AbelDialogFunc( self, True )

        self.graphPanel = self.FindWindowById(ID_GRAPH_PANEL)
        self.graphPanel.SetBackgroundColour(wx.WHITE)
        self.leftPanel = self.FindWindowById(ID_LEFT_PANEL)
        self.rightPanel = self.FindWindowById(ID_RIGHT_PANEL)
        self.lineLengthPanel = self.FindWindowById(ID_LL_PANEL)
        self.topPanel = self.FindWindowById(ID_TOP_PANEL)
        self.lockAxis = self.FindWindowById(ID_LOCK_AXIS)

        self.drawPen = wx.Pen(wx.NamedColour('BLACK'))
        self.font = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

    def drawAxisLabels(self):
        """
        Draw left y-axis labels.
        """
        #~ if sys.platform == 'darwin':
            #~ # Get the dialog box background - needed for Mac because there the
            #~ # dialog box background is not solid color but a texture.
            #~ bdc = wx.ClientDC(self)
            #~ bk = bdc.GetBackground()
            #~ # double-buffered dc
            #~ w, h = self.leftPanel.GetSizeTuple()
            #~ dc = wx.BufferedDC(wx.ClientDC(self.leftPanel), wx.EmptyBitmap(w, h))
            #~ dc.SetFont(self.font)
            #~ dc.SetBackground(bk) # set background from dialog box
            #~ dc.Clear()

            #~ # seconf double-buffered dc
            #~ w, h = self.rightPanel.GetSizeTuple()
            #~ dc2 = wx.BufferedDC(wx.ClientDC(self.rightPanel), wx.EmptyBitmap(w, h))
            #~ dc2.SetFont(self.font)
            #~ dc2.SetBackground(bk) # set background from dialog box
            #~ dc2.Clear()
        #~ else:
        dc = wx.ClientDC(self.leftPanel)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.SetFont(self.font)

        dc2 = wx.ClientDC(self.rightPanel)
        dc2.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc2.Clear()
        dc2.SetFont(self.font)

        graphPanelWidth, graphPanelHeight = self.graphPanel.GetSizeTuple()
        leftPanelWidth, leftPanelHeight = self.leftPanel.GetSizeTuple()
        tph = 20  # top panel height
        o = wx.Point(leftPanelWidth, graphPanelHeight+tph)  # axes origin
        ystep = graphPanelHeight / 8  # 8 tick marks
        # Draw y-axis tick marks
        xstart = o.x-3
        xend = o.x
        y = o.y
        for i in range(0, 8):
            y = y - ystep
            dc.DrawLine(xstart, y, xend, y)
            dc2.DrawLine(0, y, 3, y)

        if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
            dc.DrawText('0', o.x-10, o.y-8)
            dc.DrawText('.125', o.x-28, o.y-(ystep+8))
            dc.DrawText('.250', o.x-28, o.y-(ystep*2+8))
            dc.DrawText('.375', o.x-28, o.y-(ystep*3+8))
            dc.DrawText('.500', o.x-28, o.y-(ystep*4+8))
            dc.DrawText('.625', o.x-28, o.y-(ystep*5+8))
            dc.DrawText('.750', o.x-28, o.y-(ystep*6+8))
            dc.DrawText('.875', o.x-28, o.y-(ystep*7+8))
            dc.DrawText('1.00', o.x-28, o.y-(ystep*8+8))
        else:
            dc.DrawText('0', o.x-10, o.y-8)
            dc.DrawText('32', o.x-18, o.y-(ystep+8))
            dc.DrawText('64', o.x-18, o.y-(ystep*2+8))
            dc.DrawText('96', o.x-18, o.y-(ystep*3+8))
            dc.DrawText('128', o.x-25, o.y-(ystep*4+8))
            dc.DrawText('160', o.x-25, o.y-(ystep*5+8))
            dc.DrawText('192', o.x-25, o.y-(ystep*6+8))
            dc.DrawText('224', o.x-25, o.y-(ystep*7+8))
            dc.DrawText('255', o.x-25, o.y-(ystep*8+8))

        if sys.platform == 'linux2': # wx.Python on Linux will not rotate this text
            return

        # this font is a little bit more legible
        dc.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL))
        dc.DrawRotatedText('pixel intensity', 5, 160, 90)

    def drawProfile(self):
        """
        Draws the line in the graphPanel.
        """
        dc = wx.ClientDC(self.graphPanel)
        dc.Clear()
        self.drawSimpleBorder(dc)
        dc.SetPen(self.drawPen)
        if self.parent.plotProfile:
            dc.DrawLines(self.parent.plotProfile)    # draw polyline

        if self.parent.plotRefProfile:
            dc.SetPen(wx.Pen(wx.NamedColour('BLUE')))
            dc.DrawLines(self.parent.plotRefProfile)

        if self.parent.plotDistribution:
            dc.SetPen(wx.Pen(wx.NamedColour('RED')))
            dc.DrawLines(self.parent.plotDistribution)
            # draw centerline
            dc.SetPen(wx.Pen(wx.NamedColour('FOREST GREEN')))
            graphPanelWidth, graphPanelHeight = self.graphPanel.GetSizeTuple()
            x = graphPanelWidth/2
            dc.DrawLine(x, 0, x, graphPanelHeight)

    def drawSimpleBorder(self, dc):
        """
        Needed only when wxDesigner is used because there is no
        simple border.
        """
        dc.DrawLine(0, 0, 320, 0)  # top
        dc.DrawLine(0, 199, 320, 199)  # bottom
        dc.DrawLine(0, 0, 0, 199)  # left
        dc.DrawLine(319, 0, 319, 199)  # right

    def drawPixelNumber(self, lineLength):
        """
        Draws the number of pixels the line spans.
        """
        #~ if sys.platform == 'darwin':
            #~ # Get the dialog box background - needed for Mac because there the
            #~ # dialog box background is not solid color but a texture.
            #~ bdc = wx.ClientDC(self)
            #~ bk = bdc.GetBackground()
            #~ # double-buffered dc
            #~ w, h = self.lineLengthPanel.GetSizeTuple()
            #~ dc = wx.BufferedDC(wx.ClientDC(self.lineLengthPanel), wx.EmptyBitmap(w, h))
            #~ dc.SetFont(self.font)
            #~ dc.SetBackground(bk) # set background from dialog box
            #~ dc.Clear()
        #~ else:
        dc = wx.ClientDC(self.lineLengthPanel)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.SetFont(self.font)

        txt = 'line lenght (pixels):  ' + lineLength
        dc.DrawText(txt, 90, 2)

    def drawDistributionLabel(self, values, label):
        """
        Draw the right y-axis labels -- the Abel distribution values.
        """
        dc = wx.ClientDC(self.rightPanel)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        dc.SetFont(font)

        graphPanelWidth, graphPanelHeight = self.graphPanel.GetSizeTuple()
        leftPanelWidth, leftPanelHeight = self.leftPanel.GetSizeTuple()
        tph = 20  # top panel height
        o = wx.Point(leftPanelWidth, graphPanelHeight+tph)  # axes origin
        ystep = graphPanelHeight / 8  # 8 tick marks
        # Draw y-axis tick marks
        y = o.y
        for i in range(0, 9):
            if i == 0:  # first tick only
                dc.DrawLine(0, y-1, 3, y-1)
                dc.DrawText(values[i], 6, y-7)
            else:  # rest of the tick marks and labels
                dc.DrawLine(0, y, 3, y)
                dc.DrawText(values[i], 6, y-7)
            y = y - ystep

        ## CHECK THIS - still true?
        if sys.platform == 'linux2': # wxPython on Linux will not rotate this text
            return
        dc.DrawRotatedText(label, 50, 40, -90)

    def drawKey(self):
        """
        Draw the key to define what each line means.
        """
        dc = wx.ClientDC(self.topPanel)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.SetFont(self.font)
        dc.SetPen(wx.Pen(wx.NamedColour('BLACK')))
        dc.DrawLine(20, 8, 50, 8)
        dc.DrawText('profile', 55, 0)
        dc.SetPen(wx.Pen(wx.NamedColour('BLUE')))
        dc.DrawLine(100, 8, 130, 8)
        dc.DrawText('ref profile', 135, 0)
        dc.SetPen(wx.Pen(wx.NamedColour('RED')))
        dc.DrawLine(200, 8, 230, 8)
        dc.DrawText('Abel transform', 235, 0)

##---------------------------- Abel Frame  ---------------------------------------------

class AbelDialog(wx.Frame):
    def __init__(self, parentAoi, frame, title):
        if sys.platform == 'darwin':
            wx.Frame.__init__(self, frame, -1, title, size=(430, 335),
                             style=wx.CAPTION)
        else:
            wx.Frame.__init__(self, frame, -1, title, size=(430, 360),
                             style=wx.STAY_ON_TOP|wx.CAPTION)
        self.parentAoi = parentAoi
        self.frame = frame
        self.CentreOnParent()

        # Construct a MenuBar
        menuBar = wx.MenuBar()
        # Construct "File" menu
        menuFile = wx.Menu()
        txt = "Load previously saved &Abel graph"
        mLoadGraph = menuFile.Append(wx.ID_ANY, txt, "")
        self.Bind(wx.EVT_MENU, self.OnLoadAbelGraph, mLoadGraph)
        txt = "Load demo - filter test"
        mLoadDemo = menuFile.Append(wx.ID_ANY, txt, "")
        self.Bind(wx.EVT_MENU, self.OnLoadDemo, mLoadDemo)
        menuFile.AppendSeparator()
        mSave = menuFile.Append(wx.ID_ANY, "&Save", "")
        self.Bind(wx.EVT_MENU, self.OnSave, mSave)
        menuBar.Append(menuFile, "&File")
        # Construct "Options" menu
        menuOptions = wx.Menu()
        mGenOpt = menuOptions.Append(wx.ID_ANY, "&General Options...", "")
        self.Bind(wx.EVT_MENU, self.OnGeneralAbelOptions, mGenOpt)
        menuOptions.AppendSeparator()
        mSvfOpt = menuOptions.Append(wx.ID_ANY, "&SVF Options...", "")
        self.Bind(wx.EVT_MENU, self.OnSVFOptions, mSvfOpt)
        mIntOpt = menuOptions.Append(wx.ID_ANY, "&Intensity Options...", "")
        self.Bind(wx.EVT_MENU, self.OnIntensityOptions, mIntOpt)
        menuOptions.AppendSeparator()

        mAoiPos = menuOptions.Append(wx.ID_ANY, "Set &Aoi Position...", "")
        self.Bind(wx.EVT_MENU, self.OnAoiPosition, mAoiPos)

        menuBar.Append(menuOptions, "&Options")
        # Construct "About" menu
        menuHelp = wx.Menu()
        mHelp = menuHelp.Append(wx.ID_ANY, "&Filtered Abel transform...", "")
        self.Bind(wx.EVT_MENU, self.OnAbout, mHelp)
        menuBar.Append(menuHelp, "&About")

        # Add all the menus to the Menu Bar
        self.SetMenuBar(menuBar)

        # Initialize parameters
        self.aPanel = AbelPanel(self, -1)
        self.finishedPainting = True
        self.colorPlaneSelect = LUMINANCE
        self.profile = []
        self.plotProfile = []
        self.refprofile = []
        self.plotRefProfile = []
        self.distribution = []
        self.plotDistribution = []
        self.spin = self.FindWindowById(ID_L_THICKNESS)

        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SPINCTRL, self.OnLineThickness, id=ID_L_THICKNESS)
        self.Bind(wx.EVT_TEXT, self.OnLineThickness, id=ID_L_THICKNESS)
        self.Bind(wx.EVT_BUTTON, self.OnSVF, id=ID_BUTTON_SVF)
        self.Bind(wx.EVT_BUTTON, self.OnIntensity, id=ID_BUTTON_INT)

        # called when frame is closed with clicking X button - needed for Linux only
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def showMessage(self, m):
        """ Shows messages from Aoi class. """
        messageDialog(m, '', self)

    def OnLineThickness(self, event):
        """
        Updates the thickness value when spin control is clicked or when
        the text is manually typed in.
        """
        t = self.spin.GetValue()
        if t < self.spin.GetMin():
            self.spin.SetValue(self.spin.GetMin()) # min of allowable range
        if t > self.spin.GetMax():
            self.spin.SetValue(self.spin.GetMax()) # max of allowable range
        self.parentAoi.changeLineThickness(self.spin.GetValue())

    def lockAxisStatus(self):
        """ Called from the Aoi to check the status of the checkbox. """
        return self.aPanel.lockAxis.GetValue() # checkbox true/false

    def OnPaint(self, event):
        dc = wx.PaintDC(self)  #- must get wx.PaintDC (on MSW)
        self.postProfile()
        # draw some items here so they don't flicker
        self.aPanel.drawAxisLabels()
        self.aPanel.drawKey()

    def postProfile(self):
        if self.finishedPainting == True:
            wx.CallAfter(self.refreshProfile)

    def refreshProfile(self):
        """Called by the wx.PostEvent handler."""
        if self.finishedPainting == True:
            self.finishedPainting = False

            self.profile = self.parentAoi.getP()
            self.plotProfile = self.calcPlotProfile(self.profile)

            self.refprofile = self.parentAoi.getRefProfile()
            self.plotRefProfile = self.calcPlotProfile(self.refprofile)

            self.distribution = self.parentAoi.getDistribution()
            self.plotDistribution = self.calcPlotAbelTransform(self.distribution)

            self.aPanel.drawProfile()

            lineLength = str(len(self.profile))
            self.aPanel.drawPixelNumber(lineLength)

            distrValues = self.getYAxisValues(self.distribution)
            yaxislabel = self.parentAoi.getAxisLabel()
            if yaxislabel:
                self.aPanel.drawDistributionLabel(distrValues, yaxislabel)

            while wx.GetApp().Pending():
                wx.GetApp().Dispatch()

            self.finishedPainting = True

    def getYAxisValues(self, distr):
        if not distr:
            return ('', '', '', '', '', '', '', '', '')
        maxDistr = max(distr)
        minDistr = min(distr)
        # if True, means that distr came from live profile, convert to ppm
        # if False, means that distr came from a file which has already
        # been converted to ppm (parts per million)
        if self.parentAoi.multByMillion:
            maxDistr = maxDistr * 1000000
            minDistr = minDistr * 1000000
        span = maxDistr - minDistr
        # format the float values to a left-justified string (of length 4)
        v1 = self.formatYAxisValue(span + minDistr)
        v2 = self.formatYAxisValue((span * 7.0 / 8.0) + minDistr)
        v3 = self.formatYAxisValue((span * 6.0 / 8.0) + minDistr)
        v4 = self.formatYAxisValue((span * 5.0 / 8.0) + minDistr)
        v5 = self.formatYAxisValue((span * 4.0 / 8.0) + minDistr)
        v6 = self.formatYAxisValue((span * 3.0 / 8.0) + minDistr)
        v7 = self.formatYAxisValue((span * 2.0 / 8.0) + minDistr)
        v8 = self.formatYAxisValue((span * 1.0 / 8.0) + minDistr)
        v9 = self.formatYAxisValue(minDistr)
        return (v9,v8,v7,v6,v5,v4,v3,v2,v1)

    def formatYAxisValue(self, v):
        """
        Takes a float and converts to a left-justified string with only
        1 digit right of the decimal point and max of 4 chars long.
        For Zeng-Guang data allow more digits
        """
        if self.parentAoi.isDemo == True and self.parentAoi.isFromImage == False:
            sv = "%.3f" % v
            s = string.ljust(str(sv), 6)
            if len(s) > 6:
                s = s[0:6]  # limit to 6 chars
            # strip off the leading 0
            if v < 0.0:
                minus = s[0:1]
                n = s[2:]
                s = minus + n
            else:
                s = s[1:]
            return s
        else:
            if v < 100.0:
                sv = "%.2f" % v
            else:
                sv = "%.1f" % v
            s = string.ljust(str(sv), 5)
            if len(s) > 5:
                s = s[0:5]  # limit to 5 chars
            return s

    def calcPlotAbelTransform(self, distr):
        if not distr:
            return []
        num = len(distr)
        width, height = self.aPanel.graphPanel.GetSizeTuple()
        hf = float(height)
        xy = []
        p = []
        minDistr = min(distr)
        # make distribution all positive
        p = []
        for a in distr:
            p.append(a - minDistr)
        maxP = max(p)
        for i in range(num):
            x = float(i) / (num-1)*width
            yScaled = hf * float(p[i]) / float(maxP)
            y = height - int(yScaled)
            c = self.validateCoordinates(x, y)
            xy.append((int(c[0]), int(c[1])))
        return xy

    def calcPlotProfile(self, profile):
        if not profile:
            return []
        if self.parentAoi.isDemo:
            profile = self.normalizeData(profile)
        num = len(profile)
        width, height = self.aPanel.graphPanel.GetSizeTuple()
        hf = float(height)
        xy = []
        p = []
        for i in range(num):
            p.append(int(profile[i] * 256.0))
        for i in range(num):
            if p[i] < 0: p[i] = 0
            if p[i] > 255: p[i] = 255
            x = float(i) / (num-1)*width
            nn = hf * float(p[i]) / 255.0
            y = height - int(nn)
            c = self.validateCoordinates(x, y)
            xy.append((int(c[0]), int(c[1])))
        return xy

    def normalizeData(self, data):
        """
        Remaps the data array to the range of 0 to 1.0 to be compatible
        with the other profiles. Note that Demo data ranges from 0 to 3.0.
        """
        if not data:
            return data
        minData = min(data)
        maxData = max(data)
        subt = []
        for a in data:
            subt.append(a - minData)
        out = []
        for a in subt:
            out.append(a * 1.0/(maxData - minData))
        return out

    def validateCoordinates(self, x, y):
        """Make it fit on the graph. Note: the y is inverted (y=0 is on top)"""
        width, height = self.aPanel.graphPanel.GetSizeTuple()
        if x < 0: x = 0
        if x > width: x = width
        if y < 0: y = 0
        if y > height-2: y = height-2  # fudge factor to see the line (on bottom)
        return (x,y)

    def OnLoadAbelGraph(self, event):
        """
        Load a previously saved Abel graph from a text file.
        """
        fd = wx.FileDialog(self, "Load Abel graph", "", "*.txt",
                    "Input file (*.txt)|*.txt|All files (*.*)|*.*", wx.OPEN)
        if fd.ShowModal() == wx.ID_OK:
            if not os.path.isfile(fd.GetPath()):
                messageDialog('file does not exist', '', self)
                path = ''
            else:
                path = fd.GetPath()
        else:
            path = ''
        fd.Destroy()

        if path == '':
            return

        saveData = self.getSavedData(path)
        self.parentAoi.LoadExistingPlot(saveData)
        self.postProfile()

    def getSavedData(self, file):
        """
        Read the previously saved file and return properly formatted.
        """
        if os.path.isfile(file):
            try:
                xval = []
                yval = []
                profile = []
                refprofile = []
                distr = []
                f = open(file, 'r')

                # read header
                header = []
                for i in range(14):
                    header.append(f.readline())

                # read label
                label = header[0]
                label = label[12:]   # strip off unwanted part

                # read Pixel Display Type - it is used to determine whether the
                # pixel format is normalized or actual
                pixType = header[11]  # 12th line
                pixType = pixType[21:]
                pixType = string.strip(pixType) # strip off any "whitespace" chars

                columns = []
                while (1):
                    line = f.readline()
                    if line == "":
                        break
                    columns = string.split(line) # split string into list of numbers
                    if len(columns) == 6:
                        xval.append(columns[1])
                        yval.append(columns[2])
                        profile.append(columns[3])
                        refprofile.append(columns[4])
                        distr.append(columns[5])
                    else:
                        m = 'error - file should contain 6 columns of numbers'
                        messageDialog(m, '', self)
                        break

                f.close()

                # convert to numbers (from string) or set to null
                xout = []
                for i in range(len(xval)):
                    if self.isNumber(xval[i]):
                        xout.append(int(xval[i]))
                    else:
                        xout = []
                        break

                yout = []
                for i in range(len(yval)):
                    if self.isNumber(yval[i]):
                        yout.append(int(yval[i]))
                    else:
                        yout = []
                        break

                pout = []
                for i in range(len(profile)):
                    if self.isNumber(profile[i]):
                        # the output profile must be normalized
                        if pixType == 'Normalized values':
                            normPix = float(profile[i])
                        elif pixType == 'Actual values':
                            normPix = float(profile[i]) / 255.0
                        else:
                            messageDialog('Unrecognized pixType string', '', self)
                        pout.append(normPix)
                    else:
                        pout = []
                        break

                refpout = []
                for i in range(len(refprofile)):
                    if self.isNumber(refprofile[i]):
                        if pixType == 'Normalized values':
                            normPix = float(refprofile[i])
                        elif pixType == 'Actual values':
                            normPix = float(refprofile[i]) / 255.0
                        else:
                            messageDialog('Unrecognized pixType string', '', self)
                        refpout.append(normPix)
                    else:
                        refpout = []
                        break

                dout = []
                for i in range(len(distr)):
                    if self.isNumber(distr[i]):
                        dout.append(float(distr[i]))
                    else:
                        dout = []
                        break
                return (label, xout, yout, pout, refpout, dout)
            except IOError:
                messageDialog('problems reading the file', '', self)
                return None
        else:
            return None

    def isNumber(self, sn):
        'check the string if it is a number - returns True if it is'
        retCode = True
        try:
            n = float(sn)
        except ValueError:
            retCode = False
        return retCode

    def OnLoadDemo(self, event):
        """
        Load Zeng-guang's test data (half of semicircle) which he used in his
        paper. Useful for testing various filtering options.
        """
        self.parentAoi.LoadAbelDemo()
        self.postProfile()

    def OnSave(self, event):
        """
        Save profile and the Abel distribution to a file.
        """
        path = ''
        fd = wx.FileDialog(self, "Save Abel Tool graph", "", "*.txt",
                    "Input file (*.txt)|*.txt|All files (*.*)|*.*", wx.SAVE)
        if fd.ShowModal() == wx.ID_OK:
            path = fd.GetPath()
        else:
            path = ''
        fd.Destroy()

        if path == '':
            return

        profileXY = self.parentAoi.getLineProfileXY()
        profxy = []
        if self.parentAoi.isFromImage:
            intensxy = self.getIntensityXY(profileXY) # take intensity of RGB image
            for pxy in intensxy:
                pix = pxy[0]
                sx = str(pxy[1])
                sy = str(pxy[2])
                profxy.append((pix, sx, sy))
        else:
            xvalues = self.parentAoi.xvalues
            yvalues = self.parentAoi.yvalues
            sx = 'no_x_available'
            sy = 'no_y_available'
            for i in range(len(self.profile)):
                if xvalues:
                    sx = xvalues[i]
                    sy = yvalues[i]
                profxy.append((self.profile[i], sx, sy))

        if self.distribution:
            if len(profxy) != len(self.distribution):
                message = 'lenght of profile and distribution not same'
                messageDialog(message, '', self)
                f.close()
                return

        if self.refprofile:
            if len(profxy) != len(self.refprofile):
                message = 'lenght of profile and ref profile not same'
                messageDialog(message, '', self)
                f.close()
                return

        # write the header
        h0,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12 = self.generateHeader()
        f = open(path, 'w')
        f.write(h0)
        f.write('\n' + h1)
        f.write('\n' + h2)
        f.write('\n' + h3)
        f.write('\n' + h4)
        f.write('\n' + h5)
        f.write('\n' + h6)
        f.write('\n' + h7)
        f.write('\n' + h8)
        f.write('\n' + h9)
        f.write('\n' + h10)
        f.write('\n' + h11)
        f.write('\n' + h12 + '\n' + '\n')

        sd = 'no_distribution'
        sr = 'no_ref_profile'
        num = len(self.profile)
        for i in range(num):
            pxy = profxy[i]
            #pix = str(normalizedToScaled(pxy[0]))
            pix = str(pxy[0])  # saves normalized values
            sx = pxy[1]
            sy = pxy[2]
            if self.refprofile:
                #sr = str(normalizedToScaled(self.refprofile[i]))
                sr = str(self.refprofile[i]) # saves normalized values
            if self.distribution:
                if self.parentAoi.multByMillion:
                    d = self.distribution[i] * 1000000  # put in ppm (parts per million)
                else:
                    d = self.distribution[i]
                sd = "%.6f" % d
                sd = string.rjust(str(sd), 8)
            f.write(str(i)+' '+str(sx)+' '+str(sy)+' '+pix+' '+sr+' '+sd+'\n')
        f.close()

    def generateHeader(self):
        ref = self.refprofile
        yaxislabel = self.parentAoi.getAxisLabel()
        h0 = 'Operation:  ' + yaxislabel
        if self.parentAoi.isFromImage:
            s = 'from image'
            im = Spotlight.currentfile
        else:
            s = 'from file'
            im = 'None used to generate this data'
        h1 = 'Profile Source:  ' + s
        h2 = 'Image: '+ im

        params = self.parentAoi.abel.getParams()
        if params['backgroundSelection'] == 0 or params['referenceImage'] == '':
            r = 'None'
        else:
            if ref:
                r = params['referenceImage']
            else:
                r = 'None'
        h3 = 'Reference image:  ' + r
        thickness = int(self.spin.GetValue())
        h4 = 'Line thickness:  %s' % thickness

        if params['filter'] == 0:
            sfilter = 'Direct Abel transforms'
        elif params['filter'] == 1:
            sfilter = 'Low pass'
        elif params['filter'] == 2:
            sfilter = 'Smoothing w/ a 2-grid'
        else:
            sfilter = 'Smoothing w/ a 4-grid'
        h5 = 'Abel filter:  ' + sfilter
        h6 = 'Smoothing Factor:  ' + str(params['smoothingFactor'])

        if params['averageOption'] == 0:
            aveOption = 'average both sides'
        else:
            aveOption = 'calculate each side separately'
        h7 = 'Averaging Option:  ' + aveOption

        h8 = 'Pixel separation (mm):  ' + str(params['deltaSpacing'])
        if ref: # Abel transform of SVF
            #h8 = 'Pixel separation (mm):  ' + str(params['deltaSpacing'])
            w = params['wavelength'] * 1000  # convert from mm to nm
            h9 = 'Wavelength (nm):  ' + str(w)
            h10 = 'Soot refractive index:  ' + str(params['sri'])
        else:  # Abel transform of Intensity
            #h8 = 'Pixel separation (mm):  ' + 'does not apply'
            h9 = 'Wavelength (nm):  ' + 'does not apply'
            h10 = 'Soot refractive index:  ' + 'does not apply'

        if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
            h11 = 'Pixel display type:  Normalized values'
        else:
            h11 = 'Pixel display type:  Actual values'
        h12 = 'column format:  index, x, y, lineprofile, ref_profile, distribution'
        return (h0,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12)

    def getIntensityXY(self, rgbLine):
        p = []
        n = len(rgbLine)
        for i in range(n):
            colorpxy = rgbLine[i]
            cpix = colorpxy[0]
            x = colorpxy[1]
            y = colorpxy[2]
            lumin = (cpix[0] + cpix[1] + cpix[2]) / 3
            p.append((lumin,x,y))
        return p

    def OnSVF(self, event):
        self.SetCursor(wx.HOURGLASS_CURSOR)
        self.parentAoi.AbelTransformSVF()
        self.SetCursor(wx.STANDARD_CURSOR)
        self.postProfile()

    def OnIntensity(self, event):
        self.SetCursor(wx.HOURGLASS_CURSOR)
        self.parentAoi.AbelTransformIntensity()
        self.SetCursor(wx.STANDARD_CURSOR)
        self.postProfile()

    def OnGeneralAbelOptions(self, event):
        length = len(self.profile)
        d = GeneralAbelOptionsDialog("General Abel Options - common to all", self, length)
        params = self.parentAoi.abel.getParams()
        d.Centre()
        d.setFilter(params['filter'])
        d.setSmoothingFactor(str(params['smoothingFactor']))
        d.setAveragingOption(params['averageOption'])
        d.setDelta(str(params['deltaSpacing']))
        val = d.ShowModal()
        paramsOut = {}
        if val == wx.ID_OK:
            paramsOut = d.getParams()
        d.Destroy()
        if paramsOut:
            self.parentAoi.abel.setParams(paramsOut)

    def OnSVFOptions(self, event):
        d = SVFOptionsDialog("SVF Options", self)
        d.Centre()
        params = self.parentAoi.abel.getParams()
        w = params['wavelength'] * 1000000.0  # display it in nanometers
        d.setWavelength(str(w))
        d.setSRI(str(params['sri']))
        d.setBackgroundSelection(params['backgroundSelection'])
        d.setFilePath(params['referenceImage'])
        left = normalizedToScaled(params['backgroundLeft'])
        right = normalizedToScaled(params['backgroundRight'])
        d.setBackgroundLeft(str(left))
        d.setBackgroundRight(str(right))
        val = d.ShowModal()
        paramsOut = {}
        if val == wx.ID_OK:
            paramsOut = d.getParams()
        d.Destroy()
        if paramsOut:
            self.parentAoi.abel.setParams(paramsOut)

    def OnIntensityOptions(self, event):
        m = 'Currently no Intensity options exits.'
        messageDialog(m, '', self)

    def OnAbout(self, event):
        aboutString = """
Abel transform theory and original source code
was obtained from Dr. Zeng-Guang Yuan, NCMR,
NASA GRC, Cleveland.

Reference:
NASA/CR---2003-212121
Z.G. Yuan, "The Filtered Abel Transform and Its
Application in Combustion Diagnostics"
"""
        messageDialog(aboutString, "", self)

    def OnAoiPosition(self, event):
        """
        Brings up the custom Abel SetAoiPosition dialog box.
        Since the app frame is disabled which Abel dialog is showing, this function
        must be made available somewhere, why not here?
        """
        Spotlight.OnAoiSetPosition()

    def OnCancel(self, event):
        """ Post the event to close dialog and delete aoi. Then get out."""
        self.parentAoi.closeDialog()
        wx.CallAfter(self.frame.deleteAoiFromOnCancel)

    def OnCloseWindow(self, event):
        'called when frame is closed with clicking X button - needed for Linux only'
        self.OnCancel(event)

##--------- SVFOptionsDialog --------------------------

class SVFOptionsDialog(wx.Dialog):
    def __init__(self, title, parent):
        wx.Dialog.__init__(self, parent, -1, title)
        self.parent = parent

        SvfAbelOptionsDialogFunc(self, True)

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateUI) # called when dialog is created
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_SVF_BACKG1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateUI, id=ID_SVF_BACKG2)
        self.Bind(wx.EVT_BUTTON, self.OnGetPath, id=ID_SVF_SEL_RI)

    def OnUpdateUI(self, event):
        'enable/disable controls'
        path = self.FindWindowById(ID_SVF_REF_IMAGE)
        button = self.FindWindowById(ID_SVF_SEL_RI)
        left = self.FindWindowById(ID_SVF_LEFT)
        leftTxt = self.FindWindowById(ID_SVF_LEFT_TEXT)
        right = self.FindWindowById(ID_SVF_RIGHT)
        rightTxt = self.FindWindowById(ID_SVF_RIGHT_TEXT)

        s = self.getBackgroundSelection()
        if s == 0:
            path.Enable(False)
            button.Enable(False)
            left.Enable(True)
            leftTxt.Enable(True)
            right.Enable(True)
            rightTxt.Enable(True)
        else:
            path.Enable(True)
            button.Enable(True)
            left.Enable(False)
            leftTxt.Enable(False)
            right.Enable(False)
            rightTxt.Enable(False)

    def OnGetPath(self, event):
        fileTypes = Spotlight.getImageFileFilter('wxOPEN')
        dir, file = os.path.split(self.getFilePath())
        # get file - from this dialog box's file field
        path = self.getFilePath()
        d2, file = os.path.split(path)
        fd = wx.FileDialog(self, "Open Image", dir, file, fileTypes, wx.OPEN)
        if fd.ShowModal() == wx.ID_OK:
            path = fd.GetPath()
            self.setFilePath(path)
        fd.Destroy()

    def getBackgroundLeft(self):
        widgetId = self.FindWindowById(ID_SVF_LEFT)
        return widgetId.GetValue()
    def setBackgroundLeft(self, s):
        widgetId = self.FindWindowById(ID_SVF_LEFT)
        widgetId.SetValue(s)

    def getBackgroundRight(self):
        widgetId = self.FindWindowById(ID_SVF_RIGHT)
        return widgetId.GetValue()
    def setBackgroundRight(self, s):
        widgetId = self.FindWindowById(ID_SVF_RIGHT)
        widgetId.SetValue(s)

    def getFilePath(self):
        widgetId = self.FindWindowById(ID_SVF_REF_IMAGE)
        return widgetId.GetValue()
    def setFilePath(self, path):
        widgetId = self.FindWindowById(ID_SVF_REF_IMAGE)
        widgetId.SetValue(path)

    def getWavelength(self):
        widgetId = self.FindWindowById(ID_SVF_WAVELENGTH)
        return widgetId.GetValue()
    def setWavelength(self, s):
        widgetId = self.FindWindowById(ID_SVF_WAVELENGTH)
        widgetId.SetValue(s)

    def getSRI(self):
        widgetId = self.FindWindowById(ID_SVF_SRI)
        return widgetId.GetValue()
    def setSRI(self, s):
        widgetId = self.FindWindowById(ID_SVF_SRI)
        widgetId.SetValue(s)

    def getBackgroundSelection(self):
        radio1Id = self.FindWindowById(ID_SVF_BACKG1)
        if radio1Id.GetValue():
            return 0
        else:
            return 1

    def setBackgroundSelection(self, s):
        """ Manually set the radio buttons. """
        radio1Id = self.FindWindowById(ID_SVF_BACKG1)
        radio2Id = self.FindWindowById(ID_SVF_BACKG2)
        if s == 0:
            radio1Id.SetValue(True)
            radio2Id.SetValue(False)
        else:
            radio1Id.SetValue(False)
            radio2Id.SetValue(True)

    def getParams(self):
        valid = True
        if not isValid(self.getWavelength(), 0.0, 100000.0, isFloat=True):
            m = 'improper wavelength -- parameters not saved'
            messageDialog(m, 'Warning', self.parent)
            valid = False
        if not isValid(self.getSRI(), 0.0, 100.0, isFloat=True):
            m = 'improper soot refractive index -- parameters not saved'
            messageDialog(m, 'Warning', self.parent)
            valid = False

        params = {}
        if valid:
            params['wavelength'] = (float(self.getWavelength()))/1000000.0
            params['sri'] = float(self.getSRI())
            params['backgroundSelection'] = int(self.getBackgroundSelection())
            params['referenceImage'] = self.getFilePath()
            params['backgroundLeft'] = scaledToNormalized(float(self.getBackgroundLeft()))
            params['backgroundRight'] = scaledToNormalized(float(self.getBackgroundRight()))
        return params

#---------------- General Abel Options dialog box -----------------------------

class GeneralAbelOptionsDialog(wx.Dialog):
    def __init__(self, title, parent, length):
        wx.Dialog.__init__(self, parent, -1, title)
        self.parent = parent

        GeneralAbelOptionsDialogFunc(self, True)

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateUI) # called when dialog is created
        self.Bind(wx.EVT_RADIOBOX, self.OnUpdateUI, id=ID_ABEL_FILTERS)

        pf_size = length/2.0  # Zeng-guang calls it pf_size
        factorRange = self.FindWindowById(ID_ABEL_RANGE)
        factorRange.SetValue(str(pf_size))
        factorRange.Enable(False)

    def OnUpdateUI(self, event):
        filterId = self.FindWindowById(ID_ABEL_FILTERS)
        filter = filterId.GetSelection()

        t1 = self.FindWindowById(ID_ABELTEXT1)
        t2 = self.FindWindowById(ID_ABELTEXT2)
        t3 = self.FindWindowById(ID_ABELTEXT3)
        sm = self.FindWindowById(ID_ABEL_SMOOTHING_FACTOR)
        if filter == 0:
            t1.Enable(False)
            t2.Enable(False)
            t3.Enable(False)
            sm.Enable(False)
        else:
            t1.Enable(True)
            t2.Enable(True)
            t3.Enable(True)
            sm.Enable(True)

    def getAveragingOption(self):
        averagingId = self.FindWindowById(ID_ABEL_AVERAGING)
        return averagingId.GetSelection()
    def setAveragingOption(self, v):
        averagingId = self.FindWindowById(ID_ABEL_AVERAGING)
        averagingId.SetSelection(v)

    def getFilter(self):
        filterId = self.FindWindowById(ID_ABEL_FILTERS)
        return filterId.GetSelection()
    def setFilter(self, f):
        filterId = self.FindWindowById(ID_ABEL_FILTERS)
        filterId.SetSelection(f)

    def getSmoothingFactor(self):
        smId = self.FindWindowById(ID_ABEL_SMOOTHING_FACTOR)
        return smId.GetValue()
    def setSmoothingFactor(self, s):
        smId = self.FindWindowById(ID_ABEL_SMOOTHING_FACTOR)
        smId.SetValue(s)

    def getDelta(self):
        widgetId = self.FindWindowById(ID_SVF_SEPARATION)
        return widgetId.GetValue()
    def setDelta(self, s):
        widgetId = self.FindWindowById(ID_SVF_SEPARATION)
        widgetId.SetValue(s)

    def getParams(self):
        valid = True
        if not isValid(self.getDelta(), 0.0, 100.0, isFloat=True):
            m = 'improper pixel separation -- parameters not saved'
            messageDialog(m, 'Warning', self.parent)
            valid = False
        if not isValid(self.getSmoothingFactor(), 0.0, 100.0, isFloat=True):
            m = 'improper smoothing factor -- parameters not saved'
            messageDialog(m, 'Warning', self.parent)
            valid = False

        params = {}
        if valid:
            params['deltaSpacing'] = float(self.getDelta())
            params['filter'] = self.getFilter()
            params['averageOption'] = self.getAveragingOption()
            params['smoothingFactor'] = float(self.getSmoothingFactor())
        return params

#---------------------- StandardAoiPositionDialog ---------------------------------

class StandardAoiPositionDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        AoiPositionDialogFunc(self, True)
        self.CentreOnParent()

        wx.EVT_BUTTON(self, ID_POS_SAVE, self.OnSave)
        wx.EVT_BUTTON(self, ID_POS_LOAD, self.OnLoad)

    def OnSave(self, event):
        fd = wx.FileDialog(self, "Save Aoi Positions", "", "*.txt",
                "Text files (*.txt)|*.txt|All files (*.*)|*.*", wx.SAVE)
        if fd.ShowModal() == wx.ID_OK:
            if os.path.isfile(fd.GetPath()):
                message = 'The file already exists - do you want to overwrite it?'
                overwriteFlag = YesNoDialog(message)
                if overwriteFlag:
                    self.savePositionFile(fd.GetPath())
            else:
                self.savePositionFile(fd.GetPath())
        fd.Destroy()

    def savePositionFile(self, filename):
        'save to disk - use pickle to save it'
        if self.areAoiPositionsValid(self.getX1(), self.getY1(), self.getX2(), self.getY2()):
            x1 = int(self.getX1())
            y1 = int(self.getY1())
            x2 = int(self.getX2())
            y2 = int(self.getY2())
            coords = (x1, y1, x2, y2)
            f = open(filename, 'wb')
            pickle.dump(coords, f)
            f.close()

    def areAoiPositionsValid(self, sx1, sy1, sx2, sy2):
        'test that all the aoi coordinates are integers and within the bounds of the image'
        allValid = True
        try:
            x1 = int(sx1)
            y1 = int(sy1)
            x2 = int(sx2)
            y2 = int(sy2)
        except ValueError:
            messageDialog('values are not all valid numbers')
            return False
        imX, imY = Spotlight.getWorkingImageSize()
        if not (allValid and x1 >= 0 and x1 < imX and x2 >= 0 and x2 < imX):
            allValid = False
        if not (allValid and y1 >= 0 and y1 < imY and y2 >= 0 and y2 < imY):
            allValid = False
        if allValid == False:
            messageDialog('invalid value - outside the bounds of the image')
        return allValid

    def OnLoad(self, event):
        fd = wx.FileDialog(self, "Load Aoi coordinates", "", "*.txt",
                "Text files (*.txt)|*.txt|All files (*.*)|*.*", wx.OPEN)
        if fd.ShowModal() == wx.ID_OK:
            self.loadPositionFile(fd.GetPath())
        fd.Destroy()

    def loadPositionFile(self, file):
        """load from disk - use pickle to load it"""
        if not os.path.isfile(file):
            messageDialog('file does not exist')
            return

        try:
            f = open(file, 'rb')
            coords = pickle.load(f)
            sx1 = "%s" % coords[0]
            sy1 = "%s" % coords[1]
            sx2 = "%s" % coords[2]
            sy2 = "%s" % coords[3]
            self.setX1(sx1)
            self.setY1(sy1)
            self.setX2(sx2)
            self.setY2(sy2)
            f.close()
        except:  # catch any exception
            f.close()
            messageDialog('file will not load - probably not a position file')

    def getX1(self):
        a = self.FindWindowById(ID_X1)
        return a.GetValue()
    def setX1(self, v):
        a = self.FindWindowById(ID_X1)
        a.SetValue(v)

    def getY1(self):
        a = self.FindWindowById(ID_Y1)
        return a.GetValue()
    def setY1(self, v):
        a = self.FindWindowById(ID_Y1)
        a.SetValue(v)

    def getX2(self):
        a = self.FindWindowById(ID_X2)
        return a.GetValue()
    def setX2(self, v):
        a = self.FindWindowById(ID_X2)
        a.SetValue(v)

    def getY2(self):
        a = self.FindWindowById(ID_Y2)
        return a.GetValue()
    def setY2(self, v):
        a = self.FindWindowById(ID_Y2)
        a.SetValue(v)

    def getPositionParams(self):
        params = {}
        if self.areAoiPositionsValid(self.getX1(), self.getY1(), self.getX2(), self.getY2()):
            params['x1'] = int(self.getX1())
            params['y1'] = int(self.getY1())
            params['x2'] = int(self.getX2())
            params['y2'] = int(self.getY2())
        return params

#----------------- AbelToolAoiPositionDialog class ------------------------

class AbelToolAoiPositionDialog(wx.Dialog):
    """An AoiPositionDialog box specific to AoiAbelTool"""
    def __init__(self, title, parent):
        wx.Dialog.__init__(self, parent, -1, title)
        self.parent = parent

        # create vertical sizer to hold everything
        box = wx.BoxSizer(wx.VERTICAL)

        # create x,y, and length fields
        self.textX = wx.StaticText(self, -1, "center x",wx.DefaultPosition, wx.DefaultSize)
        self.x = wx.TextCtrl(self, 10, "", wx.DefaultPosition, wx.Size(40,20))
        self.textY = wx.StaticText(self, -1, "center y",wx.DefaultPosition, wx.DefaultSize)
        self.y = wx.TextCtrl(self, 12, "", wx.DefaultPosition, wx.Size(40,20))
        self.textLength = wx.StaticText(self, -1, "length (odd only)",wx.DefaultPosition, wx.DefaultSize)
        self.length = wx.TextCtrl(self, 13, "", wx.DefaultPosition, wx.Size(40,20))

        self.saveButton = wx.Button(self,20, "Save",wx.DefaultPosition, wx.Size(80,25))
        wx.EVT_BUTTON(self,20,self.OnSave)
        self.loadButton = wx.Button(self,21, "Load",wx.DefaultPosition,wx.Size(80,25))
        wx.EVT_BUTTON(self,21,self.OnLoad)

        boxTop = wx.BoxSizer(wx.VERTICAL)

        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box1.Add(self.x, 0, wx.EXPAND|wx.RIGHT, 5)
        box1.Add(self.textX)

        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box2.Add(self.y, 0, wx.EXPAND|wx.RIGHT, 5)
        box2.Add(self.textY)

        box3 = wx.BoxSizer(wx.HORIZONTAL)
        box3.Add(self.length, 0, wx.EXPAND|wx.RIGHT, 5)
        box3.Add(self.textLength)

        box4 = wx.BoxSizer(wx.VERTICAL)
        box4.Add(self.saveButton, 0, wx.EXPAND|wx.LEFT, 45)
        box4.Add(self.loadButton, 0, wx.EXPAND|wx.LEFT, 45)

        box44 = wx.BoxSizer(wx.VERTICAL)
        box44.Add(box4, 0, wx.EXPAND|wx.BOTTOM, 15)

        boxTop.Add(box1, 0, wx.EXPAND|wx.LEFT, 45)
        boxTop.Add(box2, 0, wx.EXPAND|wx.LEFT, 45)
        boxTop.Add(box3, 0, wx.EXPAND|wx.LEFT, 45)

        box.Add(boxTop)
        box.Add(box44)

        # generate boxx (contains OK and Cancel buttons)
        boxX = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self,wx.ID_OK,"OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self,wx.ID_CANCEL,"Cancel")
        boxX.Add(okButton,0, wx.BOTTOM, 15) # pad only bottom with 15
        boxX.Add(cancelButton,0, wx.BOTTOM, 15) # pad only bottom with 15

        box.Add(boxX,0,wx.CENTER)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        box.Fit(self)
        box.SetSizeHints(self)

    def OnSave(self, event):
        fd = wx.FileDialog(self, "Save Aoi Positions", "", "*.txt",
                "Text files (*.txt)|*.txt|All files (*.*)|*.*", wx.SAVE)
        if fd.ShowModal() == wx.ID_OK:
            if os.path.isfile(fd.GetPath()):
                message = 'The file already exists - do you want to overwrite it?'
                overwriteFlag = YesNoDialog(message)
                if overwriteFlag:
                    self.savePositionFile(fd.GetPath())
            else:
                self.savePositionFile(fd.GetPath())
        fd.Destroy()

    def savePositionFile(self, filename):
        'save to disk - use pickle to save it'
        if self.areAoiPositionsValid(self.getX(), self.getY(), self.getLength()):
            x = int(self.getX())
            y = int(self.getY())
            length = int(self.getLength())

            # convert centerpoint and length to line endpoints
            if length > 1:
                half = length / 2
                xx1 = x - half
                yy1 = y
                xx2 = x + half
                yy2 = y

            coords = (xx1, yy1, xx2, yy2)
            f = open(filename, 'wb')
            pickle.dump(coords, f)
            f.close()

    def areAoiPositionsValid(self, sx, sy, slength):
        """test that all the aoi coordinates are integers and within the
        bounds of the image
        """
        allValid = True
        try:
            x = int(sx)
            y = int(sy)
            length = int(slength)
        except ValueError:
            messageDialog('values are not all valid numbers')
            return False
        imX, imY = Spotlight.getWorkingImageSize()
        if not (allValid and x >= 0 and x < imX):
            allValid = False
        if not (allValid and y >= 0 and y < imY):
            allValid = False
        if not (allValid and length >= 0 and length < imX):
            allValid = False
        if allValid == False:
            m = 'invalid value - outside the bounds of the image'
            messageDialog(m)
        if not (allValid and self.odd(length)):
            messageDialog('line length must be an odd value', '', self)
            allValid = False
        return allValid

    def odd(self, a):
        'odd(a) = 1 for odd a, 0 for even a'
        if a % 2:
            return 1
        else:
            return 0

    def OnLoad(self, event):
        fd = wx.FileDialog(self, "Load Aoi coordinates", "", "*.txt",
                "Text files (*.txt)|*.txt|All files (*.*)|*.*", wx.OPEN)
        if fd.ShowModal() == wx.ID_OK:
            self.loadPositionFile(fd.GetPath())
        fd.Destroy()

    def loadPositionFile(self, file):
        """load from disk - use pickle to load it"""
        if not os.path.isfile(file):
            messageDialog('file does not exist')
            return

        try:
            f = open(file, 'rb')
            coords = pickle.load(f)
            x1 = coords[0]
            y1 = coords[1]
            x2 = coords[2]
            y2 = coords[3]

            # convert to centerpoint and length
            centerx = (x1 + x2)/2
            centery = (y1 + y2)/2
            length = x2 - x1 + 1

            scenterx = "%s" % centerx
            scentery = "%s" % centery
            slength = "%s" % length

            self.setX(scenterx)
            self.setY(scentery)
            self.setLength(slength)
            f.close()
        except:  # catch any exception
            f.close()
            m = 'file will not load - probably not a Abel position file'
            messageDialog(m)

    def getX(self):
        return self.x.GetValue()
    def setX(self, a):
        self.x.SetValue(a)
    def getY(self):
        return self.y.GetValue()
    def setY(self, a):
        self.y.SetValue(a)
    def getLength(self):
        return self.length.GetValue()
    def setLength(self, a):
        self.length.SetValue(a)

#----------------- SnakeAoiPositionDialog class ------------------------

class SnakeAoiPositionDialog(wx.Dialog):
    'an AoiPositionDialog box specific to AoiSnake'
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        msg = 'Note: only move is currently\nsupported for snake '
        message = wx.StaticText(self, -1, msg, wx.DefaultPosition, wx.DefaultSize)
        boxMessage = wx.BoxSizer(wx.HORIZONTAL)
        boxMessage.Add(message)

        self.textX = wx.StaticText(self, -1, "center x",wx.DefaultPosition, wx.DefaultSize)
        self.x = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(40,20))
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box1.Add(self.x, 0, wx.EXPAND|wx.RIGHT, 5)
        box1.Add(self.textX)

        self.textY = wx.StaticText(self, -1, "center y",wx.DefaultPosition, wx.DefaultSize)
        self.y = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(40,20))
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box2.Add(self.y, 0, wx.EXPAND|wx.RIGHT, 5)
        box2.Add(self.textY)

        self.saveButton = wx.Button(self,20, "Save",wx.DefaultPosition, wx.Size(80,25))
        wx.EVT_BUTTON(self,20,self.OnSave)
        self.loadButton = wx.Button(self,21, "Load",wx.DefaultPosition,wx.Size(80,25))
        wx.EVT_BUTTON(self,21,self.OnLoad)

        box3 = wx.BoxSizer(wx.VERTICAL)
        box3.Add(self.saveButton)
        box3.Add(self.loadButton)

        box4 = wx.BoxSizer(wx.VERTICAL)  # used to position box3
        box4.Add(box3, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 10)

        # create vertical sizer to hold everything
        box = wx.BoxSizer(wx.VERTICAL)

        box.Add(boxMessage, 0, wx.EXPAND|wx.ALL, 10)
        box.Add(box1, 0, wx.EXPAND|wx.LEFT, 40)
        box.Add(box2, 0, wx.EXPAND|wx.LEFT, 40)
        box.Add(box4, 0, wx.EXPAND|wx.LEFT, 40)

        # generate boxx (contains OK and Cancel buttons)
        boxX = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self,wx.ID_OK,"OK", size=(70, -1))
        okButton.SetDefault()
        cancelButton = wx.Button(self,wx.ID_CANCEL,"Cancel", size=(70, -1))
        boxX.Add(okButton,0, wx.BOTTOM, 10) # pad only bottom with 15
        boxX.Add(cancelButton,0, wx.BOTTOM, 10) # pad only bottom with 15

        box.Add(boxX,0,wx.CENTER)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        box.Fit(self)
        box.SetSizeHints(self)

    def OnSave(self, event):
        fd = wx.FileDialog(self, "Save Aoi Positions", "", "*.txt",
                "Text files (*.txt)|*.txt|All files (*.*)|*.*", wx.SAVE)
        if fd.ShowModal() == wx.ID_OK:
            if os.path.isfile(fd.GetPath()):
                message = 'The file already exists - do you want to overwrite it?'
                overwriteFlag = YesNoDialog(message)
                if overwriteFlag:
                    self.savePositionFile(fd.GetPath())
            else:
                self.savePositionFile(fd.GetPath())
        fd.Destroy()

    def savePositionFile(self, filename):
        'save to disk - use pickle to save it'
        params = self.getParams()
        x1 = int(params['x1'])
        y1 = int(params['y1'])
        x2 = int(params['x2'])
        y2 = int(params['y2'])
        coords = (x1, y1, x2, y2)
        f = open(filename, 'wb')
        pickle.dump(coords, f)
        f.close()

    def OnLoad(self, event):
        fd = wx.FileDialog(self, "Load Aoi coordinates", "", "*.txt",
                "Text files (*.txt)|*.txt|All files (*.*)|*.*", wx.OPEN)
        if fd.ShowModal() == wx.ID_OK:
            self.loadPositionFile(fd.GetPath())
        fd.Destroy()

    def loadPositionFile(self, file):
        'load from disk - use pickle to load it'
        if not os.path.isfile(file):
            messageDialog('file does not exist')
            return

        try:
            f = open(file, 'rb')
            coords = pickle.load(f)
            params = {}
            params['x1'] = coords[0]
            params['y1'] = coords[1]
            params['x2'] = coords[2]
            params['y2'] = coords[3]
            self.setParams(params)
            f.close()
        except:  # catch any exception
            f.close()
            messageDialog('file will not load - probably not a position file')

    def getX(self):
        return self.x.GetValue()
    def setX(self, a):
        self.x.SetValue(a)
    def getY(self):
        return self.y.GetValue()
    def setY(self, a):
        self.y.SetValue(a)

    def getParams(self):
        newCenterX = int(self.getX())
        newCenterY = int(self.getY())
        params = {}
        if self.areAoiPositionsValid(newCenterX, newCenterY):
            offsetX = newCenterX - self.centerX
            offsetY = newCenterY - self.centerY
            x1 = self.x1 + offsetX
            y1 = self.y1 + offsetY
            x2 = self.x2 + offsetX
            y2 = self.y2 + offsetY
            params['x1'] = x1
            params['y1'] = y1
            params['x2'] = x2
            params['y2'] = y2
        return params

    def setParams(self, params):
        self.x1 = int(params['x1'])
        self.y1 = int(params['y1'])
        self.x2 = int(params['x2'])
        self.y2 = int(params['y2'])
        self.centerX = (self.x1 + self.x2)/2
        self.centerY = (self.y1 + self.y2)/2
        sx = "%s" % self.centerX
        sy = "%s" % self.centerY
        self.setX(sx)
        self.setY(sy)

    def areAoiPositionsValid(self, sx, sy):
        """test that all the aoi coordinates are integers and within the
        bounds of the image
        """
        allValid = True
        try:
            x = int(sx)
            y = int(sy)
        except ValueError:
            messageDialog('values are not all valid numbers')
            return False
        imX, imY = Spotlight.getWorkingImageSize()
        if not (allValid and x >= 0 and x < imX):
            allValid = False
        if not (allValid and y >= 0 and y < imY):
            allValid = False
        if allValid == False:
            m = 'invalid value - outside the bounds of the image'
            messageDialog(m)
        return allValid

#-------------- Statistics Dialog ----------------------------

class statisticsDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)
        pos = wx.DefaultPosition

        box = wx.BoxSizer(wx.VERTICAL)

        sampleList = ['min,max,mean,stdev', 'histogram (rectangle aoi)',
                                'line profile (line aoi)', 'area (of thresholded white pixels)']
        numberOfColumns = 1
        self.rb = wx.RadioBox(self, 10, "Image Statistics", wx.DefaultPosition,
                wx.DefaultSize, sampleList, numberOfColumns, wx.RA_SPECIFY_COLS)

        # This box would expand the radio box into the dialog box
        box.Add(self.rb, 0, wx.EXPAND|wx.ALL, 10)

        boxX = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self,wx.ID_OK,"OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self,wx.ID_CANCEL,"Cancel")
        boxX.Add(okButton,0, wx.EXPAND|wx.BOTTOM|wx.RIGHT, 10) # pad only bottom with 15
        boxX.Add(cancelButton,0, wx.EXPAND|wx.BOTTOM|wx.LEFT, 10) # pad only bottom with 15

        box.Add(boxX, 0, wx.CENTER)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        box.Fit(self)
        box.SetSizeHints(self)

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateUI) # called when dialog is created

    def OnUpdateUI(self, event):
        'enable/disable controls'
        aoi = Spotlight.aList.getCurrentAoi()
        className = aoi.__class__.__name__

        if className == 'AoiLine' or className == 'AoiLineProfile':
            self.rb.EnableItem(0, False)
            self.rb.EnableItem(1, False)
            self.rb.EnableItem(2, True)
            self.rb.EnableItem(3, False)
            # make sure that the dot on the radio button is on AoiLine
            self.setStatistic(2)
        else:
            self.rb.EnableItem(0, True)
            self.rb.EnableItem(1, True)
            self.rb.EnableItem(2, False)
            self.rb.EnableItem(3, True)
            # make sure that radio button is not on line aoi option
            pos = self.getStatistic()
            if pos == 2:
                self.setStatistic(0)

    def getStatistic(self):
        return self.rb.GetSelection()
    def setStatistic(self, type):
        self.rb.SetSelection(type)

#---------------- Test dialog box -----------------------------

class TestDialog(wx.Dialog):
    def __init__(self, command, id, title,
        pos = wx.DefaultPosition, size = wx.DefaultSize,
        style = wx.DEFAULT_DIALOG_STYLE ):
        wx.Dialog.__init__(self, frame, id, title, pos, size, style)
        self.command = command

        #self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)) # for testing

        TestDialogFunc( self, True )
        self.CentreOnParent()

        # WDR: handler declarations for ThresholdDialog
        wx.EVT_SLIDER(self, ID_FACTOR_SLIDER, self.OnSlider)

    # WDR: methods for ThresholdDialog

    def GetTestSlider(self):
        return self.FindWindowById(ID_FACTOR_SLIDER)

    def GetThreshold(self):
        return self.FindWindowById(ID_FACTOR)

    # WDR: handler implementations for ThresholdDialog

    def OnSlider(self, event):
        sliderValue = self.GetTestSlider().GetValue()
        #v = str(actualToScaled(sliderValue))
        v = str(sliderValue)
        self.GetThreshold().SetValue(v)
        self.execute()

    def execute(self):
        threshold = float(self.GetThreshold().GetValue())
        self.command.executeTest(threshold)

    def getParams(self):
        params = {}
        threshold = float(self.GetThreshold().GetValue())
        params['test'] = threshold
        return params

#--------------- Program Options dialog box -------------------------------------

class OptionsDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        OptionsDialogFunc(self, True)

        self.Bind(wx.EVT_INIT_DIALOG, self.OnUpdateUI) # called when dialog is created
        self.Bind(wx.EVT_CHECKBOX, self.OnSetCheck1, id=ID_SQUARE_PIXELS)
        self.Bind(wx.EVT_CHECKBOX, self.OnSetCheck2, id=ID_ARBITRARY_ASPECT)
        self.Bind(wx.EVT_BUTTON, self.OnSelectPalette, id=ID_SELECT_PALETTE)

    def getNotebookTab(self):
        t = self.FindWindowById(ID_OPTIONS_DIALOG)
        return t.GetSelection()
    def setNotebookTab(self, tab):
        ntab = int(tab)
        t = self.FindWindowById(ID_OPTIONS_DIALOG)
        t.SetSelection(ntab)

    def getColor(self):
        a = self.FindWindowById(ID_BACKGROUND_COLORS)
        return a.GetStringSelection()
    def setColor(self, color):
        a = self.FindWindowById(ID_BACKGROUND_COLORS)
        a.SetStringSelection(color)

    def getPaletteDisplaySelection(self):
        a = self.FindWindowById(ID_APPLY_PALETTE)
        return a.GetValue()
    def setPaletteDisplaySelection(self, flag):
        a = self.FindWindowById(ID_APPLY_PALETTE)
        a.SetValue(flag)

    def getPaletteFilePath(self):
        a = self.FindWindowById(ID_PALETTE_FILE)
        return a.GetValue()
    def setPaletteFilePath(self, v):
        a = self.FindWindowById(ID_PALETTE_FILE)
        a.SetValue(v)

    def OnSelectPalette(self, event):
        lutDir, lutFile = os.path.split(self.getPaletteFilePath())
        fd = wx.FileDialog(self, "Open palette", lutDir, lutFile,
                "Palette file (*.dat; *.DAT)|*.dat; *.DAT", wx.OPEN)
        val = fd.ShowModal()
        if val == wx.ID_OK:
            self.setPaletteFilePath(os.path.abspath(fd.GetPath()))
        fd.Destroy()

    def getPixelDisplayValues(self):
        a = self.FindWindowById(ID_PIXEL_TYPE)
        return a.GetSelection()
    def setPixelDisplayValues(self, v):
        a = self.FindWindowById(ID_PIXEL_TYPE)
        a.SetSelection(v)

    ##------------ Correct image aspect ratio -----------------------------

    ## The way these two checkboxes work in tandem is to simulate a three
    ## radio buttons. This simplifies the code in Spotlight.py.

    def OnUpdateUI(self, event):
        'enable/disable aspect ratio text control at startup'
        self.OnSetCheck2(event)

    def getArbitraryWidth(self):
        a = self.FindWindowById(ID_ASPECT_RATIO)
        return a.GetValue()
    def setArbitraryWidth(self, v):
        a = self.FindWindowById(ID_ASPECT_RATIO)
        a.SetValue(v)

    def getWidthSelection1(self):
        """Checkbox1"""
        a = self.FindWindowById(ID_SQUARE_PIXELS)
        return a.GetValue()
    def setWidthSelection1(self, flag):
        a = self.FindWindowById(ID_SQUARE_PIXELS)
        a.SetValue(flag)

    def getWidthSelection2(self):
        """Checkbox2"""
        a = self.FindWindowById(ID_ARBITRARY_ASPECT)
        return a.GetValue()
    def setWidthSelection2(self, flag):
        a = self.FindWindowById(ID_ARBITRARY_ASPECT)
        a.SetValue(flag)

    def OnSetCheck1(self, event):
        """
        If checkbox1 is checked then uncheck checkbox2 and gray out the textCtrl.
        """
        chk1 = self.getWidthSelection1()
        if chk1 == 1:
            self.setWidthSelection2(0)
            a = self.FindWindowById(ID_ASPECT_RATIO)
            a.Enable(False)

    def OnSetCheck2(self, event):
        """
        If checkbox2 is checked then uncheck checkbox1 and enable the textCtrl.
        """
        chk2 = self.getWidthSelection2()
        a = self.FindWindowById(ID_ASPECT_RATIO)
        if chk2 == 1:
            self.setWidthSelection1(0)
            a.Enable(True)
        else:
            a.Enable(False)

    def setDVCorrectionType(self, flag):
        """
        Input is one of 3 possible values and this sets the two checkboxes to
        those 3 possible states (top is checked, bottom is checked, or neither
        is checked).
        """
        a = self.FindWindowById(ID_SQUARE_PIXELS)
        b = self.FindWindowById(ID_ARBITRARY_ASPECT)
        if flag == 0:
            a.SetValue(1)
            b.SetValue(0)
        elif flag == 1:
            a.SetValue(0)
            b.SetValue(1)
        else:
            a.SetValue(0)
            b.SetValue(0)

    def getDVCorrectionType(self):
        """
        Converts the two checkbox settings into a single number 0, 1, or 2.
        """
        a = self.FindWindowById(ID_SQUARE_PIXELS)
        b = self.FindWindowById(ID_ARBITRARY_ASPECT)
        chk1 = a.GetValue()
        chk2 = b.GetValue()
        if chk1==1 and chk2==0:
            selection = 0
        elif chk1==0 and chk2==1:
            selection = 1
        else:
            selection = 2
        return selection

    def getParams(self):
        valid = True
        if not isValid(self.getArbitraryWidth(), 4, 5000, isFloat=False):
            m = 'Image width adjustment is out of range (4 - 5000)'
            messageDialog(m)
            valid = False

        if not os.path.isfile(self.getPaletteFilePath()):
            if self.getPaletteFilePath() == '':
                pass  # don't flag it if path is empty - will be flagged later
            else:
                messageDialog('Invalid palette path -- file does not exist')
                valid = False

        params = {}
        if valid:
            params['backgroundColor'] = self.getColor()
            params['paletteDisplay'] = self.getPaletteDisplaySelection()
            params['latestLUTPath'] = self.getPaletteFilePath()
            params['dvCorrectionType'] = self.getDVCorrectionType()
            params['arbitraryWidth'] = int(self.getArbitraryWidth())
            params['pixelValues'] = self.getPixelDisplayValues()
            params['dialogBoxTab'] = self.getNotebookTab()
        return params

#--------------------  Scale Tool dialog box --------------------------------------

class ScaleDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        ScaleDialogFunc( self, True )
        self.CentreOnParent()

        # WDR: handler declarations
        wx.EVT_BUTTON(self, ID_SAVE_SCALE_BUTTON, self.OnSave)
        wx.EVT_BUTTON(self, ID_LOAD_SCALE_BUTTON, self.OnLoad)
        wx.EVT_BUTTON(self, ID_SCALE_RESET_BUTTON, self.OnReset)

        wx.EVT_BUTTON(self, wx.ID_OK, self.OnOk)
        wx.EVT_BUTTON(self, wx.ID_CANCEL, self.OnCancel)

    # WDR: methods
    def GetUserUnits(self):
        return self.FindWindowById(ID_SCALE_UNITS)

    def GetPixelUnits(self):
        return self.FindWindowById(ID_SCALE_PIXELS)

    def GetTimeUnits(self):
        return self.FindWindowById(ID_SCALE_TIME)

    def OnOk(self, event):
        Spotlight.ScaleOk()

    def OnCancel(self, event):
        Spotlight.ScaleCancel()

    def OnSave(self, event):
        fd = wx.FileDialog(self, "Save Scale Values", "", "*.*",
                "Text files (*.txt)|*.txt|All files (*.*)|*.*", wx.SAVE)
        if fd.ShowModal() == wx.ID_OK:
            if os.path.isfile(fd.GetPath()):
                message = 'The file already exists - do you want to overwrite it?'
                overwriteFlag = YesNoDialog(message)
                if overwriteFlag:
                    self.saveScaleFile(fd.GetPath())
            else:
                self.saveScaleFile(fd.GetPath())
        fd.Destroy()

    def saveScaleFile(self, filename):
        'save to disk - use pickle to save it'
        su = self.GetUserUnits().GetValue()
        sp = self.GetPixelUnits().GetValue()
        st = self.GetTimeUnits().GetValue()
        if self.areValuesValid(su, sp, st):
            fu = float(su)
            fp = float(sp)
            ft = float(st)
            scaleValues = (fu, fp, ft)
            f = open(filename, 'wb')
            pickle.dump(scaleValues, f)
            f.close()

    def areValuesValid(self, su, sp, st):
        allValid = True
        try:
            fu = float(su)
            fp = float(sp)
            ft = float(st)
        except ValueError:
            messageDialog('values are not all valid numbers')
            allValid = False
        return allValid

    def OnLoad(self, event):
        fd = wx.FileDialog(self, "Load Scale Values", "", "*.txt",
                "Text files (*.txt)|*.txt|All files (*.*)|*.*", wx.OPEN)
        if fd.ShowModal() == wx.ID_OK:
            self.loadScaleFile(fd.GetPath())
        fd.Destroy()

    def loadScaleFile(self, file):
        """load from disk - use pickle to load it"""
        if not os.path.isfile(file):
            messageDialog('file does not exist')
            return

        try:
            f = open(file, 'rb')
            scaleValues = pickle.load(f)
            fu = "%s" % scaleValues[0]
            fp = "%s" % scaleValues[1]
            ft = "%s" % scaleValues[2]
            self.GetUserUnits().SetValue(fu)
            self.GetPixelUnits().SetValue(fp)
            self.GetTimeUnits().SetValue(ft)
            f.close()
        except:  # catch any exception
            f.close()
            messageDialog('file will not load - probably not a scale file')

    def OnReset(self, event):
        'sets scale back to pixel units'
        Spotlight.setScaleUserUnits(1.0)
        Spotlight.setScalePixelUnits(1.0)
        Spotlight.setPixelScale(1.0)
        Spotlight.setTimeScale(1.0)
        self.GetUserUnits().SetValue(str(1.0))
        self.GetPixelUnits().SetValue(str(1.0))
        self.GetTimeUnits().SetValue(str(1.0))

#---------------- Enhance dialog box -----------------------------

class EnhanceDialog(wx.Dialog):
    def __init__(self, command, id, title,
        pos = wx.DefaultPosition, size = wx.DefaultSize,
        style = wx.DEFAULT_DIALOG_STYLE ):
        wx.Dialog.__init__(self, frame, id, title, pos, size, style)
        self.command = command

        EnhanceDialogFunc( self, True )
        self.CentreOnParent()

        # WDR: handler declarations for ThresholdDialog
        wx.EVT_SLIDER(self, ID_BRIGHTNESS_SLIDER, self.OnBrightnessSlider)
        wx.EVT_SLIDER(self, ID_CONTRAST_SLIDER, self.OnContrastSlider)

    def GetBrightnessSlider(self):
        return self.FindWindowById(ID_BRIGHTNESS_SLIDER)
    def GetBrightness(self):
        return self.FindWindowById(ID_BRIGHTNESS)

    def GetContrastSlider(self):
        return self.FindWindowById(ID_CONTRAST_SLIDER)
    def GetContrast(self):
        return self.FindWindowById(ID_CONTRAST)

#-----------

    #~ def OnBrightnessSlider(self, event):
        #~ sliderValue = self.GetBrightnessSlider().GetValue()
        #~ v = str(sliderValue/100.0)
        #~ print 'v: ', v
        #~ self.GetBrightness().SetValue(v)
        #~ self.execute()

    #~ def execute(self):
        #~ brightness = float(self.GetBrightness().GetValue())
        #~ wxCallAfter(self.executeBrightness, brightness)

    #~ def executeBrightness(self, brightness):
        #~ self.command.executeBrightness(brightness)

    #~ def getParams(self):
        #~ params = {}
        #~ brightness = float(self.GetBrightness().GetValue())
        #~ params['brightness'] = brightness
        #~ return params

#~ #-----------

    def OnBrightnessSlider(self, event):
        sliderValue = self.GetBrightnessSlider().GetValue()
        v = str(sliderValue-100)
        self.GetBrightness().SetValue(v)
        wx.CallAfter(self.executeBrightness, sliderValue)

    def executeBrightness(self, brightness):
        self.command.executeBrightness(brightness)

    def OnContrastSlider(self, event):
        sliderValue = self.GetContrastSlider().GetValue()
        v = str(sliderValue-100)
        self.GetContrast().SetValue(v)
        wx.CallAfter(self.executeContrast, sliderValue)

    def executeContrast(self, contrast):
        self.command.executeContrast(contrast)

    def getParams(self):
        params = {}
        brightness = int(self.GetBrightness().GetValue())+100
        params['brightness'] = brightness
        return params

#-------- Convert Image dialog -- converts type and/or depht ------------

class convertImageDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        ConvertDialogFunc(self, True)

        color = self.FindWindowById(ID_CONVERT_COLOR)
        if Spotlight.originalMode == 'L':
            self.setColorTypeSelection(0)
            color.EnableItem(0, True)
            color.EnableItem(1, False)
        else:
            self.setColorTypeSelection(1)
            color.EnableItem(1, True)
            color.EnableItem(0, False)

        imDepth = 8
        d = self.FindWindowById(ID_CONVERT_DEPTH)
        if imDepth == 8:
            self.setDepthSelection(0)
            #d.EnableItem(0, True)
            d.EnableItem(0, False)  ## disable - depht not applicable for 8-bit Spotlight
            d.EnableItem(1, False)
        else:
            self.setDepthSelection(1)
            d.EnableItem(1, True)
            d.EnableItem(0, False)

    def getNotebookTab(self):
        t = self.FindWindowById(ID_CONVERT_DIALOG)
        return t.GetSelection()
    def setNotebookTab(self, tab):
        ntab = int(tab)
        t = self.FindWindowById(ID_CONVERT_DIALOG)
        t.SetSelection(ntab)

    def getColorTypeSelection(self):
        a = self.FindWindowById(ID_CONVERT_COLOR)
        return a.GetSelection()
    def setColorTypeSelection(self, t):
        a = self.FindWindowById(ID_CONVERT_COLOR)
        a.SetSelection(t)

    def getDepthSelection(self):
        a = self.FindWindowById(ID_CONVERT_DEPTH)
        return a.GetSelection()
    def setDepthSelection(self, d):
        a = self.FindWindowById(ID_CONVERT_DEPTH)
        a.SetSelection(d)

    def getParams(self):
        params = {'operation': self.getNotebookTab(),
                            'type': self.getColorTypeSelection(),
                            'depth': self.getDepthSelection()}
        return params

#--------------------- AoiRectangle Options -----------------------------

class RectangleAoiOptionsDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        RectangleAoiOptionsDialogFunc(self, True)

    def getWidth(self):
        a = self.FindWindowById(ID_RESIZE_WIDTH)
        return a.GetValue()
    def setWidth(self, value):
        a = self.FindWindowById(ID_RESIZE_WIDTH)
        a.SetValue(str(value))

    def getHeight(self):
        a = self.FindWindowById(ID_RESIZE_HEIGHT)
        return a.GetValue()
    def setHeight(self, value):
        a = self.FindWindowById(ID_RESIZE_HEIGHT)
        a.SetValue(str(value))

    def getAspectFlag(self):
        a = self.FindWindowById(ID_FIXED_ASPECT)
        return a.GetValue()
    def setAspectFlag(self, flag):
        a = self.FindWindowById(ID_FIXED_ASPECT)
        a.SetValue(flag)

    def getParams(self):
        params = {'newWidth': int(self.getWidth()),
                            'newHeight': int(self.getHeight()),
                            'fixedAspect': self.getAspectFlag()}
        return params


class RectAoiOptionsDialog(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, frame, -1, title)

        RectAoiOptionsDialogFunc(self, True)

    def getWidth(self):
        a = self.FindWindowById(ID_RESIZE_WIDTH)
        return a.GetValue()
    def setWidth(self, value):
        a = self.FindWindowById(ID_RESIZE_WIDTH)
        a.SetValue(str(value))

    def getHeight(self):
        a = self.FindWindowById(ID_RESIZE_HEIGHT)
        return a.GetValue()
    def setHeight(self, value):
        a = self.FindWindowById(ID_RESIZE_HEIGHT)
        a.SetValue(str(value))

    #~ def getAspectFlag(self):
        #~ a = self.FindWindowById(ID_FIXED_ASPECT)
        #~ return a.GetValue()
    def setAspectFlag(self, flag):
        pass
        #~ a = self.FindWindowById(ID_FIXED_ASPECT)
        #~ a.SetValue(flag)

    def getParams(self):
        params = {'newWidth': int(self.getWidth()),
                            'newHeight': int(self.getHeight()),
                            'fixedAspect': True}
        return params
