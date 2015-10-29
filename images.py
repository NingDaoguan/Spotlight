#----------------------------------------------------------------------
# This file was generated by encode_bitmaps.py
#
from wx import ImageFromStream, BitmapFromImage
from wx import EmptyIcon
import cStringIO

catalog = {}
index = []

class ImageClass: pass

def getFastforwardData():
    return \
"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00^IDAT8\x8d\xe5\xd4\xc7\r\x001\x08\x04\xc0]\xdc\x7f\xc9\x0e\r\x180A\xf79\
\xbe\xa0\x91\x08\x82\x94\x81\xee\x90v\xf1\x13t\xaf\xb9\xb5B+g\xa2]\xf0\xb5\
\xfd*\xac\xce\xb4\x02\x9b\x8b\xca\xc2\xee\xf63\xf0\xd3IE\xe1'\x942\x18\xc9\
\xb9h\x14t\xd1\x0ch\xa2YPE+\xe0\x15\xad\x82\x00\xc0\x7f\xff\xd3\x03\xa2U8#N\
\xd4[\x89\x00\x00\x00\x00IEND\xaeB`\x82"

def getFastforwardBitmap():
    return BitmapFromImage(getFastforwardImage())

def getFastforwardImage():
    stream = cStringIO.StringIO(getFastforwardData())
    return ImageFromStream(stream)

def getFastforwardIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getFastforwardBitmap())
    return icon

index.append('Fastforward')
catalog['Fastforward'] = ImageClass()
catalog['Fastforward'].getData = getFastforwardData
catalog['Fastforward'].getImage = getFastforwardImage
catalog['Fastforward'].getBitmap = getFastforwardBitmap
catalog['Fastforward'].getIcon = getFastforwardIcon

#----------------------------------------------------------------------
def getNextData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00sIDAT8\x8d\xed\x921\x16\x80 \x0cC\x93\xc2\xb5<\xbd\xd7\x12pB\xd1\x87\xe8\
k\xcbf\xa6.|\x926\xa4\x04xK\xb4\x0fKN\xc5\x1d:\x02\x9b\xa0O`\xb6;\x1dEz\x13%\
\xb0\xcef\xa7\xdd\x0f\xb4\xd7oS\xb5.\x01\x07\xa7w\xa0\x19\xda\x03\x02\x86\
\xf8#\xc5:\xe4\xb4\xa9/_%!\xf2\x02\x05\x00\xae\xdd4\x9fT\x96\xd3\xd3\x94J\
\xfdP\x7f\x1d=\xf5\xac\xd4\x94\xf2\xef\x1d\xac\x1fBs\xfe\xbc\xc1\x00\x00\x00\
\x00IEND\xaeB`\x82'

def getNextBitmap():
    return BitmapFromImage(getNextImage())

def getNextImage():
    stream = cStringIO.StringIO(getNextData())
    return ImageFromStream(stream)

def getNextIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getNextBitmap())
    return icon

index.append('Next')
catalog['Next'] = ImageClass()
catalog['Next'].getData = getNextData
catalog['Next'].getImage = getNextImage
catalog['Next'].getBitmap = getNextBitmap
catalog['Next'].getIcon = getNextIcon

