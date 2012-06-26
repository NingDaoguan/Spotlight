import os, sys, pickle, math
import wx
import Spotlight
import SpotlightDialog
import SpotlightGui
import PilProcess
import images

ID_FILE_OPEN = wx.NewId()
ID_FILE_SAVEAS = wx.NewId()
ID_FILE_EXIT  = wx.NewId()
ID_BUTTON_SAVEAS = wx.NewId()
ID_FILE_SAVEAOI = wx.NewId()

ID_FILE_RECENT0 = wx.NewId()
ID_FILE_RECENT1 = wx.NewId()
ID_FILE_RECENT2 = wx.NewId()
ID_FILE_RECENT3 = wx.NewId()
ID_FILE_RECENT4 = wx.NewId()
ID_FILE_RECENT5 = wx.NewId()
ID_FILE_RECENT6 = wx.NewId()
ID_FILE_RECENT7 = wx.NewId()
ID_FILE_RECENT8 = wx.NewId()

ID_VIEW_IMAGEINFO = wx.NewId()
ID_VIEW_UNDO = wx.NewId()
ID_VIEW_REDO = wx.NewId()
ID_BUTTON_UNDO = wx.NewId()
ID_BUTTON_REDO = wx.NewId()
ID_VIEW_ZOOM_IN = wx.NewId()
ID_VIEW_ZOOM_OUT = wx.NewId()
ID_VIEW_ZOOM_ORIGINAL = wx.NewId()
ID_VIEW_OPTIONS = wx.NewId()
ID_VIEW_SCALE = wx.NewId()
ID_VIEW_FORCE_UPDATES  = wx.NewId()

ID_AOI_RECTANGLE = wx.NewId()
ID_AOI_LINEPROFILE = wx.NewId()
ID_AOI_HISTOGRAM = wx.NewId()
ID_AOI_NEWAOI = wx.NewId()
ID_AOI_DELETECURRENTAOI = wx.NewId()
ID_AOI_DELETEALLAOIS = wx.NewId()
ID_AOI_PREVIOUS = wx.NewId()
ID_AOI_NEXT = wx.NewId()
ID_BUTTON_NEXT = wx.NewId()
ID_BUTTON_PREVIOUS = wx.NewId()
ID_AOI_PROCSEQUENCE = wx.NewId()
ID_AOI_UPDATE = wx.NewId()
ID_AOI_THRESHOLDTRACK = wx.NewId()
ID_AOI_OPTIONS = wx.NewId()
ID_AOI_MANUAL = wx.NewId()
ID_AOI_CENTER = wx.NewId()
ID_AOI_LOCAL_MAX = wx.NewId()
ID_AOI_SNAKE = wx.NewId()
ID_AOI_LINEFOLLOW = wx.NewId()
ID_AOI_ANGLETOOL = wx.NewId()
ID_AOI_ABELTOOL = wx.NewId()
ID_AOI_SETPOSITION = wx.NewId()

ID_PROCESS_THRESHOLD = wx.NewId()
ID_PROCESS_FILTER = wx.NewId()
ID_PROCESS_ARITHMETIC = wx.NewId()
ID_PROCESS_EXTRACTPLANE = wx.NewId()
ID_PROCESS_CONVERT = wx.NewId()
ID_PROCESS_CONTRAST = wx.NewId()
ID_PROCESS_PSEUDOCOLOR = wx.NewId()
ID_PROCESS_MORPHOLOGICAL = wx.NewId()
ID_PROCESS_GEOMETRIC = wx.NewId()
ID_PROCESS_SAVEAOI = wx.NewId()
ID_PROCESS_RESIZE = wx.NewId()
ID_PROCESS_EXTRACTFIELD = wx.NewId()
ID_PROCESS_STATISTICS = wx.NewId()
ID_PROCESS_TEST = wx.NewId()
ID_PROCESS_ENHANCE = wx.NewId()


ID_BUTTON_REWIND = wx.NewId()
ID_BUTTON_STEPBACK = wx.NewId()
ID_BUTTON_PAUSE = wx.NewId()
ID_BUTTON_STEPFORWARD = wx.NewId()
ID_BUTTON_FASTFORWARD = wx.NewId()
ID_TRANSPORT_REWIND = wx.NewId()
ID_TRANSPORT_STEPBACK = wx.NewId()
ID_TRANSPORT_PAUSE = wx.NewId()
ID_TRANSPORT_STEPFORWARD = wx.NewId()
ID_TRANSPORT_FASTFORWARD = wx.NewId()
ID_TRANSPORT_NEXTSTEPOPTIONS = wx.NewId()
ID_TRANSPORT_GOTO_SPECIFIC = wx.NewId()

ID_TRACK_ONE = wx.NewId()
ID_TRACK_CONTINUOUS = wx.NewId()
ID_BUTTON_TRACK_ONE = wx.NewId()
ID_BUTTON_TRACK_CONTINUOUS = wx.NewId()
ID_TRACK_RESULTSFILE = wx.NewId()
ID_BUTTON_STOP = wx.NewId()

ID_HELP_ABOUT = wx.NewId()
ID_HELP_DOCUMENTATION = wx.NewId()
ID_HELP_NEW = wx.NewId()

# Mac specific menu adjustments, ignored on other platfoms
wx.App_SetMacAboutMenuItemId(ID_HELP_ABOUT)
wx.App_SetMacExitMenuItemId(ID_FILE_EXIT)
wx.App_SetMacSupportPCMenuShortcuts(True)


def convertPILtoWX(pilimage):
    if pilimage == None:
        return None
    if pilimage.mode == 'L':
        pilimage = pilimage.convert("RGB")
    wximg = wx.EmptyImage(pilimage.size[0], pilimage.size[1])
    wximg.SetData(pilimage.tostring('raw','RGB'))
    return wximg


class ImagePanel(wx.ScrolledWindow):
    def __init__(self, frame, id):
        styleType = wx.SUNKEN_BORDER
        wx.ScrolledWindow.__init__(self, frame, id, style=styleType)

        self.frame = frame
        self.palette = None

        self.pps = 8  # pixels per scroll step
        self.SetScrollbars(self.pps, self.pps, 8, 8)
        self.scale = 1.0
        self.backgroundColor =  wx.Brush("gray")
        self.dirtyZoomedImage = 0 # set whenever zoom or scroll changes
        self.fullDisplayImageCache = None
        self.zoomedDisplayImageCache = None
        self.EnableScrolling(0,0) # turn off panning the old image since we do it ourself
        self.OnSize(None)

        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_MOTION(self, self.OnMouseMove)
        wx.EVT_LEFT_DOWN(self, self.OnMouseLeftDown)
        wx.EVT_LEFT_UP(self, self.OnMouseLeftUp)
        wx.EVT_RIGHT_DOWN(self, self.OnMouseRightDown)
        wx.EVT_RIGHT_DCLICK(self, self.OnMouseRightDClick)
        wx.EVT_KEY_DOWN(self,self.OnKeyDown)
        wx.EVT_KEY_UP(self,self.OnKeyUp)
        wx.EVT_SIZE(self, self.OnSize)
        wx.EVT_SCROLLWIN(self, self.OnScroll)
        wx.EVT_ERASE_BACKGROUND(self, self.OnErase)

    def OnKeyUp(self, event):
        key = event.KeyCode()
        if key == 308:  # ctrl key
            Spotlight.setCtrlKeyDown(False)
        event.Skip()

    def OnKeyDown(self, event):
        key = event.KeyCode()
        if key == 308:  # ctrl key
            Spotlight.setCtrlKeyDown(True)
        c = 0
        if key < 256:
            c = chr(key)
            if c == 'O':
                aoi = Spotlight.aList.getCurrentAoi()
                aoi.showAoiOptions()
            if c == 'U':
                Spotlight.OnUpdate()  # calling OnUpdate() makes undo work

        if Spotlight.aList.getAoiListLength() > 1: # more than one aoi
            if key == 9:  # TAB key
                Spotlight.NextAoi()
            if key == 127 and sys.platform != 'darwin':  # del key on Win
                Spotlight.DeleteCurrentAoi()
            if key == 8 and sys.platform == 'darwin':  # del key on Mac
                Spotlight.DeleteCurrentAoi()

        event.Skip()

    def setPalette(self, palette):
        self.palette = palette

    ##-------- zoom and scroll stuff -----------------

    def OnScroll(self, event):
        """ scrollBars will be recalculated when the image is next displayed """
        self.dirtyZoomedImage=1
        event.Skip()

    def OnErase(self, event):
        """ do nothing, to prevent flicker. double buffering does not require erasing """
        pass

    def OnSize(self, event):
        self.displayWidth, self.displayHeight = self.GetClientSizeTuple()
        if self.displayHeight <= 0: # prevent exceptions when nothing is visible
            return
        self.displayBuffer = wx.EmptyBitmap(self.displayWidth, self.displayHeight)
        if Spotlight.workingImage == None:
            # an empty image displays backgroundColor so that displayBuffer always has valid data
            dc = wx.BufferedDC(None, self.displayBuffer)
            dc.SetBackground(self.backgroundColor)
            dc.Clear()
        self.Zoom()
        if event:
            event.Skip()

    def Zoom(self, zoomChange=None):
        if Spotlight.workingImage == None:
            return # don't zoom on nothing
        self.dirtyZoomedImage = 1
        ulCornerX, ulCornerY  = self.GetViewStart() # upper left corner before zooming

        if zoomChange != None:
            if zoomChange == 0:
                self.scale = 1.0
            elif zoomChange > 0:
                self.scale *= 2.0
                ulCornerX += self.displayWidth/self.pps/4
                ulCornerY += self.displayHeight/self.pps/4
            elif zoomChange < 0:
                self.scale /= 2.0
                ulCornerX -= self.displayWidth/self.pps/2
                ulCornerY -= self.displayHeight/self.pps/2

        self.pps = max(1, int(self.scale))
        self.updateScrollbars((ulCornerX, ulCornerY))

    def updateScrollbars(self, position=None):
        if position == None:
            position = self.GetViewStart()
        x, y = position
        x, y = max(0, x),  max(0, y)

        xsteps, ysteps = Spotlight.getWorkingImageSize()
        if self.scale < 1.0:
            xsteps, ysteps = int(xsteps*self.scale), int(ysteps*self.scale)

        self.SetScrollbars(self.pps, self.pps, xsteps, ysteps, x, y) # original
        self.Refresh()

