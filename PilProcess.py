###-----------------
###-------------------- Image Processing class ----------------------------------
###-----------------

from PIL import Image, ImageFilter, ImageChops, ImageEnhance
import math
import operator  # used by histogram equalization function

# needed for wxBeginBusyCursor() in Adaptive contrast function
import wx

RED = 0
GREEN = 1
BLUE = 2
HUE = 3
SATURATION = 4
LUMINANCE = 5
RGB = 6

histogram1 = []
def setHistogram(h):
    global histogram1
    histogram1 = h

def Enhance(image, factor):
    #~ enhancer = ImageEnhance.Sharpness(image)
    #~ enhancer = ImageEnhance.Color(image)
    enhancer = ImageEnhance.Brightness(image)
    #~ enhancer = ImageEnhance.Contrast(image)
    img = enhancer.enhance(factor)
    return img

def EnhanceBrightness(image, factor):
    enhancer = ImageEnhance.Brightness(image)
    img = enhancer.enhance(factor)
    return img

def EnhanceContrast(image, factor):
    enhancer = ImageEnhance.Contrast(image)
    img = enhancer.enhance(factor)
    return img

def Test(image, factor):
    #~ enhancer = ImageEnhance.Sharpness(image)
    #~ enhancer = ImageEnhance.Color(image)
    enhancer = ImageEnhance.Brightness(image)
    #~ enhancer = ImageEnhance.Contrast(image)
    img = enhancer.enhance(factor)
    return img

##---------- PIL-WX ------------------

def convertPILtoWX(pilimage):
    if pilimage == None:
        return None
    if pilimage.mode == 'L':
        pilimage = pilimage.convert("RGB")
    wximg = wx.EmptyImage(pilimage.size[0], pilimage.size[1])
    wximg.SetData(pilimage.tobytes('raw','RGB'))
    return wximg

def convertWXToPIL(wximg):
    h = wximg.GetHeight()
    w = wximg.GetWidth()
    # convert wxImage to string array RGBRGBRGB...
    soutpix = wximg.GetData()
    # convert string array to an RGB Pil image
    pilimage = Image.fromstring('RGB', (w, h), soutpix)
    return pilimage

##----------- end PIL-WX --------------

def openImage(file):
    """interface function - used by SpotlightAoi-Abel"""
    try:
        img = Image.open(file)
        img = img.convert("RGB")
    except:  # any exception
        img = None
    return img

def imageInfo(image, originalMode='RGB'):
    img = image.copy()
    info = ''
    if img:
        w = img.size[0]
        h = img.size[1]
        if originalMode == 'RGB':
            colorPlanes = 3
        else:
            colorPlanes = 1
        info = "Size:  %d x %d\nColorplanes:  %d\n" % (w,h,colorPlanes)
    return info

def convertRawToPIL(data, colorPlanes, w, h):
    pilMode = "RGB"
    if colorPlanes != 3:
        pilMode = "L"
    img = Image.new(pilMode, (w, h))
    img.fromstring(data)
    return img

def listToPilImage(list1, aoiWidth, aoiHeight):  ### FIXME: Grayscale only
    ' Convert list to PIL image (inverse of getdata())'
    soutpix = string.join(map(chr, list1), '')
    outImage = Image.fromstring('L', (aoiWidth, aoiHeight), soutpix)
    return outImage

def Threshold(image, value, type, effect):
    img = executeThreshold(image, value, type, effect)
    h = img.histogram()
    setHistogram(h)
    return img

def executeThreshold(image, value, type, effect):
    if image.mode == 'RGB':
        img = image.convert('L')
    else:
        img = image.copy()

    if type == 0:  # simple
        # set to 255 if pixel greater than value
        img = img.point(lambda i, v=value: i > v and 255)
    elif type == 1:  # low pass
        # leave unchanged if pixel is less than value
        img = img.point(lambda i, v=value: i < v and i)
    else:  # high pass
        # leave unchanged if pixel is greater than value
        img = img.point(lambda i, v=value: i > v and i)

    if effect == 0: # standard threshold
        pass
    else:  # inverse threshold
        img = invertImage(img)

    if image.mode == 'RGB': # if original was RGB, then output RGB
        img = img.convert('RGB')
    return img

def getPixel(img, x, y):
    """
    Return pixel value from the main image - int for grayscale or tuple for color
    """
    return img.getpixel((x, y))

def getPixelNorm(image, x, y):
    """returns normalized floats (0.0 - 1.0)"""
    #print 'image.mode:', image.mode
    pix = image.getpixel((x, y))
    return (pix[0]/255.0, pix[1]/255.0, pix[2]/255.0)

def setPixelNorm(image, x, y, value):
    val = int(value * 255.0)
    image.putpixel((x, y), (val, val, val))

def extractPlane(image, colorPlane):
    'extract a plane from a 24-bit image - result is another 24-bit image'
    if image.mode == 'RGB':
        r, g, b = image.split()
        if colorPlane == 0:
            image = Image.merge("RGB", (r, r, r))
        elif colorPlane == 1:
            image = Image.merge("RGB", (g, g, g))
        elif colorPlane == 2:
            image = Image.merge("RGB", (b, b, b))
        # To convert to "L", PIL uses the ITU-R 601-2 luma transform:
        # L = R * 299/1000 + G * 587/1000 + B * 114/1000
        elif colorPlane == 3:
            grayImage = image.convert("L")
            image = Image.merge("RGB", (grayImage, grayImage, grayImage))
        return image
    else:
        return image