#----------------------------------------------------------------------
def getOpenData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00\xe8IDAT8\x8d\xad\x92\xcb\r\xc20\x10Dg\xec\x14A\x0f\xf4\x01\x1d \xa4\x94\
\xc1\x19!\xc41upG\xdc)!}\xb8\x89d9\xe0U\x1c\xc7\xf9Xx$k\x13\x7f\x9ew=K\x1a\
\x8b\xd22\xc5\x89\x00\xaa\xdc\x03\xd2w\x12\xfe\xd3X\xfe\x05\x95\xbe\x93\x18\
\x92\x9a+R\xbef\xaf\x91%\x8c\n\x9f\x84\xc6\xb2J-\xe8b.P5zS\x91\xdd\x00\xa5\
\x9bl\x8e5wq\xc2\xa8\'\x80ztA\x12H7\x0b\x8e\x8c\xba\x00\xa8=X/\x08\xbfu\xcf\
\x8ah,\xbcY"\xb2\x13\x91\x8f\x8f\x8d\x8f\xe1\xdc\x10\x01\x88\x9e\x8dG\x04m&@\
\x00Y\x83\xc6.7?\xe9\xf0\xb8\xafW\xab\xba\xde\xf4\x9c\xefS\xe9;\xf9\x99\xf33\
*\x07\xd8\xb6\xc0\xeb=\x98\x964\x8at8\x1e\xb6g\x18\x02\x93\x99\x92\x0e\xe7\
\x13\xb0\xdfo\x03^o\xd3\xb6\x1aA\x01l\x06\xc6%/Bs\xb5\x08-\xa9/\x0e\x99\x98\
\'P-1{\x00\x00\x00\x00IEND\xaeB`\x82'

def getOpenBitmap():
    return BitmapFromImage(getOpenImage())

def getOpenImage():
    stream = cStringIO.StringIO(getOpenData())
    return ImageFromStream(stream)

def getOpenIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getOpenBitmap())
    return icon

index.append('Open')
catalog['Open'] = ImageClass()
catalog['Open'].getData = getOpenData
catalog['Open'].getImage = getOpenImage
catalog['Open'].getBitmap = getOpenBitmap
catalog['Open'].getIcon = getOpenIcon

#----------------------------------------------------------------------
def getPauseData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00yIDAT8\x8d\xe5\x94A\x12\x80 \x08E\x01\xbb\xff\x8d\x89\xd6%\xfc\x8f\x8d\
\xadr\xe7\xf0x\x822\xaa\xda\x90\xdd\xcb\xb6\x1b\xbf\x92\x1e\x1d\xe8t\x0fU\
\x91\x08\x11\x1bC\x19O+=\xdd\x03\xed\x97\xa5\x95\x80\x89K)KD\xf1T\xdai\x11q\
\x93\xb4+D\xbc1\xe0\x8d\xf8&\xed\x8cK\xb6\x9eyS\xfb\xab\xe2\x8cO\x1f\xaa+\
\xae\xb8r\xa4\x98\x18\xc5\xe1\xf0\x97\x95\xb0\x03Q0\x13t\xaeF\xff\xfd\x9f^\
\x13\xfb63\xe2K}\xa4\x00\x00\x00\x00IEND\xaeB`\x82'

def getPauseBitmap():
    return BitmapFromImage(getPauseImage())

def getPauseImage():
    stream = cStringIO.StringIO(getPauseData())
    return ImageFromStream(stream)

def getPauseIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getPauseBitmap())
    return icon

index.append('Pause')
catalog['Pause'] = ImageClass()
catalog['Pause'].getData = getPauseData
catalog['Pause'].getImage = getPauseImage
catalog['Pause'].getBitmap = getPauseBitmap
catalog['Pause'].getIcon = getPauseIcon

#----------------------------------------------------------------------
def getPreviousData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00rIDAT8\x8d\xed\x92Q\x0e\x800\x08C[\xb6kyz\xaf\xe56\xbf\xa6\xe8\x9c\x89\
\x83\xfd\xd9/\x12\x92G\x81\x92\x12\xe0-\xe95JN\xc5\x15j\x01>B\xad@\x00\xa0\
\xbe\xa9\x05H\t\xacu\xf7\xa6\x16\xf1\xfe}\xedVO\xff\xa2\xc6\xe9(\xe8\x15\xea\
\x01n\xd6\xf7P\xacEN\x9b9J\x12"/P\x00\xe0:\xbeuYNOS"\xf5C\xfdu\xe4\xd43RS\
\xc2\xbf\x03\x9c\xea\x1fBG\xfa<\xde\x00\x00\x00\x00IEND\xaeB`\x82'

def getPreviousBitmap():
    return BitmapFromImage(getPreviousImage())

def getPreviousImage():
    stream = cStringIO.StringIO(getPreviousData())
    return ImageFromStream(stream)

def getPreviousIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getPreviousBitmap())
    return icon

