import math
import os
import sys
import pickle
import string
import Spotlight
import SpotlightGui
import copy
import types
import operator
import Abel
import SpotlightPoint
import PilProcess

DEGtoRAD = (3.1415926536/180.0)

RED = 0
GREEN = 1
BLUE = 2
HUE = 3
SATURATION = 4
LUMINANCE = 5
RGB = 6

class Aoi:
    def __init__(self, x1, y1, x2, y2):
        r = self.clipRectToImage(x1, y1, x2, y2) # make sure aoi fits into the image
        self.x1 = r[0]
        self.y1 = r[1]
        self.x2 = r[2]
        self.y2 = r[3]
        self.angle = 0.0
        self.lastPoint = (0,0)
        self.leftdown = False
        self.closest = 0
        self.aoiImage = None
        self.lineThickness = 1
        self.ipSequenceList = []

    def updateAngle(self):
        pass
    def getConstrain(self):
        return False
    def Stop(self):
        pass
    def isSlithering(self):
        return False
    def useVelocity(self):
        return False
    def getVelocity(self):
        return (0.0, 0.0)
    def setVelocity(self, v):
        pass
    def getControlPoints(self):
        return []
    def isCloseExecuted(self):
        'overriden in all modeless AOIs'
        return False
    def isThresholdTrackingAoi(self):
        'overriden by AoiThresholdTracking and AoiCenterTracking class'
        return False
    def isWholeImageAoi(self):
        'overriden in AoiWholeImage class'
        return False
    def aoiOptionsPresent(self):
        return False
    def showAoiOptions(self):
        pass
    def getAngle(self):
        return self.angle
    def setAngle(self, angle):
        pass
    def updateModeless(self, type): # updates modeless aois
        pass
    def Track(self):
        pass
    def getTrackPoint(self):
        return (-1, -1)
    def getTrackDataLabel(self):
        return ()
    def getAdditionalDataLabel(self):
        return ()
    def getHeader(self):  # check whether needed
        return []
    def initialize(self):
        pass
    def deinitialize(self):
        pass
    def drawAoi(self, highlight):
        pass
    def OnMouseMove(self, pos):
        pass
    def OnMouseLeftDown(self, pos):
        pass
    def OnMouseLeftUp(self, pos):
        pass
    def OnMouseRightDown(self, pos):
        pass
    def OnMouseRightDClick(self, pos):
        pass
    def isManualAoi(self):
        'overriden in AoiManualTracking and AoiLineFollowing class'
        return False

    def setAoiCoordinates(self, x1, y1, x2, y2):
        'overriden in Snake'
        r = self.clipRectToImage(x1, y1, x2, y2)
        self.x1 = r[0]
        self.y1 = r[1]
        self.x2 = r[2]
        self.y2 = r[3]

    def getAoiPosition(self):
        """
        Take min and max because a line profile causes a crash if
        (depending on angle) x1 is greater than x2 and/or y1 is greater
        than y2. Also if the line is horizontal or vertical.
        """
        # make x1 and y1 smaller than x2 and y2.
        x1 = min(self.x1, self.x2)
        y1 = min(self.y1, self.y2)
        x2 = max(self.x1, self.x2)
        y2 = max(self.y1, self.y2)
        # prevent horizontal or vertical line
        x2 = max(x1+3, x2)
        y2 = max(y1+3, y2)
        # make sure coordinates are inside the image
        r = self.clipRectToImage(x1, y1, x2, y2)
        x1 = r[0]
        y1 = r[1]
        x2 = r[2]
        y2 = r[3]
        return (x1, y1, x2, y2)

    def showAoiPositionDialog(self):
        """bring up StandardAoiPosition dialog box"""
        type = 'StandardAoiPosition'
        params = {}
        params['x1'] = self.x1
        params['y1'] = self.y1
        params['x2'] = self.x2
        params['y2'] = self.y2
        params = SpotlightGui.gui.showModalDialog(type, params)
        return params

    def getAoiImage(self):
        return Spotlight.getAoiImage(self.getAoiPosition())

    def dist(self, x1, y1, x2, y2):
        t1 = t2 = 0.0
        t1 = x1 - x2
        t2 = y1 - y2
        return math.sqrt(t1*t1 + t2*t2)

    def getCross(self, center, leg):
        'returns two lines which make the cross'
        x, y = center
        line1 = []
        line1.append((x-leg, y))
        line1.append((x+leg, y))
        line2 = []
        line2.append((x, y-leg))
        line2.append((x, y+leg))
        return (line1, line2)

    def getAoiCenter(self):
        x = (self.x1 + self.x2)/2
        y = (self.y1 + self.y2)/2
        return (x, y)

    def moveAoi(self, offsetX, offsetY):
        x1 = self.x1 + offsetX
        y1 = self.y1 + offsetY
        x2 = self.x2 + offsetX
        y2 = self.y2 + offsetY
        r = self.clipRectToImage(x1, y1, x2, y2)
        self.x1 = r[0]
        self.y1 = r[1]
        self.x2 = r[2]
        self.y2 = r[3]

    def clipRectToImage(self, x1, y1, x2, y2):
        'limit mevement of Aoi only inside the image'
        imX, imY = Spotlight.getWorkingImageSize()
        w = min(imX, x2-x1)
        h = min(imY, y2-y1)
        if x1 < 0:
            x1 = 0
            x2 = w
        elif x2 > imX:
            x1 = imX - w
            x2 = imX
        if y1 < 0:
            y1 = 0
            y2 = h
        elif y2 > imY:
            y1 = imY - h
            y2 = imY
        return (x1, y1, x2, y2)

    def clipPointToImage(self, x, y, img=None):
        'prevents enlargement of Aoi when corner is dragged out of the image'
        if img:
            #imX, imY = img.columns(), img.rows()
            imX, imY = img.size
        else:
            imX, imY = Spotlight.getWorkingImageSize()

        if x < 0:
            x = 0
        if x > imX:
            x = imX
        if y < 0:
            y = 0
        if y > imY:
            y = imY
        return (x, y)

    def getPointOnRectangle(self, xx1, yy1, xx2, yy2, center, angle):
        """
        Calculates an xy location of a line intersecting a rectangle.
        Basically you have an rectangular AOI and a line going out from
        the center of the AOI at some angle and you want to know the
        point where the line (radius) intersect the rectangle.
        """
        x = 0
        y = 0
        previousX = 0
        previousY = 0
        for i in range(1,10000):
            x, y = self.calcEndPoint(center, i, angle)
            if x <= xx1 or x >= xx2 or y <= yy1 or  y >= yy2:
                break
            previousX = x
            previousY = y
        return (previousX, previousY)

    def calcEndPoint(self, p, linelength, angle):
        """
        Calculate the coordinates relative to point p, based on an
        angle. It could be thought of as a point along a circle with
        the radius (linelength) and an angle.
        """
        x = linelength*math.cos(angle*DEGtoRAD)
        y = linelength*math.sin(angle*DEGtoRAD)
        return (p[0] + int(round(x)), p[1] - int(round(y)))

    def updateStatusBar0(self):
        aoiType = self.getStatusBarText()
        if Spotlight.scaleUserUnits == 1.0 and Spotlight.scalePixelUnits == 1.0:
            message = aoiType + ': (%3d, %3d) (%3d, %3d)' \
                    % (self.x1,self.y1,self.x2,self.y2)
        else:
            x1 = self.x1 * Spotlight.pixelScale
            y1 = self.y1 * Spotlight.pixelScale
            x2 = self.x2 * Spotlight.pixelScale
            y2 = self.y2 * Spotlight.pixelScale
            message = aoiType + ': (%.3f, %.3f) (%.3f, %.3f)' \
                    % (x1, y1, x2, y2)
        SpotlightGui.gui.updateStatusBar(message, 0)

##---- The following functions deal with IpSequence dialog box

    def addThresholdOperation(self, pos=0):
        """
        Called from cmdNewAoiThresholdTracking class - adds a manditory
        threshold operation to a ipSequenceList if a threshold tracking
        aoi was selected.
        """
        threshOp = Spotlight.instantiateIpCommand({'name': 'Threshold'})
        self.ipSeqInsert(pos, threshOp) # update ipSequenceList

    def ipSeqInsert(self, pos, op):
        'insert item into the ipSequenceList'
        self.ipSequenceList.insert(pos, op)

    def ipSeqDelete(self, pos):
        'delete item at the given position'
        del self.ipSequenceList[pos]

    def getSeqItem(self, pos):
        return self.ipSequenceList[pos]

    def getSeqListLength(self):
        return len(self.ipSequenceList)

    def getDuplicateSeqList(self):
        """
        Create a copy of the sequence list - done the right way by getting
        the parameters of each ip operation, instantiating the ip operation,
        and setting the parameters again.
        """
        newSeqList = []
        for ip in self.ipSequenceList:
            params = ip.getParams()
            ip = self.instantiateIpCommand(params)
            ip.setParams(params)  # set up the class's parameters
            newSeqList.append(ip)
        return newSeqList

    def setSeqList(self, inputList):
        self.ipSequenceList = []
        n = len(inputList)
        for i in range(n):
            self.ipSequenceList.append(inputList[i])

    def instantiateIpCommand(self, params):
        'instantiates an ip operation (command) from the parameters passed in'
        return Spotlight.instantiateIpCommand(params)

##-------------------- AoiRectangle class ----------------------------

defaultWidth = 6
defaultHeight = 4
defaultAspect = False

class AoiRectangle(Aoi):
    def __init__(self, x1, y1, x2, y2):
        Aoi.__init__(self, x1, y1, x2, y2)

        params = {'newWidth': defaultWidth,
                        'newHeight': defaultHeight,
                        'fixedAspect': defaultAspect}
        self.setParams(params)

    def getStatusBarText(self):
        return 'rectangularAoi'

    def setParams(self, params):
        global defaultWidth
        global defaultHeight
        global defaultAspect
        defaultWidth = params['newWidth']
        defaultHeight = params['newHeight']
        defaultAspect = params['fixedAspect']

    def getParams(self):
        params = {'newWidth': defaultWidth,
                        'newHeight': defaultHeight,
                        'fixedAspect': defaultAspect}
        return params

    def showAoiOptions(self):
        """ Bring up Rectangle Aoi options dialog box. """
        if self.isWholeImageAoi():
            m = 'This option is only available for Rectangular Aoi.'
            SpotlightGui.gui.messageDialog(m)
            return
        type = 'RectangleAoiOptions'
        params = self.getParams()
        params = SpotlightGui.gui.showModalDialog(type, params)
        if params:
            self.setParams(params)

    def aoiOptionsPresent(self):
        'yes, this aoi has options associated with it'
        return True

    def drawAoi(self, highlight, dc=None):
        params = {}
        pointList = []
        points = []
        points.append((self.x1, self.y1))
        points.append((self.x2, self.y1))
        points.append((self.x2, self.y2))
        points.append((self.x1, self.y2))
        points.append((self.x1, self.y1))
        pointList.append(points)
        params['pointList'] = pointList
        params['highlight'] = highlight
        params['thickness'] = self.lineThickness
        params['rectHandles'] = True
        SpotlightGui.gui.iPanel.drawAoi(params, dc)

    def setAoiPosition(self, x1, y1, x2, y2, fromUpdate=False):
        """
        set aoi to the position specified - called from either
        menu Aoi-->SetPosition or from cmdUpdate class undo().
        """
        # check that minimum height or width is 4 pixels
        if y2 < y1+4:
            y1 = y1 - 2
            y2 = y1 + 4
            SpotlightGui.gui.messageDialog('box must be minimum of 4 pixels high')
        if x2 < x1+4:
            x1 = x1 - 2
            x2 = x1 + 4
            SpotlightGui.gui.messageDialog('box must be minimum of 4 pixels wide')
        r = self.clipRectToImage(x1, y1, x2, y2)
        self.x1 = r[0]
        self.y1 = r[1]
        self.x2 = r[2]
        self.y2 = r[3]
        SpotlightGui.gui.iPanel.Refresh()
        self.updateStatusBar0()

    def OnMouseMove(self, pos):
        if self.isWholeImageAoi():
            return
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
                cp = self.clipPointToImage(px, py) # prevent enlargement of Aoi when edge is reached
                px = cp[0]
                py = cp[1]

                if self.closest == 1:      # top left corner
                    self.x1 = px
                    self.y1 = py
                elif self.closest == 2:    # top right corner
                    self.x2 = px
                    self.y1 = py
                elif self.closest == 3:    # bottom right corner
                    self.x2 = px
                    self.y2 = py

                    if Spotlight.ctrlKeyDown:
                        params = self.getParams()
                        aspectRatio = float(params['newWidth']) / float(params['newHeight'])
                        diffy = self.y2 - self.y1
                        self.x2 = self.x1 + int(diffy*aspectRatio)

                elif self.closest == 4:    # bottom left corner
                    self.x1 = px
                    self.y2 = py

                self.x2 = max(self.x2, self.x1+4) # make sure it's not too small
                self.y2 = max(self.y2, self.y1+4)

            r = self.clipRectToImage(self.x1, self.y1, self.x2, self.y2)
            self.x1 = r[0]
            self.y1 = r[1]
            self.x2 = r[2]
            self.y2 = r[3]
            self.updateStatusBar0()
            self.lastPoint = (px, py)
            SpotlightGui.gui.iPanel.Refresh()  # calls OnPaint in iPanel

    def OnMouseLeftDown(self, pos):
        self.closest = self.Closest(pos)
        self.leftdown = True
        self.lastPoint = pos

    def OnMouseLeftUp(self, pos):
        self.leftdown = False

    def Closest(self, c):
        clos = 0
        d = 0.0
        dmin = 10e10
        d = self.dist(self.x1, self.y1, c[0], c[1])
        if (d<dmin and d<10):  # "near" is within 10 pixels
            dmin = d
            clos = 1
        d = self.dist(self.x2, self.y1, c[0], c[1])
        if (d<dmin and d<10):
            dmin = d
            clos = 2
        d = self.dist(self.x2, self.y2, c[0], c[1])
        if (d<dmin and d<10):
            dmin = d
            clos = 3
        d = self.dist(self.x1, self.y2, c[0], c[1])
        if (d<dmin and d<10):
            dmin = d
            clos = 4
        return clos

    def getDataLabel(self, trackPoint, columnWidth=12):
        """
        Used by all tracking AOI's. Converts to string and pads with spaces
        for writing out to file. The returned value is a tuple of 2 lists
        as shown below.
        (['   xval     '], ['   yval     '])
        """
        x = trackPoint[0]
        y = trackPoint[1]

        if Spotlight.scaleUserUnits == 1.0 and Spotlight.scalePixelUnits == 1.0:
            # do x
            x1 = '%.1f' % x  # 1 digit to right of decimal point
            sx1 = string.strip(str(x1)) # eliminate leading or trailing whitespace
            sx = string.rjust(sx1, 5)  # right justified in a string 4 wide
            if columnWidth == 12:  ####FIXME: make it variable width
                sxout = "   " + sx + "    "  # total of 12 chars
            else:
                sxout = "   " + sx + "     "  # total of 13 chars
            tx = []
            tx.append(sxout)
            # do y
            y1 = '%.1f' % y
            sy1 = string.strip(str(y1))
            sy = string.rjust(sy1, 5)
            if columnWidth == 12:  ####FIXME: make it variable width
                syout = "   " + sy + "    "  # total of 12 chars
            else:
                syout = "   " + sy + "     "  # total of 13 chars
            ty = []
            ty.append(syout)
        else:
            x = x * Spotlight.pixelScale
            y = y * Spotlight.pixelScale
            # do x
            x1 = '%.5f' % x  # 5 digit to right of decimal point
            sx1 = string.strip(str(x1)) # eliminate leading or trailing whitespace
            sx = string.rjust(sx1, 10)  # right justified in a string 4 wide
            if columnWidth == 12:  ####FIXME: make it variable width
                sxout = "" + sx + "  "  # total of 12 chars
            else:
                sxout = "" + sx + "   "  # total of 13 chars
            tx = []
            tx.append(sxout)
            # do y
            y1 = '%.5f' % y
            sy1 = string.strip(str(y1))
            sy = string.rjust(sy1, 10)
            if columnWidth == 12:  ####FIXME: make it variable width
                syout = "" + sy + "  "  # total of 12 chars
            else:
                syout = "" + sy + "   "  # total of 13 chars
            ty = []
            ty.append(syout)
        return (tx, ty)  # this format:  (['   xval     '], ['   xval     '])