def equalsConstant(image, value):
    'keep image values that equal a constant (set to 255, else 0)'
    return image.point(lambda i, v=value: (i==v)*255)

def addConstant(image, value):
    'add a constant to an image - values greater than 255 are set to 255'
    return image.point(lambda i, v=value: i + v)

def subConstant(image, value):
    'subtract a constant from an image - values less than 0 are set to 0'
    return image.point(lambda i, v=value: i - v)

def multConstant(image, value):
    'multiply an image by an constant'
    return image.point(lambda i, v=value: i * v)

def divConstant(image, value):
    'divide an image by a constant'
    if value == 0.0:
        return image
    else:
        return image.point(lambda i, v=value: i / v)

def addImage(image1, image2):
    'add two images together - image1 + image2'
    return ImageChops.add(image1, image2)

def subImage(image1, image2):
    'subtract two images'
    return ImageChops.subtract(image1, image2)

def multImage(image1, image2):
    'image1 * image2 / 255'
    return ImageChops.multiply(image1, image2)
##        # The following will multiply images without dividing by 255
##        if image1.mode == 'RGB':
##            return image1
##        else:
##            sizeX = image1.size[0]
##            sizeY = image1.size[1]
##            p1 = image1.getdata()   # convert image to 1-d array (list)
##            p2 = image2.getdata()
##
##            out = Image.new(image1.mode, image1.size, 0)
##            for y in range (0, sizeY):
##                for x in range (0, sizeX):
##                    pos = (x, y)
##                    c = y*sizeX + x
##                    p = p1[c] * p2[c]
##                    if p > 255: p = 255
##                    out.putpixel(pos, p)
##            return out

def divImage(image1, image2):
    'divide image1/image2'
    if image1.mode == 'RGB':
        return image1
    else:
        sizeX = image1.size[0]
        sizeY = image1.size[1]
        p1 = image1.getdata()   # convert image to 1-d array (list)
        p2 = image2.getdata()
        out = Image.new(image1.mode, image1.size, 0)
        for y in range (0, sizeY):
            for x in range (0, sizeX):
                c = y*sizeX + x
                pf1 = float(p1[c])
                pf2 = float(p2[c])
                if pf2 == 0.0: pf2 = 1.0
                p = pf1 / pf2
                out.putpixel((x, y), int(p))
        return out

def invertImage(image):
    'invert intensities (inverse video)'
    return ImageChops.invert(image)

def differenceImage(image1, image2):
    return ImageChops.difference(image1, image2)

def lighterImage(image1, image2):
    return ImageChops.lighter(image1, image2)

def darkerImage(image1, image2):
    return ImageChops.darker(image1, image2)

def blendImage(image1, image2, alpha=0.5):
    return ImageChops.blend(image1, image2, alpha)

def Filter(image, filterType):
    if filterType == 0:
        return image.filter(ImageFilter.SMOOTH)
    elif filterType == 1:
        return image.filter(ImageFilter.SMOOTH_MORE)
    elif filterType == 2:
        return image.filter(ImageFilter.BLUR)
    elif filterType == 3:
        return image.filter(ImageFilter.CONTOUR)
    elif filterType == 4:
        return image.filter(ImageFilter.DETAIL)
    elif filterType == 5:
        return image.filter(ImageFilter.SHARPEN)
    elif filterType == 6:
        return image.filter(ImageFilter.EDGE_ENHANCE)
    elif filterType == 7:
        return image.filter(ImageFilter.FIND_EDGES)
    elif filterType == 8:
        return invertImage(image)
    else:
        return image

def convertGrayToColor(image):
    'convert 8-bit image to 24-bit'
    if image.mode == 'L':
        img = image.convert("RGB")
        return img
    else:
        return image

def convertColorToGray(image):
    'convert 24-bit image to 8-bit image'
    if image.mode == 'RGB':
        img = image.convert("L")
        return img
    else:
        return image

def Resize(image, w, h):
    #return image.resize((w, h), Image.BICUBIC)
    return image.resize((w, h), Image.ANTIALIAS) # in PIL 1.1.3

def Roll(image, delta, direction):
    xsize, ysize = image.size
    delta = delta % xsize
    if delta == 0: return image
    img = image.copy()
    if direction == 0:  # left
        part1 = img.crop((0, 0, delta, ysize))
        part2 = img.crop((delta, 0, xsize, ysize))
        image.paste(part2, (0, 0, xsize-delta, ysize))
        image.paste(part1, (xsize-delta, 0, xsize, ysize))
    elif direction == 1:  # right
        part1 = img.crop((0, 0, xsize-delta, ysize))
        part2 = img.crop((xsize-delta, 0, xsize, ysize))
        image.paste(part1, (delta, 0, xsize, ysize))
        image.paste(part2, (0, 0, delta, ysize))
    elif direction == 2:  # up
        part1 = img.crop((0, 0, xsize, delta))
        part2 = img.crop((0, delta, xsize, ysize))
        image.paste(part2, (0, 0, xsize, ysize-delta))
        image.paste(part1, (0, ysize-delta, xsize, ysize))
    elif direction == 3:  # down
        part1 = img.crop((0, 0, xsize, ysize-delta))
        part2 = img.crop((0, ysize-delta, xsize, ysize))
        image.paste(part1, (0, delta, xsize, ysize))
        image.paste(part2, (0, 0, xsize, delta))
    return image


#~ def rotate(image, angle):
    #~ return image.rotate(angle)