index.append('Previous')
catalog['Previous'] = ImageClass()
catalog['Previous'].getData = getPreviousData
catalog['Previous'].getImage = getPreviousImage
catalog['Previous'].getBitmap = getPreviousBitmap
catalog['Previous'].getIcon = getPreviousIcon

#----------------------------------------------------------------------
def getRedoData():
    return \
"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00\x97IDAT8\x8d\xe5\x94K\n\x800\x0cD\x9bV\xf0`\xd6c\x89\xb8\xf1R\x9a\x83\
\x15\x84\xb8\n\xa8\x8d\x89J]\x88\x81\xd9$\xed\xeb'\xd3\x02\xf8\xe0J\x87/N\
\xfc\x14\xb4\xd2\x8a\xf3\x94\xe8\x98\x8bm\r\x8f\xa1\xf3\x94\xa8i\x86,\x8f\
\x98\xc8\x04\x83\x0f\x99\x10\x17r\xae#\xc4%\x13\xe7\xb7\xe3\x8e\xf3U\xe0\x95\
\x05%\xe8\xedF\xc5\xb6\x06\xc4\xdeIW\xc3q\x1b\xca\xcd\xd3\xc0j\xf7\xa5\xd0v\
\xf8\x18\n~4-\xf5\x8a\xf9MKIuK\xa7\x05\x06K\x961\xa5}}\xdc\xe9+Osw\xfa\x7f\
\xff\xa7+\xef\x90bN\x04f\n\x97\x00\x00\x00\x00IEND\xaeB`\x82"

def getRedoBitmap():
    return BitmapFromImage(getRedoImage())

def getRedoImage():
    stream = cStringIO.StringIO(getRedoData())
    return ImageFromStream(stream)

def getRedoIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getRedoBitmap())
    return icon

index.append('Redo')
catalog['Redo'] = ImageClass()
catalog['Redo'].getData = getRedoData
catalog['Redo'].getImage = getRedoImage
catalog['Redo'].getBitmap = getRedoBitmap
catalog['Redo'].getIcon = getRedoIcon

#----------------------------------------------------------------------
def getRewindData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00[IDAT8\x8d\xe5\xd4\xc9\r\x00 \x08\x04@\x17\xfb/Y\xb1\x01@\xae\xc4\x87|\
\x97\xcc\x87\x03\xa09\xba\x8b\xda\xc5\xe7(\xef\xc5\xde\xcc\x85F@\x17\x1a\x05\
\xafh\x064\xd1,\xa8\xa2\x15PD\xab\xa0\x88\x82&\xb4f+3\xd1\x0eX\x1dT\x056W*\
\x0b_\x97?\x03\xbb\xce4\n\xe3\xef\x7fz\x00\xc3\xce8#\xca\xc3\xdbB\x00\x00\
\x00\x00IEND\xaeB`\x82'

def getRewindBitmap():
    return BitmapFromImage(getRewindImage())

def getRewindImage():
    stream = cStringIO.StringIO(getRewindData())
    return ImageFromStream(stream)

def getRewindIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getRewindBitmap())
    return icon

index.append('Rewind')
catalog['Rewind'] = ImageClass()
catalog['Rewind'].getData = getRewindData
catalog['Rewind'].getImage = getRewindImage
catalog['Rewind'].getBitmap = getRewindBitmap
catalog['Rewind'].getIcon = getRewindIcon

#----------------------------------------------------------------------
def getSaveAsData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00\xdcIDAT8\x8d\xb5\x94\xd1\r\x820\x10\x86\xff\x021q\x06c|a\rW`\rS\x1eu\
\x81.\xa0\x8f\xba\x87\x0b\xf8\xc0\x1a\xb7\x87\x89\t\x1c\x0f\xf5j\x02\x05\xa4\
\x94K\xfe@8\xfe\xcb\xd7^{J%)bG\x12\xbd"\x80L^\xb8\xa9yi1\x95\xa4\n\xe8\x90\
\x1ac\\\xf2\x1f\x89G|\x027\xb8|nj\xf6i\x8cT\x9fj&\xb2T\xf86\x8b\x8d1\x0c\x80\
\xe5\xdb\x94\x00\xb0\xa8\xd4`"\xf0f\x8b\xf9\xa4\xa2\xfda\xe7\xa8K\r\x9c/\xc0\
\xed\n|\xde\x81\xa4>\xc2R\xc3y\x83\x8f\x14\x91}\n\xe1\xfd\xf1\xeb~6f\x1c\x8f\
\'\x88\n\xe4y?\xe3%\x9d\xdaO\xfbW\x01\xa0B\xf5\xea\xfb\x83I-\xe1\xd1\x9b\xeb\
\x91v\x0fsH,\xbe\xfb>\x88\xd9\xcb\x97\x0e\x03\xc3\xf3b\x95)\xb5JQ%C:\xe6\xe8\
sEcF\x0b\xb1\xac\xa4p\xc5;\x15\x96\x00\x00\x00\x00IEND\xaeB`\x82'

def getSaveAsBitmap():
    return BitmapFromImage(getSaveAsImage())

def getSaveAsImage():
    stream = cStringIO.StringIO(getSaveAsData())
    return ImageFromStream(stream)

def getSaveAsIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getSaveAsBitmap())
    return icon

