from PIL import Image
import math
#~ import PythonMagick

"""
The functions in this module support locating the trackpoint and
line following.

"""

DEGtoRAD = (3.1415926536/180.0)
RADtoDEG = 57.29577951308

def locateThresholdTrackPoint(img, ang):
    """
    Returns a track point that is the first non-zero point it finds
    in a given direction (determined by angle passed in). If in the
    same line scan it finds multiple points, it returns the half way
    point between them.
    """
    g = 0.7;  # grid size
    #aoiWidth, aoiHeight = img.columns(), img.rows()
    aoiWidth, aoiHeight = img.size

    left = 0
    right = aoiWidth-1
    top = 0
    bottom = aoiHeight-1

    if ang >= 0.0 and ang < 90.0:
        xline = float(right)   # coordinates of corner to begin with
        yline = float(top)
    elif ang >= 90.0 and ang < 180.0:
        xline = float(left)    # coordinates of corner to begin with
        yline = float(top)
    elif ang >= 180.0 and ang < 270.0:
        xline = float(left)    # coordinates of corner to begin with
        yline = float(bottom)
    elif ang >= 270.0 and ang < 360.0:
        xline = float(right)   # coordinates of corner to begin with
        yline = float(bottom)
    xstep = g * math.cos(ang/180.0*3.1415926536)
    ystep = g * math.sin(ang/180.0*3.1415926536)

    xmax = left
    xmin = right
    ymax = top
    ymin = bottom
    foundline = False

    while(1):   # loop until break occurs
        xline = xline - xstep
        yline = yline + ystep
        xtry = xline
        ytry = yline
        if xtry > float(right) or xtry < float(left) or ytry > float(bottom) or ytry < float(top):
            break  # scanned all the lines without finding anything (may miss some pixels in corner opposite start corner)
        while (xtry <= float(right) and ytry <= float(bottom) and xtry >= float(left) and ytry >= float(top)):
            x = int(xtry)
            y = int(ytry)
            r, g, b = getPixelNorm(img, x, y)

            if (r + g + b > 0.0):  # greater than threshold
                foundline = True
                if x > xmax: xmax = x
                if x < xmin: xmin = x
                if y > ymax: ymax = y
                if y < ymin: ymin = y
            xtry = xtry + ystep
            ytry = ytry + xstep
        xtry = xline
        ytry = yline
        while (xtry <= float(right) and ytry <= float(bottom) and xtry >= float(left) and ytry >= float(top)):
            xtry = xtry - ystep
            ytry = ytry - xstep
            x = int(xtry)
            y = int(ytry)
            r, g, b = getPixelNorm(img, x, y)

            if (r + g + b > 0.0):  # greater than threshold
                foundline = True
                if x > xmax: xmax = x
                if x < xmin: xmin = x
                if y > ymax: ymax = y
                if y < ymin: ymin = y
        if foundline == True:
            break
    if foundline == False:  # No Point Found
        return (-1,-1)
    else:
        return ((xmin+xmax)/2 , (ymin+ymax)/2)

def imageCenterOfMass(img):
    """
    Calculate center of an object in the image. The object may but
    doesn't have to be thresholded. If it is not thresolded then the
    background levels contribute towards the center-of-mass
    calculation.
    """
    aoiWidth, aoiHeight = img.size
    # find the common divisor (area under the curve)
    a = 0.0
    for y in range(aoiHeight):
        for x in range(aoiWidth):
            r, g, b = getPixelNorm(img, x, y)
            a = a + r
    # if all pixels are 0, return -1
    if a == 0.0:
        return (-1, -1)  # point not found
    # sum up
    a = float(a)
    px = 0.0
    py = 0.0
    for y in range(aoiHeight):
        for x in range(aoiWidth):
            r, g, b = getPixelNorm(img, x, y)
            px = px + (r * x) / a
            py = py + (r * y) / a
    centerpoint = (int(px), int(py))
    return centerpoint

def getMaxPixelValue(img):
    """ returns the max of each of the color channels"""
    aoiWidth, aoiHeight = img.size
    maxred = 0.0
    maxgreen = 0.0
    maxblue = 0.0
    for y in range(aoiHeight):
        for x in range(aoiWidth):
            r, g, b = getPixelNorm(img, x, y)
            if r > maxred: maxred = r
            if g > maxgreen: maxgreen = g
            if b > maxblue: maxblue = b
    return (maxred, maxgreen, maxblue)