def getRotationAoiCoords(aoi):
    """
    Calc max of w and h and set the aoiImage to those coords (the box is
    unaffected).
    """
    r = aoi.getAoiPosition()
    w = r[2] - r[0] # x2-x1
    h = r[3] - r[1] # y2-y1
    if w == h:
        return r
    center = ((r[2] + r[0])/2, (r[3] + r[1])/2)
    s = max(w, h)
    x1 = center[0] - s/2
    y1 = center[1] - s/2
    x2 = x1 + s
    y2 = y1 + s
    r = aoi.clipRectToImage(x1, y1, x2, y2)
    return r

def Transpose(image, direction):
    """Flips the image left-right or top-bottom."""
    if direction == 'FLIP_LEFT_RIGHT':
        return image.transpose(Image.FLIP_LEFT_RIGHT)
    else:
        return image.transpose(Image.FLIP_TOP_BOTTOM)

def RotateAoi(image, angle, r, d):
    """
    Rotate image inside non-wholeimage aoi only. This function rotates pixels
    in, from outside the aoi, so that you don't have black pixels being rotated
    into the aoi. It may still happen if the aoi is at the edge of the image.
    NOTE: this code used to be part of the executeRotation() in the PIL-based
    Spotlight1.2.2.
    """
    imCopy = image.copy()
    bigImage = createBlackPaddedImage(imCopy, d)
    rnew = createBigAoiCoords(r, d)  # relative to bigMainImage
    # extract big aoi from the big image
    bigAoi = bigImage.crop(rnew)
    # rotate
    rotAoi = bigAoi.rotate(angle, Image.BILINEAR) # try BICUBIC
    # copy rotated image back into main image
    bigImage.paste(rotAoi, (rnew[0], rnew[1]))
    # extract original aoi image
    offset = d / 2
    x1 = r[0] + offset
    y1 = r[1] + offset
    x2 = r[2] + offset
    y2 = r[3] + offset
    outAoi = bigImage.crop((x1,y1,x2,y2))
    return outAoi

def createBigAoiCoords(r, d):
    """
    Create new aoi which is big enough to properly rotate in (without bringing
    in black pixels) and is offset relative to the padded image.
    """
    offset = d / 2
    # offset r relative to the bigImage
    x1 = r[0] + offset
    y1 = r[1] + offset
    x2 = r[2] + offset
    y2 = r[3] + offset
    # build a new aoi coords
    center = ((x2 + x1)/2, (y2 + y1)/2)
    x1 = center[0] - offset
    y1 = center[1] - offset
    x2 = center[0] + offset
    y2 = center[1] + offset
    return (x1, y1, x2, y2)

def createBlackPaddedImage(mainImage, d):
    'create an image padded with black - padded with will be '
    sizeX = mainImage.size[0] + d
    sizeY = mainImage.size[1] + d
    grayscale = 0
    paddedImage = Image.new(mainImage.mode, (sizeX, sizeY), grayscale)
    # paste original image into the new big image with an offset
    offset = d / 2
    paddedImage.paste(mainImage, (offset, offset))
    return paddedImage

##----------- Contrast related functions ---------------------------

#---- linear constrast stretching functions

def linearConstrastStretch(image):
    'called by Constrast(). finds min and max and stretches to that range'
    ex = getMinMax(image) # ex[0]=min, ex[1]=max
    imgadd = subConstant(image, ex[0])
    if (ex[1]-ex[0]) != 0:
        return multConstant(imgadd, 255.0/(ex[1]-ex[0]))
    else:
        return image

#---- histogram equalization functions

def histogramEqualization(img):
    """called by Constrast(). Performs linear histogram equalization on an
    image. Obtained this from Pythonware's web site
    (http://www.pythonware.com/library/pil/notes/note04.htm).
    Written by Fredrik Lundh."""
    lut = equalize(img.histogram())  # calculate lookup table
    img = img.point(lut)  # map image through lookup table
    return img

def equalize(h):
    lut = []

    for b in range(0, len(h), 256):

        # step size
        step = reduce(operator.add, h[b:b+256]) / 255

        # create equalization lookup table
        n = 0
        for i in range(256):
            lut.append(n / step)
            n = n + h[i+b]

    return lut

#---- adaptive constrast stretching functions

def adaptiveConstrastStretch(image, localAreaSize):
    """This function performs the adaptive contrast stretching using the
    Pizer method. (see Majid Rabbani notes) It operates only on monochrome
    images."""

    image = image.convert("L")

    sizeX, sizeY = image.size
    if localAreaSize >= sizeX or localAreaSize >= sizeY:
        return linearConstrastStretch(image)
    else:
        wx.BeginBusyCursor()  # start hour-glass cursor
        mono1 = image.copy()
        ngp = getGridSize(localAreaSize, sizeX, sizeY)  # number of grid points in x and y
        gp = getGridPointLocations(ngp, sizeX, sizeY, localAreaSize) # grid point locations
        minmax = obtainMinMax(mono1, gp, ngp, localAreaSize) # set of min-max at each gridpoint
        ngpx = ngp[0]
        ngpy = ngp[1]

        for y in range(0, ngpy-1):
            for x in range(0, ngpx-1):
                upperleft = gp[y*ngpx+x]
                lowerright = gp[(y + 1)*ngpx+(x + 1)]

                gridArea = getAreaBetweenGridpoints(mono1, upperleft, lowerright)
                locmm = get4PtMinMax(minmax, x, y, ngp)
                gridArea = contrastStretchLocArea(gridArea, locmm)

                # copies gridArea to proper part of aoi
                gsX, gsY = gridArea.size
                sizeX, sizeY = mono1.size
                if upperleft[0]+gsX > sizeX:
                    upperleft[0] = sizeX - gsX
                if upperleft[1]+gsY > sizeY:
                    upperleft[1] = sizeY - gsY
                image.paste(gridArea, (upperleft[0], upperleft[1], upperleft[0]+gsX, upperleft[1]+gsY))

        wx.EndBusyCursor()  # end hour-glass cursor
        return image