index.append('SaveAs')
catalog['SaveAs'] = ImageClass()
catalog['SaveAs'].getData = getSaveAsData
catalog['SaveAs'].getImage = getSaveAsImage
catalog['SaveAs'].getBitmap = getSaveAsBitmap
catalog['SaveAs'].getIcon = getSaveAsIcon

#----------------------------------------------------------------------
def getSpotlightSmallData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\
\x00\x00\x00\x90\x91h6\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\
\x02sIDAT(\x91]\x92\xcbn\xd3@\x14@\xafg\xae\xc7\xe3\xd8\xb1\x13\xe7YJ\x93\
\x94\x8a>h\x05\x15\xad\xc4\xff\xf0\'|\x11\xff\xc0\x86\r*\x12BU\x1a\xa1J\rI\
\x93\xb4q\x9d\xd8\xf1{2\xc3\x02\x84\x04g}\xce\xeeh\x1f>\xbc\xd7u\x92$\xc5x\
\xbc\xbc\xba\xba\r\xc3\x04\xfe\x853vq|\xfc\xee\xf4\xd4\xe2\xfc\xebhD\xb2\xac\
 \x84\xd86\xef\xf5\x9a\xe7\xe7\xfb\x8eS\xf9\xcf~\xf3\xf2\xe5\xe5\xf1q\xddq\
\xd2<\x1f\x8d\xc7$\x086Bl)%\xb6\xcd\xfb\xfd\xe6\xeb\xd7\x83\xbf\rg\xec\xec\
\xe0\xe0\xe2\xe8\xa8\xe5y\x1a\xc0\xfdry\xbf\\\xd2v\xbb\xd9h8\x9c\xeb\x88\x14\
\x91\x9a&cL\x0f\xc3\x84\x009\x19\x0c\xde\x1e\x1d\xed\xb6\xdbL\xd7\xa38\xbe\
\xba\xb9\xb9\x9b\xcd(\xe7\x95v\xdb\xb5,\xce\x18RJt\x1d+\x15V\xe1\xbci\xd7_\
\xf5\xf7{\xddn\xc54\x85\x10?\x17\x8b/\xc3a\x94$\x18E\xe9d\xe2{^\xd50\xf0w\
\xc3tw\xb7\xd5\xe6\xc2"\x05r\xe4\x1a@\x9c\xa6\xe3\xc5"\x08C\x00@I\xf0\xe7t\
\xb5\xd7K,\x9b3\x83p\x83\r\x9e\x1ft\xbc\xae\xae\xe8\xc6\x8f\x17\x13?\\\xc7~\
\x18\x8d\x1f\x1e\x0b\x05\x80:\x02\x1a\xebT\xcd\x16\x9bF\xab^uX\xab\xd1}svYs\
\x9b\x94W\xef\x9f\xb25\xbd~\xfa~5\x0bV\x0f\x9bD\xa1\t \t \xdbjt2\xdf\xa4\x99\
\xf4\xaa\xde\xe1\xfe\x89,\xb7\x80\\i\xc4\xe5\xa8\xcb\xc4t\xf9\xaa\xc8b!\x01\
\x11\x90\x11 T\xa3X\n \x825\x9c&\xb0\x96\xd3\xea1\xd3\x9e\xce\x83o\xa31\xcat\
\x8b\xb2\xda0j5K\xa3\x08\x84\xa2F\xa8k\xf2\xbd\xce3\xd3h\x832f\x19\x89g\xc9\
\x8e\x95}\xfc44\x084\x08\xdc\x86yZo\xf4\xce\xa8\x1a\xde\xf9~\x84\xb6\xed\xd6\
\x9f\xbd0\x06\'\x8b\xce\xc1\xb0\xbe\xdb\xac[\xd30\xfc<\x91\xbe\xe1\x99\xae\
\xb7\xcc\xc2\xf9\xe3u:\x1d+\r\xed\xfe^\xa2\xee\x91\xd6vr\xa7\x13P+M\xd5*\xab\
\xba|\xdf\xa4k-\xfdQ\x1c\xf6\x1f\x96y\x12\xac\xe2Z+\xab\xf2\x04\xe8f:\x97\
\xe6\n3\xb9\x95\x9b(\xa3\x8fX\x88\xc78\xa6\x939}\xde!\x95.<mD\xba\x12\xdb@H!\
\xd6y\xb9\xf4\xcb\xf9\xa2\x0c\xd6X\x84\xbe(2-\xf2\t\xab\x002\xb8\xd6\x14(\
\xa9mA\xe6J$J\x14P\x96\x90\xe7*\xcbTY\x82R(\xd3Hf1\x10\r\x80\xfcYTI\x90\x12@\
\xc1\xff(\x00\xf8\x05m04TXn\xae\xa4\x00\x00\x00\x00IEND\xaeB`\x82'