##---------------------------- AoiLine class --------------------------------

class AoiLine(Aoi):
    def __init__(self, x1, y1, x2, y2):
        Aoi.__init__(self, x1, y1, x2, y2)

    def getStatusBarText(self):
        return 'lineAoi'

    def getLineLength(self):
        return self.dist(self.x1, self.y1, self.x2, self.y2)

    def setAngle(self, angle):
        self.angle = angle

    def getAngle(self):
        return self.angle

    def drawAoi(self, highlight, dc=None):
        params = {}
        pointList = []
        points = []
        points.append((self.x1, self.y1))
        points.append((self.x2, self.y2))
        pointList.append(points)
        params['pointList'] = pointList
        params['highlight'] = highlight
        params['thickness'] = self.lineThickness
        params['lineHandles'] = True
        SpotlightGui.gui.iPanel.drawAoi(params, dc)

    def setAoiPosition(self, x1, y1, x2, y2, fromUpdate=False):
        """Set aoi to the position specified - called from either
        menu Aoi-->SetPosition or from cmdUpdate class undo().
        """
        r = self.limitLineMovement(x1, y1, x2, y2) # takes line thickness into account
        self.x1 = r[0]
        self.y1 = r[1]
        self.x2 = r[2]
        self.y2 = r[3]
        SpotlightGui.gui.iPanel.Refresh()
        self.updateStatusBar0()

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
            self.updateAngle()
            SpotlightGui.gui.iPanel.Refresh()

    def OnMouseLeftDown(self, pos):
        self.closest = self.Closest(pos)
        self.leftdown = True
        self.lastPoint = pos

    def OnMouseLeftUp(self, pos):
        self.leftdown = False

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

    def limitLineMovement(self, x1, y1, x2, y2):
        imX, imY = Spotlight.getWorkingImageSize()
        lenx = min(imX, x2-x1)
        leny = min(imY, y2-y1)
        minXY = self.lineThickness / 2       # left or top edge of where line can go
        maxX = imX - self.lineThickness / 2  # right edge of where line can go
        maxY = imY - self.lineThickness / 2  # bottom edge of where line can go
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

    def getLine(self, x1, y1, x2, y2, img = None):
        """ This function was obtained from Graphics Gems, p. 685.  The routine
        uses the Bresenhams algorithm to read pixels in a straight line."""
        pixels = []
        dx = x2-x1
        dy = y2-y1
        ax = abs(dx) << 1  # fast mult by 2
        ay = abs(dy) << 1
        sx = self.sgn(dx)
        sy = self.sgn(dy)
        x = x1
        y = y1
        if ax > ay:           # x dominant
            d = ay-(ax >> 1)
            while(1):
                pix = Spotlight.getPixelNorm(x, y, img)
                pixels.append(pix)
                if x == x2:
                    break
                if d >= 0:
                    y = y + sy
                    d = d - ax
                x = x + sx
                d = d + ay
        else:                 # y dominant
            d = ax-(ay >> 1)
            while(1):
                pix = Spotlight.getPixelNorm(x, y, img)
                pixels.append(pix)
                if y == y2:
                    break
                if d >= 0:
                    x = x + sx
                    d = d - ay
                y = y + sy
                d = d + ax
        return pixels

    def sgn(self, d):
        if d > 0:
            return 1
        else:
            return -1

    def getLineXY(self, x1, y1, x2, y2, img = None):
        """Same as getLine(), except this function also returns the xy
        coordinates in addition to the profile line. This function was
        obtained from Graphics Gems, p. 685. The routine uses the Bresenhams
        algorithm to read pixels in a straight line."""
        pixels = []
        dx = x2-x1
        dy = y2-y1
        ax = abs(dx) << 1  # fast mult by 2
        ay = abs(dy) << 1
        sx = self.sgn(dx)
        sy = self.sgn(dy)
        x = x1
        y = y1
        if ax > ay:           # x dominant
            d = ay-(ax >> 1)
            while(1):
                p = Spotlight.getPixelNorm(x, y, img)
                pxy = (p, x, y)
                pixels.append(pxy)
                if x == x2:
                    break
                if d >= 0:
                    y = y + sy
                    d = d - ax
                x = x + sx
                d = d + ay
        else:                 # y dominant
            d = ax-(ay >> 1)
            while(1):
                p = Spotlight.getPixelNorm(x, y, img)
                pxy = (p, x, y)
                pixels.append(pxy)
                if y == y2:
                    break
                if d >= 0:
                    x = x + sx
                    d = d - ay
                y = y + sy
                d = d + ax
        return pixels

    def setLine(self, x1, y1, x2, y2, value, img = None):
        """This function was obtained from Graphics Gems, p. 685.  The routine
        uses the Bresenham's algorithm to read pixels in a straight line."""
        dx = x2-x1
        dy = y2-y1
        ax = abs(dx) << 1
        ay = abs(dy) << 1
        sx = self.sgn(dx)
        sy = self.sgn(dy)
        x = x1
        y = y1
        if ax > ay:   # x dominant
            d = ay-(ax >> 1)
            while(1):
                Spotlight.setPixel(x, y, value, img)
                if x == x2:
                    break
                if d >= 0:
                    y = y + sy
                    d = d - ax
                x = x + sx
                d = d + ay
        else:     # y dominant
            d = ax-(ay >> 1)
            while(1):
                Spotlight.setPixel(x, y, value, img)
                if y == y2:
                    break
                if d >= 0:
                    x = x + sx
                    d = d - ay
                y = y + sy
                d = d + ax

    def getLineProfileXY(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0, thickness = -1, img = None):
        """
        This function is used for saving the line profile values to disk.
        This function differs from getLineProfile() in that this one returns
        xy coordinates along with the profile values. It returns a single
        line profile whether or not line thickness is 1. If the thickness
        is greater than 1 then the profiles are averaged together.
        Because the line averaging function (profileAverage()) is confusing
        enought, I didn't feel like changing it to accomodate xy's as well.
        So I left is as was (no xy's) and the xy's are added to the averaged
        line profile at the end.
        """
        if x1 == 0 and x2 == 0:
            x1 = self.x1
            y1 = self.y1
            x2 = self.x2
            y2 = self.y2
        if thickness == -1:
            thickness = self.lineThickness

        if thickness == 1:
            return self.getLineXY(x1, y1, x2, y2, img)

        ### I DON'T THINK THIS PART WORKS RIGHT - when I was calling this
        ### function from LocalMaxTracking and used line thicknesses of 3 and
        ### 5, I got back results that were close but not exaclty what I
        ### expected.
        else:
            profList = []  # list of line profiles (list of lists)
            p = self.getLine(x1, y1, x2, y2, img)  # centerline
            profList.append(p)

            # append the other lines (in addition to the centerline). The loop alternates
            # between the one or the other half of the if-statement and appends one at a time.
            for i in range(1, thickness):
                dist = i / 2 + i % 2  # distance from the centerline

                if i % 2:  # i is odd (remainder exists)
                    p = self.getOtherLine(dist, -90.0, img)  # get line at -90 degrees
                    profList.append(p)
                else:  # i is even
                    p = self.getOtherLine(dist, 90.0, img)  # get line at +90 degrees
                    profList.append(p)

            minLen = self.getMinLength(profList)  # get min line length
            avprof = self.profileAverage(profList, minLen)  # average profiles

            # get only xy's from this
            pxy = self.getLineXY(x1, y1, x2, y2, img)

            # since avprof does not contain xy's, must attach the xy's from pxy to avprof
            n = min(len(avprof), len(pxy))
            avout = []
            for i in range (n):
                a = avprof[i]
                x = pxy[i][1]
                y = pxy[i][2]
                avout.append((a, x, y))
            return avout

    def getLineProfile(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0, thickness = -1, img = None):
        """
        This function is used for displaying the line profile in the
        dialog box. It is faster than getLineProfileXY, since it
        doesn't contain the xy coordinates. It returns a single line
        profile whether or not line thickness is 1. If the thickness
        is greater than 1 then the profiles are averaged together.
        """
        if x1 == 0 and x2 == 0:
            x1 = self.x1
            y1 = self.y1
            x2 = self.x2
            y2 = self.y2
        if thickness == -1:
            thickness = self.lineThickness
        if thickness == 1:
            return self.getLine(x1, y1, x2, y2, img)
        else:
            profList = []  # list of line profiles (list of lists)
            p = self.getLine(x1, y1, x2, y2, img)  # centerline
            profList.append(p)

            # append the other lines (in addition to the centerline). The loop alternates
            # between the one or the other half of the if-statement and appends one at a time.
            # for i in range(1, self.lineThickness):
            for i in range(1, thickness):
                dist = i / 2 + i % 2  # distance from the centerline

                if i % 2:  # i is odd (remainder exists)
                    p = self.getOtherLine(dist, -90.0, img)  # get line at -90 degrees
                    profList.append(p)
                else:  # i is even
                    p = self.getOtherLine(dist, 90.0, img)  # get line at +90 degrees
                    profList.append(p)

            minLen = self.getMinLength(profList)  # get min line length
            return self.profileAverage(profList, minLen)  # average profiles

    def profileAverage(self, profileList, minLen):
        """
        Calculate average of several line profiles. For grayscale images
        the 0th elements are averaged together, then 1st elements, etc. For
        color images the 0th elements of the reds are averaged together, then
        0th elements of greens, etc.
        NOTE: a PIL version of this function had if-statements checking for
        number of color planes but under PythonMagick getting pixel value
        always returns RGB.
        """
        profLen = len(profileList)
        av = []
        avr = []
        avg = []
        avb = []
        for x in range (0, minLen):  # loop over elements in each line
            sumr = 0
            sumg = 0
            sumb = 0
            for i in range (0, profLen):  # loop over each line
                sumr = sumr + profileList[i][x][0]
                sumg = sumg + profileList[i][x][1]
                sumb = sumb + profileList[i][x][2]
            avr.append(sumr / profLen)
            avg.append(sumg / profLen)
            avb.append(sumb / profLen)

        # must write out in the right format
        for x in range (0, minLen):
            r = avr[x]
            g = avg[x]
            b = avb[x]
            colorpix = (r, g, b)
            av.append(colorpix)
        return av

    def getMinLength(self, profileList):
        """Get the number of elements of the shortest profile line - in case
        they're not all the same length, it will prevent overflow on the
        shorter ones. From a quick check, all the lines were always the same
        length - but you never know"""
        minLen = 10000
        for i in range (0, len(profileList)):
            n = len(profileList[i])
            if n < minLen:
                minLen = n
        return minLen

    def getOtherLine(self, dist, ang, img = None):
        """returns a line profile which is offset from the centerline by
        dist. ang determines the angle relative to centerline where this
        line is to be placed (i.e. which side of the centerline)."""
        angle = self.calcAngle(ang)
        c1 = (self.x1, self.y1)
        a1 = self.calcEndPoint(c1, dist, angle)
        c2 = (self.x2, self.y2)
        a2 = self.calcEndPoint(c2, dist, angle)
        return self.getLine(a1[0], a1[1], a2[0], a2[1], img)

    def calcAngle(self, offsetAngle):
        """First, it calculates the angle of the main line (ang). Then it
        calculates a new angle (called angle) which is offset from the
        line angle by some number of degrees (offsetAngle). This final
        angle (named angle) is just some angle relative to the line
        angle. Note: the line angle is the angle of the line drawn between
        (self.x1, self.y1) and (self.x2, self.y2)."""
        dx = float(self.x2 - self.x1)
        dy = float(self.y2 - self.y1)
        ang = math.atan2(-dy, dx)/DEGtoRAD
        if ang < 0.0:
            ang = ang + 360.0
        if ang > 89.998 and ang < 90.002: # some round-off weirdness
            ang = 90.0000
        angle = ang + offsetAngle
        if angle < 0.0:
            angle = angle + 360.0
        if angle > 360.0:
            angle = angle - 360.0
        return angle

    def changeLineThickness(self, thickness):
        'change thickness as specified in the profile dialog box'
        self.lineThickness = thickness
        # in case the line is on the edge of image and then thickens up
        r = self.limitLineMovement(self.x1, self.y1, self.x2, self.y2)
        self.x1 = r[0]
        self.y1 = r[1]
        self.x2 = r[2]
        self.y2 = r[3]
        SpotlightGui.gui.iPanel.Refresh()
        self.updateLineProfile()

    def breakOutProfile(self, colorLine, colorPlane):
        """
        Returns a grayscale profile from a RGB profile.
        """
        p = []
        n = len(colorLine)

        for r, g, b in colorLine:
            if colorPlane == RED:
                p.append(r)
            elif colorPlane == GREEN:
                p.append(g)
            elif colorPlane == BLUE:
                p.append(b)
            elif colorPlane == LUMINANCE:
                p.append((r + g + b) / 3)
            elif colorPlane == HUE:
                #hue, sat = self.calcHue(r, g, b)
                #p.append(hue)
                h, s, v = self.Rgb2Hsv((r, g, b))
                p.append(h)
        return p

    def calcHue(self, r, g, b):
        """ Bob's original -- outputs h in [0.0 ... 6.28] or 0 to 2pi. """
        rf = float(r)
        gf = float(g)
        bf = float(b)
        rf = rf/255.0
        gf = gf/255.0
        bf = bf/255.0
        inten = (rf+gf+bf)/3.0
        if(not((r==b) and (r==g))):
            min = rf
            if(min>gf): min = gf
            if(min>bf): min = bf
            sat=1.0-(min/inten)
            t1 = rf-gf
            t2 = rf-bf
            t3 = gf-bf
            t4 = math.sqrt((t1*t1)+(t2*t3))
            t5 = (t1+t2)/2.0
            t5 = t5/t4
            hue = math.acos(t5)
            if(gf<bf): hue=2.0*math.pi-hue
        else:
            hue=-1000.0
            sat=-1.0
        return (hue, sat)

##
### RGB<-->HSV
##
    def Rgb2Hsv (self, rgbtuple):
        """ H, S, V will be in [0.0 ... 1.0] """
        r, g, b = rgbtuple
        r = r / 255.0
        g = g / 255.0
        b = b / 255.0
        minRgb = min (r, g, b)
        maxRgb = max (r, g, b)
        deltaRgb = maxRgb - minRgb
        v = maxRgb
        if (deltaRgb == 0):     # This is a gray, no chroma...
            ### RBK change: modified to reflect no hue
            h = -1.0
            s = -1.0
            #h = 0.0
            #s = 0.0
        else:                   # Chromatic data
            s = deltaRgb / maxRgb
            del_R = (((maxRgb - r) / 6.0) + (deltaRgb / 2.0)) / deltaRgb
            del_G = (((maxRgb - g) / 6.0) + (deltaRgb / 2.0)) / deltaRgb
            del_B = (((maxRgb - b) / 6.0) + (deltaRgb / 2.0)) / deltaRgb
            if   (r == maxRgb):
                h = del_B - del_G
            elif (g == maxRgb):
                h = (1.0 / 3.0) + del_R - del_B
            elif (b == maxRgb):
                h = (2.0 / 3.0) + del_G - del_R
            #end if
            h = h % 1.0
        #end if
        return (h, s, v)

    def Hsv2Rgb (self, hsvtuple):
        h, s, v = hsvtuple
        if (s == 0.0):
           r = v * 255.0
           g = v * 255.0
           b = v * 255.0
        else:
            h = h * 6.0
            I = int (h)          # floor function
            F = h - I
            P = v * (1.0 - s)
            Q = v * (1.0 - s * F)
            T = v * (1.0 - s * (1.0 - F))
            if   (I == 4):
                r = T
                g = P
                b = v
            elif (I == 5):
                r = v
                g = P
                b = Q
            elif (I == 0):
                r = v
                g = T
                b = P
            elif (I == 1):
                r = Q
                g = v
                b = P
            elif (I == 2):
                r = P
                g = v
                b = T
            elif (I == 3):
                r = P
                g = Q
                b = v
            #end if
            r = int ((r * 255.0) + 0.5)
            g = int ((g * 255.0) + 0.5)
            b = int ((b * 255.0) + 0.5)
        #end if
        return (r, g, b)