def contrastStretchLocArea(gridArea, minMax4Pt):
    """Returns contrast stretched gridArea (subAoi). Performs an adaptive
    contrast stretching of all pixels in the local area between grid points.
    For each pixel, four new intensity values are computed based on max
    and min (which determines contrast stretching) at each of the four
    corner grid points and then bi-linear interpolation is used to
    calculate the output intensity value based on the pixel's relative
    distance from the four grid points."""

    sizeX, sizeY = gridArea.size
    p = gridArea.getdata()   # convert image to 1-d array (list)
    out = Image.new(gridArea.mode, gridArea.size, 0)

    min1 = minMax4Pt[0][0]
    max1 = minMax4Pt[0][1]
    min2 = minMax4Pt[1][0]
    max2 = minMax4Pt[1][1]
    min3 = minMax4Pt[2][0]
    max3 = minMax4Pt[2][1]
    min4 = minMax4Pt[3][0]
    max4 = minMax4Pt[3][1]

    fsizeX = float(sizeX)
    fsizeY = float(sizeY)
    pixout = []

    for y in range(sizeY):
        for x in range(sizeX):
            p1 = p2 = p3 = p4 = float(p[y * sizeX + x])
            p1 = p1 - min1
            p1 = p1 * 255.0 / (max1 - min1)
            p2 = p2 - min2
            p2 = p2 * 255.0 / (max2 - min2)
            p3 = p3 - min3
            p3 = p3 * 255.0 / (max3 - min3)
            p4 = p4 - min4
            p4 = p4 * 255.0 / (max4 - min4)
            if p1 < 0.0:
                p1 = 0.0
            if p1 > 255.0:
                p1 = 255.0
            if p2 < 0.0:
                p2 = 0.0
            if p2 > 255.0:
                p2 = 255.0
            if p3 < 0.0:
                p3 = 0.0
            if p3 > 255.0:
                p3 = 255.0
            if p4 < 0.0:
                p4 = 0.0
            if p4 > 255.0:
                p4 = 255.0

            # normalize positions
            xpos = float(x) / fsizeX
            ypos = float(y) / fsizeY
            # use bi-linear interpolation to calc newPix
            newPix = (1.0-xpos)*(1.0-ypos)*p1 + xpos*(1.0-ypos)*p2 + (1.0-xpos)*ypos*p3 + xpos*ypos*p4
            if newPix < 0.0:
                newPix = 0.0
            if newPix > 255.0:
                newPix = 255.0
            pixout.append(int(newPix))
    out.putdata(pixout)
    return out

def get4PtMinMax(minMax, x, y, ngp):
    'obtain min/max for 4 gridpoints'
    # top left
    ngpx = ngp[0]
    min, max = minMax[y*ngpx+x]  # top left
    if min == max:
        max = min + 1
    if min > 254:
        max = 255
        min = 254
    topleft = (float(min), float(max))
    # top right
    xx = x + 1
    yy = y
    min, max = minMax[yy*ngpx+xx]  # top right
    if min == max:
        max = min + 1
    if min > 254:
        max = 255
        min = 254
    topright = (float(min), float(max))
    # bottom left
    xx = x
    yy = y + 1
    min, max = minMax[yy*ngpx+xx]  # bottom left
    if min == max:
        max = min + 1
    if min > 254:
        max = 255
        min = 254
    bottomleft = (float(min), float(max))
    # bottom right
    xx = x + 1
    yy = y + 1
    min, max = minMax[yy*ngpx+xx]  # bottom right
    if min == max:
        max = min + 1
    if min > 254:
        max = 255
        min = 254
    bottomright = (float(min), float(max))
    return (topleft, topright, bottomleft, bottomright)

def getAreaBetweenGridpoints(img, upperleft, lowerright):
    'extracts the area (subAOI) between grid points (including the grid points)'
    r = (upperleft[0], upperleft[1], lowerright[0], lowerright[1])
    return img.crop(r)

