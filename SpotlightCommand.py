import os
import pickle
import string
import SpotlightAoi
import Spotlight
import SpotlightGui
from PIL import Image
import PilProcess
import math

class mtCommand:
    def __init__(self):
        self.params = None
        self.undoBitmap = None
        self.undoRect = ()
        self.undoAoi = None
        self.name = ''

    def showDialog(self):
        pass
    def do(self):
        pass
    def undo(self):
        pass
    def execute(self, aoi):
        pass
    def isRedoable(self):
        return True
    def initialize(self, aoi):
        pass
    def getHeader(self):
        return ()
    def getData(self):
        return []
    def updateName(self):
        pass

    def getStartCoords(self, aoiSize, prevAoi, aoiName):
        """
        Figures out the position of the AOI, taking the zoom/scroll
        into account.
        """
        x,y,w,h = SpotlightGui.gui.iPanel.getZoomedRect()
        x1 = x + w/8
        y1 = y + h/8
        x2 = x1 + aoiSize[0]
        y2 = y1 + aoiSize[1]
        # if the previous aoi was same as this one, offset by 10 pixels
        if prevAoi:
            if prevAoi.__class__.__name__ == aoiName:
                if prevAoi.x1 > x and prevAoi.y1 > y and  prevAoi.x2 < x+w and prevAoi.y2 < y+h:
                    x1 = prevAoi.x1 + 10
                    y1 = prevAoi.y1 + 10
                    x2 = prevAoi.x2 + 10
                    y2 = prevAoi.y2 + 10
        return (x1, y1, x2, y2)

#------------- New WholeImage class ------------------------