def getMaxIntensityLocation(img):
    """
    This algorithm finds the x,y location of brightest pixel in an
    image. If it finds more than one pixel then it calculates
    the center-of-mass among those pixels and returns that location.
    """
    aoiWidth, aoiHeight = img.size
    maxRed, maxGreen, maxBlue = getMaxPixelValue(img)
    maxPix = max(maxRed, maxGreen, maxBlue)
    # find a pixel of max intensity (there may be more than one) and its coordinates
    maxPixels = []
    maxx = []
    maxy = []
    for y in range (0, aoiHeight):
        for x in range (0, aoiWidth):
            r, g, b = getPixelNorm(img, x, y)
            if maxPix == max(r, g, b):
                maxPixels.append(r)
                maxx.append(x)
                maxy.append(y)
    # now get center-of-mass the those pixels
    mx, my = arrayCenterOfMass(maxPixels, maxx, maxy)
    return (int(mx), int(my))

def arrayCenterOfMass(pixels, xx, yy):
    """
    Calculate center of mass of array of pixels. Each pixel has
    a corresponding (x,y) associated with it.
    """
    # find the common divisor (area under the curve)
    a = 0
    for p in pixels:
        a = a + p
    # if all pixels are 0, return -1
    if a == 0:
        return (-1, -1)  # point not found
    # sum up
    a = float(a)
    px = 0.0
    py = 0.0
    for i in range(len(pixels)):
        pix = float(pixels[i])
        px = px + (pix * xx[i]) / a
        py = py + (pix * yy[i]) / a
    return (px, py)

def findMaxPointAlongLine(pxy, imagePxy):
    """
    This function takes in a line profile and the x,y coordinates
    and returns the max point along that line profile.
    Note: pxy is the line profile from across the AOI,
    imagePxy is the line profile from across the whole image.
    """
    # get max pixels and its x,y positions
    pixels, maxx, maxy = findMaxPixelsXY(pxy)
    if max(pixels) == 0: # if all pixels along the line are 0
        return (-1, -1)

    # if more than one point were found, get its center of mass
    mx, my = arrayCenterOfMass(pixels, maxx, maxy)

    # since tx and ty are floating pt. numbers, they don't fall right on the
    # pixels along the original line (makes the line drift). So select the
    # closest point on the line
    return putBackOnLine(imagePxy, (mx, my))  # returns (x, y)

def findMaxPixelsXY(pxy):
    """
    This function returns lists of brightest pixels and its x,y locations.
    """
    # break out the packed lists
    pixels = []
    xx = []
    yy = []
    for ppp in pxy:
        rgb = ppp[0]
        pix = (rgb[0] + rgb[1] + rgb[2]) / 3 # assumes RGB image
        pixels.append(pix)
        xx.append(ppp[1])
        yy.append(ppp[2])

    # calc max
    maxp = 0
    for p in pixels:
        if p > maxp:
            maxp = p

    # find all the max pixels and its x,y positions
    maxPixels = []
    maxx = []
    maxy = []
    for i in range(len(pixels)):
        if pixels[i] == maxp:
            maxPixels.append(pixels[i])
            maxx.append(xx[i])
            maxy.append(yy[i])
    return (maxPixels, maxx, maxy)

def findThresholdPointAlongLine(pxy, imagePxy):
    """
    This function takes in a line profile and the x,y coordinates
    of each pixel which has been previously thresholded and figures
    out the threshold point (the trackpoint)
    Note: pxy is the line profile from across the AOI,
    imagePxy is the line profile from across the whole image.
    """
    # get lists of max pixels - for thresholded image all max's will be 255
    pixels, xx, yy = findMaxPixelsXY(pxy)

    if max(pixels) == 0: # if all pixels along the line are 0
        return (-1, -1)

    # find the first non-zero pixel
    c = 0
    for i in range(len(pixels)):
        if pixels[i] > 0:
            c = i
            break
    tx = xx[c]    # thresholded x location
    ty = yy[c]    # thresholded y location

    # since tx and ty are floating pt. numbers, they don't fall right on the
    # pixels along the original line (makes the line drift). So select the
    # closest point on the line
    return putBackOnLine(imagePxy, (tx, ty))  # returns (x, y)