def obtainMinMax(mono1, gp, ngp, localAreaSize):
    'returns a list of min-max for local area around each grid point'
    ngpx = ngp[0]
    ngpy = ngp[1]
    minMax = []
    for i in range(ngpx * ngpy):  # initialize
        minMax.append(0)
    las = localAreaSize-1 # smaller than the requested to make sure it fits in the AOI
    for y in range(1, ngpy-1):
        for x in range(1, ngpx-1):
            centX = gp[y*ngpx+x][0] # interior points
            centY = gp[y*ngpx+x][1]
            locArea = getSubAoi(mono1, las, centX, centY)
            mm = locArea.getextrema()
            pt = []
            pt.append(mm)
            i = y*ngpx+x
            minMax[i:i+1] = pt

    # Copy min/max from the interior grid points to the border grid points
    for y in range(ngpy):
        for x in range(ngpx):
            i = y*ngpx+x
            if x == 0 and y == 0:  # upper left corner
                xx = 1
                yy = 1
                pt = []
                pt.append(minMax[yy*ngpx+xx])
                minMax[i:i+1] = pt
            elif x == ngpx-1 and y == 0:  # upper right corner
                xx = ngpx-2
                yy = 1
                pt = []
                pt.append(minMax[yy*ngpx+xx])
                minMax[i:i+1] = pt
            elif x == 0 and y == ngpy-1:  # lower left corner
                xx = 1
                yy = ngpy-2
                pt = []
                pt.append(minMax[yy*ngpx+xx])
                minMax[i:i+1] = pt
            elif x == ngpx-1 and y == ngpy-1:  # lower right corner
                xx = ngpx-2
                yy = ngpy-2
                pt = []
                pt.append(minMax[yy*ngpx+xx])
                minMax[i:i+1] = pt
            elif y == 0:  # all points on top border excluding the corners
                xx = x
                yy = 1
                pt = []
                pt.append(minMax[yy*ngpx+xx])
                minMax[i:i+1] = pt
            elif y == ngpy-1:  # all points on bottom border excluding the corners
                xx = x
                yy = ngpy-2
                pt = []
                pt.append(minMax[yy*ngpx+xx])
                minMax[i:i+1] = pt
            elif x == 0:  # all points on left border excluding the corners
                xx = 1
                yy = y
                pt = []
                pt.append(minMax[yy*ngpx+xx])
                minMax[i:i+1] = pt
            elif x == ngpx-1:  # all points on right border excluding the corners
                xx = ngpx-2
                yy = y
                pt = []
                pt.append(minMax[yy*ngpx+xx])
                minMax[i:i+1] = pt
    return minMax

def getSubAoi(img, subAoiSize, centerX, centerY):
    'extracts a subAOI around the grid point passes in'
    sizeX, sizeY = img.size
    upperLeftX = centerX - (subAoiSize-1)/2
    upperLeftY = centerY - (subAoiSize-1)/2
    if upperLeftX + subAoiSize > sizeX:
        upperLeftX = sizeX - subAoiSize - 1
    if upperLeftY + subAoiSize > sizeY:
        upperLeftY = sizeY - subAoiSize - 1
    r = (upperLeftX, upperLeftY, upperLeftX + subAoiSize, upperLeftY + subAoiSize)
    return img.crop(r)

def getGridSize(localAreaSize, sizeX, sizeY):
    ' figure out how many grid points fit inside the AOI'
    xremainder = sizeX % localAreaSize
    yremainder = sizeY % localAreaSize
    x = sizeX / localAreaSize  # will round-off down
    y = sizeY / localAreaSize
    if xremainder > 0:
        x = x + 1
    if yremainder > 0:
        y = y + 1
    x = x + 2  # expand the size to include the AOI border
    y = y + 2
    return (x, y)

def getGridPointLocations(ngp, sizeX, sizeY, localAreaSize):
    """Figures out the coordinates of the grid points relative to the AOI
    including the ones on the border of the AOI. Each interior corner
    grid point is one half of the localAreaSize in from the corner of
    the AOI."""
    fsizeX = float(sizeX)
    fsizeY = float(sizeY)
    flocalAreaSize = float(localAreaSize)

    # distance between first and last point
    xdist = (fsizeX - flocalAreaSize / 2.0) - flocalAreaSize / 2.0
    ydist = (fsizeY - flocalAreaSize / 2.0) - flocalAreaSize / 2.0
    ngpx = ngp[0]
    ngpy = ngp[1]
    xstep = xdist / (ngpx-3)
    ystep = ydist / (ngpy-3)

    # figure out the corner grid points
    grPoints = []
    yposition = 0.0
    for y in range(ngpy):
        xposition = 0.0
        for x in range(ngpx):
            if x == 1:
                xposition = flocalAreaSize / 2.0
            elif x == ngpx-1:
                xposition = fsizeX - 1.0
            elif y == 1:
                yposition = flocalAreaSize / 2.0
            elif y == ngpy-1:
                yposition = fsizeY - 1.0

            pos = (int(xposition), int(yposition))
            grPoints.append(pos)
            xposition = xposition + xstep
        yposition = yposition + ystep
    return grPoints


#---- Image Statistics functions

def getExtremaColor(img):
    'returns 3 min values and 3 max values, one for each color plane'
    if img.mode == 'RGB':
        r,g,b = img.split()
        red = r.getextrema()
        green = g.getextrema()
        blue = b.getextrema()
        return (red, green, blue)
    else:
        return ((0,0), (0,0), (0,0))

def getExtremaGray(img):
    'returns min and max pixel values in a grayscale image'
    if img.mode == 'L':
        return img.getextrema()
    else:
        return (0,0)

def getMinMax(img):
    """Works for RGB and L. Returns min and max pixel values in the image.
    If image is RGB then it returns min and max between all three images."""
    if img.mode == 'RGB': # return max,min or all three planes
        r,g,b = img.split()
        rex = r.getextrema()
        gex = g.getextrema()
        bex = b.getextrema()
        mn = min(rex[0], gex[0], bex[0])
        mx = max(rex[1], gex[1], bex[1])
        return (mn, mx)
    else:
        return img.getextrema()