##    Buffered image display explanation
##
##    The image flow from workingImage to displayImage is:
##
##    1 - The workingImage is the image that all the image processing operations work upon.
##    With numarray, it is a floating point numarray, scaled so that normally 0.0 is black
##    and 1.0 is white, although numbers outside of that range are legal. With PIL, workingImage
##    is a PIL image. In either case, it is always changed by calling the setWorkingImage(...)
##    function, which will cause the display to be updated to reflect the new workingImage.
##
##    2 - The workingImage is converted to the fullDisplayImage, which is the same resolution
##    as workingImage, but is a wxImage with pixel values scaled to match the displayable
##    range of video cards (typically integers, 0 to 255).
##
##    3 - The zoomedDisplayImage is a region (sub-image) extracted from fullDisplayImage that
##    matches the current display window's aspect ratio and takes scrolling and zooming into
##    account. Like fullDisplayImage, it is a wxImage with the same scale, and it's resolution
##    is always the same or less than the fullDisplayImage.
##
##    4 - The displayImage is the actual display memory itself, and is created by resampling
##    (to zoom) the zoomedDisplayImage. It is not actually stored anywhere (except on the
##    video card), so it does not actually appear as a Python variable.
##
##    To improve performance, double buffering and caching are introduced to the flow:
##
##    2a - getFullDisplayImage() is responsible for converting workingImage into
##    fullDisplayImage and returning fullDisplayImage. However, it always stores the
##    last calculated value of fullDisplayImage in fullDisplayImageCache. If workingImage
##    has not changed, it will just return fullDisplayImageCache instead of doing any
##    conversions.
##
##    3a - getZoomedDisplayImage() is responsible for converting fullDisplayImage into
##    zoomedDisplayImage and returning zoomedDisplayImage. However, it always stores the
##    last calculated value of zoomedDisplayImage in zoomedDisplayImageCache. If workingImage
##    and the scolling/zooming have not changed, it will just return zoomedDisplayImageCache
##    instead of doing any conversions.
##
##    4a - updateDisplay() is responsible for taking the zoomedDisplayImage and resampling
##    it into a displayBuffer that represents the displayImage. If workingImage and the scolling/
##    zooming have changed, OnPaint will call updateDisplay() to regenerate displayImage and
##    save the result in displayBuffer, otherwise OnPaint() just copies displayBuffer to
##    displayImage to show the image.

    def OnPaint(self, event):
        """ recalculate display if needed, else copy displayBuffer onto the screen """
        dc = wx.PaintDC(self) # a wxPaintDC must be created even if it is not used
        if Spotlight.dirtyWorkingImage or self.dirtyZoomedImage:
            self.updateDisplay()
        # draw displayBuffer and AIOs offscreen to eliminate flicker
        tempDisplayBuffer = wx.EmptyBitmap(self.displayWidth, self.displayHeight)
        dbDc = wx.MemoryDC()
        dbDc.SelectObject(tempDisplayBuffer)
        dbDc.BeginDrawing()
        dbDc.DrawBitmap(self.displayBuffer, 0, 0)
        Spotlight.aList.redrawAll(dbDc)
        dbDc.SelectObject(wx.NullBitmap)
        dbDc.EndDrawing()
        dc.DrawBitmap(tempDisplayBuffer, 0, 0)

    def updateDisplay(self):
        """ convert zoomedDisplayImage to displayBuffer """
        zoomedDisplayImage = self.getZoomedDisplayImage()
        if zoomedDisplayImage:
            dc = wx.BufferedDC(wx.ClientDC(self), wx.EmptyBitmap(self.displayWidth, self.displayHeight))
            dc.BeginDrawing()
            dc.SetBackground(self.backgroundColor)
            dc.Clear()
            w, h = zoomedDisplayImage.GetWidth(), zoomedDisplayImage.GetHeight()
            resampledDisplayImage = zoomedDisplayImage.Scale(int(w*self.scale), int(h*self.scale))
            dc.DrawBitmap(resampledDisplayImage.ConvertToBitmap(), 0, 0)
            dc.EndDrawing()

            # cache display in self.displayBuffer
            dbDc = wx.MemoryDC()
            dbDc.SelectObject(self.displayBuffer)
            dbDc.BeginDrawing()
            dbDc.Blit(0, 0, self.displayWidth, self.displayHeight, dc, 0, 0)
            dbDc.SelectObject(wx.NullBitmap)
            dbDc.EndDrawing()

    def getZoomedDisplayImage(self):
        """ convert fullDisplayImage to zoomedDisplayImage """
        if Spotlight.workingImage == None:
            return None
        if not Spotlight.dirtyWorkingImage and not self.dirtyZoomedImage and self.zoomedDisplayImageCache:
            return self.zoomedDisplayImageCache
        fullDisplayImage = self.getFullDisplayImage()

        # get the portion of the fullDisplayImage that corresponds to the visible display
        x,y,w,h = self.getZoomedRect()
        zoomedRect = wx.Rect(x,y,w,h)
        self.zoomedDisplayImageCache = fullDisplayImage.GetSubImage(zoomedRect)
        self.dirtyZoomedImage = 0
        return self.zoomedDisplayImageCache

    def getFullDisplayImage(self):
        """ convert workingImage to fullDisplayImage """
        if not Spotlight.dirtyWorkingImage and self.fullDisplayImageCache:
            return self.fullDisplayImageCache
        if self.palette:
            # apply the palette to workingImage
            workingImageColorized = Spotlight.workingImage.point(self.palette)
            self.fullDisplayImageCache = convertPILtoWX(workingImageColorized)
        else:
            self.fullDisplayImageCache = convertPILtoWX(Spotlight.workingImage)
        Spotlight.clearDirtyWorkingImageFlag()
        return self.fullDisplayImageCache

    def getZoomedRect(self):
        """ Get the portion of the fullDisplayImage that corresponds to the
        visible display. This function is also called from SpotlightCommand """
        workingImageWidth, workingImageHeight = Spotlight.getWorkingImageSize()
        logicalCorner = self.CalcUnscrolledPosition(0,0)
        zoomedCorner = (int(logicalCorner[0]/self.scale), int(logicalCorner[1]/self.scale))
        logicalOppositeCorner = self.CalcUnscrolledPosition(self.displayWidth, self.displayHeight)
        logicalSize = (logicalOppositeCorner[0]-logicalCorner[0], logicalOppositeCorner[1]-logicalCorner[1])
        zoomedSize = (int(math.ceil(logicalSize[0]/self.scale)), int(math.ceil(logicalSize[1]/self.scale)))
        zoomedRect = (zoomedCorner[0],
                                zoomedCorner[1],
                                min(zoomedSize[0],workingImageWidth-zoomedCorner[0]),
                                min(zoomedSize[1],workingImageHeight-zoomedCorner[1]))
        return zoomedRect

    def OnMouseRightDown(self, event):
        p = event.GetPosition()
        x, y = self.clientToImagePoint((p.x, p.y))
        Spotlight.aList.OnMouseRightDown((x, y))
        event.Skip()

    def OnMouseRightDClick(self, event):
        p = event.GetPosition()
        x, y = self.clientToImagePoint((p.x, p.y))
        Spotlight.aList.OnMouseRightDClick((x, y))
        event.Skip()

    def OnMouseLeftDown(self, event):
        p = event.GetPosition()
        x, y = self.clientToImagePoint((p.x, p.y))
        Spotlight.aList.OnMouseLeftDown((x, y))
        event.Skip()

    def OnMouseLeftUp(self, event):
        p = event.GetPosition()
        x, y = self.clientToImagePoint((p.x, p.y))
        Spotlight.aList.OnMouseLeftUp((x, y))
        event.Skip()

    def OnMouseMove(self, event):
        p = event.GetPosition()
        if Spotlight.workingImage:
            x, y = self.clientToImagePoint((p.x, p.y))
            w, h = Spotlight.getWorkingImageSize()
            if x >= 0 and x < w and y >= 0 and y < h:
                if not event.Dragging():
                    text = self.generateStatusBar1Text((x,y))
                    self.frame.updateStatusBar(text, 1) # status bar 1
            Spotlight.aList.OnMouseMove((x, y))
        event.Skip()

    def generateStatusBar1Text(self, p):
        'display pixel value under the cursor'
        if Spotlight.moving:  # prevents lock-up when while moving (fastForward)
            return ""

        if Spotlight.pOptions.programOptions['pixelValues'] == 0:
            r, g, b = Spotlight.getPixelNorm(p[0], p[1])
            if Spotlight.originalMode == 'RGB':
                value = 'rgb:(%.3f, %.3f, %.3f)' % (r, g, b)
            else:
                value = 'i:%f' % r
        else:
            r, g, b = Spotlight.getPixel(p[0], p[1])
            if Spotlight.originalMode == 'RGB':
                value = 'rgb:(%3d, %3d, %3d)' % (r, g, b)
            else:
                value = 'i:%3d' % r

        if Spotlight.scaleUserUnits == 1.0 and Spotlight.scalePixelUnits == 1.0:
            position =  '(%3d, %3d) ' % (p[0], p[1])
        else:
            x = p[0] * Spotlight.pixelScale
            y = p[1] * Spotlight.pixelScale
            position =  '(%.3f, %.3f) ' % (x, y)

        return position + value


    def clientToImagePoint(self, p):
        """ Note: just convert to int here - don't round before
        converting to int. This way x=0.6 belongs to pixel 0
        instead of pixel 1.
        """
        xf = int(float(p[0]) / self.scale)
        yf = int(float(p[1]) / self.scale)
        ox, oy = self.CalcUnscrolledPosition(0, 0)
        oxf = int(float(ox) / self.scale)
        oyf = int(float(oy) / self.scale)
        x = xf + oxf
        y = yf + oyf
        return (x, y)

    def imageToClientPoint(self, p):
        """ Note: just convert to int here - don't round before
        converting to int. This way x=0.6 belongs to pixel 0
        instead of pixel 1.
        """
        x1 = float(p[0]) * self.scale
        y1 = float(p[1]) * self.scale
        ox, oy = self.CalcScrolledPosition(0, 0)
        x1 = x1 + ox
        y1 = y1 + oy
        return (int(x1), int(y1))

    ##---------------------------------------

    def drawAoi(self, params, dc=None):
        """draws an Aoi"""

        if dc == None: # this dc can be None
            return
            #dc = wx.ClientDC(self)

        dc.SetLogicalFunction(wx.INVERT)
        color = wx.Colour()
        brush = wx.Brush(color, wx.TRANSPARENT)
        dc.SetBrush(brush)

        if params['highlight']:
            if params['thickness'] == 1:
                drawThickness = 2  # current aoi of thickness 1
            else:
                drawThickness = params['thickness'] # current aoi but thick
            pen2 = wx.Pen(color, drawThickness, wx.SOLID)
            pen2.SetCap(wx.CAP_BUTT) # square endpoints
            dc.SetPen(pen2)
        else:
            pen1 = wx.Pen(color, 1, wx.SOLID)
            pen1.SetCap(wx.CAP_BUTT) # square endpoints
            dc.SetPen(pen1)

        # constrain line
        if params.has_key('constrain'):
            pen1 = wx.Pen(color, 1, wx.DOT)
            dc.SetPen(pen1)

        # draw polylines
        if params.has_key('pointList'):
            # Note: pointList is list of lists
            for line in params['pointList']: # line may be polyline
                scaledPoints = []
                for p in line:
                    cPoint = self.imageToClientPoint(p)
                    scaledPoints.append(cPoint)
                if len(scaledPoints) > 1:
                    dc.DrawLines(scaledPoints)
            # add hangles to Aois
            if params['highlight']:
                if params.has_key('rectHandles'):
                    self.drawRectHandles(scaledPoints, dc)
                elif params.has_key('lineHandles'):
                    self.drawLineHandles(scaledPoints, dc)

    def drawRectHandles(self, scaledPoints, dc):
        'Draw handles around the corners of a rectangular Aoi.'
        # upper left
        x, y = scaledPoints[0]
        dc.DrawLine(x-1, y-2, x+4, y-2) # horiz line
        dc.DrawLine(x-2, y-3, x-2, y+4) # vert line
        # upper right
        x, y = scaledPoints[1]
        dc.DrawLine(x-4, y-2, x+1, y-2)
        dc.DrawLine(x+2, y-3, x+2, y+4)
        # lower right
        x, y = scaledPoints[2]
        dc.DrawLine(x-4, y+2, x+1, y+2)
        dc.DrawLine(x+2, y-4, x+2, y+3)
        # lower left
        x, y = scaledPoints[3]
        dc.DrawLine(x-1, y+2, x+4, y+2)
        dc.DrawLine(x-2, y-4, x-2, y+3)

    def drawLineHandles(self, scaledPoints, dc):
        'Draw handles at endpoints of a line Aoi'
        color = wx.Colour()
        brush = wx.Brush(color, wx.SOLID)
        dc.SetBrush(brush)
        pen1 = wx.Pen(color, 1, wx.SOLID)
        pen1.SetCap(wx.CAP_BUTT) # square endpoints
        dc.SetPen(pen1)
        x, y = scaledPoints[0]
        dc.DrawRectangle(x-3, y-3, 6, 6)
        x, y = scaledPoints[1]
        dc.DrawRectangle(x-3, y-3, 6, 6)

    def drawRedCross(self, center):
        'small red cross to indicate track point'
        dc = wx.ClientDC(self)
        color = wx.Colour(255, 0, 0)
        pen1 = wx.Pen(color, 1, wx.SOLID)
        dc.SetPen(pen1)
        x, y = self.imageToClientPoint(center)
        leg = 5
        dc.DrawLine(x-leg, y, x+leg, y)
        dc.DrawLine(x, y-leg, x, y+leg)

    def drawRedPoint(self, center):
        'used by the line following Aoi'
        dc = wx.ClientDC(self)
        color = wx.Colour(255, 0, 0)
        pen1 = wx.Pen(color)
        dc.SetPen(pen1)
        x, y = self.imageToClientPoint(center)
        dc.DrawPoint(x, y)

    def setBackgroundColor(self, bcolor):
        self.backgroundColor =  wx.Brush(bcolor)
        ebitmap = wx.EmptyBitmap(self.displayWidth, self.displayHeight)
        dc = wx.BufferedDC(wx.ClientDC(self), ebitmap)
        dc.SetBackground(self.backgroundColor)
        dc.Clear()
        if Spotlight.workingImage:
            Spotlight.setWorkingImage(Spotlight.workingImage)