##
### RGB<-->HSL
##
    def Rgb2Hsl (self, rgbtuple):
        # H, S, L will be in [0.0 ... 1.0]
        r, g, b = rgbtuple
        rScaled = r/255.0
        gScaled = g/255.0
        bScaled = b/255.0

        rgbMin = min (rScaled, gScaled, bScaled)    # Min RGB value
        rgbMax = max (rScaled, gScaled, bScaled)    # Max RGB value
        deltaRgb = rgbMax - rgbMin                  # Delta RGB value

        L = (rgbMax + rgbMin) / 2.0

        if (deltaRgb == 0.0):   # This is a gray, no chroma.
           H = 0.0
           S = 0.0              # Done !
        else:                   # Chromatic data...
            if (L < 0.5):
                S = deltaRgb / (rgbMax + rgbMin)
            else:
                S = deltaRgb / (2.0 - rgbMax - rgbMin)
            #end if

            deltaR = (((rgbMax - rScaled)/6.0) + (deltaRgb/2.0)) / deltaRgb
            deltaG = (((rgbMax - gScaled)/6.0) + (deltaRgb/2.0)) / deltaRgb
            deltaB = (((rgbMax - bScaled)/6.0) + (deltaRgb/2.0)) / deltaRgb

            if   (rScaled == rgbMax):
                H = deltaB - deltaG
            elif (gScaled == rgbMax):
                H = (1.0/3.0) + deltaR - deltaB
            elif (bScaled == rgbMax):
                H = (2.0/3.0) + deltaG - deltaR
            #end if
            H = H % 1.0
        #end if
        return (H, S, L)

    def Hsl2Rgb (self, hsltuple):

        def HslHue2Rgb (v1, v2, vH):
           if (vH < 0.0):    vH += 1.0
           if (vH > 1.0):    vH -= 1.0
           if ((6.0 * vH) < 1.0):    return (v1 + (v2 - v1) * 6.0 * vH)
           if ((2.0 * vH) < 1.0):    return (v2)
           if ((3.0 * vH) < 2.0):    return (v1 + (v2 - v1) * ((2.0/3.0) - vH) * 6.0)
           return v1

        #------------------------

        # H, S, L in [0.0 .. 1.0]
        H, S, L = hsltuple
        if (S == 0.0):          # RGB grayscale
           r = L * 255.0        # R, G, B in [0 .. 255]
           g = L * 255.0
           b = L * 255.0
        else:
            if (L < 0.5):
                var_2 = L * (1.0 + S)
            else:
                var_2 = (L + S) - (S * L)
            #end if
            var_1 = (2.0 * L) - var_2
            r = 255 * HslHue2Rgb (var_1, var_2, H + (1.0/3.0))
            g = 255 * HslHue2Rgb (var_1, var_2, H            )
            b = 255 * HslHue2Rgb (var_1, var_2, H - (1.0/3.0))
        #end if

    #### below was commentted out by RBK as this isn't needed and the author
    #### probably meant to multiply the r,g,b's by 256 before added 0.5.
        #~ r = int (r + 0.5)
        #~ g = int (g + 0.5)
        #~ b = int (b + 0.5)
        return (r, g, b)

##------------------ Class CommonAngle ------------------------------------

class CommonAngle(AoiRectangle, AoiLine):
    """
    A base class used by AoiThresholdTracking class and AoiMaximumTracking
    class.
    """
    def __init__(self, x1, y1, x2, y2):
        AoiRectangle.__init__(self, x1, y1, x2, y2)
        self.angle = 0.0
        self.imageConstrainLine = []

    def drawAoi(self, highlight, dc=None):
        """
        This drawAoi is used by ThresholdTracking AOI always and by
        MaximumTracking AOI only when it the constraint line is in use.
        """
        params = {}
        pointList = []
        # draw main arrow line
        points = []
        c = self.getAoiCenter()
        arrowLength = self.getArrowLength()
        a = self.calcEndPoint(c, arrowLength, self.angle)
        points.append((c[0], c[1]))
        points.append((a[0], a[1]))
        pointList.append(points)
        # draw arrowhead
        points = []
        p1, p2 = self.getArrowEndPoints(a, self.angle)
        points.append((p1[0], p1[1]))
        points.append((a[0], a[1]))
        points.append((p2[0], p2[1]))
        pointList.append(points)
        params['pointList'] = pointList
        params['highlight'] = highlight
        params['thickness'] = self.lineThickness
        SpotlightGui.gui.iPanel.drawAoi(params, dc)         # draw the arrow
        AoiRectangle.drawAoi(self, highlight, dc)    # draw the rectangle

        if self.getConstrain() == True:
            params = {}
            pointList = []
            p1, p2 = self.getConstrainEndPoints(a, self.angle)
            # draw dashed line from arrow tip to edge of image
            points = []
            points.append((a[0], a[1]))
            points.append((p1[0], p1[1]))
            pointList.append(points)
            # draw dashed line from Aoi center to the other edge of image
            points = []
            points.append((c[0], c[1]))
            points.append((p2[0], p2[1]))
            pointList.append(points)
            params['constrain'] = self.getConstrain()
            params['pointList'] = pointList
            params['highlight'] = highlight
            params['thickness'] = self.lineThickness
            SpotlightGui.gui.iPanel.drawAoi(params, dc)

    def getAngle(self):
        return self.angle

    def updateStatusBar0(self):
        aoiType = self.getStatusBarText()
        if Spotlight.scaleUserUnits == 1.0 and Spotlight.scalePixelUnits == 1.0:
            m1 = aoiType + ': (%3d, %3d) (%3d, %3d)' % (self.x1,self.y1,self.x2,self.y2)
            m2 = '  angle: %.3f' % self.angle
            message = m1 + m2
        else:
            x1 = self.x1 * Spotlight.pixelScale
            y1 = self.y1 * Spotlight.pixelScale
            x2 = self.x2 * Spotlight.pixelScale
            y2 = self.y2 * Spotlight.pixelScale
            m1 = aoiType + ': (%.3f, %.3f) (%.3f, %.3f)' % (x1, y1, x2, y2)
            m2 = '  angle: %.3f' % self.angle
            message = m1 + m2
        SpotlightGui.gui.updateStatusBar(message, 0)

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
                cp = self.clipPointToImage(px, py) # prevent enlargement of Aoi when edge is reached
                px = cp[0]
                py = cp[1]

                if self.closest == 1:      # top left corner
                    self.x1 = px
                    self.y1 = py
                elif self.closest == 2:    # top right corner
                    self.x2 = px
                    self.y1 = py
                elif self.closest == 3:    # bottom right corner
                    self.x2 = px
                    self.y2 = py
                elif self.closest == 4:    # bottom left corner
                    self.x1 = px
                    self.y2 = py
                elif self.closest == 5:    # tip of arrow
                    ce = self.getAoiCenter()
                    arrowLength = self.getArrowLength()
                    dx = px - ce[0]
                    dy = py - ce[1]
                    self.angle = math.atan2(-dy, dx)/DEGtoRAD  # -180 to 180
                    if self.angle < 0.0:
                        self.angle = self.angle + 360.0

                self.x2 = max(self.x2, self.x1+4) # make sure it's not too small
                self.y2 = max(self.y2, self.y1+4)

            r = self.clipRectToImage(self.x1, self.y1, self.x2, self.y2)
            self.x1 = r[0]
            self.y1 = r[1]
            self.x2 = r[2]
            self.y2 = r[3]

            SpotlightGui.gui.iPanel.Refresh()
            self.lastPoint = (px, py)
            self.updateStatusBar0()

    def OnMouseLeftDown(self, pos):
        self.closest = self.Closest(pos)
        self.leftdown = True
        self.lastPoint = pos

    def OnMouseLeftUp(self, pos):
        self.leftdown = False
        self.setAngle(self.angle)
        self.setImageConstrainLine()

    def setImageConstrainLine(self):
        """
        Sets a constrain line across the entire image. This line will be
        the reference line to which track point pinned.
        """
        # make the rectangle 1 pixel less on all sides to eliminate edge problems
        imX, imY = Spotlight.getWorkingImageSize()
        x1 = 1
        y1 = 1
        x2 = imX - 2  # must make 2 less
        y2 = imY - 2
        c = self.getAoiCenter()
        angle = self.getAngle()
        self.imageConstrainLine = self.getConstrainLine(x1, y1, x2, y2, c, angle)

    def getImageConstrainLine(self):
        return self.imageConstrainLine

    def getConstrainLine(self, x1, y1, x2, y2, aoiCenter, angle):
        'Returns a line profile across an Aoi. '
        pf = self.getPointOnRectangle(x1, y1, x2, y2, aoiCenter, angle)
        angle = angle + 180.0
        if angle >= 360.0:
            angle = angle - 360.0
        pb= self.getPointOnRectangle(x1, y1, x2, y2, aoiCenter, angle)
        return self.getLineProfileXY(pf[0], pf[1], pb[0], pb[1], 1)  # thickness = 1

    def Closest(self, c):
        clos = 0
        d = 0.0
        dmin = 10e10
        d = self.dist(self.x1, self.y1, c[0], c[1])
        if (d<dmin and d<10):  # "near" is within 10 pixels
            dmin = d
            clos = 1
        d = self.dist(self.x2, self.y1, c[0], c[1])
        if (d<dmin and d<10):
            dmin = d
            clos = 2
        d = self.dist(self.x2, self.y2, c[0], c[1])
        if (d<dmin and d<10):
            dmin = d
            clos = 3
        d = self.dist(self.x1, self.y2, c[0], c[1])
        if (d<dmin and d<10):
            dmin = d
            clos = 4
        ce = self.getAoiCenter()
        arrowLength = self.getArrowLength()
        ax = ce[0] + arrowLength*math.cos(self.angle*DEGtoRAD)
        ay = ce[1] - arrowLength*math.sin(self.angle*DEGtoRAD)
        d = self.dist(ax, ay, c[0], c[1])
        if (d<dmin and d<10):
            dmin = d
            clos = 5
        return clos

    def getConstrainEndPoints(self, centerPt, angle):
        """
        Calculate hypethetical endpoints - the vector is 1000 pixels
        long,  you don't see it running off the edge of the image because
        the draw region is clipped in drawAoi function in SpotlightMain.py
        """
        # in direction of arrow
        x1 = 1000.0*math.cos(angle*DEGtoRAD)
        y1 = 1000.0*math.sin(angle*DEGtoRAD)
        p1 = (centerPt[0] + int(round(x1)), centerPt[1] - int(round(y1)))
        # opposite
        x2 = 1000.0*math.cos((angle+180.0)*DEGtoRAD)
        y2 = 1000.0*math.sin((angle+180.0)*DEGtoRAD)
        p2 = (centerPt[0] + int(round(x2)), centerPt[1] - int(round(y2)))
        return (p1, p2)

    def getArrowEndPoints(self, p, angle):
        # half the arrowhead
        x1 = 7.0*math.cos((angle+135.0)*DEGtoRAD)
        y1 = 7.0*math.sin((angle+135.0)*DEGtoRAD)
        xy1 = (p[0] + int(round(x1)), p[1] - int(round(y1)))
        # second half of the arrowhead
        x2 = 7.0*math.cos((angle+225.0)*DEGtoRAD)
        y2 = 7.0*math.sin((angle+225.0)*DEGtoRAD)
        xy2 = (p[0] + int(round(x2)), p[1] - int(round(y2)))
        return (xy1, xy2)

    def calcEndPoint(self, p, linelength, angle):
        """
        Calculate the coordinates relative to point p, based on an
        angle. It could be thought of as a point along a circle with
        the radius (linelength) and an angle.
        """
        x = linelength*math.cos(angle*DEGtoRAD)
        y = linelength*math.sin(angle*DEGtoRAD)
        return (p[0] + int(round(x)), p[1] - int(round(y)))

    def getArrowLength(self):
        w = abs((self.x1 - self.x2)/2)
        h = abs((self.y1 - self.y2)/2)
        len = max(14, min(w,h))
        len = len - 4  # so it doesn't overlap side of the main rectangle
        return len

##------------------ Class AoiThresholdTracking ------------------------------------

# Threshold Tracking Aoi Options
defaultTTTrackAngle = 0.0
defaultTTVelocity = (0, 0)
defaultTTUseVelocity = False
defaultTTConstrain = False
defaultTTSearchType = 0

class AoiThresholdTracking(CommonAngle):
    def __init__(self, x1, y1, x2, y2):
        CommonAngle.__init__(self, x1, y1, x2, y2)
        self.trackPoint = (-1, -1)
        self.angle = defaultTTTrackAngle
        self.velocity = defaultTTVelocity
        self.useV = defaultTTUseVelocity
        self.constrain = defaultTTConstrain
        self.searchType = defaultTTSearchType

    def isThresholdTrackingAoi(self):
        return True

    def getStatusBarText(self):
        'this is the name of Aoi that shows up on the status bar'
        return 'thresholdTrackingAoi'

    def useVelocity(self):
        return self.useV
    def setUseVelocity(self, flag):
        self.useV = flag
        global defaultTTUseVelocity
        defaultTTUseVelocity = flag

    def getVelocity(self):
        return self.velocity
    def setVelocity(self, v):
        self.velocity = v
        global defaultTTVelocity
        defaultTTVelocity = v

    def getAngle(self):
        return self.angle
    def setAngle(self, angle):
        'this is also called from OnMouseMove in CommonAngle class'
        self.angle = angle
        global defaultTTTrackAngle
        defaultTTTrackAngle = angle

    def getConstrain(self):
        return self.constrain
    def setConstrain(self, c):
        self.constrain = c
        global defaultTTConstrain
        defaultTTConstrain = c

    def getSearchType(self):
        return self.searchType
    def setSearchType(self, s):
        self.searchType = s
        global defaultTTSearchType
        defaultTTSearchType = s

    def aoiOptionsPresent(self):
        'yes, this aoi has options associated with it'
        return True

    def showAoiOptions(self):
        'bring up ThresholdTracking options dialog box'
        type = 'ThresholdTrackingOptions'
        params = {'angle': self.getAngle(),
                        'velocity': self.getVelocity(),
                        'useVelocity': self.useVelocity(),
                        'constrain': self.getConstrain(),
                        'searchType': self.getSearchType()}

        params = SpotlightGui.gui.showModalDialog(type, params)
        if params:
            self.setUseVelocity(params['useVelocity'])
            self.setVelocity(params['velocity'])
            self.setAngle(params['angle'])
            self.setConstrain(params['constrain'])
            self.setSearchType(params['searchType'])
            SpotlightGui.gui.iPanel.Refresh()
            self.updateStatusBar0()
            self.setImageConstrainLine()

    def Track(self):
        oldCenter = self.getAoiCenter() # old center

        # get track point
        pointFound = self.FindTrackPoint()
        if pointFound[0] == -1 and pointFound[1] == -1:
            message1 = 'Threshold Tracking failed - change the threshold level'
            SpotlightGui.gui.messageDialog(message1)
            Spotlight.OnStop()
        else:
            dx = pointFound[0] - oldCenter[0]
            dy = pointFound[1] - oldCenter[1]
            self.moveAoi(dx, dy)
            self.setTrackPoint(pointFound)  # update trackPoint
            SpotlightGui.gui.iPanel.Refresh()

            # draw a little red cursor
            SpotlightGui.gui.iPanel.drawRedCross(pointFound)

    def FindTrackPoint(self):
        angle = self.getAngle()  # get the angle from CommonAngle class
        self.aoiImage = Spotlight.getAoiImage(self.getAoiPosition())
        pointFound = SpotlightPoint.locateThresholdTrackPoint(self.aoiImage, angle)
        if pointFound[0] == -1 and pointFound[1] == -1: # point not found
            return pointFound  # (-1, -1)

        if self.getConstrain() == False:
            return (pointFound[0]+self.x1, pointFound[1]+self.y1)
        else:
            c = self.getAoiCenter() # old center
            if self.getSearchType() == 0:
                # Constrain the search to a line. Make the rectangle 1 pixel
                # less on all sides to eliminate edge problems
                x1 = self.x1 + 1
                y1 = self.y1 + 1
                x2 = self.x2 - 1
                y2 = self.y2 - 1
                pxy = self.getConstrainLine(x1, y1, x2, y2, c, angle)
                imgpxy = self.getImageConstrainLine()
                pointFound = SpotlightPoint.findThresholdPointAlongLine(pxy, imgpxy)
                return pointFound
            else:
                #-- Search the full Aoi and constrain only the movement of the
                #-- Aoi to a line
                p = (pointFound[0]+self.x1, pointFound[1]+self.y1)
                dx = -math.cos(angle * DEGtoRAD)    # constraint direction
                dy = math.sin(angle * DEGtoRAD)
                mag = math.sqrt((c[0]-p[0])*(c[0]-p[0]) + (c[1]-p[1])*(c[1]-p[1]))
                a2 = math.atan2(p[0]-c[0], p[1]-c[1])
                adiff = angle - a2/DEGtoRAD
                cosa = math.sin(adiff * DEGtoRAD)
                nx = float(c[0]) + (dx * mag * cosa)
                ny = float(c[1]) + (dy * mag * cosa)
                pointFound = SpotlightPoint.putBackOnLine(self.getImageConstrainLine(), (nx, ny))
                return pointFound

    def getTrackPoint(self):
        return self.trackPoint

    def setTrackPoint(self, p):
        self.trackPoint = p

    def getTrackDataLabel(self):
        """
        Converts to string and formats for writing out to file.
        The returned value is a tuple of 2 lists as shown below.
        (['   xval     '], ['   yval     '])
        """
        return self.getDataLabel(self.trackPoint)

    def getHeader(self):
        h = []
        h.append('x')
        h.append('y')
        return h