def getMeanStDev(img):
    'returns the mean and standard deviation of the pixel values in the aoi'
    img = img.copy()
    meanh = 0
    stdev = 0.0
    if img.mode == 'RGB': # convert RGB to luminance and then calc mean, st.dev
        img = img.convert("L")
    p = img.getdata()  # convert to 1-d
    # calc mean
    n = len(p)
    for i in range(0, n):
        meanh = meanh + p[i]
    meanh = meanh/n
    # calc standard deviation
    for i in range(0, n):
        stdev = stdev + ((p[i] - meanh) * (p[i] - meanh))
    stdev = math.sqrt(stdev/n)
    return (meanh, stdev)

## #-------- Morphological functions ---------------------

def Morphological(image, type, iterations=1):
    # morphological operations are grayscale only
    if image.mode == 'RGB':
        img = image.convert('L')
    else:
        img = image.copy()

    # use standard threshold the image first - in case it wasn't done by the user
    img = Threshold(img, 128, 0, 0)

    if type == 0:
        img = erode(img, iterations)
    elif type == 1:
        img = dilate(img, iterations)
    elif type == 2:  # reconstruct
        img = reconstruct(img, iterations)
    elif type == 3:  # outline
        img = outline(img)
    elif type == 4:  # skeleton
        #return image
        pass
    elif type == 5:  # hole fill
        img = holefill(img)
    elif type == 6:  # hole extract
        img = holeExtract(img)
    elif type == 7:  # border kill
        img = borderkill(img)
    elif type == 8:  # border line kill
        img = borderLineKill(img)

    if image.mode == 'RGB': # if original was RGB, then output RGB
        img = img.convert('RGB')

    return img

def erode(image, iterations=1):
    """Binary erosion - image must be thresholded first for it to work right.
        The input image must be padded to eliminate edge effects. """
    img = image.copy()
    for i in range(iterations):
        paddedImage = createPaddedImage(img, 1)
        # use standard threshold the image first - in case it wasn't done by the user
        thresholdImg = Threshold(paddedImage, 128, 0, 0)
        # edge detection - leaves an edge 1 pixel wide.
        filteredImg = Filter(thresholdImg, 7)
        # take a second threshold - because the filtering leaves some pixels less than 255
        thresholdImg2 = Threshold(filteredImg, 128, 0, 0)
        # subtract the edge line - makes object smaller
        arithImg = subImage(thresholdImg, thresholdImg2)
        # extract the original sized image
        box = (1, 1, arithImg.size[0]-1, arithImg.size[1]-1)
        img = arithImg.crop(box)
    return img

def dilate(image, iterations=1):
    """Binary dilation - image must be thresholded first for it to work right.
        The input image must be padded to eliminate edge effects. """
    img = image.copy()
    for i in range(iterations):
        paddedImage = createPaddedImage(img, 1)
        thresholdImg = Threshold(paddedImage, 128, 0, 0) #in case it wasn't done by the user
        thresholdImg2 = Threshold(thresholdImg, 128, 0, 1) # inverse threshold
        filteredImg = Filter(thresholdImg2, 7)
        thresholdImg3 = Threshold(filteredImg, 128, 0, 0)
        arithImg = addImage(thresholdImg, thresholdImg3)
        box = (1, 1, arithImg.size[0]-1, arithImg.size[1]-1)
        img = arithImg.crop(box)
    return img

def createPaddedImage(img, pad):
    """Create an padded image - since it is created with resize() the border pixels
        will be same (almost) as the original edge pixels."""
    sizeX, sizeY = img.size
    paddedImage = img.resize((sizeX+2*pad, sizeY+2*pad))
    # paste original image into the new big image with an offset
    paddedImage.paste(img, (pad, pad))
    return paddedImage

def outline(img):
    'generate border around the object - one pixel thick'
    thresholdImg = Threshold(img, 128, 0, 0)
    filteredImg = Filter(thresholdImg, 7)
    return Threshold(filteredImg, 128, 0, 0)

def reconstruct(image, iterations=1):
    wx.BeginBusyCursor()  # start hour-glass cursor
    img = image.copy()
    erodedImg = erode(img, iterations)
    seedLocations = findSeedLocations(erodedImg)

    markColor = 100
    img = floodFillAll(img, seedLocations, markColor)
    wx.EndBusyCursor()  # end hour-glass cursor

    # keep only the marked blobs
    img = equalsConstant(img, markColor)
    return img

def floodFillAll(image, seedLocations, markColor):
    'perform flood fill on all objects specified by seedLocations'
    img = image.copy()
    for seed in seedLocations:
        # skip if already flood-filled
        if img.getpixel(seed) != markColor:
            wx.GetApp().Yield()
            img = floodFill(img, seed, markColor)
    return img

def findSeedLocations(img):
    width, height = img.size
    pixels = img.getdata()
    imageSize = len(pixels)
    seedLocations = []

    c = 0
    while(c<imageSize):
        if pixels[c] > 0:
            y = int(c / width)
            x = int(c - (y * width))
            seedLocations.append((x, y))
            wx.GetApp().Yield()
            img = floodFill(img, (x,y), 0)
            pixels = img.getdata()
        c = c + 1
    return seedLocations

