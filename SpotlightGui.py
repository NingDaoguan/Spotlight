
class DummyGui:
    "any GUI must implement these functions"

    def messageDialog(self, title, message):
        print '"%s" dialog says "%s"' % (title, message)

    def updateStatusBar(self, text, number):
        print 'status bar0 is "%s"' % text

    def display(self):
        print 'display updated'

    def setWindowTitle(self, title):
        print 'window title is "%s"' % title

    def Yield(self):
        pass

    def showStopButton(self, button):
        print 'enable/disable toolbar buttons'

    def removeStopButton(self, button):
        print 'enable/disable toolbar buttons'

    def drawAoi(self, params, dc=None):
        print 'draw Aoi'

    def showModalDialog(self, type, params=None):
        print 'showModalDialog function'
        return False

    # generic modeless dialog
    # returns a 'dialog' (something that can be passed to the other 2 modeless functions)
    def createModelessDialog(self, type, params, changeNotificationFunction=None):
        """ type is used to instantiate different kinds of dialogs'
        changeNotificationFunction is called when this dialog wants updated
        parameters (i.e., to redraw)changeNotificationFunction is called with a
        dictionary of things the dialog has changed"""
        print 'createModelessDialog type: %s' % type
        return None

    def destroyModelessDialog(self, dialog):
        print 'destroyModelessDialog'

    def updateModelessDialog(self, dialog, params={}):
        ' params is a dictionary of new values for the dialog'
        pass

gui = DummyGui()

###-------- Plug in a different GUI ---------

def setGui(newGui):
    global gui
    gui = newGui