##------------------ class AoiWholeImage -------------------

class AoiWholeImage(AoiRectangle):
    def __init__(self, x1, y1, x2, y2):
        AoiRectangle.__init__(self, x1, y1, x2, y2)

    def isWholeImageAoi(self):
        return True

    def getStatusBarText(self):
        return 'WholeImageAoi'

##------------------ Class AoiLineProfile ------------------------------------

class AoiLineProfile(AoiLine):
    def __init__(self, x1, y1, x2, y2):
        AoiLine.__init__(self, x1, y1, x2, y2)
        self.dd = None

    def isCloseExecuted(self):
        'all modeless AOIs must have this'
        return self.closeExecuted

    def getStatusBarText(self):
        return 'lineProfileAoi'

    def initialize(self):
        self.dd = SpotlightGui.gui.createModelessDialog('LineProfile', {}, None, self)
        self.closeExecuted = False

    def deinitialize(self):
        SpotlightGui.gui.destroyModelessDialog(self.dd)

    def OnMouseMove(self, pos):
        if self.leftdown:
            AoiLine.OnMouseMove(self, pos)
            self.updateLineProfile()

    def closeDialog(self):
        self.closeExecuted = True

    def updateLineProfile(self):
        """post the request to update"""
        if self.dd:
            #~ self.dd.refreshProfile()  # seems to work just as well with this
            self.dd.postProfile()

    def getP(self, colorplane):
        line = self.getLineProfile()
        if colorplane != RGB:
            line = self.breakOutProfile(line, colorplane)
        return line

    def updateModeless(self, refreshAxes=False):
        """
        Called when loading a new image or when line profile needs updating.
        Also called when Program Options are changed.
        """
        if refreshAxes:
            self.dd.postProfile()

        # in case the line is on the edge of image and then thickens up
        r = self.limitLineMovement(self.x1, self.y1, self.x2, self.y2)
        self.x1 = r[0]
        self.y1 = r[1]
        self.x2 = r[2]
        self.y2 = r[3]
        self.updateLineProfile()


##------------------ Class AoiHistogram ------------------------------------


class AoiHistogram(AoiRectangle):
    def __init__(self, x1, y1, x2, y2):
        AoiRectangle.__init__(self, x1, y1, x2, y2)
        self.dd = None

    def isCloseExecuted(self):
        'all modeless AOIs must have this'
        return self.closeExecuted

    def getStatusBarText(self):
        return 'HistogramAoi'

    def initialize(self):
        self.histogram = []
        self.colorPlane = LUMINANCE
        # 0=call OnPaint, 1=update only hist, 2=hist+stat, 3=update only statistics
        self.updateType = 2
        self.closeExecuted = False
        params = {}
        params['colorPlane'] = self.colorPlane
        params['updateType'] = self.updateType
        self.histogram = self.getH()
        params['histogram'] = self.histogram
        params['statistics'] = self.getHistogramStatistics()

        self.dd = SpotlightGui.gui.createModelessDialog('Histogram', params, self.changeNotificationFunction)
        #self.changeNotificationFunction({}) # force initial dialog drawing, set any default values here
        self.updateHistogram()

    def deinitialize(self):
        SpotlightGui.gui.destroyModelessDialog(self.dd)

    def changeNotificationFunction(self, params):
        # on Mac  the dialog box's OnPaint fires and calls this function before
        # self.dd exists, hence the test below.
        if self.dd == None:
            return
        if params.has_key('closeExecuted'):
            self.closeExecuted = True
        if params.has_key('colorPlane'):     # might have been changed in dialog
            self.colorPlane = params['colorPlane']
        if params.has_key('updateType'):     # might have been changed in dialog
            self.updateType = params['updateType']

        paramsOut = {}
        paramsOut['updateType'] = self.updateType

        # one of the color selection buttons (R, G, B, or L) was clicked
        if self.updateType == 2:
            self.histogram = self.getH()
            paramsOut['histogram'] = self.histogram
            paramsOut['statistics'] = self.getHistogramStatistics()

        # mouse was moved
        if params.has_key('histogram'):
            self.histogram = self.getH()
            paramsOut['histogram'] = self.histogram

        # left mouse key up triggers updating of stats
        if params.has_key('updateStats'):
            paramsOut['statistics'] = self.getHistogramStatistics()

        if self.closeExecuted == False:
            SpotlightGui.gui.updateModelessDialog(self.dd, paramsOut) # tell the dialog to update with the new results


    def getHistogramStatistics(self):
        minh, maxh = PilProcess.getHistogramMinMax(self.aoiImage, self.colorPlane)
        meanh, stdev = PilProcess.getHistogramStatistics(self.aoiImage, self.colorPlane)
        return (minh, maxh, meanh, stdev)

    def OnMouseMove(self, pos):
        if self.leftdown:
            AoiRectangle.OnMouseMove(self, pos)
            self.updateHistogram()

    def OnMouseLeftUp(self, pos):
        self.leftdown = False
        self.updateStatistics()

    def updateStatistics(self):
        """update only statistics which are slow to calculate"""
        params = {}
        self.updateType = 3  # 3 = update statistics only
        params['updateType'] = self.updateType
        SpotlightGui.gui.updateModelessDialog(self.dd, params)
        #self.updateType = 1

    def updateHistogram(self):
        params = {}
        self.updateType = 1  # 1 = update histogram only
        params['updateType'] = self.updateType
        SpotlightGui.gui.updateModelessDialog(self.dd, params)


    def getH(self):
        p = []
        if self.colorPlane == RED:
            colorPix = self.getHistogram()
            for i in range(0,256):
                p.append(colorPix[i])
        elif self.colorPlane == GREEN:
            colorPix = self.getHistogram()
            for i in range(256,512):
                p.append(colorPix[i])
        elif self.colorPlane == BLUE:
            colorPix = self.getHistogram()
            for i in range(512,768):
                p.append(colorPix[i])
        elif self.colorPlane == LUMINANCE:
            p = self.getLuminanceHistogram()
        else:
            p = []
        return p

    def getHistogram(self):
        """
        This function returns a gray histogram if image is grayscale or
        3 separate histograms (R,G,B) if image is color. Luminance
        histogram is calculated by getLuminanceHistogram().
        """
        self.aoiImage = self.getAoiImage()
        return self.aoiImage.histogram()

    def getLuminanceHistogram(self):
        self.aoiImage = self.getAoiImage()
        grayImage = self.aoiImage.convert("L")
        return grayImage.histogram()

    def updateModeless(self, refreshAxes=False):
        'update histogram - called by updateModelessAois() in AoiList'
        if refreshAxes:
            pass  # not needed here
        # check if box is outside the new image - if it is then move it inside
        imX, imY = Spotlight.getWorkingImageSize()
        mustMove = False
        x1 = self.x1
        x2 = self.x2
        if self.x2 > imX:
            lenx = abs(self.x2 - self.x1)
            x1 = imX - (lenx + 1)
            x2 = imX - 1
            mustMove = True
        y1 = self.y1
        y2 = self.y2
        if self.y2 > imY:
            leny = abs(self.y2 - self.y1)
            y1 = imY - (leny + 1)
            y2 = imY - 1
            mustMove = True
        if mustMove:
            self.setAoiPosition(x1, y1, x2, y2)

        self.aoiImage = self.getAoiImage()  # update AOI

        self.updateType = 2
        paramsOut = {}
        paramsOut['updateType'] = self.updateType
        self.histogram = self.getH()
        paramsOut['histogram'] = self.histogram
        paramsOut['statistics'] = self.getHistogramStatistics()
        SpotlightGui.gui.updateModelessDialog(self.dd, paramsOut) # tell the dialog to update with the new results

##-------------------- AoiManualTracking class ----------------------------

class AoiManualTracking(AoiRectangle):
    def __init__(self, x1, y1, x2, y2):
        AoiRectangle.__init__(self, x1, y1, x2, y2)
        self.waiting = False
        self.trackPoint = (-1, -1)

    def isManualAoi(self):
        """
        Identifies this aoi as a type of Aoi that requires a mouse click before
        it can go on. This requirement can make it 'hang' is some situations.
        """
        return True

    def getStatusBarText(self):
        return 'manualAoi'

    def Stop(self):
        self.waiting = False

    def Track(self):
        self.leftdown = False # takes care of weirdness (sometimes its True)
        oldCenter = self.getAoiCenter() # old center
        self.setTrackPoint(oldCenter) # start trackPoint and oldCenter the same

        self.waiting = True
        if Spotlight.stopImmediately: # skip the while loop
            self.waiting = False
        while(self.waiting):
            SpotlightGui.gui.Yield()

        self.waiting = False
        newCenter = self.getTrackPoint() # trackPoint has already been set
        dx = newCenter[0] - oldCenter[0]
        dy = newCenter[1] - oldCenter[1]
        self.moveAoi(dx, dy)
        SpotlightGui.gui.iPanel.Refresh()

    def getTrackPoint(self):
        return self.trackPoint

    def setTrackPoint(self, p):
        self.trackPoint = p

    def OnMouseLeftDown(self, pos):
        self.waiting = self.continueWaiting(pos)
        if self.waiting == False:
            self.setTrackPoint(pos)
        AoiRectangle.OnMouseLeftDown(self, pos)

    def continueWaiting(self, pos):
        'returns False if mouse click occured within image boundaries'
        imX, imY = Spotlight.getWorkingImageSize()
        x, y = pos
        if x > 0 and y > 0 and x < imX and y < imY:
            return False
        else:
            return True

    def getTrackDataLabel(self):
        """converts to string and formats for writing out to file.
        The returned value is a tuple of 2 lists as shown below.
        (['   xval     '], ['   yval     '])"""
        return self.getDataLabel(self.trackPoint)

    def getHeader(self):
        h = []
        h.append('x')
        h.append('y')
        return h


##-------------------- AoiCenterTracking class ----------------------------

#- Center Aoi Options
defaultCenterVelocity = (0, 0)
defaultCenterUseVelocity = False
defaultCenterTrackingType = 0 # 0=center of mass - threshold, 1=c.o.m - grayscale, 2=four side edge
defaultCenterSaveResults = 0  # 0=save center point only, 1=center,w,h, 2=c,w,h,4points

class AoiCenterTracking(AoiRectangle):
    def __init__(self, x1, y1, x2, y2):
        AoiRectangle.__init__(self, x1, y1, x2, y2)
        self.trackPoint = (-1, -1)
        self.velocity = defaultCenterVelocity
        self.useV = defaultCenterUseVelocity
        self.trackingType = defaultCenterTrackingType
        self.saveResults = defaultCenterSaveResults
        self.blobSize = (0, 0)  # w, h
        self.p1 = (0, 0)  # x, y
        self.p2 = (0, 0)
        self.p3 = (0, 0)
        self.p4 = (0, 0)

    def isThresholdTrackingAoi(self):
        """Automatically adds threshold processing selection to the
        Process Sequence dialog box."""
        if self.getTrackingType() == 1:
            return False
        else:
            return True

    def drawAoi(self, highlight, dc=None):
        # draw the box
        AoiRectangle.drawAoi(self, highlight, dc)
        # add the cross
        params = {}
        pointList = []
        center = self.getAoiCenter()
        leg = 5
        vertline, horizline = self.getCross(center, leg)
        pointList.append(vertline)
        pointList.append(horizline)
        params['pointList'] = pointList
        params['highlight'] = highlight
        params['thickness'] = self.lineThickness
        SpotlightGui.gui.iPanel.drawAoi(params, dc)

    def getStatusBarText(self):
        'this is the name of Aoi that shows up on the status bar'
        return 'CenterTrackingAoi'

    def useVelocity(self):
        return self.useV
    def setUseVelocity(self, flag):
        self.useV = flag
        global defaultCenterUseVelocity
        defaultCenterUseVelocity = flag

    def getVelocity(self):
        return self.velocity
    def setVelocity(self, v):
        self.velocity = v
        global defaultCenterVelocity
        defaultCenterVelocity = v

    def getTrackingType(self):
        return self.trackingType
    def setTrackingType(self, c):
        self.updateThresholdOp(c)
        self.trackingType = c
        global defaultCenterTrackingType
        defaultCenterTrackingType = c

    def getSaveResults(self):
        return self.saveResults
    def setSaveResults(self, v):
        self.saveResults = v
        global defaultCenterSaveResults
        defaultCenterSaveResults = v

    def updateStatusBar0(self):
        aoiType = self.getStatusBarText()
        if Spotlight.scaleUserUnits == 1.0 and Spotlight.scalePixelUnits == 1.0:
            m1 = aoiType + ': (%3d, %3d) (%3d, %3d)' % (self.x1,self.y1,self.x2,self.y2)
            cx, cy = self.getAoiCenter()
            m2 = '  Center: (%3d, %3d)' % (cx, cy)
            message = m1 + m2
        else:
            x1 = self.x1 * Spotlight.pixelScale
            y1 = self.y1 * Spotlight.pixelScale
            x2 = self.x2 * Spotlight.pixelScale
            y2 = self.y2 * Spotlight.pixelScale
            m1 = aoiType + ': (%.3f, %.3f) (%.3f, %.3f)' % (x1, y1, x2, y2)
            cx, cy = self.getAoiCenter()
            sx = cx * Spotlight.pixelScale
            sy = cy * Spotlight.pixelScale
            m2 = '  Center: (%.3f, %.3f)' % (sx, sy)
            message = m1 + m2
        SpotlightGui.gui.updateStatusBar(message, 0)

    def aoiOptionsPresent(self):
        """yes, this aoi has options associated with it"""
        return True

    def showAoiOptions(self):
        """bring up CenterTrackingOptions options dialog box"""
        type = 'CenterTrackingOptions'
        params = {'trackingType': self.getTrackingType(),
                        'velocity': self.getVelocity(),
                        'useVelocity': self.useVelocity(),
                        'saveResults': self.getSaveResults()}

        params = SpotlightGui.gui.showModalDialog(type, params)
        if params:
            self.setUseVelocity(params['useVelocity'])
            self.setVelocity(params['velocity'])
            self.setTrackingType(params['trackingType'])
            self.setSaveResults(params['saveResults'])
            SpotlightGui.gui.iPanel.Refresh()
            self.updateStatusBar0()

    def updateThresholdOp(self, newTrackingType):
        """
        Checks whether the automatically inserted threshold operation
        should be deleted or inserted in the IPSequence dialog box.
        This is needed because this AOI (CenterTrackingAoi) has two types
        of tracking - one that requires thresholding and one that
        shouldn't have it(center of mass - grayscale).

        Four possibilities exist:
        1. newTrackingType is threshold and thresh op is present in the
           IpSequence dialog as last op - action: do nothing
        2. newTrackingType is threshold and thresh op is NOT present
           action: add thresh op
        3. newTrackingType is grayscale and thresh op is present as
           last op - action: delete thresh op
        4. newTrackingType is grayscale and thresh op is NOT present as
           last op - action: do nothin
        """

        # threhold-based TrackingType requested and one or more ops in IpSequence dialog
        if newTrackingType != 1 and self.getSeqListLength() > 0:
            op = self.getSeqItem(self.getSeqListLength()-1) # check if last op is threshold
            if op.params['name'] == 'Threshold':
                pass
            else:
                self.addThresholdOperation(self.getSeqListLength())

        # threhold-based TrackingType requested, but no ops in IpSequence dialog
        elif newTrackingType != 1 and self.getSeqListLength() == 0: # add thresh
            self.addThresholdOperation()

        # grayscale-based TrackingType requested and one or more ops in IpSequence dialog
        elif newTrackingType == 1 and self.getSeqListLength() > 0:
            op = self.getSeqItem(self.getSeqListLength()-1) # check if last op is threshold
            if op.params['name'] == 'Threshold':
                self.ipSeqDelete(self.getSeqListLength()-1)

        # the last possibility
        # grayscale-based TrackingType requested and the last op is not threshold
        else:
            pass

    def Track(self):
        oldCenter = self.getAoiCenter() # old center
        # get track point
        xfound, yfound = self.FindTrackPoint()
        if xfound == -1 and yfound == -1:
            Spotlight.OnStop()
        else:
            x = xfound + self.x1
            y = yfound + self.y1
            newCenter = (int(x), int(y))
            # draw aoi in new position
            dx = newCenter[0] - int(oldCenter[0])
            dy = newCenter[1] - int(oldCenter[1])
            self.moveAoi(dx, dy)
            self.setTrackPoint((x, y))  # update trackPoint

            # draw a little red cursor if type=1 (four side edge tracking)
            if self.getTrackingType() == 2:
                SpotlightGui.gui.iPanel.drawRedCross(self.p1)
                SpotlightGui.gui.iPanel.drawRedCross(self.p2)
                SpotlightGui.gui.iPanel.drawRedCross(self.p3)
                SpotlightGui.gui.iPanel.drawRedCross(self.p4)

    def FindTrackPoint(self):
        self.aoiImage = Spotlight.getAoiImage(self.getAoiPosition())

        if self.getTrackingType() == 0 or self.getTrackingType() == 1:
            p = SpotlightPoint.imageCenterOfMass(self.aoiImage)
            if p[0] == -1:
                m1 = 'All pixels are 0 - no Center of Mass'
                SpotlightGui.gui.messageDialog(m1)
            return p
        else:
            self.aoiImage = Spotlight.getAoiImage(self.getAoiPosition())
            p1 = SpotlightPoint.locateThresholdTrackPoint(self.aoiImage, 0.0)
            p2 = SpotlightPoint.locateThresholdTrackPoint(self.aoiImage, 90.0)
            p3 = SpotlightPoint.locateThresholdTrackPoint(self.aoiImage, 180.0)
            p4 = SpotlightPoint.locateThresholdTrackPoint(self.aoiImage, 270.0)

            # check that all pixels were not 0 - thresholds were met - one side is all you need
            if p1[0] == -1:
                m1 = 'Threshold Tracking failed\n'
                m2 = 'All pixels are 0 - change the threshold level'
                SpotlightGui.gui.messageDialog(m1+m2)
                return (-1, -1)  # point not found

            # width, height
            w = p1[0] - p3[0]
            h = p4[1] - p2[1]
            self.blobSize = (w, h)
            # center
            xcenter = (float(p1[0]) + float(p3[0]))/2.0
            ycenter = (float(p4[1]) + float(p2[1]))/2.0

            # convert to image coordinates (from Aoi coordinates)
            x = int(p1[0] + self.x1)
            y = int(p1[1] + self.y1)
            self.p1 = (x, y)
            x = int(p2[0] + self.x1)
            y = int(p2[1] + self.y1)
            self.p2 = (x, y)
            x = int(p3[0] + self.x1)
            y = int(p3[1] + self.y1)
            self.p3 = (x, y)
            x = int(p4[0] + self.x1)
            y = int(p4[1] + self.y1)
            self.p4 = (x, y)
            return (int(xcenter), int(ycenter))

    def getTrackPoint(self):
        return self.trackPoint

    def setTrackPoint(self, p):
        self.trackPoint = p

    def getTrackDataLabel(self):
        'return string-formatted data for writing to results file'
        columnWidth = 13
        #columnWidth = 15
        if self.getTrackingType() == 0 or self.getTrackingType() == 1:
            x, y = self.getDataLabel(self.trackPoint, columnWidth)
            return (x, y)  # this format:  (['   xval     '], ['   xval     '])
        else:
            x, y = self.getDataLabel(self.trackPoint, columnWidth)
            if self.getSaveResults() == 0:
                return (x, y)  # this format:  (['   xval     '], ['   xval     '])
            elif self.getSaveResults() == 1:
                w, h = self.getDataLabel(self.blobSize, columnWidth)
                return (x, y, w, h)
            else:
                w, h = self.getDataLabel(self.blobSize, columnWidth)
                x1, y1 = self.getDataLabel(self.p1, columnWidth)
                x2, y2 = self.getDataLabel(self.p2, columnWidth)
                x3, y3 = self.getDataLabel(self.p3, columnWidth)
                x4, y4 = self.getDataLabel(self.p4, columnWidth)
            return (x, y, w, h, x1, y1, x2, y2, x3, y3, x4, y4)

    def getHeader(self):
        h = []
        h.append('cx')
        h.append('cy')
        #h.append(' cx ')
        #h.append(' cy ')

        if self.getTrackingType() == 0 or self.getTrackingType() == 1:
            return h
        else:
            if self.getSaveResults() == 0:
                return h
            elif self.getSaveResults() == 1:
                h.append(' w')
                h.append(' h')
                return h
            else:
                h.append(' w')
                h.append(' h')
                h.append('x1')
                h.append('y1')
                h.append('x2')
                h.append('y2')
                h.append('x3')
                h.append('y3')
                h.append('x4')
                h.append('y4')
                return h