###---------------------------------------------------

class SpotlightFrame(wx.Frame):
    def __init__(self, parent, ID, title):
        initialSize =  wx.Size(700, 590)
        wx.Frame.__init__(self, parent, ID, title, pos=(150, 150), size=initialSize)

        # Construct a StatusBar
        statusBar = self.CreateStatusBar(3)
        statusBar.SetStatusWidths([-1, 210, 140])

        ## Construct a ToolBar
        self.tb = self.CreateToolBar(wx.TB_HORIZONTAL|wx.NO_BORDER|wx.TB_FLAT)
        self.tb.SetToolBitmapSize((21,19)) # make buttons bigger than default 16x15

        wx.InitAllImageHandlers()
        openImg            = images.getOpenBitmap()
        saveAsImg          = images.getSaveAsBitmap()
        undoImg            = images.getUndoBitmap()
        redoImg            = images.getRedoBitmap()
        nextImg            = images.getNextBitmap()
        previousImg        = images.getPreviousBitmap()
        rewindImg          = images.getRewindBitmap()
        stepbackImg        = images.getStepbackBitmap()
        pauseImg           = images.getPauseBitmap()
        stepforwardImg     = images.getStepforwardBitmap()
        fastforwardImg     = images.getFastforwardBitmap()
        trackOneImg        = images.getTrackOneBitmap()
        trackContinuousImg = images.getTrackContinuousBitmap()
        zoomInImg          = images.getZoominBitmap()
        zoomOutImg         = images.getZoomoutBitmap()

        self.tb.AddSimpleTool(ID_FILE_OPEN, openImg, "Open image", "")
        wx.EVT_TOOL(self, ID_FILE_OPEN, self.OnOpen)
        self.tb.AddSimpleTool(ID_BUTTON_SAVEAS, saveAsImg, "Save As", "")
        wx.EVT_TOOL(self, ID_BUTTON_SAVEAS,  self.OnSave)
        self.tb.AddSeparator()
        self.tb.AddSimpleTool(ID_BUTTON_UNDO, undoImg, "Undo", "")
        wx.EVT_TOOL(self, ID_BUTTON_UNDO,  self.OnUndo)
        self.tb.AddSimpleTool(ID_BUTTON_REDO, redoImg, "Redo", "")
        wx.EVT_TOOL(self, ID_BUTTON_REDO,  self.OnRedo)
        self.tb.AddSeparator()
        self.tb.AddSimpleTool(ID_VIEW_ZOOM_IN, zoomInImg, "Zoom In", "")
        wx.EVT_TOOL(self, ID_VIEW_ZOOM_IN, self.OnZoomIn)
        self.tb.AddSimpleTool(ID_VIEW_ZOOM_OUT, zoomOutImg, "Zoom Out", "")
        wx.EVT_TOOL(self, ID_VIEW_ZOOM_OUT, self.OnZoomOut)
        self.tb.AddSeparator()
        self.tb.AddSimpleTool(ID_BUTTON_NEXT, nextImg, "Next Aoi", "")
        wx.EVT_TOOL(self, ID_BUTTON_NEXT,  self.OnNextAoi)
        self.tb.AddSimpleTool(ID_BUTTON_PREVIOUS, previousImg, "Previous Aoi", "")
        wx.EVT_TOOL(self, ID_BUTTON_PREVIOUS,  self.OnPreviousAoi)
        self.tb.AddSeparator()
        self.tb.AddSimpleTool(ID_BUTTON_REWIND, rewindImg, "Rewind", "")
        wx.EVT_TOOL(self, ID_BUTTON_REWIND,  self.OnRewind)
        self.tb.AddSimpleTool(ID_BUTTON_STEPBACK, stepbackImg, "Step back", "")
        wx.EVT_TOOL(self, ID_BUTTON_STEPBACK,  self.OnStepback)
        self.tb.AddSimpleTool(ID_BUTTON_PAUSE, pauseImg, "Stop/Pause", "")
        wx.EVT_TOOL(self, ID_BUTTON_PAUSE,  self.OnPause)
        self.tb.AddSimpleTool(ID_BUTTON_STEPFORWARD, stepforwardImg,  "Step forward", "")
        wx.EVT_TOOL(self, ID_BUTTON_STEPFORWARD,  self.OnStepforward)
        self.tb.AddSimpleTool(ID_BUTTON_FASTFORWARD, fastforwardImg, "Fast forward", "")
        wx.EVT_TOOL(self, ID_BUTTON_FASTFORWARD,  self.OnFastforward)
        self.tb.AddSeparator()
        self.tb.AddSimpleTool(ID_BUTTON_TRACK_ONE, trackOneImg,  "Track One", "")
        wx.EVT_TOOL(self, ID_BUTTON_TRACK_ONE,  self.OnTrackOne)
        self.tb.AddSimpleTool(ID_BUTTON_TRACK_CONTINUOUS,trackContinuousImg, "Track Continuous", "")
        wx.EVT_TOOL(self, ID_BUTTON_TRACK_CONTINUOUS,  self.OnTrackContinuous)
        wx.EVT_TOOL(self, ID_BUTTON_STOP, self.OnStop)
        self.tb.Realize()

        ## Construct a MenuBar
        self.menuBar = wx.MenuBar()
        ## Construct "File" menu
        self.menuFile = wx.Menu()
        self.menuFile.Append(ID_FILE_OPEN, "&Open","Open file")
        self.Bind(wx.EVT_MENU, self.OnOpen, id=ID_FILE_OPEN)
        wx.EVT_UPDATE_UI(self, ID_FILE_OPEN, self.OnOpenUpdate) # UI-Update
        self.menuFile.Append(ID_FILE_SAVEAS, "&Save As","Save file")
        self.Bind(wx.EVT_MENU, self.OnSave, id=ID_FILE_SAVEAS)
        self.menuFile.Append(ID_FILE_SAVEAOI, "&Save Aoi","")
        self.Bind(wx.EVT_MENU, self.OnSaveAoi, id=ID_FILE_SAVEAOI)

        if sys.platform != 'darwin': # File->Exit is bad form on a Mac
            self.menuFile.AppendSeparator()
            self.menuFile.Append(ID_FILE_EXIT, "E&xit", "Terminate the program")
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_FILE_EXIT)
        self.menuBar.Append(self.menuFile, "&File")

        ## Construct "View" menu
        self.menuView = wx.Menu()
        self.menuView.Append(ID_VIEW_IMAGEINFO, "&Image info...",
                             "display image info")
        self.Bind(wx.EVT_MENU, self.OnImageInfo, id=ID_VIEW_IMAGEINFO)
        self.menuView.AppendSeparator()
        self.menuView.Append(ID_VIEW_UNDO, "&Undo", "Undo last IP operation")
        self.Bind(wx.EVT_MENU, self.OnUndo, id=ID_VIEW_UNDO)
        self.menuView.Append(ID_VIEW_REDO, "&Redo", "Redo last IP operation")
        self.Bind(wx.EVT_MENU, self.OnRedo, id=ID_VIEW_REDO)
        self.menuView.AppendSeparator()
        self.menuView.Append(ID_VIEW_ZOOM_IN, "Zoom In",
            "Zoom In - each step is 2X")
        self.Bind(wx.EVT_MENU, self.OnZoomIn, id=ID_VIEW_ZOOM_IN)
        self.menuView.Append(ID_VIEW_ZOOM_OUT, "Zoom Out",
            "Zoom Out - each step is 0.5X")
        self.Bind(wx.EVT_MENU, self.OnZoomOut, id=ID_VIEW_ZOOM_OUT)
        self.menuView.Append(ID_VIEW_ZOOM_ORIGINAL, "Zoom Original",
            "Zoom Original - No zooming performed")
        self.Bind(wx.EVT_MENU, self.OnZoomOriginal, id=ID_VIEW_ZOOM_ORIGINAL)
        self.menuView.AppendSeparator()
        self.menuView.Append(ID_VIEW_SCALE, "&Scale...",
                             "convert pixels to units")
        self.Bind(wx.EVT_MENU, self.OnScale, id=ID_VIEW_SCALE)
        self.menuView.Append(ID_VIEW_FORCE_UPDATES, "Force update after every operation", "", 1)
        self.Bind(wx.EVT_MENU, self.OnForceUpdates, id=ID_VIEW_FORCE_UPDATES)
        self.menuView.Append(ID_VIEW_OPTIONS, "&Options...",
                             "display program options")
        self.Bind(wx.EVT_MENU, self.OnProgramOptions, id=ID_VIEW_OPTIONS)
        self.menuBar.Append(self.menuView, "&View")

        ## Construct "Transport" menu
        self.menuTransport = wx.Menu()
        self.menuTransport.Append(ID_TRANSPORT_GOTO_SPECIFIC, "&Goto specific frame...",
                                    "a quick way of going to a particular frame")
        self.Bind(wx.EVT_MENU, self.OnGotoSpecificFrame, id=ID_TRANSPORT_GOTO_SPECIFIC)
        self.menuTransport.AppendSeparator()
        self.menuTransport.Append(ID_TRANSPORT_REWIND, "&Rewind",
                                  "step backwards as fast as possible")
        self.Bind(wx.EVT_MENU, self.OnRewind, id=ID_TRANSPORT_REWIND)
        self.menuTransport.Append(ID_TRANSPORT_STEPBACK, "Step &back",
                                  "step back one frame")
        self.Bind(wx.EVT_MENU, self.OnStepback, id=ID_TRANSPORT_STEPBACK)
        self.menuTransport.Append(ID_TRANSPORT_PAUSE, "&Stop/Pause",
                                  "stop rewind or fast forward motion")
        self.Bind(wx.EVT_MENU, self.OnPause, id=ID_TRANSPORT_PAUSE)
        self.menuTransport.Append(ID_TRANSPORT_STEPFORWARD, "&Step forward",
                                  "step forward one frame")
        self.Bind(wx.EVT_MENU, self.OnStepforward, id=ID_TRANSPORT_STEPFORWARD)
        self.menuTransport.Append(ID_TRANSPORT_FASTFORWARD, "&Fast forward",
                                  "step forwards as fast as possible")
        self.Bind(wx.EVT_MENU, self.OnFastforward, id=ID_TRANSPORT_FASTFORWARD)
        self.menuTransport.AppendSeparator()
        self.menuTransport.Append(ID_TRANSPORT_NEXTSTEPOPTIONS, "&Next Step Options...",
                                  "brings up next step options dialog box")
        self.Bind(wx.EVT_MENU, self.OnNextStepOptions, id=ID_TRANSPORT_NEXTSTEPOPTIONS)
        self.menuBar.Append(self.menuTransport, "T&ransport")

        ## Construct "Aoi" menu
        self.menuAoi = wx.Menu()
        self.submenuAoiNew = wx.Menu()
        self.submenuAoiNew.Append(ID_AOI_RECTANGLE, "rectangle",
            "draw new rectangle")
        self.Bind(wx.EVT_MENU, self.OnNewRectangle, id=ID_AOI_RECTANGLE)
        self.submenuAoiNew.Append(ID_AOI_LINEPROFILE, "line profile",
            "draw new line profile")
        self.Bind(wx.EVT_MENU, self.OnNewLineProfile, id=ID_AOI_LINEPROFILE)
        self.submenuAoiNew.Append(ID_AOI_HISTOGRAM, "histogram",
            "draw new histogram")
        self.Bind(wx.EVT_MENU, self.OnNewHistogram, id=ID_AOI_HISTOGRAM)
        self.submenuAoiNew.Append(ID_AOI_ANGLETOOL, "angle tool", "")
        self.Bind(wx.EVT_MENU, self.OnNewAngleTool, id=ID_AOI_ANGLETOOL)
        self.submenuAoiNew.Append(ID_AOI_ABELTOOL, "abel transform tool", "")
        self.Bind(wx.EVT_MENU, self.OnNewAbelTool, id=ID_AOI_ABELTOOL)
        self.submenuAoiNew.AppendSeparator()
        self.submenuAoiNew.Append(ID_AOI_MANUAL, "manual tracking",
            "user manually specifies track point")
        self.Bind(wx.EVT_MENU, self.OnNewManualTracking, id=ID_AOI_MANUAL)
        self.submenuAoiNew.Append(ID_AOI_THRESHOLDTRACK,
            "threshold tracking", "")
        self.Bind(wx.EVT_MENU, self.OnNewThresholdTracking, id=ID_AOI_THRESHOLDTRACK)
        self.submenuAoiNew.Append(ID_AOI_CENTER, "center tracking", "")
        self.Bind(wx.EVT_MENU, self.OnNewCenterTracking, id=ID_AOI_CENTER)
        self.submenuAoiNew.Append(ID_AOI_LOCAL_MAX, "local maximum tracking", "")
        self.Bind(wx.EVT_MENU, self.OnNewMaximumTracking, id=ID_AOI_LOCAL_MAX)
        self.submenuAoiNew.Append(ID_AOI_SNAKE, "snake tracking",
            "tracking using active contours")
        self.Bind(wx.EVT_MENU, self.OnNewSnakeTracking, id=ID_AOI_SNAKE)
        self.submenuAoiNew.Append(ID_AOI_LINEFOLLOW, "line following",
            "user manually specifies line to follow")
        self.Bind(wx.EVT_MENU, self.OnNewLineFollowing, id=ID_AOI_LINEFOLLOW)
        self.menuAoi.AppendMenu(ID_AOI_NEWAOI, '&New', self.submenuAoiNew, 'new aois')
        self.menuAoi.Append(ID_AOI_DELETECURRENTAOI, "&Delete", "delete current Aoi")
        self.Bind(wx.EVT_MENU, self.OnDeleteCurrentAoi, id=ID_AOI_DELETECURRENTAOI)
        self.menuAoi.Append(ID_AOI_DELETEALLAOIS, "Delete &All", "delete All")
        self.Bind(wx.EVT_MENU, self.OnDeleteAll, id=ID_AOI_DELETEALLAOIS)
        self.menuAoi.AppendSeparator()
        self.menuAoi.Append(ID_AOI_NEXT, "&Next", "next Aoi")
        self.Bind(wx.EVT_MENU, self.OnNextAoi, id=ID_AOI_NEXT)
        self.menuAoi.Append(ID_AOI_PREVIOUS, "&Previous", "previous Aoi")
        self.Bind(wx.EVT_MENU, self.OnPreviousAoi, id=ID_AOI_PREVIOUS)
        self.menuAoi.AppendSeparator()
        self.menuAoi.Append(ID_AOI_SETPOSITION, "&Set Position...",
            "manually set aoi position")
        self.Bind(wx.EVT_MENU, self.OnAoiSetPosition, id=ID_AOI_SETPOSITION)
        self.menuAoi.Append(ID_AOI_OPTIONS, "Aoi &Options... (key 'o')",
            "tracking aoi options")
        self.Bind(wx.EVT_MENU, self.OnAoiOptions, id=ID_AOI_OPTIONS)
        self.menuAoi.Append(ID_AOI_PROCSEQUENCE, "Process Se&quence...",
            "bring up IP Sequence dialog")
        self.Bind(wx.EVT_MENU, self.OnProcSequence, id=ID_AOI_PROCSEQUENCE)
        self.menuAoi.Append(ID_AOI_UPDATE, "&Update   (key 'u')",
            "executes items in the IP Sequence list and tracks current frame")
        self.Bind(wx.EVT_MENU, self.OnUpdate, id=ID_AOI_UPDATE)
        self.menuBar.Append(self.menuAoi, "&Aoi")

        ## Construct "Process" menu
        self.menuProcess = wx.Menu()
        self.menuProcess.Append(ID_PROCESS_THRESHOLD, "&Threshold...", "threshold")
        self.Bind(wx.EVT_MENU, self.OnThreshold, id=ID_PROCESS_THRESHOLD)
        self.menuProcess.Append(ID_PROCESS_FILTER, "&Filter...", "filter")
        self.Bind(wx.EVT_MENU, self.OnFilter, id=ID_PROCESS_FILTER)
        self.menuProcess.Append(ID_PROCESS_ARITHMETIC, "&Arithmetic...",
            "arithmetic functions")
        self.Bind(wx.EVT_MENU, self.OnArithmetic, id=ID_PROCESS_ARITHMETIC)
        self.menuProcess.Append(ID_PROCESS_CONTRAST, "&Contrast...",
            "contrast stretching functions")
        self.Bind(wx.EVT_MENU, self.OnContrast, id=ID_PROCESS_CONTRAST)
        self.menuProcess.Append(ID_PROCESS_MORPHOLOGICAL, "&Morphological...",
            "binary morphological functions")
        self.Bind(wx.EVT_MENU, self.OnMorphological, id=ID_PROCESS_MORPHOLOGICAL)
        self.menuProcess.Append(ID_PROCESS_EXTRACTPLANE, "&Extract Plane...",
            "extract plane")
        self.Bind(wx.EVT_MENU, self.OnExtractPlane, id=ID_PROCESS_EXTRACTPLANE)
        self.menuProcess.Append(ID_PROCESS_GEOMETRIC, "&Geometric...", "rotate")
        self.Bind(wx.EVT_MENU, self.OnGeometric, id=ID_PROCESS_GEOMETRIC)
        self.menuProcess.Append(ID_PROCESS_STATISTICS, "&Statistics...",
            "image statistics")
        self.Bind(wx.EVT_MENU, self.OnStatistics, id=ID_PROCESS_STATISTICS)
        self.menuProcess.Append(ID_PROCESS_SAVEAOI, "Sa&ve Aoi...","")
        self.Bind(wx.EVT_MENU, self.OnProcessSaveAoi, id=ID_PROCESS_SAVEAOI)
        self.menuProcess.Append(ID_PROCESS_EXTRACTFIELD, "E&xtract Field...",
            "extract odd or even field")
        self.Bind(wx.EVT_MENU, self.OnExtractField, id=ID_PROCESS_EXTRACTFIELD)
        self.menuProcess.AppendSeparator()
        self.menuProcess.Append(ID_PROCESS_PSEUDOCOLOR, "&Pseudocolor...",
            "pseudocolor functions")
        self.Bind(wx.EVT_MENU, self.OnPseudocolor, id=ID_PROCESS_PSEUDOCOLOR)
        self.menuProcess.Append(ID_PROCESS_CONVERT, "&Convert Image...",
            "Converts grayscale image to RGB and back")
        self.Bind(wx.EVT_MENU, self.OnConvertImage, id=ID_PROCESS_CONVERT)
        self.menuProcess.Append(ID_PROCESS_RESIZE, "&Resize Image...",
            "chage size of the image")
        self.Bind(wx.EVT_MENU, self.OnResizeImage, id=ID_PROCESS_RESIZE)
        self.menuBar.Append(self.menuProcess, "&Process")

        ## Construct "Track" menu
        self.menuTrack = wx.Menu()
        self.menuTrack.Append(ID_TRACK_ONE, "&Track One", "Track one")
        self.Bind(wx.EVT_MENU, self.OnTrackOne, id=ID_TRACK_ONE)
        self.menuTrack.Append(ID_TRACK_CONTINUOUS, "Track &Continuous",
            "Track continuous")
        self.Bind(wx.EVT_MENU, self.OnTrackContinuous, id=ID_TRACK_CONTINUOUS)
        self.menuTrack.AppendSeparator()
        self.menuTrack.Append(ID_TRACK_RESULTSFILE, "&Results File...",
            "saves data to file")
        self.Bind(wx.EVT_MENU, self.OnResultsFile, id=ID_TRACK_RESULTSFILE)
        self.menuBar.Append(self.menuTrack, "&Track")

        ## Construct "Help" menu
        self.menuHelp = wx.Menu()
        self.menuHelp.Append(ID_HELP_DOCUMENTATION, "&View Documentation...",
            "PDF file document")
        self.Bind(wx.EVT_MENU, self.OnViewDocumentation, id=ID_HELP_DOCUMENTATION)
        self.menuHelp.Append(ID_HELP_NEW, "&New since last release...",
            "shows what has been added")
        self.Bind(wx.EVT_MENU, self.OnNewSinceLastRelease, id=ID_HELP_NEW)
        self.menuHelp.Append(ID_HELP_ABOUT, "&About Spotlight...",
            "about this program")
        self.Bind(wx.EVT_MENU, self.OnAboutSpotlight, id=ID_HELP_ABOUT)

        self.menuBar.Append(self.menuHelp, "&Help")

        # Add all the menus to the Menu Bar
        self.SetMenuBar(self.menuBar)

        # Recent file history menu handlers
        wx.EVT_MENU(self, ID_FILE_RECENT0, self.OnRecentFile)
        wx.EVT_MENU(self, ID_FILE_RECENT1, self.OnRecentFile)
        wx.EVT_MENU(self, ID_FILE_RECENT2, self.OnRecentFile)
        wx.EVT_MENU(self, ID_FILE_RECENT3, self.OnRecentFile)
        wx.EVT_MENU(self, ID_FILE_RECENT4, self.OnRecentFile)
        wx.EVT_MENU(self, ID_FILE_RECENT5, self.OnRecentFile)
        wx.EVT_MENU(self, ID_FILE_RECENT6, self.OnRecentFile)
        wx.EVT_MENU(self, ID_FILE_RECENT7, self.OnRecentFile)
        wx.EVT_MENU(self, ID_FILE_RECENT8, self.OnRecentFile)

        # called when frame is closed - with menu->Exit or clicking X button
        wx.EVT_CLOSE(self, self.OnCloseWindow)

        #--- Initialize Parameters ---
        self.iPanel = ImagePanel(self, -1)
        SpotlightDialog.setFrame(self)
        self.iRecent = RecentFiles(self)
        if sys.platform == 'win32':
            self.iPanel.setBackgroundColor(Spotlight.pOptions.programOptions['backgroundColor'])
        self.stopButtonShowing = False

        # Set icon. Note: the image (spotlightSmall.xpm) from which the icon
        # was generated was scaled down to 16x16 but the full size 32x32 icon
        # would also work (wxPython scales it down).
        if sys.platform != 'darwin':
            icon = images.getSpotlightSmallIcon()  # wxPython demo icon
            self.SetIcon(icon)


    def EnableMenuBar(self, flag):
        """
        Enable/disable the menubar. This is used when the Abel Aoi is opened
        to prevent any dialogs to pop up because they would show up behind
        the Abel window (which is a frame set to be ALWAYS_ON_TOP).
        """
        menubar = self.GetMenuBar()
        menubar.EnableTop(0, flag)
        menubar.EnableTop(1, flag)
        menubar.EnableTop(2, flag)
        menubar.EnableTop(3, flag)
        menubar.EnableTop(4, flag)
        menubar.EnableTop(5, flag)
        menubar.EnableTop(6, flag)

    def OnOpenUpdate(self, event):
        'updates image depended menus'
        self.updateWidgets()

    def updateWidgets(self):
        self.menuFile.Enable(ID_FILE_SAVEAS, Spotlight.imageLoaded)
        self.menuFile.Enable(ID_FILE_SAVEAOI, Spotlight.imageLoaded)
        self.menuView.Enable(ID_VIEW_IMAGEINFO, Spotlight.imageLoaded)
        self.menuView.Enable(ID_VIEW_ZOOM_ORIGINAL, Spotlight.imageLoaded)
        self.menuView.Enable(ID_VIEW_SCALE, Spotlight.imageLoaded)
        self.menuAoi.Enable(ID_AOI_PROCSEQUENCE, Spotlight.imageLoaded)
        self.menuAoi.Enable(ID_AOI_UPDATE, Spotlight.imageLoaded)
        self.menuTransport.Enable(ID_TRANSPORT_NEXTSTEPOPTIONS, Spotlight.imageLoaded)
        self.menuAoi.Enable(ID_AOI_NEWAOI, Spotlight.imageLoaded)
        self.menuProcess.Enable(ID_PROCESS_THRESHOLD, Spotlight.imageLoaded)
        self.menuProcess.Enable(ID_PROCESS_FILTER, Spotlight.imageLoaded)
        self.menuProcess.Enable(ID_PROCESS_ARITHMETIC, Spotlight.imageLoaded)
        self.menuProcess.Enable(ID_PROCESS_EXTRACTPLANE, Spotlight.imageLoaded)
        self.menuProcess.Enable(ID_PROCESS_CONTRAST, Spotlight.imageLoaded)
        self.menuProcess.Enable(ID_PROCESS_MORPHOLOGICAL, Spotlight.imageLoaded)
        self.menuProcess.Enable(ID_PROCESS_GEOMETRIC, Spotlight.imageLoaded)
        self.menuProcess.Enable(ID_PROCESS_STATISTICS, Spotlight.imageLoaded)
        self.menuProcess.Enable(ID_PROCESS_SAVEAOI, Spotlight.imageLoaded)
        self.menuProcess.Enable(ID_PROCESS_EXTRACTFIELD, Spotlight.imageLoaded)

        # Transport related
        p = True # next
        n = True # previous
        avi = False # avi file
        if Spotlight.previousfile == "":
            p = False
        if Spotlight.nextfile == "":
            n = False
        if Spotlight.fileType == 'AVI':
            avi = True
        self.menuTransport.Enable(ID_TRANSPORT_REWIND, Spotlight.imageLoaded and p)
        self.menuTransport.Enable(ID_TRANSPORT_STEPBACK, Spotlight.imageLoaded and p)
        self.menuTransport.Enable(ID_TRANSPORT_PAUSE, Spotlight.imageLoaded and (n or p))
        self.menuTransport.Enable(ID_TRANSPORT_STEPFORWARD, Spotlight.imageLoaded and n)
        self.menuTransport.Enable(ID_TRANSPORT_FASTFORWARD, Spotlight.imageLoaded and n)
        self.menuTransport.Enable(ID_TRANSPORT_GOTO_SPECIFIC, Spotlight.imageLoaded and avi)

        # Create True/False flag for whether more than one aoi exists
        if Spotlight.aList.getAoiListLength() > 1:
            moreThanOne = True
        else:
            moreThanOne = False
        self.menuAoi.Enable(ID_AOI_NEXT, Spotlight.imageLoaded and moreThanOne)
        self.menuAoi.Enable(ID_AOI_PREVIOUS, Spotlight.imageLoaded and moreThanOne)

        # Create True/False flag for whether more than two aoi exists
        # Note: one aoi is always the AoiWholeImage
        if Spotlight.aList.getAoiListLength() > 2:
            moreThanTwo = True
        else:
            moreThanTwo = False
        self.menuAoi.Enable(ID_AOI_DELETEALLAOIS, Spotlight.imageLoaded and moreThanTwo)

        # UndoRedo
        undoredo = False
        if len(Spotlight.aList.urList) > 0:
            undoredo = True
        undo = False
        if Spotlight.aList.lastExecuted > -1:
            undo = True
        self.menuView.Enable(ID_VIEW_UNDO, undoredo and undo)
        self.menuView.Enable(ID_VIEW_REDO, undoredo and Spotlight.aList.allowRedo)

        # Track related
        a = False # aoi not exists
        if Spotlight.aList.getAoiListLength() > 0:
            a = True
        self.menuTrack.Enable(ID_TRACK_ONE, Spotlight.imageLoaded and a and n)
        self.menuTrack.Enable(ID_TRACK_CONTINUOUS, Spotlight.imageLoaded and a and n)

        # Aoi dependent widgets
        aoi = Spotlight.aList.getCurrentAoi()
        if aoi:
            self.menuAoi.Enable(ID_AOI_OPTIONS, aoi.aoiOptionsPresent())
            self.menuAoi.Enable(ID_AOI_DELETECURRENTAOI, not aoi.isWholeImageAoi())
            self.menuAoi.Enable(ID_AOI_SETPOSITION, not aoi.isWholeImageAoi())
            self.menuProcess.Enable(ID_PROCESS_PSEUDOCOLOR, aoi.isWholeImageAoi())
            self.menuProcess.Enable(ID_PROCESS_RESIZE, aoi.isWholeImageAoi())
            self.menuProcess.Enable(ID_PROCESS_CONVERT, aoi.isWholeImageAoi())
        else:
            self.menuAoi.Enable(ID_AOI_OPTIONS, False)
            self.menuAoi.Enable(ID_AOI_DELETECURRENTAOI, False)
            self.menuAoi.Enable(ID_AOI_SETPOSITION, False)
            self.menuProcess.Enable(ID_PROCESS_PSEUDOCOLOR, False)
            self.menuProcess.Enable(ID_PROCESS_RESIZE, False)
            self.menuProcess.Enable(ID_PROCESS_CONVERT, False)

        # Zoom related
        zoomin = True
        if self.iPanel.scale > 64:
            zoomin = False
        self.menuView.Enable(ID_VIEW_ZOOM_IN, Spotlight.imageLoaded and zoomin)
        zoomout = True
        if self.iPanel.scale < 0.0625:
            zoomout = False
        self.menuView.Enable(ID_VIEW_ZOOM_OUT, Spotlight.imageLoaded and zoomout)

        if Spotlight.tracking:
            pass
        elif self.stopButtonShowing:
            pass
        else:
            toolbarButtons = {}
            toolbarButtons['open'] = True
            toolbarButtons['saveAs'] = Spotlight.imageLoaded
            toolbarButtons['undo'] = undoredo and undo
            toolbarButtons['redo'] = undoredo and Spotlight.aList.allowRedo
            toolbarButtons['zoomin'] = Spotlight.imageLoaded and zoomin
            toolbarButtons['zoomout'] = Spotlight.imageLoaded and zoomout
            toolbarButtons['nextAoi'] = Spotlight.imageLoaded and moreThanOne
            toolbarButtons['previousAoi'] = Spotlight.imageLoaded and moreThanOne
            toolbarButtons['rewind'] = Spotlight.imageLoaded and p
            toolbarButtons['stepback'] = Spotlight.imageLoaded and p
            toolbarButtons['pause'] = Spotlight.imageLoaded and (n or p)
            toolbarButtons['stepforward'] = Spotlight.imageLoaded and n
            toolbarButtons['fastforward'] = Spotlight.imageLoaded and n
            toolbarButtons['trackOne'] = Spotlight.imageLoaded and a and n
            toolbarButtons['trackContinuous'] = Spotlight.imageLoaded and a and n
            self.setToolbarButtons(toolbarButtons)

    def setToolbarButtons(self, buttons):
        """enable/disable buttons from values passed in"""
        self.tb.EnableTool(ID_FILE_OPEN, buttons['open'])
        self.tb.EnableTool(ID_BUTTON_SAVEAS, buttons['saveAs'])
        self.tb.EnableTool(ID_BUTTON_UNDO, buttons['undo'])
        self.tb.EnableTool(ID_BUTTON_REDO, buttons['redo'])
        self.tb.EnableTool(ID_VIEW_ZOOM_IN, buttons['zoomin'])
        self.tb.EnableTool(ID_VIEW_ZOOM_OUT, buttons['zoomout'])
        self.tb.EnableTool(ID_BUTTON_NEXT, buttons['nextAoi'])
        self.tb.EnableTool(ID_BUTTON_PREVIOUS, buttons['previousAoi'])
        self.tb.EnableTool(ID_BUTTON_REWIND, buttons['rewind'])
        self.tb.EnableTool(ID_BUTTON_STEPBACK, buttons['stepback'])
        self.tb.EnableTool(ID_BUTTON_PAUSE, buttons['pause'])
        self.tb.EnableTool(ID_BUTTON_STEPFORWARD, buttons['stepforward'])
        self.tb.EnableTool(ID_BUTTON_FASTFORWARD, buttons['fastforward'])
        self.tb.EnableTool(ID_BUTTON_TRACK_ONE, buttons['trackOne'])
        if self.stopButtonShowing == False:
            self.tb.EnableTool(ID_BUTTON_TRACK_CONTINUOUS, buttons['trackContinuous'])

    def showStopButton(self):
        'change the Track Continuous button to Stop button'
        if self.stopButtonShowing == False:
            self.tb.DeleteTool(ID_BUTTON_TRACK_CONTINUOUS)
            self.tb.AddSimpleTool(ID_BUTTON_STOP, images.getStopBitmap(), "Stop", "")
            self.tb.Realize()
            self.stopButtonShowing = True
            toolbarButtons = self.getDisabledToolbar()
            self.setToolbarButtons(toolbarButtons)

    def removeStopButton(self):
        'change the Stop button to Track Continuous button'
        if self.stopButtonShowing:
            self.tb.DeleteTool(ID_BUTTON_STOP)
            self.tb.AddSimpleTool(ID_BUTTON_TRACK_CONTINUOUS,
                                  images.getTrackContinuousBitmap(), "Track Continuous", "")
            self.tb.Realize()
            self.stopButtonShowing = False
            self.updateWidgets()

    def getDisabledToolbar(self):
        """For now just disable all. Eventually this function
        can be modified to enable some and disable others."""
        toolbarButtons = {}
        toolbarButtons['open'] = False
        toolbarButtons['saveAs'] = False
        toolbarButtons['undo'] = False
        toolbarButtons['redo'] = False
        toolbarButtons['zoomin'] = False
        toolbarButtons['zoomout'] = False
        toolbarButtons['nextAoi'] = False
        toolbarButtons['previousAoi'] = False
        toolbarButtons['rewind'] = False
        toolbarButtons['stepback'] = False
        toolbarButtons['pause'] = False
        toolbarButtons['stepforward'] = False
        toolbarButtons['fastforward'] = False
        toolbarButtons['trackOne'] = False
        toolbarButtons['trackContinuous'] = False
        return toolbarButtons

    ##-------------------- File functions ------------------------------------

    def OnOpen(self, event):
        fileTypes = Spotlight.getImageFileFilter('wxOPEN')
        path = Spotlight.pOptions.programOptions['latestLoadPath'] # persitent path
        dir, file = os.path.split(path)
        fd = wx.FileDialog(self, "Open Image", dir, file, fileTypes, wx.OPEN)
        if fd.ShowModal() == wx.ID_OK:
            path = fd.GetPath()
            self.openImageFile(path)
            Spotlight.pOptions.setLatestLoadPath(path) # persitent path
        fd.Destroy()

    def openImageFile(self, path):
        'performs GUI related operations in loading an image file'
        Spotlight.setLastFile(Spotlight.currentfile)
        name, ext = os.path.splitext(path)
        if ext == '.avi' or ext == '.AVI' or ext == '.mov' or ext == '.MOV':
            Spotlight.setImageType('AVI')
        else:
            Spotlight.setImageType('IMG')

        file = Spotlight.getExtendedFilename(path)
        Spotlight.setCurrentFile(file)
        noproblem = Spotlight.loadImage(Spotlight.currentfile)
        if noproblem:
            self.iRecent.setNewFile(path)
            s = Spotlight.stepsize
            Spotlight.setNextFile(Spotlight.getNextFilename(s))
            Spotlight.setPreviousFile(Spotlight.getNextFilename(-s))
        else:
            if not os.path.isfile(path):
                self.messageDialog('file does not exist')

    def OnSave(self, event):
        fileTypes = Spotlight.getImageFileFilter('wxSAVE')
        path = Spotlight.pOptions.programOptions['latestSavePath'] # persitent path
        dir, file = os.path.split(path)
        fd = wx.FileDialog(self, "Save Image", dir, file, fileTypes, wx.SAVE)

        if fd.ShowModal() == wx.ID_OK:
            imageExists = os.path.isfile(fd.GetPath())
            if imageExists:
                message = 'The file already exists - do you want to overwrite it?'
                overwriteFlag = SpotlightDialog.YesNoDialog(message)
                if overwriteFlag:
                    path = fd.GetPath()
                    Spotlight.saveImage(Spotlight.workingImage, path)
                    Spotlight.pOptions.setLatestSavePath(path) # persitent path
            else:
                path = fd.GetPath()
                Spotlight.saveImage(Spotlight.workingImage, path)
                Spotlight.pOptions.setLatestSavePath(path) # persitent path
        fd.Destroy()

    def OnSaveAoi(self, event):
        aoi = Spotlight.aList.getCurrentAoi()
        if aoi:
            aoiImage = aoi.getAoiImage()
            fileTypes = Spotlight.getImageFileFilter('wxSAVE')
            path = Spotlight.pOptions.programOptions['latestSavePath'] # persitent path
            dir, file = os.path.split(path)
            fd = wx.FileDialog(self, "Save Image", dir, file, fileTypes, wx.SAVE)

            if fd.ShowModal() == wx.ID_OK:
                imageExists = os.path.isfile(fd.GetPath())
                if imageExists:
                    message = 'The file already exists - do you want to overwrite it?'
                    overwriteFlag = SpotlightDialog.YesNoDialog(message)
                    if overwriteFlag:
                        path = fd.GetPath()
                        Spotlight.saveImage(aoiImage, path)
                        Spotlight.pOptions.setLatestSavePath(path) # persitent path
                else:
                    path = fd.GetPath()
                    Spotlight.saveImage(aoiImage, path)
                    Spotlight.pOptions.setLatestSavePath(path) # persitent path
            fd.Destroy()

    def OnRecentFile(self, event):
        'this gets executed when any of the recent image file menus gets selected'
        id = event.GetId()
        i = id - int(ID_FILE_RECENT0)
        file = self.iRecent.getRecentFile(i)
        self.openImageFile(file)

    def OnCloseWindow(self, event):
        self.iRecent.saveRecentFilesList()  # save to disk
        # make sure that tracking cycle has run its course, otherwise don't
        # let it destroy window
        if self.stopButtonShowing:
            return
        self.Destroy()

    def OnExit(self, event):
        self.Close(True)

    ##----------------------- View functions ----------------------------------

    def OnImageInfo(self, event):
        Spotlight.OnImageInfo()

    def OnUndo(self, event):
        Spotlight.aList.undo()

    def OnRedo(self, event):
        """
        The showStopButton and removeStopButton are only needed for the
        ManualTracking or LineFollowing aoi's when you try to REDO a
        previously selected Aoi->Update command.
        """
        aoi = Spotlight.aList.getCurrentAoi()
        Spotlight.aList.redo()

    def OnZoomIn(self, event):
        self.iPanel.Zoom(+1)
        self.iPanel.Refresh()

    def OnZoomOut(self, event):
        self.iPanel.Zoom(-1)
        self.iPanel.Refresh()

    def OnZoomOriginal(self, event):
        self.iPanel.Zoom(0)
        self.iPanel.Refresh()

    def OnScale(self, event):
        Spotlight.OnScale()

    def OnForceUpdates(self, event):
        if Spotlight.forceEveryOperationToRedisplay:
            Spotlight.setForceEveryOperationToRedisplay(0)
            self.menuView.Check(ID_VIEW_FORCE_UPDATES, 0)
        else:
            Spotlight.setForceEveryOperationToRedisplay(1)
            self.menuView.Check(ID_VIEW_FORCE_UPDATES, 1)

    def OnProgramOptions(self, event):
        Spotlight.OnProgramOptions()

    ##---------------- Transport functions -------------------------------------

    def OnGotoSpecificFrame(self, event):
        Spotlight.OnGotoSpecificFrame()

    def OnRewind(self, event):
        Spotlight.Rewind()

    def OnStepback(self, event):
        Spotlight.Stepback()

    def OnPause(self, event):
        Spotlight.Pause()

    def OnStepforward(self, event):
        Spotlight.Stepforward()

    def OnFastforward(self, event):
        Spotlight.Fastforward()

    def OnNextStepOptions(self, event):
        Spotlight.OnNextStepOptions()

    ##-------------------- AOI functions ----------------------------------

    def OnNewRectangle(self, event):
        Spotlight.OnNewRectangle()

    def OnNewLineProfile(self, event):
        Spotlight.OnNewLineProfile()

    def OnNewHistogram(self, event):
        Spotlight.OnNewHistogram()

    def OnNewAngleTool(self, event):
        Spotlight.OnNewAngleTool()

    def OnNewAbelTool(self, event):
        Spotlight.OnNewAbelTool()

    def OnNewManualTracking(self, event):
        Spotlight.OnNewManualTracking()

    def OnNewThresholdTracking(self, event):
        Spotlight.OnNewThresholdTracking()

    def OnNewCenterTracking(self, event):
        Spotlight.OnNewCenterTracking()

    def OnNewMaximumTracking(self, event):
        Spotlight.OnNewMaximumTracking()

    def OnNewSnakeTracking(self, event):
        Spotlight.OnNewSnakeTracking()

    def OnNewLineFollowing(self, event):
        Spotlight.OnNewLineFollowing()

    def OnDeleteCurrentAoi(self, event):
        Spotlight.DeleteCurrentAoi()

    def OnDeleteAll(self, event):
        Spotlight.DeleteAll()

    def OnNextAoi(self, event):
        Spotlight.NextAoi()

    def OnPreviousAoi(self, event):
        Spotlight.PreviousAoi()

    def OnAoiSetPosition(self, event):
        Spotlight.OnAoiSetPosition()

    def OnProcSequence(self, event):
        Spotlight.OnProcSequence()

    def OnAoiOptions(self, event):
        Spotlight.OnAoiOptions()

    def OnUpdate(self, event):
        Spotlight.OnUpdate()

    def deleteAoiFromOnCancel(self):
        '--- called when modeless dialog is closed using a cancel button ---'
        Spotlight.deleteAoiFromOnCancel()

    #-------------------- Process functions ------------------------------

    #~ def OnTest(self, event):
        #~ Spotlight.OnTest()

    def OnThreshold(self, event):
        Spotlight.OnThreshold()

    def OnFilter(self, event):
        Spotlight.OnFilter()

    def OnArithmetic(self, event):
        Spotlight.OnArithmetic()

    def OnContrast(self, event):
        Spotlight.OnContrast()

    def OnMorphological(self, event):
        Spotlight.OnMorphological()

    def OnExtractPlane(self, event):
        Spotlight.OnExtractPlane()

    def OnExtractField(self, event):
        Spotlight.OnExtractField()

    def OnGeometric(self, event):
        Spotlight.OnGeometric()

    def OnStatistics(self, event):
        Spotlight.OnStatistics()

    def OnProcessSaveAoi(self, event):
        Spotlight.OnProcessSaveAoi()

    def OnPseudocolor(self, event):
        Spotlight.OnPseudocolor()

    def OnConvertImage(self, event):
        Spotlight.OnConvertImage()

    def OnResizeImage(self, event):
        Spotlight.OnResizeImage()