class cmdNewAoiWholeImage(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'WholeImage'
        self.newAoi = None

    def initialize(self, prevAoi):
        imX, imY = Spotlight.getWorkingImageSize()
        self.newAoi = SpotlightAoi.AoiWholeImage(0, 0, imX, imY)

    def do(self, aoi):
        Spotlight.aList.setNewAoi(self.newAoi)

#------------- New Rectangle class ------------------------

class cmdNewAoiRectangle(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'Rectangle'
        self.newAoi = None

    def initialize(self, prevAoi):
        x1, y1, x2, y2 = self.getStartCoords((70, 70), prevAoi, 'AoiRectangle')
        self.newAoi = SpotlightAoi.AoiRectangle(x1, y1, x2, y2)

        # if the previous aoi was same as this one, copy previous ipSequenceList
        if prevAoi:
            if prevAoi.__class__.__name__ == 'AoiRectangle':
                prevSeqList = prevAoi.getDuplicateSeqList()
                self.newAoi.setSeqList(prevSeqList)

    def do(self, aoi):
        Spotlight.aList.setNewAoi(self.newAoi)
        self.undoAoi = Spotlight.aList.getCurrentAoi()

    def undo(self):
        Spotlight.aList.deleteCurrentAoi()


#---------------- New Line Profile class ------------------------

class cmdNewAoiLineProfile(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'LineProfile'
        self.newAoi = None

    def initialize(self, prevAoi):
        x1, y1, x2, y2 = self.getStartCoords((10, 70), prevAoi, 'AoiLineProfile')
        self.newAoi = SpotlightAoi.AoiLineProfile(x1, y1, x2, y2)

        # if the previous aoi was same as this one copy previous ipSequenceList
        if prevAoi:
            if prevAoi.__class__.__name__ == 'AoiLineProfile':
                prevSeqList = prevAoi.getDuplicateSeqList()
                self.newAoi.setSeqList(prevSeqList)

    def do(self, aoi):
        self.newAoi.initialize()
        Spotlight.aList.setNewAoi(self.newAoi)
        self.undoAoi = Spotlight.aList.getCurrentAoi()

    def undo(self):
        self.undoAoi.deinitialize()
        Spotlight.aList.deleteCurrentAoi()

#-------------- New Histogram class ----------------------------

class cmdNewAoiHistogram(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'Histogram'
        self.newAoi = None

    def initialize(self, prevAoi):
        x1, y1, x2, y2 = self.getStartCoords((50, 50), prevAoi, 'AoiHistogram')
        self.newAoi = SpotlightAoi.AoiHistogram(x1, y1, x2, y2)

        # if the previous aoi was same as this one copy previous ipSequenceList
        if prevAoi:
            if prevAoi.__class__.__name__ == 'AoiHistogram':
                prevSeqList = prevAoi.getDuplicateSeqList()
                self.newAoi.setSeqList(prevSeqList)

    def do(self, aoi):
        self.newAoi.initialize()
        Spotlight.aList.setNewAoi(self.newAoi)
        self.undoAoi = Spotlight.aList.getCurrentAoi()

    def undo(self):
        self.undoAoi.deinitialize()
        Spotlight.aList.deleteCurrentAoi()

#--------------- New AngleTool class ----------------------------

class cmdNewAoiAngleTool(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'AngleTool'
        self.newAoi = None

    def initialize(self, prevAoi):
        x1, y1, x2, y2 = self.getStartCoords((10, 70), prevAoi, 'AoiAngleTool')
        self.newAoi = SpotlightAoi.AoiAngleTool(x1, y1, x2, y2)

        # if the previous aoi was same as this one copy previous ipSequenceList
        if prevAoi:
            if prevAoi.__class__.__name__ == 'AoiAngleTool':
                prevSeqList = prevAoi.getDuplicateSeqList()
                self.newAoi.setSeqList(prevSeqList)

    def do(self, aoi):
        Spotlight.aList.setNewAoi(self.newAoi)
        self.undoAoi = Spotlight.aList.getCurrentAoi()

    def undo(self):
        Spotlight.aList.deleteCurrentAoi()

#---------------- New Abel Tool class ------------------------

class cmdNewAoiAbelTool(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'AbelTool'
        self.newAoi = None

    def initialize(self, prevAoi):
        x1, y1, x2, y2 = self.getStartCoords((70, 0), prevAoi, 'AoiAbelTool')
        self.newAoi = SpotlightAoi.AoiAbelTool(x1, y1, x2, y2) # length=71

        # if the previous aoi was same as this one copy previous ipSequenceList
        if prevAoi:
            if prevAoi.__class__.__name__ == 'AoiAbelTool':
                prevSeqList = prevAoi.getDuplicateSeqList()
                self.newAoi.setSeqList(prevSeqList)

    def do(self, aoi):
        self.newAoi.initialize()
        Spotlight.aList.setNewAoi(self.newAoi)
        self.undoAoi = Spotlight.aList.getCurrentAoi()

    def undo(self):
        self.undoAoi.deinitialize()
        Spotlight.aList.deleteCurrentAoi()

#------------- New ManualTracking class ------------------------

class cmdNewAoiManualTracking(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'ManualTracking'
        self.newAoi = None

    def initialize(self, prevAoi):
        x1, y1, x2, y2 = self.getStartCoords((60, 60), prevAoi, 'AoiManualTracking')
        self.newAoi = SpotlightAoi.AoiManualTracking(x1, y1, x2, y2)

        # if the previous aoi was same as this one, copy previous ipSequenceList
        if prevAoi:
            if prevAoi.__class__.__name__ == 'AoiManualTracking':
                prevSeqList = prevAoi.getDuplicateSeqList()
                self.newAoi.setSeqList(prevSeqList)

    def do(self, aoi):
        Spotlight.aList.setNewAoi(self.newAoi)
        self.undoAoi = Spotlight.aList.getCurrentAoi()

    def undo(self):
        Spotlight.aList.deleteCurrentAoi()

#------------- New Threshold Tracking class ------------------------

class cmdNewAoiThresholdTracking(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'ThresholdTracking'
        self.newAoi = None

    def initialize(self, prevAoi):
        x1, y1, x2, y2 = self.getStartCoords((50, 50), prevAoi, 'AoiThresholdTracking')
        self.newAoi = SpotlightAoi.AoiThresholdTracking(x1, y1, x2, y2)
        # if the previous aoi was same as this one, copy previous ipSequenceList
        if prevAoi:
            if prevAoi.__class__.__name__ == 'AoiThresholdTracking':
                self.newAoi.setUseVelocity(prevAoi.useVelocity())
                self.newAoi.setVelocity(prevAoi.getVelocity())
                self.newAoi.setAngle(prevAoi.getAngle())
                self.newAoi.setConstrain(prevAoi.getConstrain())
                # copy previous ipSequenceList
                prevSeqList = prevAoi.getDuplicateSeqList()
                self.newAoi.setSeqList(prevSeqList)
            else:
                self.newAoi.addThresholdOperation() # if previous is not thresholdTrackingAoi
        else:
            self.newAoi.addThresholdOperation() # if no previous aoi exists

    def do(self, aoi):
        Spotlight.aList.setNewAoi(self.newAoi)
        self.undoAoi = Spotlight.aList.getCurrentAoi()

    def undo(self):
        Spotlight.aList.deleteCurrentAoi()

#------------- New CenterTracking class ------------------------

class cmdNewAoiCenterTracking(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'CenterTracking'
        self.newAoi = None

    def initialize(self, prevAoi):
        x1, y1, x2, y2 = self.getStartCoords((60, 60), prevAoi, 'AoiCenterTracking')
        self.newAoi = SpotlightAoi.AoiCenterTracking(x1, y1, x2, y2)
        # if the previous aoi was same as this one, copy previous ipSequenceList
        if prevAoi:
            if prevAoi.__class__.__name__ == 'AoiCenterTracking':
                prevSeqList = prevAoi.getDuplicateSeqList()
                self.newAoi.setSeqList(prevSeqList)
            else:
                self.newAoi.addThresholdOperation() # if previous is not centerTrackingAoi
        else:
            self.newAoi.addThresholdOperation() # if no previous aoi exists

        self.newAoi.updateThresholdOp(self.newAoi.getTrackingType()) # add/delete thresh op

    def do(self, aoi):
        Spotlight.aList.setNewAoi(self.newAoi)
        self.undoAoi = Spotlight.aList.getCurrentAoi()

    def undo(self):
        Spotlight.aList.deleteCurrentAoi()

#------------- New Local Maximum Tracking class ------------------------

class cmdNewAoiMaximumTracking(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'MaximumTracking'
        self.newAoi = None

    def initialize(self, prevAoi):
        x1, y1, x2, y2 = self.getStartCoords((60, 60), prevAoi, 'AoiMaximumTracking')
        self.newAoi = SpotlightAoi.AoiMaximumTracking(x1, y1, x2, y2)

        # if the previous aoi was same as this one, copy previous ipSequenceList
        if prevAoi:
            if prevAoi.__class__.__name__ == 'AoiMaximumTracking':
                prevSeqList = prevAoi.getDuplicateSeqList()
                self.newAoi.setSeqList(prevSeqList)

    def do(self, aoi):
        Spotlight.aList.setNewAoi(self.newAoi)
        self.undoAoi = Spotlight.aList.getCurrentAoi()

    def undo(self):
        Spotlight.aList.deleteCurrentAoi()

#------------- New Snake class ------------------------

class cmdNewAoiSnake(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'Snake'
        self.newAoi = None

    def initialize(self, prevAoi):
        x1, y1, x2, y2 = self.getStartCoords((10, 10), prevAoi, 'AoiSnake')
        self.newAoi = SpotlightAoi.AoiSnake(x1, y1, x2, y2)

        # if the previous aoi was same as this one, offset coordinates
        # and copy previous ipSequenceList
        if prevAoi:
            if prevAoi.__class__.__name__ == 'AoiSnake':
                # the standard setAoiCoordinates() is overriden in AoiSnake class
                cPoints = prevAoi.controlPoints
                fPoints = prevAoi.pinnedPoints
                c = prevAoi.connected
                params = prevAoi.params
                self.newAoi.setAoiCoordinates(cPoints, fPoints, c, params)
                # copy previous ipSequenceList
                prevSeqList = prevAoi.getDuplicateSeqList()
                self.newAoi.setSeqList(prevSeqList)

    def do(self, aoi):
        Spotlight.aList.setNewAoi(self.newAoi)
        self.undoAoi = Spotlight.aList.getCurrentAoi()

    def undo(self):
        Spotlight.aList.deleteCurrentAoi()

#------------- New LineFollowing class ------------------------

class cmdNewAoiLineFollowing(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'LineFollowing'
        self.newAoi = None

    def initialize(self, prevAoi):
        x1, y1, x2, y2 = self.getStartCoords((70, 70), prevAoi, 'AoiLineFollowing')
        self.newAoi = SpotlightAoi.AoiLineFollowing(x1, y1, x2, y2)

        # if the previous aoi was same as this one, copy previous ipSequenceList
        if prevAoi:
            if prevAoi.__class__.__name__ == 'AoiLineFollowing':
                prevSeqList = prevAoi.getDuplicateSeqList()
                self.newAoi.setSeqList(prevSeqList)

    def do(self, aoi):
        Spotlight.aList.setNewAoi(self.newAoi)
        self.undoAoi = Spotlight.aList.getCurrentAoi()

    def undo(self):
        Spotlight.aList.deleteCurrentAoi()

#----------------- Next Aoi class --------------------------

class cmdNextAoi(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'NextAoi'

    def do(self, aoi):
        Spotlight.aList.nextAoi()

    def undo(self):
        Spotlight.aList.previousAoi()

#------------------ Previous Aoi class ----------------------

class cmdPreviousAoi(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'PreviousAoi'

    def do(self, aoi):
        Spotlight.aList.previousAoi()

    def undo(self):
        Spotlight.aList.nextAoi()

#---------------- Delete Current Aoi class ----------------------

class cmdDeleteCurrentAoi(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'DeleteCurrentAoi'

    def do(self, aoi):
        aoi.deinitialize()
        self.undoAoi = aoi
        Spotlight.aList.deleteCurrentAoi()

    def undo(self):
        self.undoAoi.initialize()
        Spotlight.aList.setNewAoi(self.undoAoi)

    def isRedoable(self):
        return False  # don't redo at end of list

#----------------- Delete Selected Aoi class ----------------------

class cmdDeleteSelectedAoi(mtCommand):
    'called when modeless dialog Close button is clicked'
    def __init__(self, selectedAoi):
        mtCommand.__init__(self)
        self.name = 'DeleteSelectedAoi'
        self.undoAoi = selectedAoi

    def do(self, aoi):
        self.undoAoi.deinitialize()
        Spotlight.aList.deleteSelectedAoi(self.undoAoi)

    def undo(self):
        self.undoAoi.initialize()
        Spotlight.aList.setNewAoi(self.undoAoi)

    def isRedoable(self):
        return False  # don't redo at end of list

#----------------- Delete All Aoi's class ----------------------------

class cmdDeleteAllAois(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'DeleteAllAois'
        self.delAoiList = []

    def do(self, aoi):
        n = Spotlight.aList.getAoiListLength()
        for i in range(n):
            Spotlight.aList.currentAoi = i
            aoiCurr = Spotlight.aList.getCurrentAoi()
            if not aoiCurr.isWholeImageAoi():
                self.delAoiList.append(aoiCurr)
        Spotlight.aList.deleteAllAois()

    def undo(self):
        n = len(self.delAoiList)
        for i in range(n):
            restoreAoi = self.delAoiList[i]
            restoreAoi.initialize()
            Spotlight.aList.setNewAoi(restoreAoi)
        self.delAoiList = []

    def isRedoable(self):
        return False # don't redo at end of list

#--------------- Set Aoi Position class --------------------------

class cmdAoiSetPosition(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'AoiSetPosition'
        self.x1 = 0   # new position
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.undox1 = 0  # previous position
        self.undoy1 = 0
        self.undox2 = 0
        self.undoy2 = 0

    def do(self, aoi):
        self.undox1 = aoi.x1  # save original aoi positions
        self.undoy1 = aoi.y1
        self.undox2 = aoi.x2
        self.undoy2 = aoi.y2
        self.undoPoints = aoi.getControlPoints()
        aoi.setAoiPosition(self.x1, self.y1, self.x2, self.y2)
        self.undoAoi = aoi
        Spotlight.aList.updateModelessAois()

    def undo(self):
        self.undoAoi.setAoiPosition(self.undox1, self.undoy1, self.undox2, self.undoy2)
        Spotlight.aList.updateModelessAois()

    def showDialog(self, aoi):
        okPressed = False
        params = aoi.showAoiPositionDialog()
        if params:
            self.x1 = params['x1']
            self.y1 = params['y1']
            self.x2 = params['x2']
            self.y2 = params['y2']
            okPressed = True
        return okPressed

    def isRedoable(self):
        return False # don't redo at end of list


##--------------------------------------------------------------------
##---------------- Image Processing Command classes ------------------
##--------------------------------------------------------------------

#---------------- Test class ----------------------------

defaultTest = 4.0

class cmdTest(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        params = {'name': 'Test', 'test': defaultTest}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        global defaultTest
        defaultTest = params['test']
        self.params = {'name': 'Test', 'test': params['test']}

    def do(self, aoi):
        """
        This function is called only if OK was clicked in the threshold
        dialog box. If Cancel was clicked in the dialog box then its
        handled in the showDialog() function.
        """
        self.undoRect = aoi.getAoiPosition()
        aoiBitmap = Spotlight.getAoiImage(self.undoRect)
        self.undoBitmap = aoiBitmap.copy()
        self.execute(aoi)

    def undo(self):
        Spotlight.setAoiImage(self.undoBitmap, self.undoRect)
        Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        params = self.getParams()
        type = params['test']
        aoiBitmap = aoi.getAoiImage()
        aoiRect = aoi.getAoiPosition()
        self.executeTest(type, aoiBitmap, aoiRect)

    def executeTest(self, type, aoiBitmap=None, aoiRect=None):
        """
        If aoiBitmap and aoiRect are not supplied then this function is called
        from the slider dialog box. If on the other hand aoiBitmap and aoiRect
        are supplied then this function is being called from the execute() or do()
        function.
        """
        #type = type - 4.0
        type = type / 4.0
        print type
        if aoiBitmap:
            img = aoiBitmap.copy()
        else:
            img = self.undoBitmap.copy()
        img = PilProcess.Test(img, type)
        if aoiRect:
            Spotlight.setAoiImage(img, aoiRect)
        else:
            Spotlight.setAoiImage(img, self.undoRect)
        Spotlight.aList.updateModelessAois()

    def showDialog(self):
        aoi = Spotlight.aList.getCurrentAoi()
        self.do(aoi)
        params = self.getParams()
        params = SpotlightGui.gui.showModalDialog(params['name'], params, self)
        if params:
            self.setParams(params)
            self.undo()  # undo the above call to do()
            return True
        else:
            return False

##--------------- Threshold class ---------------------------------

defaultThresholdType = 0      # 0=simple (0 below threshold, 255 above)
defaultThresholdMode = 0     # 0=standard (not inverse)
defaultThreshold = 128

class cmdThreshold(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        params = {'name': 'Threshold',
            'type': defaultThresholdType,
            'mode': defaultThresholdMode,
            'threshold': defaultThreshold}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        'sets the values to the class variable (self.params) and saves to frame'
        global defaultThresholdType
        global defaultThresholdMode
        global defaultThreshold
        defaultThresholdType = params['type']
        defaultThresholdMode = params['mode']
        defaultThreshold = params['threshold']
        self.params = {'name': 'Threshold',
            'type': params['type'],
            'mode': params['mode'],
            'threshold': params['threshold']}
        self.setName(params['type'], params['mode'], params['threshold'])

    def updateName(self):
        """
        Forces updating of threshold value when the Image Sequence dialog
        box is displayed. If the Viewing Pixel Values is changed in the Program
        Options dialog box (say from Normalized to 8-bit), this would not be
        reflected when the Image Sequence dialog box is displayed.
        """
        params = self.getParams()
        self.setName(params['type'], params['mode'], params['threshold'])

    def setName(self, thresholdType, thresholdMode, threshold):
        if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
            s = '%.3f' % (threshold / 255.0)
        else:
            s = str(threshold)
        if thresholdType == 0:
            if thresholdMode == 0:
                self.name = 'Threshold - simple - standard (' + s + ')'
            else:
                self.name = 'Threshold - simple - inverse (' + s + ')'
        elif thresholdType == 1:
            if thresholdMode == 0:
                self.name = 'Threshold - low pass - standard (' + s + ')'
            else:
                self.name = 'Threshold - low pass - inverse (' + s + ')'
        else:
            if thresholdMode == 0:
                self.name = 'Threshold - high pass - standard (' + s + ')'
            else:
                self.name = 'Threshold - high pass - inverse (' + s + ')'

    def do(self, aoi):
        """
        This function is called only if OK was clicked in the threshold
        dialog box. If Cancel was clicked in the dialog box then its
        handled in the showDialog() function.
        """
        self.undoRect = aoi.getAoiPosition()
        aoiBitmap = Spotlight.getAoiImage(self.undoRect)
        self.undoBitmap = aoiBitmap.copy()
        self.execute(aoi)

    def undo(self):
        Spotlight.setAoiImage(self.undoBitmap, self.undoRect)
        Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        params = self.getParams()
        threshold = params['threshold']
        type = params['type']
        mode = params['mode']
        aoiBitmap = aoi.getAoiImage()
        aoiRect = aoi.getAoiPosition()
        self.executeThreshold(threshold, type, mode, aoiBitmap, aoiRect)

    def executeThreshold(self, threshold, type, mode, aoiBitmap=None, aoiRect=None):
        """
        If aoiBitmap and aoiRect are not supplied then this function is called
        from the slider dialog box. If on the other hand aoiBitmap and aoiRect
        are supplied then this function is being called from the execute() or do()
        function.
        """
        if aoiBitmap:
            img = aoiBitmap.copy()
        else:
            img = self.undoBitmap.copy()
        img = PilProcess.Threshold(img, threshold, type, mode)
        if aoiRect:
            Spotlight.setAoiImage(img, aoiRect)
        else:
            Spotlight.setAoiImage(img, self.undoRect)
        Spotlight.aList.updateModelessAois()

    def showDialog(self):
        aoi = Spotlight.aList.getCurrentAoi()
        self.do(aoi)
        params = self.getParams()
        params = SpotlightGui.gui.showModalDialog(params['name'], params, self)
        if params:
            self.setParams(params)
            self.undo()  # undo the above call to do()
            return True
        else:
            return False

    def isRedoable(self):
        return False # makes no sense to redo threshold twice


##---------------- Filter class ----------------------------

defaultFilterType = 0

class cmdFilter(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        params = {'name': 'Filter', 'type': defaultFilterType}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        filterType = params['type']
        global defaultFilterType
        defaultFilterType = filterType
        self.params = {'name': 'Filter', 'type': filterType}
        self.setName(filterType)

    def setName(self, filterType):
        if filterType == 0:
            self.name = 'Filter - smooth'
        elif filterType == 1:
            self.name = 'Filter - smooth more'
        elif filterType == 2:
            self.name = 'Filter - blur'
        elif filterType == 3:
            self.name = 'Filter - contour'
        elif filterType == 4:
            self.name = 'Filter - sharpen'
        elif filterType == 5:
            self.name = 'Filter - sharpen more'
        elif filterType == 6:
            self.name = 'Filter - edge enhance'
        elif filterType == 7:
            self.name = 'Filter - edge detect'
        elif filterType == 8:
            self.name = 'Filter - invert'

    def do(self, aoi):
        aoiPosition = aoi.getAoiPosition()
        aoiBitmap = Spotlight.getAoiImage(aoiPosition)
        self.undoBitmap = aoiBitmap.copy()
        self.undoRect = aoiPosition
        self.execute(aoi)
        Spotlight.aList.updateModelessAois()

    def undo(self):
        Spotlight.setAoiImage(self.undoBitmap, self.undoRect)
        Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        aoiRect = aoi.getAoiPosition()
        aoiBitmap = Spotlight.getAoiImage(aoiRect)
        outImage = self.executeFilter(aoiBitmap, self.params)
        if outImage:
            Spotlight.setAoiImage(outImage, aoiRect)

    def executeFilter(self, image, params):
        return PilProcess.Filter(image, params['type'])

    def showDialog(self):
        params = SpotlightGui.gui.showModalDialog(self.params['name'], self.params)
        if params:
            self.setParams(params)
            return True
        else:
            return False

#------------------ Arithmetic class -----------------------------

defaultArithConstant1 = 0.0
defaultArithConstant2 = 0.0
defaultArithSource1 = 0
defaultArithSource2 = 1
defaultArithOperation = 0
defaultArithFile1 = 'temp.tif'
defaultArithFile2 = 'temp.tif'

class cmdArithmetic(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        params = {'name': 'Arithmetic',
                    'operation': defaultArithOperation,
                    'constant1': defaultArithConstant1,
                    'constant2': defaultArithConstant2,
                    'source1': defaultArithSource1,
                    'source2': defaultArithSource2,
                    'file1': defaultArithFile1,
                    'file2': defaultArithFile2}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        global defaultArithOperation
        global defaultArithConstant1
        global defaultArithConstant2
        global defaultArithSource1
        global defaultArithSource2
        global defaultArithFile1
        global defaultArithFile2
        defaultArithOperation = params['operation']
        defaultArithConstant1 = params['constant1']
        defaultArithConstant2 = params['constant2']
        defaultArithSource1 = params['source1']
        defaultArithSource2 = params['source2']
        defaultArithFile1 = params['file1']
        defaultArithFile2 = params['file2']
        self.params = {'name': 'Arithmetic',
                        'operation': params['operation'],
                        'constant1': params['constant1'],
                        'constant2': params['constant2'],
                        'source1': params['source1'],
                        'source2': params['source2'],
                        'file1': params['file1'],
                        'file2': params['file2']}
        self.setName(params['operation'])

    def setName(self, arithOperation):
        if arithOperation == 0:
            self.name = 'Arithmetic - add'
        elif arithOperation == 1:
            self.name = 'Arithmetic - subtract'
        elif arithOperation == 2:
            self.name = 'Arithmetic - multiply'
        elif arithOperation == 3:
            self.name = 'Arithmetic - divide'
        elif arithOperation == 4:
            self.name = 'Arithmetic - difference'
        elif arithOperation == 5:
            self.name = 'Arithmetic - lighter'
        elif arithOperation == 6:
            self.name = 'Arithmetic - darker'
        elif arithOperation == 7:
            self.name = 'Arithmetic - screen'

    def do(self, aoi):
        aoiBitmap = aoi.getAoiImage()
        self.undoBitmap = aoiBitmap.copy()
        self.undoRect = aoi.getAoiPosition()
        self.execute(aoi)
        Spotlight.aList.updateModelessAois()

    def undo(self):
        Spotlight.setAoiImage(self.undoBitmap, self.undoRect)
        Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        aoiRect = aoi.getAoiPosition()
        aoiBitmap = Spotlight.getAoiImage(aoiRect)
        outImage = self.executeArithmetic(aoiBitmap, self.params)
        if outImage:
            Spotlight.setAoiImage(outImage, aoiRect)

    def executeArithmetic(self, image, params):
        arithOperation = params['operation']
        arithConstant1 = params['constant1']
        arithConstant2 = params['constant2']
        arithSource1 = params['source1']
        arithSource2 = params['source2']
        arithFile1 = params['file1']
        arithFile2 = params['file2']

        # check Source1
        if arithSource1 == 0:     # use current image as Source1
            aoiImage1 = image.copy()
        elif arithSource1 == 1:   # use constant image as Source1
            const1 = int(arithConstant1)
            color1 = (const1, const1, const1)
            aoiImage1 = Image.new(image.mode, image.size, color1)
        else:                           # use file as Source1
            aoiImage1 = Image.open(arithFile1)
            if aoiImage1.mode == 'L':
                aoiImage1 = aoiImage1.convert("RGB")

        # check Source2
        if arithSource2 == 0:      # use current image as Source2
            aoiImage2 = image.copy()
        elif arithSource2 == 1:    # use constant image as Source2
            const2 = int(arithConstant2)
            color2 = (const2, const2, const2)
            aoiImage2 = Image.new(image.mode, image.size, color2)
        else:                            # use file as Source2
            aoiImage2 = Image.open(arithFile2)
            if aoiImage2.mode == 'L':
                aoiImage2 = aoiImage2.convert("RGB")

        # check if the two images are the same size and type
        if aoiImage1.size != aoiImage2.size:
            m = 'aoiImage1 and aoiImage2 are different sizes'
            SpotlightGui.gui.messageDialog(m, 'Aoi Size Error')
            return None

        # Do the operation
        if arithOperation == 0:  # Add
            aoiImage = PilProcess.addImage(aoiImage1, aoiImage2)
        elif arithOperation == 1: # Subtract
            aoiImage = PilProcess.subImage(aoiImage1, aoiImage2)

        elif arithOperation == 2: # Multiply
            if arithSource1 == 1:  # Source1 is a constant - mult by const
                aoiImage = PilProcess.multConstant(aoiImage2, arithConstant1)
            if arithSource2 == 1:  # Source2 is a constant - mult by const
                aoiImage = PilProcess.multConstant(aoiImage1, arithConstant2)
            if arithSource1 != 1 and arithSource2 != 1: # neither Source1 or Source2 is a constant
                aoiImage = PilProcess.multImage(aoiImage1, aoiImage2)
        elif arithOperation == 3: # Divide
            if arithSource1 == 1:  # Source1 is a constant - div by const
                aoiImage = PilProcess.divConstant(aoiImage2, arithConstant1)
            if arithSource2 == 1:  # Source2 is a constant - div by const
                aoiImage = PilProcess.divConstant(aoiImage1, arithConstant2)
            if arithSource1 != 1 and arithSource2 != 1: # neither Source1 or Source2 is a constant
                aoiImage = PilProcess.divImage(aoiImage1, aoiImage2)
        elif arithOperation == 4: # Difference
            aoiImage = PilProcess.differenceImage(aoiImage1, aoiImage2)
        elif arithOperation == 5: # Lighter
            aoiImage = PilProcess.lighterImage(aoiImage1, aoiImage2)
        elif arithOperation == 6: # Darker
            aoiImage = PilProcess.darkerImage(aoiImage1, aoiImage2)
        elif arithOperation == 7: # Blend
            aoiImage = PilProcess.blendImage(aoiImage1, aoiImage2, 0.5)
        return aoiImage

    def showDialog(self):
        params = SpotlightGui.gui.showModalDialog(self.params['name'], self.params)
        if params:
            self.setParams(params)
            return True
        else:
            return False

#------------------ Contrast class ------------------------------

defaultContrastType = 0      # 0=contrast stretch
defaultSubAoiSize = 45       # for adaptive contrast stretch

class cmdContrast(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        params = {'name': 'Contrast',
                  'type': defaultContrastType,
                  'subAoiSize': defaultSubAoiSize}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        global defaultContrastType
        global defaultSubAoiSize
        defaultContrastType = params['type']
        defaultSubAoiSize = params['subAoiSize']
        self.params = {'name': 'Contrast',
                                'type': params['type'],
                                'subAoiSize': params['subAoiSize']}
        self.setName(params['type'], params['subAoiSize'])

    def setName(self, contrastType, subAoiSize):
        if contrastType == 0:
            self.name = 'Contrast - linear stretch'
        elif contrastType == 1:
            self.name = 'Contrast - histogram equalization'
        elif contrastType == 2:
            self.name = 'Contrast - contrast enhance'
        elif contrastType == 3:
            s = str(subAoiSize)
            self.name = 'Contrast - adaptive stretch (' + s + ')'

    def do(self, aoi):
        aoiPosition = aoi.getAoiPosition()
        aoiBitmap = Spotlight.getAoiImage(aoiPosition)
        self.undoBitmap = aoiBitmap.copy()
        self.undoRect = aoiPosition
        self.execute(aoi)
        Spotlight.aList.updateModelessAois()

    def undo(self):
        Spotlight.setAoiImage(self.undoBitmap, self.undoRect)
        Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        aoiRect = aoi.getAoiPosition()
        aoiBitmap = Spotlight.getAoiImage(aoiRect)
        outImage = self.executeContrast(aoiBitmap, self.params)
        if outImage:
            Spotlight.setAoiImage(outImage, aoiRect)

    def executeContrast(self, image, params):
        if params['type'] == 0:  # linear stretch
            return PilProcess.linearConstrastStretch(image)
        elif params['type'] == 1:  # equalize
            return PilProcess.histogramEqualization(image)
        elif params['type'] == 2:  # adaptive contrast stretching
            params = self.getParams()
            return PilProcess.adaptiveConstrastStretch(image, params['subAoiSize'])
        else:
            return image

    def showDialog(self):
        params = SpotlightGui.gui.showModalDialog(self.params['name'], self.params)
        if params:
            self.setParams(params)
            return True
        else:
            return False

#------------------ Morphological class ------------------------------

defaultMorphologicalType = 0
defaultIterations = 1

class cmdMorphological(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        params = {'name': 'Morphological',
                        'type': defaultMorphologicalType,
                        'iterations': defaultIterations}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        global defaultMorphologicalType
        global defaultIterations
        defaultMorphologicalType = params['type']
        defaultIterations = params['iterations']
        self.params = {'name': 'Morphological',
                                'type': params['type'],
                                'iterations': params ['iterations']}
        self.setName(params['type'], params ['iterations'])

    def setName(self, type, iterations):
        s = str(iterations)
        if type == 0:
            self.name = 'Morphological - erosion  (' + s + ')'
        elif type == 1:
            self.name = 'Morphological - dilation  (' + s + ')'
        elif type == 2:
            self.name = 'Morphological - reconstruct  (' + s + ')'
        elif type == 3:
            self.name = 'Morphological - outline'
        elif type == 4:
            self.name = 'Morphological - skeleton'
        elif type == 5:
            self.name = 'Morphological - hole fill'
        elif type == 6:
            self.name = 'Morphological - hole extract'
        elif type == 7:
            self.name = 'Morphological - border kill'
        elif type == 8:
            self.name = 'Morphological - border line kill'

    def do(self, aoi):
        aoiPosition = aoi.getAoiPosition()
        aoiBitmap = Spotlight.getAoiImage(aoiPosition)
        self.undoBitmap = aoiBitmap.copy()
        self.undoRect = aoiPosition
        self.execute(aoi)
        Spotlight.aList.updateModelessAois()

    def undo(self):
        Spotlight.setAoiImage(self.undoBitmap, self.undoRect)
        Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        aoiRect = aoi.getAoiPosition()
        aoiBitmap = Spotlight.getAoiImage(aoiRect)
        outImage = self.executeMorphological(aoiBitmap, self.params)
        if outImage:
            Spotlight.setAoiImage(outImage, aoiRect)

    def executeMorphological(self, image, params):
        type = params['type']
        iterations = params['iterations']
        img = PilProcess.Morphological(image, type, iterations)
        return img

    def showDialog(self):
        params = SpotlightGui.gui.showModalDialog(self.params['name'], self.params)
        if params:
            if params['type'] != 4:
                self.setParams(params)
                return True
            else:
                SpotlightGui.gui.messageDialog('skeleton is currently not supported')
                return False
        else:
            return False


#------------------ ExtractPlane class ------------------------------

defaultExtractColorPlane = 0 # 0=red

class cmdExtractPlane(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        params = {'name': 'ExtractPlane', 'type': defaultExtractColorPlane}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        colorPlane = params['type']
        global defaultExtractColorPlane
        defaultExtractColorPlane = colorPlane
        self.params = {'name': 'ExtractPlane', 'type': colorPlane}
        self.setName(colorPlane)

    def setName(self, colorPlane):
        if colorPlane == 0:
            self.name = 'ExtractPlane - red'
        elif colorPlane == 1:
            self.name = 'ExtractPlane - green'
        elif colorPlane == 2:
            self.name = 'ExtractPlane - blue'
        elif colorPlane == 3:
            self.name = 'ExtractPlane - intensity'

    def do(self, aoi):
        aoiBitmap = aoi.getAoiImage()
        self.undoBitmap = aoiBitmap.copy()
        self.undoRect = aoi.getAoiPosition()
        self.execute(aoi)
        Spotlight.aList.updateModelessAois()

    def undo(self):
        Spotlight.setAoiImage(self.undoBitmap, self.undoRect)
        Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        aoiRect = aoi.getAoiPosition()
        aoiBitmap = Spotlight.getAoiImage(aoiRect)
        outImage = self.executeExtractPlane(aoiBitmap, self.params)
        if outImage:
            Spotlight.setAoiImage(outImage, aoiRect)

    def executeExtractPlane(self, image, params):
        return PilProcess.extractPlane(image, params['type'])

    def showDialog(self):
        params = SpotlightGui.gui.showModalDialog(self.params['name'], self.params)
        if params:
            self.setParams(params)
            return True
        else:
            return False

    def isRedoable(self):
        return False # don't redo at end of list

#---------------- ExtractField class ----------------------------

defaultExtractField = 0 # 0=odd, 1=even, 2=swap fields

class cmdExtractField(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        params = {'name': 'ExtractField', 'field': defaultExtractField}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        field = params['field']
        global defaultExtractField
        defaultExtractField = field
        self.params = {'name': 'ExtractField', 'field': field}
        self.setName(field)

    def setName(self, field):
        if field == 0:
            self.name = 'ExtractField - odd'
        elif field == 1:
            self.name = 'ExtractField - even'
        elif field == 2:
            self.name = 'ExtractField - swap field order'

    def do(self, aoi):
        aoiBitmap = aoi.getAoiImage()
        self.undoBitmap = aoiBitmap.copy()
        self.undoRect = aoi.getAoiPosition()
        self.execute(aoi)
        Spotlight.aList.updateModelessAois()

    def undo(self):
        Spotlight.setAoiImage(self.undoBitmap, self.undoRect)
        Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        aoiRect = aoi.getAoiPosition()
        aoiBitmap = Spotlight.getAoiImage(aoiRect)
        outImage = self.executeExtractField(aoiBitmap, self.params)
        if outImage:
            Spotlight.setAoiImage(outImage, aoiRect)

    def executeExtractField(self, image, params):
        return PilProcess.fieldOperation(image, params['field'])

    def showDialog(self):
        params = SpotlightGui.gui.showModalDialog(self.params['name'], self.params)
        if params:
            self.setParams(params)
            return True
        else:
            return False

    def isRedoable(self):
        return False # don't redo at end of list

#------------------- Geometric class -------------------------------

defaultGeomOperation = 0     # 0=rotate
defaultRotateAngle = 90.0
defaultRotateAngleSelection = 3 # 0=90, 1=180, 2=270, 3=other, 4=flip, 5=flop
defaultTransDirection = 0    # 0=left
defaultTransDistance = 10

class cmdGeometric(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        params = {'name': 'Geometric',
                   'operation': defaultGeomOperation,
                   'angle': defaultRotateAngle,
                   'angleselection': defaultRotateAngleSelection,
                   'direction': defaultTransDirection,
                   'distance': defaultTransDistance}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        operation = params['operation']
        angle = params['angle']
        angleselection = params['angleselection']
        direction = params['direction']
        distance = params['distance']
        global defaultGeomOperation
        global defaultRotateAngle
        global defaultRotateAngleSelection
        global defaultTransDirection
        global defaultTransDistance
        defaultGeomOperation = operation
        defaultRotateAngle = angle
        defaultRotateAngleSelection = angleselection
        defaultTransDirection = direction
        defaultTransDistance = distance
        self.params = {'name': 'Geometric',
                       'operation': operation,
                       'angle': angle,
                       'angleselection': angleselection,
                       'direction': direction,
                       'distance': distance}
        self.setName()

    def setName(self):
        if self.params['operation'] == 0:  # rotate
            if self.params['angleselection'] == 4:
                self.name = 'Geometric - rotate - flip'
            elif self.params['angleselection'] == 5:
                self.name = 'Geometric - rotate - flop'
            else:
                s = str(self.params['angle'])
                self.name = 'Geometric - rotate  (' + s + ')'
        else:
            dist = str(self.params['distance'])
            if self.params['direction'] == 0:   # left
                dir = 'left'
            elif self.params['direction'] == 1: # right
                dir = 'right'
            elif self.params['direction'] == 2: # up
                dir = 'up'
            else:                # down
                dir = 'down'
            self.name = 'Geometric - translate - (' + dist + ' - ' + dir + ')'

    def do(self, aoi):
        self.undoRect = aoi.getAoiPosition()
        aoiBitmap = Spotlight.getAoiImage(self.undoRect)
        self.undoBitmap = aoiBitmap.copy()
        self.undoAoi = aoi
        self.execute(aoi)
        Spotlight.aList.updateModelessAois()

    def undo(self):
        if self.undoAoi.isWholeImageAoi():
            Spotlight.setWorkingImage(self.undoBitmap)
            Spotlight.updateWholeImageAoiSize()
        else:
            Spotlight.setAoiImage(self.undoBitmap, self.undoRect)
            Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        aoiBitmap = aoi.getAoiImage()
        aoiRect = aoi.getAoiPosition()
        if self.params['operation'] == 0:    # rotate
            outImage = self.executeRotation(aoi, aoiBitmap, self.params)
            if not aoi.isWholeImageAoi():
                Spotlight.setAoiImage(outImage, aoiRect)
        else:   # roll
            outImage = self.executeRoll(aoiBitmap, self.params)
            Spotlight.setAoiImage(outImage, aoiRect)

    def executeRotation(self, aoi, aoiImage, params):
        angle = float(params['angle'])

        if aoi.isWholeImageAoi():
            if params['angleselection'] == 4:
                outImage = PilProcess.Transpose(aoiImage, 'FLIP_LEFT_RIGHT')
            elif params['angleselection'] == 5:
                outImage = PilProcess.Transpose(aoiImage, 'FLIP_TOP_BOTTOM')
            else:
                # Rotate the whole image, thus changing the size or the image.
                # This rotation is done using wxImage rotation function (not PIL).
                #wximg = SpotlightGui.gui.iPanel.getIm()  # return wxImage RGB
                wximg = PilProcess.convertPILtoWX(Spotlight.workingImage)
                if angle == 90.0:
                    wximg = wximg.Rotate90(False)
                elif angle == 180.0:
                    wximg = wximg.Rotate90(False)
                    wximg = wximg.Rotate90(False)
                elif angle == 270.0:
                    wximg = wximg.Rotate90()
                else:
                    DEGtoRAD = (3.1415926536/180.0)
                    center = aoi.getAoiCenter()
                    wximg = wximg.Rotate(angle*DEGtoRAD, center)
                outImage = PilProcess.convertWXToPIL(wximg)

            Spotlight.setWorkingImage(outImage)
            Spotlight.updateWholeImageAoiSize()
        else:
            if params['angleselection'] == 4:
                outImage = PilProcess.Transpose(aoiImage, 'FLIP_LEFT_RIGHT')
            elif params['angleselection'] == 5:
                outImage = PilProcess.Transpose(aoiImage, 'FLIP_TOP_BOTTOM')
            else:
                # Rotate image inside non-wholeimage aoi only. This function
                # rotates pixels in, from outside the aoi, so that you don't
                # have black pixels being rotated into the aoi. It may still
                # happen if the aoi is at the edge of the image.
                r = aoi.getAoiPosition()
                d = int(aoi.dist(r[0], r[1], r[2], r[3])) + 1  # corner to corner
                outImage = PilProcess.RotateAoi(Spotlight.workingImage, angle, r, d)
            return outImage

    def executeRoll(self, aoiImage, params):
        distance = params['distance']
        direction = params['direction']
        return PilProcess.Roll(aoiImage, distance, direction)

    def showDialog(self):
        params = SpotlightGui.gui.showModalDialog(self.params['name'], self.params)
        if params:
            tab = params['operation']
            angleSelection = params['angleselection']
            direction = params['direction']
            # do some testing
            s_angle = params['angle']
            s_distance = params['distance']
            angValid = self.isAngleValid(s_angle)
            distValid = self.isDistanceValid(s_distance)
            if angValid and distValid:
                angle = float(params['angle'])
                distance = int(params['distance'])

                outParams = {'name': 'Geometric',
                           'operation': tab,
                           'angle': angle,
                           'angleselection': angleSelection,
                           'direction': direction,
                           'distance': distance}

                self.setParams(outParams)
            else:
                m = 'angle or distance is not a valid number'
                SpotlightGui.gui.messageDialog(m)
            return True
        else:
            return False

    def isAngleValid(self, s):
        try:
            n = float(s)
            if n < -360.0 or n > 360.0:
                return False
            else:
                return True
        except ValueError:
            return False

    def isDistanceValid(self, s):
        try:
            imX, imY = Spotlight.workingImage.size
            #imX, imY = Spotlight.workingImage.columns(), Spotlight.workingImage.rows()

            d = int(s)
            num = min(imX, imY)
            if d < 0 or d > num:
                return False
            else:
                return True
        except ValueError:
            return False

#---------------- Statistics class ----------------------------

defaultStatisticsType = 0  # latest one selected, 0=min,max,mean

class cmdStatistics(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        params = {'name': 'Statistics', 'type': defaultStatisticsType}
        self.setParams(params)
        self.stats = []
        self.histo = []
        self.lineprof = []
        self.area = []

    def getParams(self):
        return self.params

    def setParams(self, params):
        statisticsType = params['type']

        # make sure that the statistics type matches the aoi type
        aoi = Spotlight.aList.getCurrentAoi()
        className = aoi.__class__.__name__
        if className == 'AoiLine' or className == 'AoiLineProfile':
            if params['type'] != 2:
                statisticsType = 2
        else:
            if params['type'] == 2:
                statisticsType = 0

        global defaultStatisticsType
        defaultStatisticsType = statisticsType
        self.params = {'name': 'Statistics', 'type': statisticsType}
        self.setName(statisticsType)

    def setName(self, statisticsType):
        if statisticsType == 0:
            self.name = 'Statistics - min,max,mean,stdev'
        elif statisticsType == 1:
            self.name = 'Statistics - histogram'
        elif statisticsType == 2:
            self.name = 'Statistics - line profile'
        elif statisticsType == 3:
            self.name = 'Statistics - area measure'

    def do(self, aoi):
        self.execute(aoi)

    def execute(self, aoi):
        aoiBitmapTemp = aoi.getAoiImage()
        aoiBitmap = aoiBitmapTemp.copy()
        # MIN, MAX, MEAN, STDEV
        if self.params['type'] == 0:
            # Note: For RGB images getMinMax() returns min and max
            # between all three planes, not min and max of intensity plane.
            min, max = PilProcess.getMinMax(aoiBitmap)
            mean, stdev = PilProcess.getMeanStDev(aoiBitmap)
            smin, smax, smean, sstdev = self.statsToString(min, max, mean, stdev)
            if Spotlight.tracking:
                self.setData((smin, smax, smean, sstdev))
            else:
                s = '  min: %s   max: %s   mean: %s   stdev: %s' % (smin, smax, smean, sstdev)
                if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
                    SpotlightGui.gui.infoBox('\n'+s, 420, 120, "Image Statistics")
                else:
                    SpotlightGui.gui.infoBox('\n'+s, 330, 120, "Image Statistics")
        # HISTOGRAM
        elif self.params['type'] == 1:
            histo = PilProcess.getHistogram(aoiBitmap)
            histo = self.convertColumns(histo)
            if Spotlight.tracking:
                self.setData(histo)
            else:
                sHisto = 'index  histogram' + '\n'
                sHisto = sHisto + '====  ========' + '\n' + '\n'
                count = 0
                for i in histo:
                    sHisto = sHisto + str(count) + '        ' + str(i)+ '\n'
                    count = count + 1
                SpotlightGui.gui.infoBox(sHisto, 260, 480)
        # LINE PROFILE
        elif self.params['type'] == 2:
            profile = aoi.getLine(aoi.x1, aoi.y1, aoi.x2, aoi.y2)
            sprofile = self.profileToString(profile)
            if Spotlight.tracking:
                self.setData(sprofile)
            else:
                sProf = 'index  profile' + '\n'
                sProf = sProf + '====  =======' + '\n' + '\n'
                count = 0
                for p in sprofile:
                    r, g, b = p
                    sProf = sProf + str(count) + '        ' + r + '  ' + g + '  ' + b + '  ' + '\n'
                    count = count + 1
                SpotlightGui.gui.infoBox(sProf, 210, 480)
        # AREA MEASUREMENT
        elif self.params['type'] == 3:
            img = PilProcess.Threshold(aoiBitmap, 128, 0, 0)
            histo = PilProcess.getHistogram(img)
            area = histo[255]
            objectArea = Spotlight.scaleArea(area)
            percent = Spotlight.getPercent()
            if Spotlight.tracking:
                self.setData((objectArea, percent))
            else:
                objectArea = '  thresholded area: ' + objectArea
                percent = '  percent of total: ' + percent
                if Spotlight.scaleUserUnits == 1.0 and Spotlight.scalePixelUnits == 1.0:
                    u = ' pixels'
                else:
                    u = ' units squared'
                s = objectArea + u + '\n' + percent + ' %'
                SpotlightGui.gui.infoBox('\n'+s, 300, 120, "Area of thresholded pixels")


    def setData(self, data):
        params = self.getParams()
        # min,max,mean,st.dev
        if params['type'] == 0:
            dmin, dmax, dmean, dstdev = self.formatStats(data)
            self.stats = []
            self.stats.append(dmin)
            self.stats.append(dmax)
            self.stats.append(dmean)
            self.stats.append(dstdev)
        # histogram
        elif params['type'] == 1:
            self.histo = []
            histogram = self.formatHistogram(data)
            self.histo.append(histogram)
        # line profile
        elif params['type'] == 2:
            self.lineprof = []
            lineprofile = self.formatProfile(data)
            self.lineprof.append(lineprofile)
        # area
        elif params['type'] == 3:
            area, percent = self.formatArea(data)
            self.area = []
            self.area.append(area)
            self.area.append(percent)


    def formatArea(self, data):
        area, percent = data
        if Spotlight.scaleUserUnits == 1.0 and Spotlight.scalePixelUnits == 1.0:
            # area
            area = string.rjust(area, 8)
            area = '   ' + area + '    '
            darea = []
            darea.append(area)
            # percent
            percent = string.rjust(percent, 8)
            percent = '     ' + percent + '     '
            dpercent = []
            dpercent.append(percent)
        else:
            # area
            area = string.rjust(area, 8)
            area = '   ' + area + '    '
            darea = []
            darea.append(area)
            # percent
            percent = string.rjust(percent, 8)
            percent = '     ' + percent + '     '
            dpercent = []
            dpercent.append(percent)
        return (darea, dpercent)


    def profileToString(self, lineprofile):
        prof = []
        for p in lineprofile:
            if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
                r = '%.4f' % p[0] # profile is already normalized
                g = '%.4f' % p[1]
                b = '%.4f' % p[2]
            else:
                r = '%3d' % int(p[0]*255.0)
                g = '%3d' % int(p[1]*255.0)
                b = '%3d' % int(p[2]*255.0)
            prof.append((r, g, b))
        return prof

    def formatProfile(self, lineprofile):
        prof = []
        for p in lineprofile:
            r, g, b = p
            if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
                sr = string.rjust(r, 7)
                sg = string.rjust(g, 7)
                sb = string.rjust(b, 7)
                s = sr + sg + sb
                sout = '   ' + s + '    '
                prof.append(sout)
            else:
                sr = string.rjust(r, 7)
                sg = string.rjust(g, 7)
                sb = string.rjust(b, 7)
                s = sr + sg + sb
                sout = '   ' + s + '    '
                prof.append(sout)
        return prof

    def convertColumns(self, histo):
        """For RGB images, PIL returns a histogram as a list of numbers
        768 long. This method convers it into 3 columns of 256 numbers."""
        r = []
        g = []
        b = []
        rgb = []
        for i in range(0, 256):
            r.append(histo[i])
        for i in range(256, 512):
            g.append(histo[i])
        for i in range(512, 768):
            b.append(histo[i])
        for i in range(256):
            rgb.append((r[i], g[i], b[i]))
        return rgb

    def formatHistogram(self, histogram):
        hist = []
        for p in histogram:
            r,g,b = p
            sr = string.rjust(str(r), 7)
            sg = string.rjust(str(g), 7)
            sb = string.rjust(str(b), 7)
            s = sr + sg + sb
            sout = ' ' + s + '    '
            hist.append(sout)
        return hist

    def statsToString(self, min, max, mean, stdev):
        """
        Convert to string and take pixel value type into account.
        """
        if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
            smin = '%.4f' % (min/255.0)
            smax = '%.4f' % (max/255.0)
            smean = '%.4f' % (mean/255.0)
            sstdev = '%.4f' % (stdev/255.0)
        else:
            smin = str(min)
            smax = str(max)
            smean = str(mean)
            sstdev = '%.4f' % stdev
        return (smin, smax, smean, sstdev)

    def formatStats(self, data):
        smin, smax, smean, sstdev = data
        if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
            # min
            smin = string.rjust(smin, 6)
            smin = '   ' + smin + '     '
            # max
            smax = string.rjust(smax, 6)
            smax = '   ' + smax + '     '
            # mean
            smean = string.rjust(smean, 6)
            smean = '   ' + smean + '      '
            # stdev
            sstdev = string.rjust(sstdev, 9)
            sstdev = '   ' + sstdev + '    '
        else:
            # min
            smin = string.rjust(smin, 4)
            smin = '    ' + smin + '      '
            # max
            smax = string.rjust(smax, 4)
            smax = '    ' + smax + '      '
            # mean
            smean = string.rjust(smean, 4)
            smean = '    ' + smean + '       '
            # stdev
            sstdev = string.rjust(sstdev, 9)
            sstdev = '   ' + sstdev + '    '
        dmin = []
        dmin.append(smin)
        dmax = []
        dmax.append(smax)
        dmean = []
        dmean.append(smean)
        dstdev = []
        dstdev.append(sstdev)
        return (dmin, dmax, dmean, dstdev)

    def getData(self):
        params = self.getParams()
        if params['type'] == 0: #  min,max,mean,st.dev
            return self.stats
        elif params['type'] == 1: #  histogram
            return self.histo
        elif params['type'] == 2: #  line profile
            return self.lineprof
        elif params['type'] == 3: #  area
            return self.area

    def getHeader(self):
        """
        Sets the width of the header columns and the header text.
        """
        params = self.getParams()
        if params['type'] == 0: #  min,max,mean,st.dev
            h = []
            h.append('min')
            h.append('max')
            h.append('mean')
            h.append('stdev')
            return h
        elif params['type'] == 1: #  histogram
            h = []
            h.append('   histogram   ')
            return h
        elif params['type'] == 2: #  line profile
            lp = []
            lp.append('     lineprof    ')
            return lp
        elif params['type'] == 3: #  area
            h = []
            h.append('area')
            h.append('percent')
            return h


    def showDialog(self):
        params = SpotlightGui.gui.showModalDialog(self.params['name'], self.params)
        if params:
            self.setParams(params)
            return True
        else:
            return False

#------------------------ SaveAoi class ------------------------------------

defaultPath = 'temp0.tif'
defaultAppNumFlag = True
defaultSaveAsGrayscaleFlag = False

class cmdSaveAoi(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        path = Spotlight.pOptions.programOptions['latestSavePath']
        params = {'name': 'SaveAoi',
                        'path': defaultPath,
                        'appNumFlag': defaultAppNumFlag,
                        'saveAsGrayscaleFlag': defaultSaveAsGrayscaleFlag}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        global defaultPath
        global defaultAppNumFlag
        global defaultSaveAsGrayscaleFlag
        defaultPath = params['path']
        defaultAppNumFlag = params['appNumFlag']
        defaultSaveAsGrayscaleFlag = params['saveAsGrayscaleFlag']
        self.params = {'name': 'SaveAoi',
                        'path': params['path'],
                        'appNumFlag': params['appNumFlag'],
                        'saveAsGrayscaleFlag': params['saveAsGrayscaleFlag']}
        self.setName(params['path'])

    def setName(self, path):
        dir, file = os.path.split(path)
        base1, ext = os.path.splitext(file)
        base = os.path.abspath(path)
        outname = base + '  (' + ext + ')'
        self.name = 'Save Aoi - ' + outname

    def do(self, aoi):
        self.execute(aoi)

    def execute(self, aoi):
        aoiImage = aoi.getAoiImage()
        path = self.params['path']
        appNumFlag = self.params['appNumFlag']
        saveAsGrayscaleFlag = self.params['saveAsGrayscaleFlag']

        # test append number checkbox
        if appNumFlag:
            dir, file = os.path.split(path)
            base, ext = os.path.splitext(file)
            basename, numeric = Spotlight.splitNumeric(base)
            n = int(numeric)
            n = n + 1 # increment for next time the dialog is opened
            basePath = os.path.abspath(os.path.join(dir, basename))
            newpath = basePath + str(n) + ext

            # save new appendnumber
            params = {'name': 'SaveAoi',
                        'path': newpath,
                        'appNumFlag': appNumFlag,
                        'saveAsGrayscaleFlag': saveAsGrayscaleFlag}
            self.setParams(params)

        # test save as grayscale checkbox
        if saveAsGrayscaleFlag:
            grayimage = PilProcess.convertColorToGray(aoiImage)
            grayimage.save(path)
        else:
            Spotlight.saveImage(aoiImage, path)

    def showDialog(self):
        params = SpotlightGui.gui.showModalDialog(self.params['name'], self.params)
        if params:
            self.setParams(params)
            return True
        else:
            return False

    def isRedoable(self):
        return False # saving image to disk can't be undone

#------------------- Pseudocolor class -----------------------------

defaultPalettePath = 'None'

class cmdPseudocolor(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        params = {'name': 'Pseudocolor', 'palettePath': defaultPalettePath}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        palettePath = params['palettePath']
        global defaultPalettePath
        defaultPalettePath = palettePath
        self.params = {'name': 'Pseudocolor', 'palettePath': palettePath}
        self.setName(palettePath)

    def setName(self, palettePath):
        if palettePath == 'None':
            paletteName = 'None'
        else:
            paletteName = os.path.split(palettePath)[-1]
        self.name = 'Pseudocolor (LUT) - ' + paletteName

    def do(self, aoi):
        imgBitmap = Spotlight.workingImage
        self.undoBitmap = imgBitmap.copy()
        self.execute(aoi)
        Spotlight.aList.updateModelessAois()

    def undo(self):
        Spotlight.setWorkingImage(self.undoBitmap)
        Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        imgBitmap = Spotlight.workingImage.copy()
        outImage = self.executePseudocolor(imgBitmap)
        if outImage:
            Spotlight.setWorkingImage(outImage)

    def executePseudocolor(self, image):
        if self.params['palettePath'] == 'None':
            return None

        # apply palette to image
        if Spotlight.pOptions.programOptions['paletteDisplay'] == 0:
            palette = self.loadPalette(self.params['palettePath'])
            if palette:
                img = PilProcess.convertGrayToColor(image)
                SpotlightGui.gui.iPanel.setPalette(None)
                return img.point(palette)
            else:
                return None
        else:   # apply palette to display
            palette = self.loadPalette(self.params['palettePath'])
            if palette:
                SpotlightGui.gui.iPanel.setPalette(palette)
                return image  # original image
            else:
                return None

    def showDialog(self):
        # add latestLUTPath to local params
        path = Spotlight.pOptions.programOptions['latestLUTPath']
        params = {}
        params['latestLUTPath'] = path
        params = SpotlightGui.gui.showModalDialog(self.params['name'], params)
        if params:
            self.setParams(params)
            Spotlight.pOptions.setLatestLUTPath(params['palettePath'])
            return True
        else:
            return False

    def loadPalette(self, file):
        """load palette from disk and return the palette as a list of RGB
        values. If the palette has fewer than 256 values a blank palette is
        returned. If the palette has more than 256 values, then it returns
        only the first 256."""
        if os.path.isfile(file):
            try:
                palette = []
                f = open(file, 'r')
                i = 0
                while (i < 256): # limit to 256 triplets
                    line = f.readline()
                    if line == '':
                        break
                    # get rid of newline char at the end of each line
                    line = line[:-1]
                    # split string into list of numbers
                    num = string.split(line)
                    # only RGB triplet - skip blank lines at the end of file
                    if len(num) == 3:
                        r = int(num[0])
                        g = int(num[1])
                        b = int(num[2])
                        palette.append((r, g, b))
                    i = i + 1
                f.close()
                if len(palette) < 256:
                    m1 = 'palette has less than 256 values'
                    m2 = '\n\n blank palette will be returned'
                    m = m1 + m2
                    SpotlightGui.gui.messageDialog(m)
                    return []
                else:
                    # change palette format from a list of 256 RGB tuples to a
                    # 1-d array mapped as 256 red values, 256 green values,
                    # and 256 blue values as needed by PIL point function
                    pout = []
                    for i in range (0, 256):
                        r,g,b = palette[i]
                        pout.append(r)
                    for i in range (0, 256):
                        r,g,b = palette[i]
                        pout.append(g)
                    for i in range (0, 256):
                        r,g,b = palette[i]
                        pout.append(b)
                    return pout
            except IOError:
                print "can't open the file"
                return None
        else:
            return None

#---------------- ResizeImage class ----------------------------

defaultNewWidth = 0
defaultNewHeight = 0
defaultConstrainAspect = True
defaultType = 'pixels'

class cmdResizeImage(mtCommand):
    """
    Changes the size of the image. This function operates only on the
    whole image.
    """
    def __init__(self):
        mtCommand.__init__(self)
        if defaultNewWidth == 0:
            w, h = Spotlight.getWorkingImageSize()
            params = {'name': 'ResizeImage',
                                'newWidth': w,
                                'newHeight': h,
                                'constrain': defaultConstrainAspect,
                                'type': defaultType}
        else:
            params = {'name': 'ResizeImage',
                                'newWidth': defaultNewWidth,
                                'newHeight': defaultNewHeight,
                                'constrain': defaultConstrainAspect,
                                'type': defaultType}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        global defaultNewWidth
        global defaultNewHeight
        global defaultConstrainAspect
        global defaultType
        defaultNewWidth = params['newWidth']
        defaultNewHeight = params['newHeight']
        defaultConstrainAspect = params['constrain']
        defaultType = params['type']
        self.params = {'name': 'ResizeImage',
                            'newWidth': params['newWidth'],
                            'newHeight': params['newHeight'],
                            'constrain': params['constrain'],
                            'type': params['type']}
        self.setName()

    def setName(self):
        params = self.getParams()
        size = str(params['newWidth']) + 'x' + str(params['newHeight'])
        self.name = 'Resize image to ' + size

    def do(self, aoi):
        self.undoBitmap = Spotlight.workingImage.copy()
        self.execute(aoi)
        Spotlight.aList.updateModelessAois()

    def undo(self):
        Spotlight.setWorkingImage(self.undoBitmap)
        # take care of whole image aoi and refresh
        Spotlight.updateWholeImageAoiSize()
        Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        img = Spotlight.workingImage.copy()
        outImage = self.executeResize(img)
        if outImage:
            Spotlight.setWorkingImage(outImage)
            # take care of whole image aoi and refresh
            Spotlight.updateWholeImageAoiSize()

    def executeResize(self, image):
        params = self.getParams()
        if params['type'] == 'percent':
            w, h = Spotlight.getWorkingImageSize()
            newWidth = int(w * params['newWidth'] / 100.0)
            newHeight = int(h * params['newHeight'] / 100.0)
            return PilProcess.Resize(image, newWidth, newHeight)
        else:
            return PilProcess.Resize(image, params['newWidth'], params['newHeight'])

    def showDialog(self):
        params = SpotlightGui.gui.showModalDialog(self.params['name'], self.params)
        if params:
            # this eliminates a weird problem that when the original size is the
            # same as the new size (and OK is clicked) it would move the image
            # down by a pixel (probably a resampling side-effect)
            w, h = Spotlight.getWorkingImageSize()
            if params['type'] == 'percent':
                newWidth = int(w * params['newWidth'] / 100.0)
                newHeight = int(h * params['newHeight'] / 100.0)
            else:
                newWidth = int(params['newWidth'])
                newHeight = int(params['newHeight'])
            if newWidth == w and newHeight == h:
                self.setParams(params)  # set the params anyway
                return False  # same as clicking Cancel
            else:
                self.setParams(params)
                return True
        else:
            return False

    def isRedoable(self):
        return False # not a redoable type operation

#---------------- ConvertImage class ----------------------------
## NOTE: this class was lifted from the 16-bit Spotlight and still has parts
## of the code (like depht) which do not apply here, but it does not interfere.

defaultConvOperation = 0     # 0=type, 1=depth
defaultConvDepth = 0           # 0=convert from 8-bit to 16-bit

class cmdConvertImage(mtCommand):
    """
    ConvertImage does two types of conversion: type and depth. Type refers
    to color (e.g. from 8-bit to 24-bit) and depth refers to bits per pixel (e.g. from
    8 bit to 16 bit)
    """
    def __init__(self):
        mtCommand.__init__(self)

        if Spotlight.originalMode == 'L':
            mode = 0
        else:
            mode = 1

        params = {'name': 'ConvertImage',
                        'operation': defaultConvOperation,
                        'type': mode,
                        'depth': defaultConvDepth}
        self.setParams(params)

    def getParams(self):
        return self.params

    def setParams(self, params):
        global defaultConvOperation
        global defaultConvDepth
        defaultConvOperation = params['operation']
        defaultConvDepth = params['depth']
        self.params = {'name': 'ConvertImage',
                            'operation': params['operation'],
                            'type': params['type'],
                            'depth': params['depth']}
        self.setName()

    def setName(self):
        if self.params['operation'] == 0:  # color type conversion
            if self.params['type'] == 0:
                self.name = 'Convert image - grayscale to color'
            else:
                self.name = 'Convert image - color to grayscale'
        else:
            if self.params['depth'] == 0:
                self.name = 'Convert image - 8-bit to 16-bit'
            else:
                self.name = 'Convert image - 16-bit to 8-bit'

    def do(self, aoi):
        self.undoBitmap = Spotlight.workingImage.copy()
        self.execute(aoi)
        Spotlight.aList.updateModelessAois()

    def undo(self):
        Spotlight.setOriginalMode('RGB')
        Spotlight.setWorkingImage(self.undoBitmap)
        Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        img = Spotlight.workingImage.copy()
        if self.params['operation'] == 0:    # color type conversion
            outImage = self.executeConvertType(img)
        else:
            outImage = self.executeConvertDepth(img)

        if outImage:
            Spotlight.setWorkingImage(outImage)

    def executeConvertType(self, image):
        pMode = self.params['type']
        if Spotlight.originalMode == 'L' and pMode == 0:
            Spotlight.setOriginalMode('RGB')
            return image
        elif Spotlight.originalMode == 'RGB' and pMode == 1:
            Spotlight.setOriginalMode('L')
            image = image.convert('L')  # this grays the image
            image = image.convert('RGB')  # convert back (Spotlight is 24-bit internally)
            return image
        else:
            return image

    def executeConvertDepth(self, image):
        return None

    def showDialog(self):
        params = SpotlightGui.gui.showModalDialog(self.params['name'], self.params)
        if params:
            self.setParams(params)
            return True
        else:
            return False

    def isRedoable(self):
        return False # don't redo at end of list


#---------------- Update class ----------------------------

class cmdUpdate(mtCommand):
    def __init__(self):
        mtCommand.__init__(self)
        self.name = 'Update IP Sequence'
        self.undox1 = 0  # previous position
        self.undoy1 = 0
        self.undox2 = 0
        self.undoy2 = 0
        self.undoAngle = 0.0
        self.undoSnakePoints = []

    def do(self, aoi):
        if aoi:
            # save stuff for undo
            aoiRect = aoi.getAoiPosition()
            aoiBitmap = Spotlight.getAoiImage(aoiRect)
            self.undoBitmap = Spotlight.workingImage.copy()
            self.undox1 = aoi.x1  # save original aoi positions
            self.undoy1 = aoi.y1
            self.undox2 = aoi.x2
            self.undoy2 = aoi.y2
            self.undoAngle = aoi.angle
            self.undoAoi = aoi
            #self.undoSnakePoints = copy.deepcopy(aoi.getControlPoints())
            # execute ip and tracking
            self.execute(aoi)
            Spotlight.aList.updateModelessAois()

    def undo(self):
        Spotlight.setWorkingImage(self.undoBitmap)
        self.undoAoi.setAngle(self.undoAngle)
        self.undoAoi.setAoiPosition(self.undox1, self.undoy1, self.undox2, self.undoy2, True)
        Spotlight.aList.updateModelessAois()

    def execute(self, aoi):
        # execute sequence of operations in the ipSequence dialog box
        self.data = []
        n = aoi.getSeqListLength()
        for pos in range(n):
            cmdIp = aoi.getSeqItem(pos)
            cmdIp.execute(aoi)
            d = cmdIp.getData() # d is list of lists
            if len(d) > 0: # if d contains data
                for item in d:
                    self.data.append(item)
        # preform tracking
        aoi.Track()
        self.trackPoint = aoi.getTrackPoint()
        self.trackPointLabel = aoi.getTrackDataLabel()
        aoi.updateStatusBar0()

    def getData(self):
        return self.data

    def getHeader(self, aoi):
        h = []
        # get header(s) from the process operations sequence, if any
        n = aoi.getSeqListLength()
        for pos in range(n):
            cmdIp = aoi.getSeqItem(pos)
            ipheader = cmdIp.getHeader()
            h.append(ipheader)
        # get header from this aoi, if any
        aoiheader = aoi.getHeader() #currently only tracking Aois returns a header
        h.append(aoiheader)
        return h

    def getTrackDataLabel(self):
        return self.trackPointLabel

    def getTrackPoint(self):
        return self.trackPoint