##-------------------- AoiLocalMaxTracking class ----------------------------

#- Max Aoi Options
defaultMaxAngle = 0.0
defaultMaxVelocity = (0, 0)
defaultMaxUseVelocity = False
defaultMaxConstrain = False

class AoiMaximumTracking(CommonAngle):
    def __init__(self, x1, y1, x2, y2):
        CommonAngle.__init__(self, x1, y1, x2, y2)
        self.trackPoint = (-1, -1)
        self.angle = defaultMaxAngle
        self.velocity = defaultMaxVelocity
        self.useV = defaultMaxUseVelocity
        self.constrain = defaultMaxConstrain

    def drawAoi(self, highlight, dc=None):
        if self.getConstrain():
            CommonAngle.drawAoi(self, highlight, dc)
        else:
            AoiRectangle.drawAoi(self, highlight, dc)
        # add the cross
        params = {}
        pointList = []
        center = self.getAoiCenter()
        vertline, horizline = self.getCross(center, 5)
        pointList.append(vertline)
        pointList.append(horizline)
        params['pointList'] = pointList
        params['highlight'] = highlight
        params['thickness'] = self.lineThickness
        SpotlightGui.gui.iPanel.drawAoi(params, dc)

    def getStatusBarText(self):
        'this is the name of Aoi that shows up on the status bar'
        return 'MaximumTrackingAoi'

    def updateStatusBar0(self):
        if self.getConstrain():
            CommonAngle.updateStatusBar0(self)
        else:
            aoiType = self.getStatusBarText()
            if Spotlight.scaleUserUnits == 1.0 and Spotlight.scalePixelUnits == 1.0:
                m1 = aoiType + ': (%3d, %3d) (%3d, %3d)' % (self.x1,self.y1,self.x2,self.y2)
                cx, cy = self.getAoiCenter()
                m2 = '  Center: (%3d, %3d)' % (cx, cy)
                message = m1 + m2
            else:
                x1 = self.x1 * Spotlight.pixelScale
                y1 = self.y1 * Spotlight.pixelScale
                x2 = self.x2 * Spotlight.pixelScale
                y2 = self.y2 * Spotlight.pixelScale
                m1 = aoiType + ': (%.3f, %.3f) (%.3f, %.3f)' % (x1, y1, x2, y2)
                cx, cy = self.getAoiCenter()
                sx = cx * Spotlight.pixelScale
                sy = cy * Spotlight.pixelScale
                m2 = '  Center: (%.3f, %.3f)' % (sx, sy)
                message = m1 + m2
            SpotlightGui.gui.updateStatusBar(message, 0)

    def getAngle(self):
        return self.angle
    def setAngle(self, angle):
        'this is also called from OnMouseMove in CommonAngle class'
        self.angle = angle
        global defaultMaxAngle
        defaultMaxAngle = angle

    def getVelocity(self):
        return self.velocity
    def setVelocity(self, v):
        self.velocity = v
        global defaultMaxVelocity
        defaultMaxVelocity = v

    def useVelocity(self):
        return self.useV
    def setUseVelocity(self, flag):
        self.useV = flag
        global defaultMaxUseVelocity
        defaultMaxUseVelocity = flag

    def getConstrain(self):
        return self.constrain
    def setConstrain(self, c):
        self.constrain = c
        global defaultMaxConstrain
        defaultMaxConstrain = c

    def aoiOptionsPresent(self):
        'yes, this aoi has options associated with it'
        return True

    def showAoiOptions(self):
        'bring up MaximumTrackingOptions dialog box'
        type = 'MaximumTrackingOptions'
        params = {'angle': self.getAngle(),
                        'velocity': self.getVelocity(),
                        'useVelocity': self.useVelocity(),
                        'constrain': self.getConstrain()}
        params = SpotlightGui.gui.showModalDialog(type, params)
        if params:
            self.setUseVelocity(params['useVelocity'])
            self.setVelocity(params['velocity'])
            self.setAngle(params['angle'])
            self.setConstrain(params['constrain'])
            SpotlightGui.gui.iPanel.Refresh()
            self.updateStatusBar0()

    def Track(self):
        oldCenter = self.getAoiCenter() # old center
        # get track point
        pointFound = self.FindTrackPoint()
        if pointFound[0] == -1 and pointFound[1] == -1:
            message1 = 'Local Maximum point not found'
            SpotlightGui.gui.messageDialog(message1)
            Spotlight.OnStop()
        else:
            dx = pointFound[0] - int(oldCenter[0])
            dy = pointFound[1] - int(oldCenter[1])
            self.moveAoi(dx, dy)
            self.setTrackPoint(pointFound)  # update trackPoint
            SpotlightGui.gui.iPanel.Refresh()
            SpotlightGui.gui.iPanel.drawRedCross(pointFound)

    def FindTrackPoint(self):
        angle = self.getAngle()
        self.aoiImage = Spotlight.getAoiImage(self.getAoiPosition())
        if self.getConstrain() == False:
            mx, my = SpotlightPoint.getMaxIntensityLocation(self.aoiImage)
            x = int(mx)
            y = int(my)
            return (x + self.x1, y + self.y1)
        else:
            # make the rectangle 1 pixel less on all sides to eliminate edge problems
            x1 = self.x1 + 1
            y1 = self.y1 + 1
            x2 = self.x2 - 1
            y2 = self.y2 - 1
            c = self.getAoiCenter()
            pxy = self.getConstrainLine(x1, y1, x2, y2, c, angle)
            imgpxy = self.getImageConstrainLine()
            mx, my = SpotlightPoint.findMaxPointAlongLine(pxy, imgpxy)
            return (mx, my)

    def getTrackPoint(self):
        return self.trackPoint

    def setTrackPoint(self, p):
        self.trackPoint = p

    def getTrackDataLabel(self):
        """converts to string and formats for writing out to file.
        The returned value is a tuple of 2 lists as shown below.
        (['   xval     '], ['   yval     '])"""
        return self.getDataLabel(self.trackPoint)

    def getHeader(self):
        h = []
        h.append('x')
        h.append('y')
        return h

##-------------------- AoiSnake class ----------------------------

defaultIntensityWeight = 1
defaultGradientWeight = 0
defaultDerivativeWeight = 1
defaultEvenSpacingWeight = 0
defaultTotalLengthWeight = 0
defaultResultFormat = 0
defaultSnakePointsFormat = 0
defaultFixedNumber = 50
defaultPercent = 20
defaultPixelsToSearch = 3
defaultIdealIntensity = 90
#defaultIdealIntensity = 0.5
defaultProcessingRadius = 20
defaultSnakeVelocity = (0, 0)
defaultSnakeUseVelocity = True