#----------------------- Track functions ---------------------------------------

    def OnTrackOne(self, event):
        Spotlight.OnTrackOne()

    def OnTrackContinuous(self, event):
        Spotlight.OnTrackContinuous()

    def OnResultsFile(self, event):
        Spotlight.OnResultsFile()

    def OnStop(self, event):
        Spotlight.OnStop()

#-------------------- Help functions ----------------------------------

    def OnViewDocumentation(self, event):
        Spotlight.OnViewDocumentation()

    def OnNewSinceLastRelease(self, event):
        Spotlight.OnNewSinceLastRelease()

    def OnAboutSpotlight(self, event):
        Spotlight.OnAboutSpotlight()


    #### override the dummy versions of these functions: #####

    def updateStatusBar(self, text, num):
        self.SetStatusText(text, num)

    def messageDialog(self, message, title='standard message'):
        'display a Message message dialog'
        SpotlightDialog.messageDialog(message, title)

    def YesNoDialog(self, message, title='Yes or No'):
        'display a Message message dialog'
        return SpotlightDialog.YesNoDialog(message, title)

    def infoBox(self, message, xsize=400, ysize=380, title = 'InfoBox'):
        SpotlightDialog.infoBox(message, xsize, ysize, title)

    def setWindowTitle(self, title):
        self.SetTitle(title)

    def Yield(self):
        wx.GetApp().Yield()

    def setCursor(self, type):
        if type == 'hourglass':
            self.SetCursor(wx.HOURGLASS_CURSOR)
        else:
            self.SetCursor(wx.STANDARD_CURSOR)

    def showModalDialog(self, type, params={}, parent = None):
        if type == 'wxFileDialog':
            params = SpotlightDialog.showWxFileDialog(params)
            return params
        elif type == 'Threshold':
            params = SpotlightDialog.showThresholdDialog(params, parent)
            return params
        elif type == 'AdaptiveThreshold':
            params = SpotlightDialog.showAdaptiveThresholdDialog(params, parent)
            return params
        elif type == 'Filter':
            params = SpotlightDialog.showFilterDialog(params)
            return params
        elif type == 'IpSequence':
            params = SpotlightDialog.showIpSequenceDialog(params)
            return params
        elif type == 'ThresholdTrackingOptions':
            params = SpotlightDialog.showThresholdTrackingOptionsDialog(params)
            return params
        elif type == 'TrackingResultsDialog':
            params = SpotlightDialog.showTrackingResultsDialog(params)
            return params
        elif type == 'StandardAoiPosition':
            params = SpotlightDialog.showStandardAoiPositionDialog(params)
            return params
        elif type == 'Statistics':
            params = SpotlightDialog.showStatisticsDialog(params)
            return params
        elif type == 'Pseudocolor':
            params = SpotlightDialog.showPseudocolorDialog(params)
            return params
        elif type == 'ProgramOptions':
            params = SpotlightDialog.showProgramOptionsDialog(params)
            return params
        elif type == 'NextStepOptions':
            params = SpotlightDialog.showNextStepOptionsDialog(params)
            return params
        elif type == 'AngleToolOptions':
            params = SpotlightDialog.showAngleToolOptionsDialog(params, parent)
            return params
        elif type == 'Geometric':
            params = SpotlightDialog.showGeometricDialog(params)
            return params
        elif type == 'AbelFileLoad':
            params = SpotlightDialog.showAbelFileLoadDialog(params)
            return params
        elif type == 'AbelToolAoiPosition':
            params = SpotlightDialog.showAbelToolAoiPositionDialog(params, parent)
            return params
        elif type == 'ConvertImage':
            params = SpotlightDialog.showConvertImageDialog(params)
            return params
        elif type == 'Arithmetic':
            params = SpotlightDialog.showArithmeticDialog(params)
            return params
        elif type == 'Contrast':
            params = SpotlightDialog.showContrastDialog(params)
            return params
        elif type == 'ExtractPlane':
            params = SpotlightDialog.showExtractPlaneDialog(params)
            return params
        elif type == 'SaveAoi':
            params = SpotlightDialog.showSaveAoiDialog(params)
            return params
        elif type == 'SnakeOptions':
            params = SpotlightDialog.showSnakeOptionsDialog(params, parent)
            return params
        elif type == 'SnakeAoiPosition':
            params = SpotlightDialog.showSnakeAoiPositionDialog(params)
            return params
        elif type == 'GotoSpecificFrame':
            params = SpotlightDialog.showGotoSpecificFrameDialog(params)
            return params
        elif type == 'CenterTrackingOptions':
            params = SpotlightDialog.showCenterTrackingOptionsDialog(params)
            return params
        elif type == 'MaximumTrackingOptions':
            params = SpotlightDialog.showMaximumTrackingOptionsDialog(params)
            return params
        elif type == 'Morphological':
            params = SpotlightDialog.showMorphologicalDialog(params)
            return params
        elif type == 'ResizeImage':
            params = SpotlightDialog.showResizeImageDialog(params)
            return params
        elif type == 'ExtractField':
            params = SpotlightDialog.showExtractFieldDialog(params)
            return params
        elif type == 'Test':
            params = SpotlightDialog.showTestDialog(params, parent)
            return params
        elif type == 'Enhance':
            params = SpotlightDialog.showEnhanceDialog(params, parent)
            return params
        elif type == 'RectangleAoiOptions':
            params = SpotlightDialog.showRectangleAoiOptionsDialog(params)
            return params

        elif type == 'TrackingFailed':
            params = SpotlightDialog.showTrackingFailedDialog(params)
            return params

        else:
            return {}

    def createModelessDialog(self, type, params, changeNotificationFunction=None, parentAoi = None):
        if type == 'LineProfile':
            title = "Line profile: Luminance"

            #~ dd = SpotlightDialog.LineProfileDialog(title, params, changeNotificationFunction)
            dd = SpotlightDialog.LineProfileDialog(parentAoi, self, title)

            sh = dd.Show(True)
            return dd
        elif type == 'Histogram':
            title = "Histogram: Luminance"
            dd = SpotlightDialog.HistogramDialog(title, params, changeNotificationFunction)
            #dd.Center()
            sh = dd.Show(True)
            return dd
        if type == 'AbelTool':
            title = "Abel Tool"
            #dd = SpotlightDialog.AbelDialog(title, params, changeNotificationFunction)
            dd = SpotlightDialog.AbelDialog(parentAoi, self, title)
            sh = dd.Show(True)
            return dd
        elif type == 'ScaleTool':
            title = "ScaleTool"
            dd = SpotlightDialog.ScaleDialog(title)
            sh = dd.Show(True)
            return dd
        else:
            return None

    def destroyModelessDialog(self, dialog):
        if dialog:
            dialog.Destroy()

    def updateModelessDialog(self, dialog, params={}):
        ' params is a dictionary of new values for the dialog'
        if dialog:
            dialog.update(params)