def putBackOnLine(pxy, p):
    """
    Returns an x,y point from pxy which is closest to point p.
    Basically, pxy contains a list of x,y positions (a line) and
    p is a floating point number close but not right on the
    line. This function returns one of the points on the line.
    """
    xx = []
    yy = []
    for ppp in pxy:
        xx.append(ppp[1])
        yy.append(ppp[2])

    # find closest point
    mindist = 10000.0
    c = 0
    for i in range(len(xx)):
        d = dist(p[0], p[1], xx[i], yy[i])
        if d < mindist:
            mindist = d
            c = i
    return (xx[c], yy[c])

def dist(x1, y1, x2, y2):
    t1 = t2 = 0.0
    t1 = x1 - x2
    t2 = y1 - y2
    return math.sqrt(t1*t1 + t2*t2)


###------------- Line Following functions --------------------------

def LineFollow(image, startpoint, r):
    """
    r is the AOI rectangle
    """
    #img = PythonMagick.Image(image) # copy
    img = image.copy()
    xstartpt, ystartpt = findFirstPoint(img, startpoint)
    if xstartpt == -1 or ystartpt == -1:
        return []
    xytemp = saveStartArea(img, xstartpt, ystartpt)

    # Set the first point (the startpoint) to black
    setPixelNorm(img, xstartpt, ystartpt, 0.0)

    # Fill in the first three points along the line (to one side of the
    # starting point (xy1) and then the other side (xy2))
    xy1, xy2 = getInitialLinePoints(img, xstartpt, ystartpt)

    # Write back the pixels that were set to 0 by other functions
    writeStartArea(img, xstartpt, ystartpt, xytemp)
    setPixelNorm(img, xstartpt, ystartpt, 0.0) # set startpoint back to 0
    x1 = r[0]
    y1 = r[1]
    x2 = r[2]
    y2 = r[3]

    # one side
    save1 = []
    x = xstartpt
    y = ystartpt
    bPtFound = True
    while (x > x1 and x < x2 and y > y1 and y < y2) and (bPtFound == True):
        angle = calcAngle(xy1, x, y)  # angle of the next likely pixel
        bPtFound, xnew, ynew = findNextPixel(img, angle, x, y)
        if bPtFound:
            save1.append((x, y))
            xy1 = shiftArrray(xy1, x, y)
            x = xnew
            y = ynew

    # other side
    save2 = []
    x = xstartpt
    y = ystartpt
    bPtFound = True
    while (x > x1 and x < x2 and y > y1 and y < y2) and (bPtFound == True):
        angle = calcAngle(xy2, x, y)  # angle of the next likely pixel
        bPtFound, xnew, ynew = findNextPixel(img, angle, x, y)
        if bPtFound:
            save2.append((x, y))
            xy2 = shiftArrray(xy2, x, y)
            x = xnew
            y = ynew

    # save1 will contain all the pixels
    save1.reverse()
    for i in range(1, len(save2)):
        save1.append(save2[i])

    return save1

def getInitialLinePoints(img, xstartpt, ystartpt):
    # Fill in the first three points along the line (to one side of the
    # starting point)
    xy1 = []   # xy1 is an array of tuples ((x1,y1), (x2,y2), (x3,y3), ...)
    x = xstartpt
    y = ystartpt

    for i in range(3):
        x, y = getNeighborhoodPoint(img, x, y)
        xy1.append((x,y))

    # Fill in the first three points along the line (to the other side of the
    # starting point)
    xy2 = [] # xy2 is an array of tuples ((x1,y1), (x2,y2), (x3,y3), ...)
    x = xstartpt
    y = ystartpt

    for i in range(3):
        x, y = getNeighborhoodPoint(img, x, y)
        xy2.append((x,y))

    return (xy1, xy2)