class AoiSnake(Aoi):
    def __init__(self, x1, y1, x2, y2):
        Aoi.__init__(self, x1, y1, x2, y2)
        params = {'intensityWeight': defaultIntensityWeight,
                    'gradientWeight': defaultGradientWeight,
                    'derivativeWeight': defaultDerivativeWeight,
                    'evenSpacingWeight': defaultEvenSpacingWeight,
                    'totalLengthWeight': defaultTotalLengthWeight,
                    'resultFormat': defaultResultFormat,
                    'snakePointsFormat': defaultSnakePointsFormat,
                    'fixedNumber': defaultFixedNumber,
                    'percent': defaultPercent,
                    'velocity': defaultSnakeVelocity,
                    'useVelocity': defaultSnakeUseVelocity,
                    'pixelsToSearch': defaultPixelsToSearch,
                    'idealIntensity': defaultIdealIntensity,
                    'processingRadius': defaultProcessingRadius}
        self.setParams(params)
        self.clearSnake()

    def clearSnake(self):
        self.oldPoints = None
        self.controlPointsCache = None
        self.pointList = []  # all points in the snake line
        self.displayPointList = [] # points in the snake line used for drawing
        self.setControlPoints([])
        self.lastP = -5
        self.connected = False
        self.slithering = False
        self.controlPoints = []
        self.pinnedPoints = []   # pinned control points
        self.trackPoint = (-1, -1)
        self.pixelCache = None

    def setParams(self, params):
        global defaultIntensityWeight
        global defaultGradientWeight
        global defaultDerivativeWeight
        global defaultEvenSpacingWeight
        global defaultTotalLengthWeight
        global defaultResultFormat
        global defaultSnakePointsFormat
        global defaultFixedNumber
        global defaultPercent
        global defaultSnakeVelocity
        global defaultSnakeUseVelocity
        global defaultPixelsToSearch
        global defaultIdealIntensity
        global defaultProcessingRadius
        defaultIntensityWeight = params['intensityWeight']
        defaultGradientWeight = params['gradientWeight']
        defaultDerivativeWeight = params['derivativeWeight']
        defaultEvenSpacingWeight = params['evenSpacingWeight']
        defaultTotalLengthWeight = params['totalLengthWeight']
        defaultResultFormat = params['resultFormat']
        defaultSnakePointsFormat = params['snakePointsFormat']
        defaultFixedNumber = params['fixedNumber']
        defaultPercent = params['percent']
        defaultSnakeVelocity = params['velocity']
        defaultSnakeUseVelocity = params['useVelocity']
        defaultPixelsToSearch = params['pixelsToSearch']
        defaultIdealIntensity = params['idealIntensity']
        defaultProcessingRadius = params['processingRadius']
        #~ self.params = {}
        #~ self.params['intensityWeight'] = params['intensityWeight']
        #~ self.params['gradientWeight'] = params['gradientWeight']
        #~ self.params['derivativeWeight'] = params['derivativeWeight']
        #~ self.params['evenSpacingWeight'] = params['evenSpacingWeight']
        #~ self.params['totalLengthWeight'] = params['totalLengthWeight']
        #~ self.params['resultFormat'] = params['resultFormat']
        #~ self.params['snakePointsFormat'] = params['snakePointsFormat']
        #~ self.params['fixedNumber'] = params['fixedNumber']
        #~ self.params['percent'] = params['percent']
        #~ self.params['velocity'] = params['velocity']
        #~ self.params['useVelocity'] = params['useVelocity']
        #~ self.params['pixelsToSearch'] = params['pixelsToSearch']
        #~ self.params['idealIntensity'] = params['idealIntensity']
        #~ self.params['processingRadius'] = params['processingRadius']
        self.params = params

    def updateStatusBar0(self, moving=False):
        if moving:
            message = self.getBoundingBoxMessage()
        else:
            if self.connected:
                message = 'DRAG-LEFT to move or resize, RIGHT-CLICK to start new snake'
            else:
                message = 'RIGHT-CLICK to add points, RIGHT-DOUBLE-CLICK to close snake'
        SpotlightGui.gui.updateStatusBar(message, 0)

    def getBoundingBoxMessage(self):
        if Spotlight.scaleUserUnits == 1.0 and Spotlight.scalePixelUnits == 1.0:
            message = 'SnakeAoi bounding box: (%3d, %3d) (%3d, %3d) energy:%s' \
                    % (self.x1,self.y1,self.x2,self.y2,self.snakeEnergy())
        else:
            x1 = self.x1 * Spotlight.pixelScale
            y1 = self.y1 * Spotlight.pixelScale
            x2 = self.x2 * Spotlight.pixelScale
            y2 = self.y2 * Spotlight.pixelScale
            message = 'SnakeAoi bounding box: (%.3f, %.3f) (%.3f, %.3f) energy:%s' \
                    % (x1, y1, x2, y2,self.snakeEnergy())
        return message

    def setControlPoints(self, controlPoints):
        'this should be the only function allowed to change the control points'
        if controlPoints == self.controlPointsCache:
            return
        self.controlPointsCache = copy.deepcopy(controlPoints)
        self.controlPoints = copy.deepcopy(controlPoints)
        self.calculatePointList()

    def getControlPoints(self):
        'called from cmdUpdate class to be able to undo'
        return self.controlPoints

    def addControlPoint(self, pos):
        self.controlPoints.append(pos)
        self.calculatePointList()

    def addPinnedPoint(self):
        self.pinnedPoints.append(False)

    def setPinnedPoints(self, pinnedPoints):
        self.pinnedPoints = copy.deepcopy(pinnedPoints)

    def togglePinned(self, i):
        self.pinnedPoints[i] = not self.pinnedPoints[i]

    def aoiOptionsPresent(self):
        'yes, this aoi has options associated with it'
        return True

    def showAoiOptions(self):
        'brings up Snake options dialog box'
        type = 'SnakeOptions'
        params = SpotlightGui.gui.showModalDialog(type, self.params, self)
        if params:
            self.setParams(params)
            # refresh snake with new params
            self.calculatePointList()
            SpotlightGui.gui.iPanel.Refresh()
        self.updateStatusBar0()

    def isSlithering(self):
        return self.slithering

    def useVelocity(self):
        return self.params['useVelocity']

    def getVelocity(self):
        return self.params['velocity']

    def setVelocity(self, v):
        'called from Spotlight.trackOne() to update the velocity'
        self.params['velocity'] = v
        global defaultSnakeVelocity
        defaultSnakeVelocity = v

    def getTrackPoint(self):
        return self.trackPoint

    def getAverageRadius(self):
        r = 0
        centerX=self.centerX
        centerY=self.centerY
        for (x,y) in self.pointList:
            r += math.sqrt((x-centerX)*(x-centerX)+(y-centerY)*(y-centerY))
        return r/len(self.pointList)

    def setAoiCoordinates(self, controlPoints, pinnedPoints, c, params):
        """
        Called from cmdNewAoiSnake class when making a copy of previous Aoi.
        """
        self.params = params
        self.connected = c
        self.setPinnedPoints(pinnedPoints)
        offsetX = offsetY = 10
        self.moveAoi(offsetX, offsetY, controlPoints, True)
        self.setBoundingBox()  # set new bounding rectange

    def showAoiPositionDialog(self):
        """brings up a SnakeAoiPosition dialog box"""
        type = 'SnakeAoiPosition'
        params = {}
        params['x1'] = self.x1
        params['y1'] = self.y1
        params['x2'] = self.x2
        params['y2'] = self.y2
        params = SpotlightGui.gui.showModalDialog(type, params)
        return params

    def setAoiPosition(self, x1, y1, x2, y2, fromUpdate=False):
        """
        Set aoi to the position specified - called from either
        menu Aoi-->SetPosition or from cmdUpdate class undo().
        """
        if fromUpdate:
            self.Reset()
        else:
            offsetX = x1 - self.x1
            offsetY = y1 - self.y1
            self.moveAoi(offsetX, offsetY, [], True)
            self.setBoundingBox()
            SpotlightGui.gui.iPanel.Refresh()
            self.updateStatusBar0()

    def drawAoi(self, highlight, dc=None):
        params = {}
        pointList = []
        points = self.displayPointList
        pointList.append(points)

        # draw cross at control point
        for i in range(len(self.controlPoints)):
            line1 = []
            line2 = []
            if self.pinnedPoints[i] == True:
                line1, line2 = self.getFixedCross(self.controlPoints[i], 5)
            else:
                line1, line2 = self.getCross(self.controlPoints[i], 5) # located in Aoi class
            pointList.append(line1)
            pointList.append(line2)

        params['pointList'] = pointList
        params['highlight'] = highlight
        params['thickness'] = self.lineThickness
        SpotlightGui.gui.iPanel.drawAoi(params, dc)

    def getFixedCross(self, center, leg):
        'returns two lines which make the cross'
        x, y = center
        line1 = []
        line1.append((x-leg, y-leg))
        line1.append((x+leg, y+leg))
        line2 = []
        line2.append((x-leg, y+leg))
        line2.append((x+leg, y-leg))
        return (line1, line2)

    def updateModeless(self, refreshAxes=False):
        """
        Strictly speaking this is not a modeless Aoi but this is a convenient
        way to clear cached values when new image is loaded -- Just using the
        mechanism already in place.
        """
        self.pixelCache = None

    def updatePixelCache(self):
        """
        The pixelCache is a 1-d array to speed up reading pixels from the image.
        """
        if not self.pixelCache:
            img = Spotlight.workingImage.copy()
            img = img.convert('L')  # convert to grayscale
            self.sx = img.size[0]
            self.sy = img.size[1]
            self.pixelCache = img.getdata()

    def moveAoi(self, offsetX, offsetY, controlPoints=[], moveAll=False):
        """moves control points by the offsets specified"""
        newPoints = self.moveCoordinates(offsetX, offsetY, controlPoints, moveAll)
        self.setControlPoints(newPoints)

    def moveCoordinates(self, offsetX, offsetY, controlPoints, moveAll):
        """returns a new list of control points"""
        if controlPoints:
            cPoints = controlPoints
        else:
            cPoints = self.controlPoints

        newPoints = []
        for i in range(len(cPoints)):
            x, y = cPoints[i]
            if moveAll:  # move all points no matter what
                x = x + offsetX
                y = y + offsetY
            else:        # move points only if not pinned
                if self.pinnedPoints[i] == False:
                    x = x + offsetX
                    y = y + offsetY
            newPoints.append((x, y))
        return newPoints

    def movePoint(self, pos):
        newPoints = copy.deepcopy(self.controlPoints)
        newPoints[self.closest] = pos
        return newPoints

    def OnMouseMove(self, pos):
        if self.slithering:
            return
        if self.leftdown:
            px = pos[0]
            py = pos[1]
            offsetWidth = px - self.lastPoint[0]
            offsetHeight = py - self.lastPoint[1]
            oldDisplayPointList, oldControlPoints = self.obtainMouseBuffer()

            if self.closest == -1:   # move Aoi
                self.moveAoi(offsetWidth, offsetHeight, [], True)
            else:               # move control point
                newPoints = self.movePoint((px, py))
                self.setControlPoints(newPoints)

            newDisplayPointList, newControlPoints = self.obtainMouseBuffer()
            self.storeMouseBuffer(oldDisplayPointList, oldControlPoints)
            self.storeMouseBuffer(newDisplayPointList, newControlPoints)
            self.setBoundingBox()
            self.updateStatusBar0(True)
            self.lastPoint = (px, py)
            SpotlightGui.gui.iPanel.Refresh()

    def obtainMouseBuffer(self):
        """
        Do not use otherwise - used only for reducing amount of code in
        OnMouseMove()
        """
        return (self.displayPointList, self.controlPoints)

    def storeMouseBuffer(self, displayPointList, controlPoints):
        """Do not use otherwise - used only for reducing amount of code in
        OnMouseMove()"""
        self.displayPointList = displayPointList
        self.controlPoints = controlPoints

    def OnMouseLeftDown(self, pos):
        if self.slithering:
            return
        self.closest = self.Closest(pos)
        if Spotlight.ctrlKeyDown:
            self.togglePinned(self.closest)
            SpotlightGui.gui.iPanel.Refresh()
        self.leftdown = True
        self.lastPoint = pos

    def OnMouseLeftUp(self, pos):
        if self.slithering:
            return
        self.leftdown = False
        self.updateStatusBar0()

    def OnMouseRightDown(self, pos):
        if self.slithering:
            return
        if self.connected:
            self.clearSnake()
        self.addControlPoint(pos)
        self.addPinnedPoint()
        self.setBoundingBox()
        self.updateStatusBar0()
        SpotlightGui.gui.iPanel.Refresh()

    def OnMouseRightDClick(self, pos):
        if self.slithering:
            return
        if len(self.controlPoints) < 3:
            return
        self.connected = True
        p = sys.platform
        if p[0:5] == 'linux':
            n = len(self.controlPoints)
            self.setControlPoints(self.controlPoints[0:n-1])
            self.setPinnedPoints(self.pinnedPoints[0:n-1])
        else:
            self.calculatePointList()
        self.setBoundingBox()
        self.updateStatusBar0()
        SpotlightGui.gui.iPanel.Refresh()

    def Closest(self, c):
        clos = -1
        d = 0.0
        dmin = 10e10
        for i in range(len(self.controlPoints)):
            x, y = self.controlPoints[i]
            d = self.dist(x, y, c[0], c[1])
            if (d<dmin and d<10):  # "near" is within 10 pixels
                dmin = d
                clos = i
        return clos

    def setBoundingBox(self):
        try:
            test = self.minX
        except AttributeError:
            return
        self.updatePixelCache()
        radius = self.params['processingRadius']
        self.x1 = int(max(0, self.minX - radius))
        self.y1 = int(max(0, self.minY - radius))
        self.x2 = int(min(self.sx, self.maxX + radius))
        self.y2 = int(min(self.sy, self.maxY + radius))
        return

    def snakeSplineLengths(self):
        """ return a list of the approximate lengths of the snakes splines"""
        lengths = []
        l = len(self.controlPoints) -1
        if l > 1:
            if self.connected:
                l = l + 1
            for i in range(l): # for each spline
                dist = 0
                reps = (5+math.sqrt(self.snakeCPDist(i, i+1))) /2
                r = 0
                while r < 1:
                    x,y = (self.splinePoints(i, r))
                    if r > 0: # approximate by a number of short straight lines
                        dist = dist + math.sqrt((x-lastX)*(x-lastX) + (y-lastY)*(y-lastY))
                    lastX,lastY = x,y
                    r = r + 1.0/reps
                lengths.append(dist)
        return lengths

    def calculateSPPointList(self):
        """calculate evenly spaced points along the snake from the control points
        in parametric coordinates (spline, percentage)"""
        self.spPointList = []
        lengths = self.snakeSplineLengths()
        if not lengths:
            return self.spPointList
        totalLength = reduce(operator.add, lengths)

        if self.params['snakePointsFormat'] == 0:
            numPoints = self.params['fixedNumber']
        else: # otherwise base it on the length of the snake
            numPoints = int(totalLength * self.params['percent'] / 100)

        eachLength = totalLength/(numPoints-1)
        allowableRoundoffError = 0.00001
        spline = 0
        splineStart = 0
        length = 0
        totalLengthPlusRoundoff = totalLength + allowableRoundoffError
        while length<totalLengthPlusRoundoff:
            # Prevent division by 0. This might happen if snake shrinks up to
            # a point.
            if lengths[spline] == 0.0:
                break
            r = (length-splineStart)/lengths[spline]
            self.spPointList.append((spline,r))
            length += eachLength
            if length > (splineStart + lengths[spline]+ allowableRoundoffError):
                splineStart += lengths[spline]
                spline += 1
        return self.spPointList

    def calculatePointList(self):
        """calculate evenly spaced points along the snake from the control points
        for efficiency, calculate min, max, and center at the same time"""
        self.lastP = -5
        pointList = []

        self.spPointList = self.calculateSPPointList()
        numPoints = len(self.spPointList)
        if numPoints == 0:
            return

        maxX = maxY = totalX = totalY = 0
        minX = minY = 100000 # arbitrary big number

        for s,r in self.spPointList:
            x,y = self.splinePoints(s, r)
            totalX += x
            totalY += y
            maxX = max(maxX, x)
            maxY = max(maxY, y)
            minX = min(minX, x)
            minY = min(minY, y)
            pointList.append((x,y))
        self.maxX = maxX
        self.maxY = maxY
        self.minX = minX
        self.minY = minY
        self.centerX = totalX / numPoints
        self.centerY = totalY / numPoints
        self.pointList = pointList

        # build smaller displayPointList for faster display
        numPointsToDisplay = min(len(self.controlPoints) * 10, numPoints)
        keepEveryNthPoint = int(len(pointList) / numPointsToDisplay)
        self.displayPointList = []
        for i in range(len(pointList)):
            if i%keepEveryNthPoint == 0:
                self.displayPointList.append((int(pointList[i][0]), int(pointList[i][1])))
        if len(pointList)%keepEveryNthPoint != 1: # always include last point
            self.displayPointList.append((int(pointList[-1][0]), int(pointList[-1][1])))

    def Reset(self):
        'called from Snake Parameters dialog to undo previous slither'
        if self.slithering:
            return
        if self.oldPoints:
            self.setControlPoints(copy.deepcopy(self.oldPoints))
            self.setBoundingBox()
            self.updateStatusBar0(True)
            SpotlightGui.gui.iPanel.Refresh()

    def Slither(self, calledFromDialog=False, params={}):
        if self.slithering:
            return
        if params:
            self.setParams(params)
        if self.params['pixelsToSearch'] == 0:
            return
        if self.oldPoints != self.controlPoints:
            self.oldPoints = copy.deepcopy(self.controlPoints) # save for reset

        if not Spotlight.tracking:
            SpotlightGui.gui.showStopButton()
        self.slithering = True
        if Spotlight.stopImmediately:
            self.slithering = False
        self.SlitherSearch(self.params['pixelsToSearch'])
        self.slithering = False
        if not Spotlight.tracking:
            SpotlightGui.gui.removeStopButton()
            Spotlight.setStopImmediately(False)
        self.setBoundingBox()
        self.updateStatusBar0(True)

    def Stop(self):
        self.slithering = False

    def Track(self):
        self.Slither()
        self.trackPoint = self.getAoiCenter()

    def getAoiCenter(self):
        """used by Spotlight.trackOne() -- overrides the Aoi class getAoiCenter()
        which returns the center of rectangular box (ip box)"""
        return (self.centerX, self.centerY)

    def getImagePixelIntensity(self, xx, yy):
        self.updatePixelCache()
        x = int(xx)
        y = int(yy)
        if x<0 or x>self.sx:
            return 0
        if y<0 or y>self.sy:
            return 0
        try:
            return self.pixelCache[y * self.sx + x]
        except IndexError:
            return 0

    def SlitherSearch(self, distance, startEnergy=None):
        if distance == 0:
            return
        originalPoints = copy.deepcopy(self.controlPoints)
        newPoints = copy.deepcopy(self.controlPoints)
        if not startEnergy:
            startEnergy = self.snakeEnergy()
        newEnergy = startEnergy
        for i in range(len(self.controlPoints)):
            if 1 == self.pinnedPoints[i]:
                continue
            ox,oy = newPoints[i]
            SpotlightGui.gui.updateStatusBar('Slithering...pt:%s d:%s energy:%s' % (i,distance,newEnergy) , 0)
            SpotlightGui.gui.Yield()
            for ax,ay in ((0, -1),(0, 1),(-1, 0),(1, 0),(1, -1),(-1, 1),(-1,-1),(1, 1)):
                tx = ox + ax * distance
                ty = oy + ay * distance
                newControlPoints = copy.deepcopy(self.controlPoints)
                newControlPoints[i] = (tx, ty)
                self.setControlPoints(newControlPoints)
                tEnergy = self.snakeEnergy()
                if tEnergy<newEnergy:
                    newEnergy = tEnergy
                    newPoints[i] = (tx,ty)
            newControlPoints = copy.deepcopy(self.controlPoints)
            newControlPoints[i] = newPoints[i]
            self.setControlPoints(newControlPoints)
            if not self.slithering:
                break

        if not self.slithering:
            self.setControlPoints(originalPoints)
            # get rid of half-drawn snake artifacts by repainting the image
            SpotlightGui.gui.iPanel.Refresh()
            return
        self.setControlPoints(originalPoints)
        if newEnergy<startEnergy:
            self.setControlPoints(newPoints)
            SpotlightGui.gui.iPanel.Refresh()
            distance = self.params['pixelsToSearch']
            self.SlitherSearch(distance, newEnergy)
        else:
            self.SlitherSearch(distance-1, newEnergy)

    def snakeEnergy(self): # calculate the energy of the snake
        if len(self.controlPoints) < 3:
            return 0
        ie = ge = de = ee = te = count = pdistav = pdistsd = 0
        pdisti = []
        doDe = self.params['derivativeWeight'] > 0
        doGe = self.params['gradientWeight'] > 0
        doIe = self.params['intensityWeight'] > 0
        doEe = self.params['evenSpacingWeight'] > 0
        doTe = self.params['totalLengthWeight'] > 0
        inten = self.params['idealIntensity']

        l = len(self.controlPoints) -1
        if self.connected:
            l += 1
        for i in range(l):
            if doEe or doTe:
                pd = self.snakeCPDist(i, i+1)
                pdisti.append(pd)
                pdistav += pd/l

        count = 0
        for s,r in self.spPointList:
            count += 1
            if doDe or doGe:
                x, y, dx1, dy1, dx2, dy2 = self.splineDerrivatives(s, r)
            else:
                x, y = self.splinePoints(s, r)

            # for each point along the splines...

            # attraction to a specific intensity
            if doIe:
                intensity = self.getImagePixelIntensity(x, y)
                ie += 100 * abs(intensity-inten)

            if doDe:
                # second derrivatives contribute to energy
                de += (dx2*dx2+dy2*dy2)*.5;

            if doGe:
                # attraction to gradient
                if dx1 == 0:
                    gx = 1
                    gy = 0
                elif dy1 == 0:
                    gx = 0
                    gy = 1
                elif abs(dx1) < abs(dy1):
                    gx = 1
                    gy = -dx1/dy1
                else:
                    gx = dy1/dx1
                    gy = -1

                intensity = self.getImagePixelIntensity(x, y)
                gav = intensity
                garray = [intensity]
                gsize = 5 # number of pixels perpendicular to snake to exmine for gradient
                for g in range(1,gsize):
                    pix = self.getImagePixelIntensity(x+g*gx, y+g*gy)
                    garray.append(pix)
                    gav += pix
                    pix = self.getImagePixelIntensity(x-g*gx, y-g*gy)
                    garray.append(pix)
                    gav += pix
                gav /= len(garray)
                gvar = garray[0] # weighted std deviation type thing (gradient near snake counts more)
                for g in range(1,len(garray),2):
                    gvar += (garray[g]-gav)*(garray[g]-gav)/g
                    gvar += (garray[g+1]-gav)*(garray[g+1]-gav)/g
                gvar = math.sqrt(gvar/(gsize*2-1))
                ge += 10000 / (1+gvar)

        # lower energy for longer snakes
        if doTe:
            te += 100000000 / pdistav

        # lower energy for evenly spaced points
        if doEe:
            for i in range(l):
                pdistsd += (pdisti[i]-pdistav)*(pdisti[i]-pdistav)
                ee += 5000 * math.sqrt(pdistsd/l)

        totalEnergy  = ie*self.params['intensityWeight']
        totalEnergy += ge*self.params['gradientWeight']
        totalEnergy += de*self.params['derivativeWeight']
        totalEnergy += ee*self.params['evenSpacingWeight']
        totalEnergy += te*self.params['totalLengthWeight']
        # Snake might shrink up when slithering on solid background and
        # count goes to 0. Doesn't happen every time.
        if count == 0:
            count = 1
        snakeE = totalEnergy/count
        return snakeE

    def snakeCPDist(self, i, j): # distance between two control points
        i = i % len(self.controlPoints) # wrap around
        j = j % len(self.controlPoints)
        xi, yi = self.controlPoints[i]
        xj, yj = self.controlPoints[j]
        return math.sqrt((xi-xj) * (xi-xj) + (yi-yj) * (yi-yj))