def getSpotlightSmallBitmap():
    return BitmapFromImage(getSpotlightSmallImage())

def getSpotlightSmallImage():
    stream = cStringIO.StringIO(getSpotlightSmallData())
    return ImageFromStream(stream)

def getSpotlightSmallIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getSpotlightSmallBitmap())
    return icon

index.append('SpotlightSmall')
catalog['SpotlightSmall'] = ImageClass()
catalog['SpotlightSmall'].getData = getSpotlightSmallData
catalog['SpotlightSmall'].getImage = getSpotlightSmallImage
catalog['SpotlightSmall'].getBitmap = getSpotlightSmallBitmap
catalog['SpotlightSmall'].getIcon = getSpotlightSmallIcon

#----------------------------------------------------------------------
def getStepbackData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00SIDAT8\x8d\xe5\xd4\xc1\r\x000\x08\x02\xc0\xa2\xfb\x8f\xdc\xda\x11\x04\
\xc3\xa3I\x1d\xe0>\x80@\xe4r_\xd8\xc5\xa7\xd0:\xbb\xach\x07\xca(\x03J(\x0b\
\xd2\xa8\x02R\xa8\n\xb6\xe8\x04lQD\xc2\x8eNa*(\x15\xa6+\xa5\xc0R\xf9YX\x9e)\
\x03\xe3\xef\x7fz\x01nS\x1c*\xfc\xbdf\x10\x00\x00\x00\x00IEND\xaeB`\x82'

def getStepbackBitmap():
    return BitmapFromImage(getStepbackImage())

def getStepbackImage():
    stream = cStringIO.StringIO(getStepbackData())
    return ImageFromStream(stream)

def getStepbackIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getStepbackBitmap())
    return icon

index.append('Stepback')
catalog['Stepback'] = ImageClass()
catalog['Stepback'].getData = getStepbackData
catalog['Stepback'].getImage = getStepbackImage
catalog['Stepback'].getBitmap = getStepbackBitmap
catalog['Stepback'].getIcon = getStepbackIcon

#----------------------------------------------------------------------
def getStepforwardData():
    return \
"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00UIDAT8\x8d\xe5\xd4\xdb\t\x000\x08\x03\xc0D\xf7\x1f\xb9\x8f\x11LD\xe8G\
\x1d\xe0\xc0D$#1=1.>A\xcf^g\x1c\xed\xc2\xd2\xfa.,g\xea\xc0VQ*l\xb7\xaf\xc0\
\xad\x93\xaa\xe0\x16\xcaH\x8e\xa2\x15h\xa3\nh\xa1*(\xa3\x0e(\xa1.\x08\x00\
\xfc\xfb\x9f^m\xab\x1c*'\x19\x8d\xa4\x00\x00\x00\x00IEND\xaeB`\x82"

def getStepforwardBitmap():
    return BitmapFromImage(getStepforwardImage())

def getStepforwardImage():
    stream = cStringIO.StringIO(getStepforwardData())
    return ImageFromStream(stream)

def getStepforwardIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getStepforwardBitmap())
    return icon

index.append('Stepforward')
catalog['Stepforward'] = ImageClass()
catalog['Stepforward'].getData = getStepforwardData
catalog['Stepforward'].getImage = getStepforwardImage
catalog['Stepforward'].getBitmap = getStepforwardBitmap
catalog['Stepforward'].getIcon = getStepforwardIcon

#----------------------------------------------------------------------
def getStopData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00\x9dIDAT8\x8d\xb5\x94K\x0e\x80 \x0cD;\xc5\xa5W1\xde\xff\x18\x86\x03x\t\
\xb7\x8a\x0b\x83\x86R\x82H\x9d\rR\x86\x97~\x0c\x00;\xb2\xd6\xa0\x05\x97c\x0f\
o\x013;\xc8\x18\xf7\x00K~\xae\x19\xbe\x80\xb9t\xd0\x03f\x0b\xa0\x04g=\xb5P2\
\xfd)<\t{\xa0y\x1f\x95e\xea\x81\xdb W\xf9\xad\xedU\xa8\x852\xe8\x14BRVM\x9a7\
\xe9i,\xa5\x05\xba*\xe5\x17\x07\xf56\xb3\x8d\x88F\xe1\x01\xd8\x99\xfd\xa7D\
\xd7[\xf0\xdf\xa0\xb4\x97\xe6\x8b"\x87e\xa0\x17\x98@{\xc0\xf2^\xd6\xd3V\xb0\
\xe6?\x01\xc9\x94H\xef\xfc\x0e\x0f\x8e\x00\x00\x00\x00IEND\xaeB`\x82'

def getStopBitmap():
    return BitmapFromImage(getStopImage())

def getStopImage():
    stream = cStringIO.StringIO(getStopData())
    return ImageFromStream(stream)

def getStopIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getStopBitmap())
    return icon

index.append('Stop')
catalog['Stop'] = ImageClass()
catalog['Stop'].getData = getStopData
catalog['Stop'].getImage = getStopImage
catalog['Stop'].getBitmap = getStopBitmap
catalog['Stop'].getIcon = getStopIcon

#----------------------------------------------------------------------
def getTrackContinuousData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00gIDAT8\x8d\xedTA\x0e\xc00\x08\x02\xed\xff\x7f\xbcuW\xd3\xe8\xb2N\xbd\x95\
\x9b1\x12\x04#)\x8ajH9#\x80\x01\x00\xf3\xbe\xe6\xee E\x19\xf5Z\x942\xf2\xd4\
\xaa\x7fS\xe5!\xad\xd4\xb3.E\x1ae1*\x08W\xab~+\xb5>S\x94\xb6N\xad\x1f\x05\
\x98\x0e\xca#n\xb9\xd3CZ\x8f\xed\xe3\xff\xf2\xd1\xc2\x87\x92A\xcb\xfa\x0f\
\xd0L\x1cCP\xacI\x1d\x00\x00\x00\x00IEND\xaeB`\x82'

def getTrackContinuousBitmap():
    return BitmapFromImage(getTrackContinuousImage())

def getTrackContinuousImage():
    stream = cStringIO.StringIO(getTrackContinuousData())
    return ImageFromStream(stream)

def getTrackContinuousIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getTrackContinuousBitmap())
    return icon

index.append('TrackContinuous')
catalog['TrackContinuous'] = ImageClass()
catalog['TrackContinuous'].getData = getTrackContinuousData
catalog['TrackContinuous'].getImage = getTrackContinuousImage
catalog['TrackContinuous'].getBitmap = getTrackContinuousBitmap
catalog['TrackContinuous'].getIcon = getTrackContinuousIcon

#----------------------------------------------------------------------
def getTrackOneData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00aIDAT8\x8d\xed\x94\xc1\n\xc0 \x0cC\x93\xd6\xff\xff\xe3\xcd\x9d\x842\xcc\
\xa0Xa\x07{\x8d>\x1f\x05C\x9a\xa3z\xac\x9c\x08\xa0\x01@\xbf\xaf\x9e\xbdHs\
\xaal\x8b)\xd5N\xa3\xfd\x97\xd5l\xb6\x98\x1e\xe8\x81\xfe\x11\xfa\xfe\xe6e\
\xa6\x11\xdcV\x8cf9\xcd\x99\x82\xaa\x0e\x18\x8f\x8d\\B\xb3%\x12\xcf\xcb\x96Z\
\x99\x07\xa2\x16\x1c>1f<\x1a\x00\x00\x00\x00IEND\xaeB`\x82'

def getTrackOneBitmap():
    return BitmapFromImage(getTrackOneImage())

def getTrackOneImage():
    stream = cStringIO.StringIO(getTrackOneData())
    return ImageFromStream(stream)

def getTrackOneIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getTrackOneBitmap())
    return icon

