#!/usr/bin/env pythonw

# Video file frame reader, using QuickTime

import sys
import string
import struct
import os

from Carbon import Qt
from Carbon import QuickTime
from Carbon import Qd
from Carbon import Qdoffs
from Carbon import QDOffscreen

debug = 0 # set to 1 to enable debugging print statements

def writeError(outputImageName, message):
    """ format an error message in the output file for spotlight to read """
    print message
    f = open(outputImageName, "w")
    l = len(message)
    f.write(struct.pack('i', 4)) # offset to start of error message
    f.write(struct.pack('i', l)) # length of error message
    f.write(message)
    f.close()
    sys.exit(1)

def readFrame(inputMovieName, outputImageName, frameNumber):
    try: os.unlink(outputImageName) # delete the existing outputImageName, if it exists
    except: pass

    try:
        Qt.EnterMovies()
        fd = Qt.OpenMovieFile(inputMovieName, 0)
        movie, junk1, junk2 = Qt.NewMovieFromFile(fd, 0, 0)
        try:
            videotrack = movie.GetMovieIndTrackType(1, QuickTime.VisualMediaCharacteristic, QuickTime.movieTrackCharacteristic)
            videomedia = videotrack.GetTrackMedia()
        except Qt.Error:
            videotrack = videomedia = None
        if videotrack:
            x0, y0, x1, y1 = movie.GetMovieBox()
            width, height = x1-x0, y1-y0
            old_port, old_dev = Qdoffs.GetGWorld()
            try:
                movie_rect = (0, 0, width, height)
                gworld = Qdoffs.NewGWorld(32,  movie_rect, None, None, QDOffscreen.keepLocal)
                pixmap = gworld.GetGWorldPixMap()
                Qdoffs.LockPixels(pixmap)
                Qdoffs.SetGWorld(gworld.as_GrafPtr(), None)
                Qd.EraseRect(movie_rect)
                movie.SetMovieGWorld(gworld.as_GrafPtr(), None)
                movie.SetMovieBox(movie_rect)
                movie.SetMovieActive(1)
                movie.MoviesTask(0)
                movie.SetMoviePlayHints(QuickTime.hintsHighQuality, QuickTime.hintsHighQuality)
            finally:
                Qdoffs.SetGWorld(old_port, old_dev)
        # finished with Quicktime initialization

        QTSearchFlags = QuickTime.nextTimeMediaSample|QuickTime.nextTimeEdgeOK
        startTime, frameDuration =  videomedia.GetMediaNextInterestingTime(QTSearchFlags, 0, 1.0)
        # startTime is time at start of movie (start offset)
        # frameDuration is the number of video time units that pass each frame (in videotimescale units)
        if debug: print "frameDuration", frameDuration
        movieDuration = videotrack.GetTrackDuration() # in movietimescale units
        if debug: print "movieDuration", movieDuration
        movietimescale = movie.GetMovieTimeScale()
        if debug: print "movietimescale", movietimescale
        videotimescale = videomedia.GetMediaTimeScale()
        if debug: print "videotimescale", videotimescale
        movieDurationSeconds = float(movieDuration) / movietimescale
        if debug: print "movieDurationSeconds", movieDurationSeconds
        frameLengthSeconds = float(frameDuration) / videotimescale
        if debug: print "frameLengthSeconds", frameLengthSeconds, "(inverse)", 1.0/frameLengthSeconds
        totalFrames = movieDurationSeconds / frameLengthSeconds
        if debug: print "totalFrames", totalFrames, "(rounded)", int(round(totalFrames))
        frames = int(round(totalFrames))

        if debug: print "reading frame", frameNumber, "at videotime", startTime+frameNumber*frameDuration
        timestamp = videomedia.GetMediaNextInterestingTimeOnly(QTSearchFlags, startTime+frameNumber*frameDuration, 1)
        if timestamp < 0:
            raise "Quicktime error", "error %s, frame search failed at videotime %s" % (timestamp,startTime+frameNumber*frameDuration)
        moviecurtime, junk1, junk2 = Qt.ConvertTimeScale((timestamp, videotimescale, None), movietimescale)

        # I don't know why this time adjustment is needed, but it sometimes seeks to the wrong frame without it
        movieframetime, junk1, junk2 = Qt.ConvertTimeScale((frameDuration, videotimescale, None), movietimescale)
        if debug: print "movieframetime", movieframetime
        if movieframetime > 1:
            moviecurtime += 1

        movie.SetMovieTimeValue(moviecurtime)
        movie.MoviesTask(0)

        # shuffle the offscreen PixMap data, because it may have funny stride values and alpha channel
        rowbytes = Qdoffs.GetPixRowBytes(pixmap)
        start = 0
        rv = []
        for i in range(height):
            nextline = Qdoffs.GetPixMapBytes(pixmap, start, width*4)
            for j in range(width):
                rgb = nextline[4*j+1:4*j+4] # skip alpha plane data at nextline[4*j]
                rv.append(rgb)
            start = start + rowbytes
        data = string.join(rv, '')

        if debug: print "timestamp found", timestamp, "length of image data", len(data)
        videomedia = videotrack = movie = None # this is required to deallocate memory

    except Exception, err:
        writeError(outputImageName, err.__str__())

    f = open(outputImageName, "w")
    f.write(struct.pack('i', 0))      # error code offset, 0 for no error
    f.write(struct.pack('i', frames)) # video frames
    f.write(struct.pack('i', width))  # video width
    f.write(struct.pack('i', height)) # video height
    f.write(struct.pack('i', 3))      # video planes
    f.write(struct.pack('i', 8))      # bits per plane
    f.write(data)                     # the raw image itself
    f.close()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print sys.argv
        print "usage:\n  %s inputMovieName outputImageName frameNumber" % sys.argv[0]
        sys.exit(1)

    inputMovieName = sys.argv[1]
    outputImageName = sys.argv[2]
    frameNumber = string.atoi(sys.argv[3])

    readFrame(inputMovieName, outputImageName, frameNumber)

    sys.exit(0)