# recalculate spline coefficients
#  (only you are working with a different segment than last time)
    def splineCoefficients(self, p):
        if  p != self.lastP:
            self.lastP = p
            l = len(self.controlPoints)
            p0 = self.controlPoints[(p-1)%l]
            p1 = self.controlPoints[p]
            p2 = self.controlPoints[(p+1)%l]
            p3 = self.controlPoints[(p+2)%l]
            if not self.connected and p == 0:
                p0 = p1
            if not self.connected and p == l-2:
                p3 = p2
            if not self.connected and p == l-1:
                p3 = p2 = p1
            self.dsp = 6 # these are the coefficients for bezier splines
            self.b3x = -1 * p0[0] +  3 * p1[0] + -3 * p2[0] + p3[0];
            self.b2x =  3 * p0[0] + -6 * p1[0] +  3 * p2[0];
            self.b1x = -3 * p0[0] +               3 * p2[0];
            self.b0x =      p0[0] +  4 * p1[0] +      p2[0];
            self.b3y = -1 * p0[1] +  3 * p1[1] + -3 * p2[1] + p3[1];
            self.b2y =  3 * p0[1] + -6 * p1[1] +  3 * p2[1];
            self.b1y = -3 * p0[1] +               3 * p2[1];
            self.b0y =      p0[1] +  4 * p1[1] +      p2[1];

    def splinePoints(self, p, t):
        """ calculate points along spline curves
            p is the spline to calculate
            (p=2 means the curve segment between snake points 2 and 3)
            t is the % along that segment to calculate
            (p=2,t=.2 means 20% of the way between points 2 and 3 """
        self.splineCoefficients(p) # update coefficients
        x = (((self.b3x*t + self.b2x)*t + self.b1x)*t + self.b0x)/self.dsp
        y = (((self.b3y*t + self.b2y)*t + self.b1y)*t + self.b0y)/self.dsp
        return (x, y)

    def splineDerrivatives(self, p, t):
        x, y = self.splinePoints(p, t)
        dx1 = ((3*self.b3x*t + 2*self.b2x)*t +self.b1x)/self.dsp
        dy1 = ((3*self.b3y*t + 2*self.b2y)*t +self.b1y)/self.dsp
        dx2 = (6*self.b3x*t + 2*self.b2x)/self.dsp
        dy2 = (6*self.b3y*t + 2*self.b2y)/self.dsp
        return (x, y, dx1, dy1, dx2, dy2)

##------------- code related to saving to Results file ------------

    def getTrackDataLabel(self):
        """
        Converts to string and formats for writing out to file.
        The returned value is a tuple of 2 lists as shown below.
        (['   xval     '], ['   yval     '])
        """
        rf = self.params['resultFormat']
        resultLabel = ''
        if rf == 0:
            resultLabel = self.getShortFormatLabel()
        else:
            resultLabel = self.getLongFormatLabel()
        return resultLabel

    def getShortFormatLabel(self):
        """
        The Short Format is one row of output per each frame.
        Formats the values to a fixed width (6 in this case) and pads
        with the right number of blanks to make the columns line up.
        The total width is determined by how wide the header field is.
        """
        x, y = self.scaleCoordinates(self.centerX, self.centerY)
        labelx = self.getFormatted(x, 8, 19)
        labely = self.getFormatted(y, 8, 19)

        w = self.maxX - self.minX
        h = self.maxY - self.minY
        w, h = self.scaleCoordinates(w, h)
        labelw = self.getFormatted(w, 8, 16)
        labelh = self.getFormatted(h, 8, 17)

        radius = self.getAverageRadius()
        radius, dummy = self.scaleCoordinates(radius, 0)
        labelrad = self.getFormatted(radius, 8, 17)

        # stick it into a list -- its put into lists because some data may have
        # multiple values like histograms or snake points
        centerx = []
        centerx.append(labelx)
        centery = []
        centery.append(labely)
        maxw = []
        maxw.append(labelw)
        maxh = []
        maxh.append(labelh)
        rad = []
        rad.append(labelrad)
        # this format:  (['   xval     '], ['   xval     '])
        return (centerx, centery, maxw, maxh, rad)

    def getFormatted(self, n, textWidth, totalWidth):
        """
        Returns the number n as a string padded with blanks.
        """
        n1 = '%.4f' % n
        sn1 = string.strip(str(n1))  # eliminate leading or trailing whitespace
        sn = string.rjust(sn1, textWidth)    # right justified in a string
        rightPadWidth = int((totalWidth - textWidth) / 2) + 1
        leftPadWidth = totalWidth - (rightPadWidth + textWidth)
        leftPadding = ' ' * leftPadWidth
        rightPadding = ' ' * rightPadWidth
        label = leftPadding + sn + rightPadding
        return label

    def scaleCoordinates(self, x, y):
        """
        Take care of pixel scaling when ScaleTool was used.
        """
        if Spotlight.scaleUserUnits == 1.0 and Spotlight.scalePixelUnits == 1.0:
            pass
        else:
            x = x * Spotlight.pixelScale
            y = y * Spotlight.pixelScale
        return (x, y)

    def normalizedToScaled(self, value):
        """
        Take care of pixelValues (actual or normalized).
        Input value is always normalized and output is either normalized or actual.
        """
        if Spotlight.pOptions.programOptions['pixelValues'] == 0: # normalized
            v = value
        else:
            v = int(value * 255.0)
        return v

    def getLongFormatLabel(self):
        """The Long Format is list of points per each frame."""
        #### HERE IS WHAT THE DATA LOOKS LIKE
        ## centerx = 123.0
        ## centery = 100.000
        ## xx = [1.04, 55.001, 66.333, 122.000]
        ## yy = [222.000, 0.0, 44.0, 133.088]
        ## rr = [100.00, 100.00, 123.0, 123.00]
        ## gg = [100.00, 100.00, 123.0, 123.00]
        ## bb = [100.00, 100.00, 123.0, 123.00]

        # format the data
        xcen, ycen = self.scaleCoordinates(self.centerX, self.centerY)
        label = self.getFormatted(xcen, 8, 19)
        cx = []
        cx.append(label)
        label = self.getFormatted(ycen, 8, 19)
        cy = []
        cy.append(label)

        # the ScaleTool scaling (of x,y) and displaying of pixel values (as
        # actual or normalized) is taken care of in getDataLists() function
        xx, yy, rr, gg, bb = self.getDataLists()
        x = []
        for item in xx:
            label = self.getFormatted(item, 8, 12)
            x.append(label)
        y = []
        for item in yy:
            label = self.getFormatted(item, 8, 12)
            y.append(label)
        r = []
        for item in rr:
            label = self.getFormatted(item, 8, 12)
            r.append(label)
        g = []
        for item in gg:
            label = self.getFormatted(item, 8, 12)
            g.append(label)
        b = []
        for item in bb:
            label = self.getFormatted(item, 8, 12)
            b.append(label)
        return (cx, cy, x, y, r, g, b)

    def getDataLists(self):
        xx = []
        yy = []
        rr = []
        gg = []
        bb = []
        img = PilProcess.convertGrayToColor(Spotlight.workingImage)

        for xy in self.pointList:
            xp, yp = xy
            cp = self.clipPointToImage(xp, yp, img)
            xxp, yyp = self.scaleCoordinates(cp[0], cp[1]) # ScaleTool scaling
            # fill in xx and yy lists (snake line x and y coordinates)
            xx.append(xxp)
            yy.append(yyp)
            # Fill in rr, gg, bb lists (pixel value under snake line).
            # Note: xp and yp are un-scaled position coordinates
            pix = PilProcess.getPixelNorm(img, int(xp), int(yp))
            red = self.normalizedToScaled(pix[0])
            green = self.normalizedToScaled(pix[1])
            blue = self.normalizedToScaled(pix[2])
            rr.append(red)
            gg.append(green)
            bb.append(blue)
        return (xx, yy, rr, gg, bb)

    def getHeader(self):
        rf = self.params['resultFormat']
        h = []
        if rf == 0:
            h.append('center x')
            h.append('center y')
            h.append('width')
            h.append('height')
            h.append('radius')
        else:
            h.append('center x')
            h.append('center y')
            h.append('x')
            h.append('y')
            h.append('r')
            h.append('g')
            h.append('b')
        return h

##-------------------- AoiLineFollowing class ----------------------------

class AoiLineFollowing(AoiManualTracking):
    def __init__(self, x1, y1, x2, y2):
        AoiManualTracking.__init__(self, x1, y1, x2, y2)
        self.linedata = []
        self.stopped = False  # stopped by clicking the Stop button (True/False)

    def isManualAoi(self):
        """
        Identifies this aoi as a type of Aoi that requires a mouse click before
        it can go on. This requirement can make it 'hang' is some situations.
        """
        return True

    def getStatusBarText(self):
        return 'LineFollowingAoi'

    def Track(self):
        self.leftdown = False # takes care of weirdness (sometimes its True)
        self.waiting = True
        if Spotlight.stopImmediately: # skip the while loop
            self.waiting = False
        while(self.waiting):
            SpotlightGui.gui.Yield()

        self.waiting = False
        self.lineFollowing()
        self.leftdown = False # otherwise the Aoi sticks to the mouse
        self.stopped = False

    def lineFollowing(self):
        self.setLineData([])  # initialize it to None
        if self.stopped:
            return
        startpoint = self.getTrackPoint()
        aoiposition = self.getAoiPosition()
        #img = Spotlight.workingImage.copy()
        linedata = SpotlightPoint.LineFollow(Spotlight.workingImage, startpoint, aoiposition)
        self.setLineData(linedata)
        if linedata:
            # color the saved pixels to red
            for item in linedata:
                x, y = item
                SpotlightGui.gui.iPanel.drawRedPoint((x, y))
        else:  # clicked too far away from the line
            m = 'NO startpoint found - click closer to a line'
            SpotlightGui.gui.messageDialog(m)
            Spotlight.OnStop() # this calls Stop() below, and other things

    def Stop(self):
        self.stopped = True
        self.waiting = False

    def setLineData(self, data):
        self.linedata = []
        for d in data:
            self.linedata.append(d)

    def getLineData(self):
        return self.linedata

    def getTrackDataLabel(self):
        """
        converts to string and formats for writing out to file.
        The returned value is a tuple of 2 lists as shown below.
        (['   xval     '], ['   yval     '])
        """
        return self.getLongFormatLabel()

    def getFormatted(self, n, textWidth, totalWidth):
        """returns the number n as a string padded with blanks"""
        n1 = '%.3f' % n              # 1 digit to right of decimal point
        sn1 = string.strip(str(n1))  # eliminate leading or trailing whitespace
        sn = string.rjust(sn1, textWidth)    # right justified in a string
        rightPadWidth = int((totalWidth - textWidth) / 2) + 1
        leftPadWidth = totalWidth - (rightPadWidth + textWidth)
        leftPadding = ' ' * leftPadWidth
        rightPadding = ' ' * rightPadWidth
        label = leftPadding + sn + rightPadding
        return label

    def getLongFormatLabel(self):
        """
        The Long Format is list of points per each frame.
        """
        #### HERE IS WHAT THE DATA LOOKS LIKE
        ## xx = [1.04, 55.001, 66.333, 122.000]
        ## yy = [222.000, 0.0, 44.0, 133.088]

        linedata = self.getLineData()
        xx = []
        yy = []
        for item in linedata:
            x, y = item
            label = self.getFormatted(x, 8, 12)
            xx.append(label)
            label = self.getFormatted(y, 8, 12)
            yy.append(label)
        return (xx, yy)

##------------------ Class AoiAngleTool ----------------------------------

defaultRelativeTo = 0
defaultDisplayMode = 0