index.append('TrackOne')
catalog['TrackOne'] = ImageClass()
catalog['TrackOne'].getData = getTrackOneData
catalog['TrackOne'].getImage = getTrackOneImage
catalog['TrackOne'].getBitmap = getTrackOneBitmap
catalog['TrackOne'].getIcon = getTrackOneIcon

#----------------------------------------------------------------------
def getUndoData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00\xa1IDAT8\x8d\xd5\x94A\n\xc30\x0c\x04\xb5r\xa1\x0fs\xfb\xac\x10r\xe9\xa7\
\x12=\xcc\x10PO\x86\xc4\xae\x1c+\xa4\x87\x08\xf6`Y\x1e\xb0\xb4\x08\xe0@W\x07\
_N\xbc\x15\xf4\xd1S\xb4\xccI\xcb\xdc\xeb\xfd\xc4i\xe82\'\x8dq\xaa\xf2"IM08\
\xecD4\xa8\xc8\xaa\xe0@"\xab\xe6s\xa9m]\xc5\xb0\xa0G\x0f[\xf7\xe6\xa0b\x9cHd\
l\xf6\xce\x8a\x9f\xd0\x0c\xcc=\xf5B\xcdAm\x87\x03\xa7\xf1*(\xf8\xe3\xfen\x19\
\x7f1\x7f5\xd5\x1e\xb9-u$\xa2\xa1\t\x04\x07\x82w\xf5e7\xb4\xac\xe6\x86\xf6\
\xc4}V\xdf\x17\xf5\xcfbQ\xdd\xf58\xd8\x00\x00\x00\x00IEND\xaeB`\x82'