#---------- Manage the recentFileList class----------------------

class RecentFiles:
    """This class manages the recently used files which are placed under
    the File menu. The list is saved in a "recentfiles.txt" file before
    the frame is distroyed (from OnCloseWindow function) and is loaded
    at start of program. """
    def __init__(self, parent):
        self.parent = parent
        if sys.platform == 'win32':
            prefix = ''
        else:
            prefix = '.spotlight-'
        self.recentFilesPath = os.path.abspath(os.path.join(Spotlight.userDirectory(), prefix+'recentfiles.txt'))
        self.loadRecentFilesList()

    def loadRecentFilesList(self):
        'checks if recentFilesList exists on disk - uses the pickle module to read it'
        if os.path.isfile(self.recentFilesPath):
            f = open(self.recentFilesPath, 'rb')
            rf = pickle.load(f)
            self.recentFiles = rf
            f.close()
            self.separatorExists = False
            self.Update()
        else:
            self.recentFiles = []

    def saveRecentFilesList(self):
        'called from frame when program is being exited - from OnCloseWindow function'
        f = open(self.recentFilesPath, 'wb')
        pickle.dump(self.recentFiles, f)
        f.close()

    def setNewFile(self, file1):
        'add a new file to the recentFiles'
        self.removeExisting(file1)
        self.checkLength()
        self.recentFiles.insert(0, file1)  # insert at beginning of list
        self.Update()

    def removeExisting(self, filename):
        'remove existing item is same as filename - dont want duplicates'
        for i in self.recentFiles:
            if i == filename:
                self.recentFiles.remove(i)

    def checkLength(self):
        'max of 9 entries allowed - one more will be appended in setNewFile()'
        if len(self.recentFiles) > 8:
            self.recentFiles = self.recentFiles[:-1] # delete last element

    def getRecentFile(self, i):
        'returns a specific file from the list'
        return self.recentFiles[i]

    def Update(self):
        'update the File menu'
        num = len(self.recentFiles)

        # delete items but the first 3
        nf = self.parent.menuFile.GetMenuItems()
        count = self.parent.menuFile.GetMenuItemCount()
        c = int(count) - 3 # the 3 menu items are Open, SaveAs, and SaveAoi
        for i in range (c):
            ii = i + 1
            self.parent.menuFile.DestroyItem (nf[len (nf) - ii])

        # add all recent file menus
        self.parent.menuFile.AppendSeparator()

        for i in range (num):
            filename = self.getRecentFile(i)
            self.parent.menuFile.Append(ID_FILE_RECENT0 + i, filename, "")
        # add 'Exit' and separator
        if sys.platform != 'darwin': # File->Exit is bad form on a Mac
            self.parent.menuFile.AppendSeparator()
            self.parent.menuFile.Append(ID_FILE_EXIT, "E&xit", "Terminate the program")

class mtApp(wx.App):
    def OnInit(self):
        frame = SpotlightFrame(None, -1, "Spotlight")
        self.SetTopWindow(frame)
        frame.Show(True)
        SpotlightGui.setGui(frame) # tell Spotlight to use frame as the GUI
        return True