class AoiAngleTool(AoiLine):
    def __init__(self, x1, y1, x2, y2):
        AoiLine.__init__(self, x1, y1, x2, y2)

        self.relativeTo = defaultRelativeTo
        self.displayMode = defaultDisplayMode
        self.rotateNow = False
        self.updateAngle()

    def getStatusBarText(self):
        return 'AngleToolAoi'

    def updateStatusBar0(self):
        aoiType = self.getStatusBarText()
        if Spotlight.scaleUserUnits == 1.0 and Spotlight.scalePixelUnits == 1.0:
            m1 = aoiType + ': (%3d, %3d) (%3d, %3d)' % (self.x1,self.y1,self.x2,self.y2)
            m2 = '  angle: %.3f' % self.getAngle()
            message = m1 + m2
        else:
            x1 = self.x1 * Spotlight.pixelScale
            y1 = self.y1 * Spotlight.pixelScale
            x2 = self.x2 * Spotlight.pixelScale
            y2 = self.y2 * Spotlight.pixelScale
            m1 = aoiType + ': (%.3f, %.3f) (%.3f, %.3f)' % (x1, y1, x2, y2)
            m2 = '  angle: %.3f' % self.getAngle()
            message = m1 + m2
        SpotlightGui.gui.updateStatusBar(message, 0)

    def updateAngle(self):
        """Calculates the angle based on selections in the Options dialog
        box; relative to x or y axis and displayed (0 to 360) or
        (-180 to +180)."""
        d = self.getLineLength()
        dx = self.x1 - self.x2
        dy = self.y1 - self.y2
        angle = math.atan2(-dy, dx)/DEGtoRAD  # -180 to 180

        if self.relativeTo == 0:
            if self.displayMode == 0:       # x-axis (0 -- 360)
                if angle < 0.0:
                    angle = angle + 360.0
            else:                           # x-axis (-180 -- 180)
                pass
        else:
            if self.displayMode == 0:       # y-axis (0 -- 360)
                angle = angle - 90.0
                if angle < 0.0:
                    angle = angle + 360.0
            else:
                angle = angle - 90.0        # y-axis (-180 -- 180)
                if angle < -179.999999999: # sets -180.0 to 180.0
                    angle = angle + 360.0

        if abs(angle) < 0.0001:  # prevents -0.0000 (set to 0.0000)
            angle = 0.0
        self.setAngle(angle)

    def setOptions(self, dm, rt, rot):
        self.displayMode = dm
        self.relativeTo = rt
        self.rotateNow = rot
        global defaultDisplayMode
        global defaultRelativeTo
        defaultDisplayMode = self.displayMode
        defaultRelativeTo = self.relativeTo

    def rotateWholeImageAoi(self):
        'make WholeImageAoi the current aoi and rotate image'
        if self.rotateNow:
            currentAoiPos = Spotlight.aList.currentAoi
            Spotlight.aList.setWholeImageAoiAsCurrent()
            command = Spotlight.instantiateIpCommand({'name': 'Geometric'})
            angle = self.getAngle()
            params = command.getParams()
            params['angle'] = -angle
            command.setParams(params)
            Spotlight.aList.do(command) # do the rotation
            Spotlight.aList.currentAoi = currentAoiPos
            SpotlightGui.gui.iPanel.Refresh()

    def drawAoi(self, highlight, dc=None):
        # the main line
        AoiLine.drawAoi(self, highlight, dc)
        params = {}
        pointList = []
        points = []
        # cross
        center = (self.x2, self.y2)
        leg = 20
        vertline, horizline = self.getCross(center, leg)
        pointList.append(vertline)
        pointList.append(horizline)
        # circle
        center = (self.x1, self.y1)
        diameter = 7
        params['circle'] = (center, diameter)
        params['pointList'] = pointList
        params['highlight'] = highlight
        params['thickness'] = self.lineThickness
        SpotlightGui.gui.iPanel.drawAoi(params, dc)

    def aoiOptionsPresent(self):
        'yes, this aoi has options associated with it'
        return True

    def showAoiOptions(self):
        'brings up AngleTool options dialog box'
        self.rotateNow = False # set check off
        type = 'AngleToolOptions'
        params = {}
        params['relativeTo'] = self.relativeTo
        params['displayMode'] = self.displayMode
        params['rotateNow'] = self.rotateNow
        params['angle'] = self.getAngle()
        params = SpotlightGui.gui.showModalDialog(type, params, self)
        if params:
            rel = params['relativeTo']
            dm = params['displayMode']
            rotate = params['rotateNow']
            self.setOptions(dm, rel, rotate)
            self.rotateWholeImageAoi()
        self.updateStatusBar0()

##------------------ Class AbelTool ------------------------------------

class AoiAbelTool(AoiLine):
    def __init__(self, x1, y1, x2, y2):
        AoiLine.__init__(self, x1, y1, x2, y2)
        self.dd = None

    def isCloseExecuted(self):
        'all modeless AOIs must have this'
        return self.closeExecuted

    def closeDialog(self):
        self.closeExecuted = True

    def updateStatusBar0(self):
        c = self.getAoiCenter()
        if Spotlight.scaleUserUnits == 1.0 and Spotlight.scalePixelUnits == 1.0:
            message = 'AbelToolAoi: (%3d, %3d) (%3d, %3d)    Center: (%3d, %3d)' \
                        % (self.x1, self.y1, self.x2, self.y2, c[0], c[1])
        else:
            x1 = self.x1 * Spotlight.pixelScale
            y1 = self.y1 * Spotlight.pixelScale
            x2 = self.x2 * Spotlight.pixelScale
            y2 = self.y2 * Spotlight.pixelScale
            c0 = c[0] * Spotlight.pixelScale
            c1 = c[1] * Spotlight.pixelScale
            message = 'AbelToolAoi: (%.3f, %.3f) (%.3f, %.3f)  Center: (%.3f, %.3f)' \
                        % (x1, y1, x2, y2, c0, c1)
        SpotlightGui.gui.updateStatusBar(message, 0)

    def initialize(self):
        self.distribution = []
        self.profile = []
        self.refprofile = []
        self.xvalues = []
        self.yvalues = []
        self.yaxislabel = ''
        self.closeExecuted = False
        self.multByMillion = True
        self.isFromImage = True
        self.isDemo = False
        self.abel = Abel.AbelTransform(self)
        self.updateMeans()
        self.dd = SpotlightGui.gui.createModelessDialog('AbelTool', {}, None, self)

        # Disable the frame menubar to prevent any other dialog boxes
        # to be displayed. This is because they would show up behind the Abel
        # window (which is ALWAYS_ON_TOP).
        SpotlightGui.gui.EnableMenuBar(False)

    def setParams(self, params):
        if params.has_key('filter'):
            self.abel.setParams({'filter': params['filter']})
        if params.has_key('averageOption'):
            self.abel.setParams({'averageOption': params['averageOption']})
        if params.has_key('smoothingFactor'):
            self.abel.setParams({'smoothingFactor': params['smoothingFactor']})
        if params.has_key('deltaSpacing'):
            self.abel.setParams({'deltaSpacing': params['deltaSpacing']})
        if params.has_key('wavelength'):
            self.abel.setParams({'wavelength': params['wavelength']})
        if params.has_key('sri'):
            self.abel.setParams({'sri': params['sri']})
        if params.has_key('backgroundSelection'):
            self.abel.setParams({'backgroundSelection': params['backgroundSelection']})
        if params.has_key('referenceImage'):
            self.abel.setParams({'referenceImage': params['referenceImage']})
        if params.has_key('backgroundLeft'):
            self.abel.setParams({'backgroundLeft': params['backgroundLeft']})
        if params.has_key('backgroundRight'):
            self.abel.setParams({'backgroundRight': params['backgroundRight']})

    def deinitialize(self):
        SpotlightGui.gui.destroyModelessDialog(self.dd)
        SpotlightGui.gui.EnableMenuBar(True) # re-enable the menubar

    def drawAoi(self, highlight, dc=None):
        # vertical line - thickness of one (specified by highlight=False)
        params = {}
        pointList = []
        points = []
        x = (self.x2 + self.x1)/2
        imX,imY = Spotlight.getWorkingImageSize()
        points.append((x, 1))
        points.append((x, imY-1))
        pointList.append(points)
        params['pointList'] = pointList
        params['highlight'] = False
        SpotlightGui.gui.iPanel.drawAoi(params, dc)
        # horizontal line
        AoiLine.drawAoi(self, highlight, dc)

    def OnMouseMove(self, pos):
        if self.leftdown:
            px = pos[0]
            py = pos[1]
            offsetWidth = px - self.lastPoint[0]
            offsetHeight = py - self.lastPoint[1]

            if self.closest == 0:   # move Aoi
                if self.dd.lockAxisStatus() == False:
                    self.x1 = self.x1 + offsetWidth
                    self.x2 = self.x2 + offsetWidth
                self.y1 = self.y1 + offsetHeight
                self.y2 = self.y2 + offsetHeight
            else:   # move line endpoint
                'forces line to be of odd length 9,11,13,...'
                if self.closest == 1:      # top left corner
                    d = (self.x1 - px) / 2
                    if self.x2+d > self.x1-d  + 5: # min of 9 pix
                        self.x2 = self.x2 + d + 1
                        self.x1 = self.x1 - d - 1
                elif self.closest == 3:    # bottom right corner
                    d = (self.x2 - px) / 2
                    if self.x2-d > self.x1+d  + 5: # min of 9 pix
                        self.x2 = self.x2 - d + 1
                        self.x1 = self.x1 + d - 1

            r = self.limitLineMovement(self.x1, self.y1, self.x2, self.y2)
            self.x1 = r[0]
            self.y1 = r[1]
            self.x2 = r[2]
            self.y2 = r[3]
            self.lastPoint = (px, py)
            self.updateStatusBar0()
            SpotlightGui.gui.iPanel.Refresh()
            self.updateLineProfile()
            self.resetAbelParameters()

    def OnMouseLeftDown(self, pos):
        self.resetAbelParameters()
        AoiLine.OnMouseLeftDown(self, pos)

    def OnMouseLeftUp(self, pos):
        self.updateMeans()
        AoiLine.OnMouseLeftUp(self, pos)

    def updateLineProfile(self):
        if self.dd:
            self.dd.postProfile()

    def getP(self, colorplane=LUMINANCE):
        if self.isFromImage:
            rgbline = self.getLineProfile()
            self.profile = self.breakOutProfile(rgbline, LUMINANCE)
            return self.profile
        else:
            #return None ## this will read line profile from file
            return self.profile

    def getRefProfile(self):
        return self.refprofile
    def getDistribution(self):
        return self.distribution

    def resetAbelParameters(self):
        self.isFromImage = True
        self.isDemo = False
        self.distribution = []
        self.refprofile = []
        self.setAxisLabel('')

    def updateModeless(self, refreshAxes=False):
        """
        Called when Pixel Display Type (actual/normalized) is changed or when
        new image is loaded.
        """
        if refreshAxes:
            self.dd.aPanel.drawAxisLabels()
        # in case the line is on the edge of image and then thickens up
        r = self.limitLineMovement(self.x1, self.y1, self.x2, self.y2)
        self.x1 = r[0]
        self.y1 = r[1]
        self.x2 = r[2]
        self.y2 = r[3]
        self.updateLineProfile()
        self.resetAbelParameters()
        self.updateMeans()

    def updateMeans(self):
        leftMean, rightMean = self.getBothMeans()
        self.abel.setParams({'backgroundLeft': leftMean})
        self.abel.setParams({'backgroundRight': rightMean})

    def getAxisLabel(self):
        return self.yaxislabel
    def setAxisLabel(self, label):
        self.yaxislabel = label

    def AbelTransformSVF(self):
        'called when SVF button is clicked'
        if self.isFromImage:
            self.svfFromImage()
        else:
            self.svfFromFile()

    def AbelTransformIntensity(self):
        'called when Intensity button is clicked'
        self.distribution = []
        #self.refprofile = []
        if self.isFromImage:
            self.abelIntensityFromImage()
        else:
            self.abelIntensityFromFile()

    def svfFromImage(self):
        """calculate Soot Volume Fraction using Abel Transform"""
        params = self.abel.getParams()
        if params['backgroundSelection'] == 0: # use background values
            backgroundLeft = params['backgroundLeft']
            backgroundRight = params['backgroundRight']
            if params['averageOption'] == 0:
                backgroundValue = (backgroundLeft + backgroundRight) / 2
                self.refprofile = self.getAsList(backgroundValue, len(self.profile))
            else:
                left, right = self.abel.splitProfile(self.profile)
                leftRef = self.getAsList(backgroundLeft, len(left))
                rightRef = self.getAsList(backgroundRight, len(right))
                self.refprofile = self.abel.combineProfiles(leftRef, rightRef)
        else:   # use ref image
            file = params['referenceImage']
            if not os.path.isfile(file):
                m = 'reference file does not exist - use SVF Options to change it'
                self.showMessage(m)
                return

            referenceImage = PilProcess.openImage(file)
            if not referenceImage:
                self.showMessage('bad file - can not open')
                return
            rgbline = self.getLineProfile(0,0,0,0,-1,referenceImage)
            self.refprofile = self.breakOutProfile(rgbline, LUMINANCE)

        svf = self.abel.calcSootVolumeFraction(self.profile, self.refprofile, True)
        self.distribution = svf
        self.multByMillion = True
        self.setAxisLabel('Abel transform - SVF (ppm)')
        self.isFromImage = True

    def svfFromFile(self):
        # If SVF graph was saved then there exists a ref profile, however
        # if only a line profile was saved or if an Intensity graph was saved
        # then there is no ref profile and so can't do this operation.
        if self.refprofile:
            svf = self.abel.calcSootVolumeFraction(self.profile, self.refprofile, False)
            self.distribution = svf
            self.multByMillion = True
            self.setAxisLabel('Abel transform - SVF (ppm)')
        else:
            m0 = 'No reference profile exists in the data  '
            m1 = 'as this profile data came from a file. '
            m2 = 'Only option availabe is the Abel transform of Intensity '
            m = m0 + '\n' + m1 + '\n' + '\n' + m2
            self.showMessage(m)

    def showMessage(self, m):
        """
        Displays the messageDialog on top of the Abel window. This method
        is called from here as well as from Abel.py.
        """
        self.dd.showMessage(m)

    def abelIntensityFromImage(self):
        'calculate Intensity using Abel Transform'
        self.distribution = self.abel.calcIntensity(self.profile)
        self.multByMillion = False
        self.setAxisLabel('Abel transform - Intensity')
        self.isFromImage = True

    def abelIntensityFromFile(self):
        if self.isDemo:
            proj = self.profile
            self.distribution = self.abel.AbelTestFromFile(self.el, proj)
            self.setAxisLabel('     Abel transform ')
        else:
            self.distribution = self.abel.calcIntensity(self.profile)
            self.setAxisLabel('Abel transform - Intensity')
        self.multByMillion = False
        self.isFromImage = False

    def getAsList(self, number, listlength):
        'returns a list of identical values'
        out = []
        for i in range(listlength):
            out.append(number)
        return out

    def getLeftAoi(self):
        x1 = self.x1 - 8
        y1 = self.y1 - 4
        x2 = self.x1
        y2 = self.y1 + 4
        # make sure coordinates are inside the image
        r = self.clipRectToImage(x1, y1, x2, y2)
        x1 = r[0]
        y1 = r[1]
        x2 = r[2]
        y2 = r[3]
        return (x1, y1, x2, y2)

    def getRightAoi(self):
        x1 = self.x2
        y1 = self.y2 - 4
        x2 = self.x2 + 8
        y2 = self.y2 + 4
        # make sure coordinates are inside the image
        r = self.clipRectToImage(x1, y1, x2, y2)
        x1 = r[0]
        y1 = r[1]
        x2 = r[2]
        y2 = r[3]
        return (x1, y1, x2, y2)

    def getMean(self, img):
        img = PilProcess.extractPlane(img, 3) # luminance
        mean = 0.0
        aoiWidth, aoiHeight = img.size
        for y in range(aoiHeight):
            for x in range(aoiWidth):
                r, g, b = PilProcess.getPixelNorm(img, x, y)
                mean = mean + r
        mean = mean /(aoiWidth * aoiHeight)
        return mean

    def getBothMeans(self):
        imgLeft = Spotlight.getAoiImage(self.getLeftAoi())
        imgRight = Spotlight.getAoiImage(self.getRightAoi())
        meanLeft = self.getMean(imgLeft)
        meanRight = self.getMean(imgRight)
        return (meanLeft, meanRight)

    def showAoiPositionDialog(self):
        """
        Brings up a AbelToolAoiPositionDialog box. This would normally be called
        from the menu Aoi->Set Position but since Abel disables the menubar, a
        menu for this has been created in the Abel window.
        """
        type = 'AbelToolAoiPosition'
        params = {}
        params['x1'] = self.x1
        params['y1'] = self.y1
        params['x2'] = self.x2
        params['y2'] = self.y2
        params = SpotlightGui.gui.showModalDialog(type, params, self.dd)
        return params

    def LoadExistingPlot(self, data):
        label, xval, yval, profile, refp, distr = data
        if profile: # note: distr can be Null but profile can not
            #label = label[:-1] # strip off line-feed (came from file)
            label = string.strip(label) # strip off line-feed (came from file)
            self.setAxisLabel(label)
            self.xvalues = xval
            self.yvalues = yval
            self.profile = profile
            self.refprofile = refp
            for i in range(len(distr)):
                distr[i] = distr[i] / 1000000
            self.distribution = distr
            self.isFromImage = False
            self.multByMillion = True
            self.isDemo = False

    def LoadAbelDemo(self):
        self.el, proj = self.abel.getZengGuangsTestData()
        if proj:
            self.setAxisLabel('       double half circle')
            self.profile = proj
            self.refprofile = []
            self.distribution = []
            self.isFromImage = False
            self.multByMillion = False
            self.isDemo = True