def getUndoBitmap():
    return BitmapFromImage(getUndoImage())

def getUndoImage():
    stream = cStringIO.StringIO(getUndoData())
    return ImageFromStream(stream)

def getUndoIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getUndoBitmap())
    return icon

index.append('Undo')
catalog['Undo'] = ImageClass()
catalog['Undo'].getData = getUndoData
catalog['Undo'].getImage = getUndoImage
catalog['Undo'].getBitmap = getUndoBitmap
catalog['Undo'].getIcon = getUndoIcon

#----------------------------------------------------------------------
def getZoominData():
    return \
"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00\xafIDAT8\x8d\xed\x93\xc1\x15\xc3 \x0cC%\xe8(\x0c\xc2\x18\x8c\x981\x18$\
\xab\x80{hi\x08\xc54i\xe8\xad\xbe\xe1\xc7\xfbHF&\x8d\xc5\xec2\xd3\x89\x00n\
\xbd\xa6\xe4$m\x8f\xc6\xf2k\xa8\xe4$\xcb\xfa\xc6Dp\x94\xa3\xe0\x9d}\r\x08\
\x00\xcb*]\x07C\xe8\x08x\x16\xfc\x93\x8f\xfaC\x1fEc\x19\xdc81\xc1\x111\xf6s\
\\\x17\xdb5\xed\xa5\xa0<\x16\xe3\xd6\xf3^_\x88\x1dTr\x12\x1aKm\xa3$'9\x02\
\xeeBU_\xcf;\x9f\xc0\xa7?\x8a\xc6\xd2\xfb\xed\xdc\x9b1\x01\xa8C\x1f\xa9.\xa0\
\xa2\xbaV|\xda\xbe\x06\xafE\\\xce\xe9K]%fJ\xf8[ww\xfb\x9ab\xc7\x11o\x97^\x00\
\x00\x00\x00IEND\xaeB`\x82"