def getNeighborhoodPoint(img, px, py):
    x = px
    y = py
    pointFound = (-1, -1)
    neighborhood = 1
    found = False
    # First check the pixels in the imediate neighborhood of x and y
    for angle in range(0, 360, 15): # cycle through with 15 degree angle steps
        found, x, y = CheckPixel1(img, angle, neighborhood, x, y)
        if found:
            pointFound = (x, y)
            break

    # If thresholded pixel wasn't found in the imediate neighborhood
    # then go further out
    neighborhood = 2
    if found == False:
        for angle in range(0, 360, 15):
            found, x, y = CheckPixel1(img, angle, neighborhood, x, y)
            if found:
                pointFound = (x, y)
                break
    return pointFound

def CheckPixel1(img, angle, neighborhood, xcurrent, ycurrent):
    # make sure that angle is within 0 - 360 range
    angle = float(angle)
    if angle < 0.0:
        angle = angle + 360.0
    if angle > 360.0:
        angle = angle - 360.0

    # Figure out the radius (going through center of pixels)
    radius = 0.0
    if angle >= 0.0 and angle <= 45.0:
        radius = neighborhood / math.cos(angle*DEGtoRAD)
    if angle > 45.0 and angle <= 135.0:
        radius = neighborhood / math.sin(angle*DEGtoRAD)
    if angle > 135.0 and angle <= 225.0:
        radius = -neighborhood / math.cos(angle*DEGtoRAD)
    if angle > 225.0 and angle <= 315.0:
        radius = -neighborhood / math.sin(angle*DEGtoRAD)
    if angle > 315.0:
        radius = neighborhood / math.cos(angle*DEGtoRAD)

    # Calculate step size to locate center of pixels (depends on radius and angle)
    fx = radius*math.cos(angle*DEGtoRAD)
    fy = radius*math.sin(angle*DEGtoRAD)
    ix = round(fx)
    iy = round(fy)
    iy = -iy;   # inverse y-sign for pixel space (origin in upper-left) ?????????

    # Calculate the new pixel position (pixel coordinates)
    xn = int(xcurrent + ix)
    yn = int(ycurrent + iy)

    # Read the pixel value at the new position
    r, g, b = getPixelNorm(img, xn, yn)
    if r == 1.0:
        setPixelNorm(img, xn, yn, 0.0) # Set the new pixel found to 0
        # the x and y change to the new location where a thresholded point was found
        xnew = xn
        ynew = yn
        ptFound = True
    else:
        xnew = xcurrent   # the x and y does not change
        ynew = ycurrent
        ptFound = False
    return (ptFound, xnew, ynew)

def findFirstPoint(img, startpoint):
    """
    This is a proximity detector. Search for a point on the line in a
    9x9 neighborhood of the point passed in (startpoint). This allows
    that the user don't have to click exactly on the line, only in
    the 9x9 neighborhood.
    """
    pix = 0
    pt = (-1, -1)
    xpoints = []
    ypoints = []

    for yn in range(startpoint[1]-4, startpoint[1]+5):
        for xn in range(startpoint[0]-4, startpoint[0]+5):
            # look for thresholded pixels
            r, g, b = getPixelNorm(img, xn, yn)
            if r == 1.0:
                xpoints.append(xn)
                ypoints.append(yn)

    # find closest point to startpoint
    if xpoints:
        mindist = 10000.0
        c = 0
        for i in range(len(xpoints)):
            d = dist(startpoint[0], startpoint[1], xpoints[i], ypoints[i])
            if d < mindist:
                mindist = d
                c = i
        return (xpoints[c], ypoints[c])
    else:
        return (-1, -1)

def saveStartArea(img, xstartpt, ystartpt):
    """
    Save the 7x7 area around the starting point.  It will be deleted
    during the search for the starting 6 pixels (3 on either side of
    the starting point)
    """
    xytemp = []
    for yn in range(ystartpt-3, ystartpt+4):
        for xn in range(xstartpt-3, xstartpt+4):
            r,g,b = getPixelNorm(img, xn, yn) # get a pixel
            xytemp.append(r)
    return xytemp

def writeStartArea(img, xstartpt, ystartpt, xytemp):
    """
    Retrieve the 7x7 area around the starting point.  It was deleted
    during the search for the starting 6 pixels (3 on either side of
    the starting point)
    """
    c = 0
    for yn in range(ystartpt-3, ystartpt+4):
        for xn in range(xstartpt-3, xstartpt+4):
            setPixelNorm(img, xn, yn, xytemp[c])
            c = c + 1