def floodFill(image, seedPoint, newColor=255):
    """Optimized seed fill algorithm from Graphics Gems 1"""
    floodedImage = Image.new(image.mode, image.size)
    floodedImage.paste(image)
    floodedVector = list(floodedImage.getdata())

    width, height = floodedImage.size
    seedX, seedY = seedPoint

    oldColor = floodedVector[seedX+seedY*width]
    if oldColor == newColor:
        return image

    # stack holds (Y, startX, endX, parentY)
    stack = []
    stack.append((seedY,   seedX, seedX,  1))
    stack.append((seedY+1, seedX, seedX, -1))

    while stack:
        (y, x1, x2, dy) = stack.pop()
        y = y + dy

        if x2 >= width or x1 < 0 or y >= height or y < 0:
            continue

        x = x1
        while x >= 0: # fill left
            index = x + y*width
            if floodedVector[index] == oldColor:
                floodedVector[index] = newColor
                x = x-1
            else:
                break

        if x < x1: # not skip
            l = x+1
            if l < x1:
                stack.append((y, l, x1-1, -1*dy))
            x = x1 + 1
            while x<width:
                index = x + y*width
                if floodedVector[index] == oldColor:
                    floodedVector[index] = newColor
                    x = x+1
                else:
                    break
            stack.append((y, l, x-1, dy))
            if x > x2+1:
                stack.append((y, x2+1, x-1, -1*dy))

        x = x + 1
        while x <= x2:
            index = x + y*width
            if floodedVector[index] != oldColor:
                x = x + 1
            else:
                break
        l = x

        while x<=x2:
            while x<width:
                index = x + y*width
                if floodedVector[index] == oldColor:
                    floodedVector[index] = newColor
                    x = x+1
                else:
                    break
            stack.append((y, l, x-1, dy))
            if x > x2+1:
                stack.append((y, x2+1, x-1, -1*dy))
            x = x + 1
            while x<=x2:
                index = x + y*width
                if floodedVector[index] != oldColor:
                    x = x + 1
                else:
                    break
            l = x

    floodedImage.putdata(floodedVector)
    return floodedImage

def holefill(image):
    'fill in holes in thresholded objects'

    wx.BeginBusyCursor()  # start hour-glass cursor
    img = Threshold(image, 128, 0, 1)  # inverse threshold
    seedLocations = findSeedLocations(img)
    if seedLocations == []: # the entire image was white
        wx.EndBusyCursor()  # end hour-glass cursor
        return image

    # when the threshold is inverted, the background becomes white so the
    # first seed returned is the (0,0) point of the background (not a hole).
    if seedLocations[0] == (0, 0):
        del seedLocations[0]

    img = Threshold(img, 128, 0, 1)  # inverse back
    markColor = 255
    img = floodFillAll(img, seedLocations, markColor)
    wx.EndBusyCursor()  # end hour-glass cursor

    return img

def holeExtract(image):
    'extract holes from thresholded objects'

    wx.BeginBusyCursor()  # start hour-glass cursor
    img = Threshold(image, 128, 0, 1)  # inverse threshold
    seedLocations = findSeedLocations(img)

    # when the threshold is inverted, the background becomes white so the
    # first seed returned is the (0,0) point of the background (not a hole).
    if seedLocations[0] == (0, 0):
        del seedLocations[0]

    img = Threshold(img, 128, 0, 1)  # inverse back
    markColor = 100
    img = floodFillAll(img, seedLocations, markColor)

    # keep only the marked blobs
    img = equalsConstant(img, markColor)
    wx.EndBusyCursor()  # end hour-glass cursor

    return img

def borderLineKill(image):
    'draws a black line (1 pix thick) around the border of the image'
    img = Image.new(image.mode, image.size)
    croppedImg = image.crop((1, 1, image.size[0]-1, image.size[1]-1))
    img.paste(croppedImg, (1,1))
    return img

def borderkill(img):
    sizeX, sizeY = img.size
    # top
    y = 0
    for x in range(sizeX):
        if img.getpixel((x,y)) > 0:
            img = floodFill(img, (x,y), 0)
    wx.GetApp().Yield()
    # bottom
    y = sizeY - 1
    for x in range(sizeX):
        if img.getpixel((x,y)) > 0:
            img = floodFill(img, (x,y), 0)
    wx.GetApp().Yield()
    # left
    x = 0
    for y in range(sizeY):
        if img.getpixel((x,y)) > 0:
            img = floodFill(img, (x,y), 0)
    wx.GetApp().Yield()
    # right
    x = sizeX - 1
    for y in range(sizeY):
        if img.getpixel((x,y)) > 0:
            img = floodFill(img, (x,y), 0)
    wx.GetApp().Yield()
    return img

##------------- statistics ----------------

def getHistogram(image):
    return image.histogram()

def getHistogramMinMax(image, colorPlane):
    """
    Returns min and max pixel values in the image.
    NOTE: the image passed in is always RGB.
    """
    if colorPlane == RED or colorPlane == GREEN or colorPlane == BLUE:
        r,g,b = image.split()
        if colorPlane == RED:
            return r.getextrema()
        if colorPlane == GREEN:
            return g.getextrema()
        if colorPlane == BLUE:
            return b.getextrema()
    else:  # LUMINANCE
        img = image.convert("L")
        return img.getextrema()

def getHistogramStatistics(image, colorPlane):
    """
    Returns the mean and standard deviation of the pixel values in the aoi.
    NOTE: the image passed in is always RGB because of the conversion to PIL
    makes it this way.
    """
    meanh = 0
    stdev = 0.0
    p = []
    if colorPlane == RED or colorPlane == GREEN or colorPlane == BLUE:
        r,g,b = image.split()
        if colorPlane == RED:
            p = r.getdata()   # convert image to 1-d array (list)
        if colorPlane == GREEN:
            p = g.getdata()
        if colorPlane == BLUE:
            p = b.getdata()
    else: # includes LUMINANCE
        img = image.convert("L")
        p = img.getdata()
    # calc mean
    n = len(p)
    for i in range(0, n):
        meanh = meanh + p[i]
    meanh = meanh/n
    # calc standard deviation
    for i in range(0, n):
        stdev = stdev + ((p[i] - meanh) * (p[i] - meanh))
    stdev = math.sqrt(stdev/n)
    return (meanh, stdev)