def getZoominBitmap():
    return BitmapFromImage(getZoominImage())

def getZoominImage():
    stream = cStringIO.StringIO(getZoominData())
    return ImageFromStream(stream)

def getZoominIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getZoominBitmap())
    return icon

index.append('Zoomin')
catalog['Zoomin'] = ImageClass()
catalog['Zoomin'].getData = getZoominData
catalog['Zoomin'].getImage = getZoominImage
catalog['Zoomin'].getBitmap = getZoominBitmap
catalog['Zoomin'].getIcon = getZoominIcon

#----------------------------------------------------------------------
def getZoomoutData():
    return \
"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x15\x00\x00\x00\x13\x08\x06\
\x00\x00\x00\x7fNF\x8b\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\
\x00\xaaIDAT8\x8d\xed\x93\xd1\x11\xc3 \x0cC%\xe8(\x0c\xc2\x18\x8c\x981\x18$\
\xab\x80\xfb\xd1\xa3\xa1\xc1p\xd0\xa4\x7f\xd5\x1f>\xee!\x19\x9b4\x16w\xcb\
\xdcN\x04\xf0\xd0\x8a\x92\x93\x9ck4\x96_C%'\xd9\xf6\x86\x89\xe0(\xb3\xe0\x8f\
\xf8= \x00l\xbb\xa8\t\x86\xd0\x11p\x15\xfc\x93\x8f\xfaC_\xa2\xb1\x0cn<1\xc1\
\x111\xeas\\\x8b\xe75\xd5\xa6\xa0<\x16\xe3Q\xf3\xbe\xbf\x10\r\xb4\x80\x9b\
\x8b\xc6Rr\x92\x19\xb0\n\x1di\x06\xbc\xfcQ4\x96\xde\x1fg\xad\xc7\x04\xd0m\
\xfah\xd7\x0b\xa8\xb8\xae\x1d/\xc7\xef\xc1k\x13\x97\xe7\xf4\xed\xaeJu\xd9\
\xa9\xa6'i\xf8V\xc5\x12\xe6\xb0\x05\x00\x00\x00\x00IEND\xaeB`\x82"

def getZoomoutBitmap():
    return BitmapFromImage(getZoomoutImage())

def getZoomoutImage():
    stream = cStringIO.StringIO(getZoomoutData())
    return ImageFromStream(stream)

def getZoomoutIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getZoomoutBitmap())
    return icon

index.append('Zoomout')
catalog['Zoomout'] = ImageClass()
catalog['Zoomout'].getData = getZoomoutData
catalog['Zoomout'].getImage = getZoomoutImage
catalog['Zoomout'].getBitmap = getZoomoutBitmap
catalog['Zoomout'].getIcon = getZoomoutIcon