def calcAngle(xy, x, y):
    xsum = xy[0][0] + xy[1][0] + xy[2][0]   # sum up the last 3 pixels
    ysum = xy[0][1]+ xy[1][1] + xy[2][1]
    xav = float(xsum) / 3.0   # x and y average of last 3 pixels
    yav = float(ysum) / 3.0
    xdiff = float(x) - xav # diff between current pixel and the average
    ydiff = float(y) - yav
    angle = RADtoDEG * math.atan2(-ydiff, xdiff)   # calculate the angle
    if angle < 0.0:
        angle = angle + 360.0
    return angle

def shiftArrray(xy, x, y):
    'Shift the xy array down one pixel'
    x2 = xy[1][0]
    x1 = xy[0][0]
    x0 = x
    y2 = xy[1][1]
    y1 = xy[0][1]
    y0 = y
    xy = []
    xy.append((x0, y0))
    xy.append((x1, y1))
    xy.append((x2, y2))
    return xy

def findNextPixel(img, ang1, x, y):
    'find the next pixel along the line'
    # Searching 1st level of forward pixels
    bPtFound = False
    neighborhood = 1
    if bPtFound == False:   # look in the direction of the angle
        angle = ang1
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:   # check 45 degrees more than the angle
        angle = ang1 + 45.0
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:   # check 45 degrees less than the angle
        angle = ang1 - 45.0
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:   # 360 degree scan
        # cycle through with 15 degree angle steps
        for angle in range(0, 360, 15):
            bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
            if  bPtFound:
                break

    # Point not found in the forward 1st level -  Do forward
    # search of 2nd level of forward pixels
    neighborhood = 2
    if bPtFound == False:   # look in the direction of the angle
        angle = ang1
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:   # check 22.5 degrees more than the angle
        angle = ang1 + 22.5
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:  # check 22.5 degrees less than the angle
        angle = ang1 - 22.5
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:  # check 45 degrees more than the angle
        angle = ang1 + 45.0
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:   # check 45 degrees less than the angle
        angle = ang1 - 45.0
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)

    # Point not found in the forward 2 levels -  Do forward search
    # of 3rd level of forward pixels
    neighborhood = 3
    if bPtFound == False:  # look in the direction of the angle
        angle = ang1
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:  # check 15 degrees more than the angle
        angle = ang1 + 15.0
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:   # check 15 degrees less than the angle
        angle = ang1 - 15.0
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:   # check 30 degrees more than the angle
        angle = ang1 + 30.0
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:  # check 30 degrees less than the angle
        angle = ang1 - 30.0
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:   # check 45 degrees more than the angle
        angle = ang1 + 45.0
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
    if bPtFound == False:   # check 45 degrees less than the angle
        angle = ang1 - 45.0
        bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)

    # Point still not found - Search 2nd level of surrounding (360 degree scan) pixels
    if bPtFound == False:
        neighborhood = 2
        # cycle through with 15 degree angle steps
        for angle in range(0, 360, 15):
            bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
            if bPtFound:
                break

    # Point still not found - Search 3rd level of surrounding pixels  (360 degree scan) pixels
    if bPtFound == False:
        neighborhood = 3
        # cycle through with 15 degree angle steps
        for angle in range(0, 360, 15):
            bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
            if bPtFound:
                break

    # Point still not found - Search 4th level of surrounding pixels  (360 degree scan) pixels
    if bPtFound == False:
        neighborhood = 4
        # cycle through with 10 degree angle steps
        for angle in range(0, 360, 10):
            bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
            if bPtFound:
                break

    # Point still not found - Search 5th level of surrounding pixels  (360 degree scan) pixels
    if bPtFound == False:
        neighborhood = 5
        # cycle through with 10 degree angle steps
        for angle in range(0, 360, 10):
            bPtFound, xnew, ynew = CheckPixel1(img, angle, neighborhood, x, y)
            if bPtFound:
                break

    return (bPtFound, xnew, ynew)

def getPixelNorm(image, x, y):
    """returns normalized floats (0.0 - 1.0)"""
    pix = image.getpixel((x, y))
    return (pix[0]/255.0, pix[1]/255.0, pix[2]/255.0)

def setPixelNorm(image, x, y, value):
    val = int(value * 255.0)
    image.putpixel((x, y), (val, val, val))