##------------------------ Extract Field -----------------------------------

def fieldOperation(image, fieldSelection):
    'called from manu item Process->Extract Field'
    if fieldSelection == 0:
        return extractField(image, 'odd')
    elif fieldSelection == 1:
        return extractField(image, 'even')
    else:
        return swapFieldOrder(image)

def extractField(img, field='odd'):
    """
    Extract a field from a frame. Averages the field lines to fill in the
    in-between lines.
    NOTE: odd field is first in the images (rows 0, 2, 3...) and even field
    is second (rows 1, 3, 5...).
    """
    #if not (img.mode == 'L' or img.mode == 'RGB'):
    if not (img.mode == 'RGB'):
        print 'the input image must be either L or RGB'
        return img

    w, h = img.size
    remainder = h % 2

    # If the input image has odd number of rows, enlarge the image
    # vertically by 1 so that it has an even number of rows. It will be cut
    # down to the original size at the end.
    if remainder == 1:
        temp = Image.new(img.mode, (w, h+1))
        temp.paste(img, (0, 0, w, h))
        # fill in last row with data from the previous row of the same
        # field (two rows back)
        row = temp.crop((0, h-2, w, h-1))
        temp.paste(row, (0, h, w, h+1))
        img = temp.copy()
        w, h = img.size

    # by flipping it you process the other set of lines
    if field == 'even':
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # create a blank image with half the size vertically
    ### Python 2.1
    if remainder == 0:
        h2 = h / 2
    else:
        h2 = (h-1) / 2
    ###

    ### Available in Python 2.2
    #h2 = h // 2  # the // returns floor division (round down)
    ###
    imghalf = Image.new(img.mode, (w, h2))

    # extract the field - this image is half the height
    i = 0
    for y in range(0, h, 2):
        row = img.crop((0, y, w, y+1))
        if i < h2:
            imghalf.paste(row, (0, i, w, i+1))
        i = i + 1

    # resize the half-size field image back to original size
    fieldImage = imghalf.resize((w, h2*2), Image.BILINEAR)
    hh = fieldImage.size[1]

    # The bilinear resize operation appears to shift the image by 1
    # pixel to the right and down, so shift it back over. Note: the bicubic
    # resize  shifts by 2 pixels.
    temp = fieldImage.crop((1, 1, w, hh))
    fieldImage.paste(temp, (0, 0, w-1, hh-1))

    # copy last column from original image and interpolate every other value
    lastcolumn = img.crop((w-1, 0, w, hh))
    fieldImage.paste(lastcolumn, (w-1, 0, w, hh))
    width, height = fieldImage.size
    r, g, b = fieldImage.split()
    for y in range(height-2):
        if not y % 2:  # rows 0, 2, 4...
            # red plane
            p1 = r.getpixel((width-1, y))
            p2 = r.getpixel((width-1, y+2))
            r.putpixel((width-1, y+1), (p1+p2)/2)
            # green plane
            p1 = g.getpixel((width-1, y))
            p2 = g.getpixel((width-1, y+2))
            g.putpixel((width-1, y+1), (p1+p2)/2)
            # blue plane
            p1 = b.getpixel((width-1, y))
            p2 = b.getpixel((width-1, y+2))
            b.putpixel((width-1, y+1), (p1+p2)/2)
    fieldImage = Image.merge("RGB", (r, g, b))

    # copy the next to last row into the last row
    for x in range(width):
        p = fieldImage.getpixel((x, height-2))
        fieldImage.putpixel((x, height-1), p)

    if field == 'even':
        fieldImage = fieldImage.transpose(Image.FLIP_TOP_BOTTOM)

    # remove the last row
    if remainder == 1:
        temp = fieldImage.crop((0, 0, w, h-1))
        fieldImage = temp.copy()

    return fieldImage

### This routine doubles up the rows
#~ def extractField(img, field='odd'):
    #~ """
    #~ Extract a field from a frame.If 'raw' is set to true then only the true
    #~ raw field is displayed where alternate lines are black.

    #~ NOTE: odd field is first in the images (rows 0, 2, 3...) and even field
    #~ is second (rows 1, 3, 5...).
    #~ """
    #~ w, h =img.size
    #~ out = Image.new(img.mode, img.size)
    #~ if field == 'odd':
        #~ startrow = 0
    #~ else:
        #~ startrow = 1
    #~ for y in range(startrow, h, 2):
        #~ row = img.crop((0, y, w, y+1))
        #~ out.paste(row, (0, y, w, y+1))
        #~ if y+1 < h:
            #~ out.paste(row.copy(), (0, y+1, w, y+2))
    #~ return out

def swapFieldOrder(img):
    w, h =img.size
    out = Image.new(img.mode, img.size)
    # do odd lines
    startrow = 0
    for y in range(startrow, h, 2):
        row = img.crop((0, y, w, y+1))     # read odd row
        if y+1 < h:
            out.paste(row, (0, y+1, w, y+2))   # paste in even row
    # do even lines
    startrow = 1
    for y in range(startrow, h, 2):
        row = img.crop((0, y, w, y+1))   # read even row
        out.paste(row, (0, y-1, w, y)) # paste in odd row
    return out
