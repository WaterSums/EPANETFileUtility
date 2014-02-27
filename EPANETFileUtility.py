# ex:set ts=4 sw=4: <- for vim
#
# EPANET File Utility
# Uses EPAENTOutputFile.py to read the EPANET output file into memory and
# then displays the content in different ways.
#
# Dependencies:
# - Python 2.6 or 2.7 (32- or 64-bit)
# - wxPython 3.0.0 (32- or 64-bit to match installed version of Python)
# - EPANETOutputFile/EPANETOutputFile.py
#
# Available translations/locales:
# en_AU.UTF-8

import wx
import wx.gizmos
import wx.propgrid as wxpg
import os
import platform
import codecs
import sys
import gettext
from EPANETOutputFile import EPANETOutputFile

from DataPage import DataPage
from TablePage import TablePage
from ExportPage import ExportPage


_hasXLRD = True
try:
    import xlrd
    #_hasXLRD = False
except ImportError:
    _hasXLRD = False


_hasXLWT = True
try:
    import xlwt
    #_hasXLWT = False
except ImportError:
    _hasXLWT = False


_hasXLUTILS = True
try:
    import xlutils
    #_hasXLUTILS = False
except ImportError:
    _hasXLUTILS = False


def main():

    # New versions of wxPython require us to create the app very early, so...
    # Create a new app, don't redirect stdout/stderr to a window.
    app = wx.App(False)

    # mostly taken from the wxPython internationalisation example...
    # but in the end not using wx Locale because of the difficulty of
    # mapping from language name (string) to wx language constant (number)

    # initialise language settings:
    path = sys.path[0].decode(sys.getfilesystemencoding())
    try:
        langIni = codecs.open(os.path.join(path,u'language.ini'),'r', 'utf-8')
    except IOError:
        #language = u'en' #defaults to english
        #print('Could not read language.ini')
        language = None
        pass
    else:
        language = langIni.read()

    locales = {
        u'en' : (wx.LANGUAGE_ENGLISH, u'en_US.UTF-8'),
        #u'es' : (wx.LANGUAGE_SPANISH, u'es_ES.UTF-8'),
        #u'fr' : (wx.LANGUAGE_FRENCH, u'fr_FR.UTF-8'),
        }
    langdir = os.path.join(path,u'locale')
    if language is None:
        Lang = gettext.translation(u'EPANETFileUtility', langdir,
                fallback=True)
        Lang.install(unicode=1)
        if Lang.__class__.__name__ == 'NullTranslations' and str(Lang.__class__) == 'gettext.NullTranslations':
            print('Language not found')
        else:
            try:
                language = Lang._info['language']
                print('Language %s found.' % language)
            except (KeyError):
                print('Language found (details not available).')
        # Lang.info() content seems to depend on the .mo file containing
        # the correct language information.  If it is not set, the list
        # returned is empty and there doesn't seem to be any way to find
        # the information
        #print('Lang.info() = %s' % Lang.info())
        #language = Lang._info['language']
        # TODO convert from language name (string) to wx.LANGUAGE_... (number)
        #mylocale = wx.Locale(language, wx.LOCALE_LOAD_DEFAULT)
    else:
        Lang = gettext.translation(u'EPANETFileUtility', langdir, languages=[language])
        Lang.install(unicode=1)
        #mylocale = wx.Locale(locales[language][0], wx.LOCALE_LOAD_DEFAULT)

    if platform.system() == 'Linux':
        try:
            # to get some language settings to display properly:
            os.environ['LANG'] = locales[language][1]

        except (ValueError, KeyError):
            pass


    # A Frame is a top-level window.
    frame = MyFrame(None, _("EPANET File Utility"))
    app.MainLoop()

def getNextImageID(count):
    imID = 0
    while True:
        yield imID
        imID += 1
        if imID == count:
            imID = 0
    

"""
Our main panel contains the following:
    - a menu bar
    - a Frame with a box sizer containing a MyListbook with pictures down the
      LHS for the Data/Tables/Graphs/Export options.
      At the start, we put a box sizer and a Panel containing a box sizer
      with a ColouredPanel in each page: this
      must be replaced with valid content when a file is loaded
    - TODO allow file name to be specified on the command line
    - at startup time, we open a data file and build an EPANETOutputFile object
      which we display by:
      - creating a box sizer in the MyListbook 'Data' page and adding to it:
        - a PropertyGridManager with 4 pages, viz:
          - Prolog: properties read from the prolog of the data file but not
            including the node and link information
          - Energy Usage: a single property
          - Dynamic Results: a property grid
          - Epilog: a property grid
        - a box sizer (treesizer) in which we switch TreeListCtrls as necessary
          for the different pages of the PropertyGridManager
"""
class MyFrame(wx.Frame):

    """ We simply derive a new class of Frame. """

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800,600),
                #style = wx.SIMPLE_BORDER | wx.TAB_TRAVERSAL
                )
        self.control = MyListbook(self, -1, None)
        self.basetitle = title
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(self.control, 1, wx.GROW)
        self.dataPage = None
        self.tablePage = None
        self.exportPage = None
        self.dirname = ''
        self.filename = None
        self.epanetoutputfile = None

        il = wx.ImageList(80, 80)
        bmp = wx.Bitmap('images/led_circle_yellow.png', wx.BITMAP_TYPE_PNG)
        il.Add(bmp)
        bmp = wx.Bitmap('images/led_circle_orange.png', wx.BITMAP_TYPE_PNG)
        il.Add(bmp)
        bmp = wx.Bitmap( 'images/led_circle_blue.png', wx.BITMAP_TYPE_PNG)
        il.Add(bmp)
        bmp = wx.Bitmap('images/led_circle_green.png', wx.BITMAP_TYPE_PNG)
        il.Add(bmp)
        bmp = wx.Bitmap('images/led_circle_purple.png', wx.BITMAP_TYPE_PNG)
        il.Add(bmp)
        bmp = wx.Bitmap('images/led_circle_red.png', wx.BITMAP_TYPE_PNG)
        il.Add(bmp)
        bmp = wx.Bitmap('images/led_circle_grey.png', wx.BITMAP_TYPE_PNG)
        il.Add(bmp)
        bmp = wx.Bitmap('images/led_circle_black.png', wx.BITMAP_TYPE_PNG)
        il.Add(bmp)

        self.control.AssignImageList(il)
        imageIdGenerator = getNextImageID(il.GetImageCount())


        # Now make a bunch of panels for the list book

        colourList = [ "Yellow", "Coral", "Medium orchid", "Green", ]
        titleList = [   _("Data"),
                        _("Tables"),
                        _("Graphs"),
                        _("Export"),
                    ]

        for i in range(len(titleList)):

            colour = colourList[i]
            title = titleList[i]

            if i == 0:
                self.dataPage = win = DataPage(self, self.control, colour)
                self.control.AddPage(win, title, imageId=imageIdGenerator.next())

            elif i == 1:
                self.tablePage = win = TablePage(self, self.control, colour)
                self.control.AddPage(win, title, imageId=imageIdGenerator.next())

            elif i == 2:
                win = self.makeColourPanel(colour)
                self.control.AddPage(win, title, imageId=imageIdGenerator.next())
                sizer = wx.BoxSizer(wx.VERTICAL)
                win.win.SetSizer(sizer)
                st = wx.StaticText(win.win, -1,
                              _(
"""EPANET File Utility

Displaying graphs is not yet supported."""))
                sizer.Add(st, 1, wx.GROW | wx.ALL, 10)


            elif i == 3:
                self.exportPage = win = ExportPage(self, self.control, colour)
                self.control.AddPage(win, title, imageId=imageIdGenerator.next())
            else:
                win = self.makeColourPanel(colour)
                self.control.AddPage(win, title, imageId=imageIdGenerator.next())
                win = self.control.GetPage(i)
                st = wx.StaticText(win.win, -1,
                          _("EPANET File Utility."),
                          wx.Point(10, 10))


        #win = self.makeColourPanel(colour)
        #st = wx.StaticText(win.win, -1, "this is a sub-page", (10,10))
        #self.control.AddSubPage(win, 'a sub-page', imageId=imageIdGenerator.next())

        self.control.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.control.OnPageChanged)
        self.control.Bind(wx.EVT_LISTBOOK_PAGE_CHANGING, self.control.OnPageChanging)

        # A Statusbar in the bottom of the window used with menu help text, etc.
        self.CreateStatusBar()
        self.SetStatusBarPane(0)

        # Setting up the menu.
        filemenu= wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        # wx.ID_OPEN
        menuOpen = filemenu.Append(wx.ID_OPEN, _("&Open..."),_(" Open an EPANET output file"))
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        menuAbout = filemenu.Append(wx.ID_ABOUT, _("&About"),_(" Information about this program"))
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT,_("E&xit"),_(" Terminate the program"))
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,_("&File")) # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)

        # we need a Listbook where each page contains a PropertyGrid
        # as long as Property Grids can have more than 2 columns (for diffing.)
        # possibly a Treebook would also work.
        # we need to be able to show graphs as well as just tabular output
        # and also options to export the data in a controlled way.


        # TODO iff no filename has been given, open a file
        #self.OnOpen(None)
        # after upgrading to wxPython 3.0.0 we can't call OnOpen any more
        # as the Open panel displays and then closes with a cancel
        # message.  Instead we bind to the idle event which is
        # called after startup is complete.  This works.
        self.Bind(wx.EVT_IDLE, self.OnStartup)


    def OnStartup(self, event):
        self.Unbind(wx.EVT_IDLE)
        self.OnOpen(event)
        event.Skip()

    def OnOpen(self, event):
        """ Open a file"""
        dlg = wx.FileDialog(self, _("Choose a file"), self.dirname, "", "*", wx.OPEN)
        try:
            result = dlg.ShowModal()
            if result == wx.ID_OK:
                self.filename = dlg.GetFilename()
                self.dirname = dlg.GetDirectory()
                progress = MyProgressDialog(200)

                try:
                    progress.SetStepLimits(0,100)
                    self.epanetoutputfile = eof = EPANETOutputFile.EPANETOutputFile([
                        '-vs',
                        '--demo_all',
                        # os.path.join(self.dirname, self.filename)
                        self.dirname+os.sep+self.filename],
                        progress)

                    progress.SetStepLimits(100,200)
                    progress.Update(1,_('Displaying data'))

                    # configure the data, tables and export pages
                    self.dataPage.OnOpen(event, progress)
                    self.tablePage.OnOpen(event, progress)
                    self.exportPage.OnOpen(event, progress)

                    #self.SetAutoLayout(True)
                    self.Layout()

                    progress.Update(100,_('Done'))

                #except Exception as ex:
                #    #print(ex)
                #    raise ex
                finally:
                    progress.Hide()
                    progress.Destroy()

                self.SetTitle('%s: %s' % (self.basetitle, self.filename))

            else:
                #print("FileDialog.ShowModal selection didn't work: returned %s" % result)
                pass

        except Exception as ex:
            print(ex)
            errdlg = wx.MessageDialog(self, str(ex), _('Error'), style=wx.OK | wx.ICON_ERROR)
            errdlg.ShowModal()
            errdlg.Destroy()
        finally:
            dlg.Destroy()

    def OnAbout(self, event):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, _("EPANET File Utility by Mark Morgan, WaterSums."), _("About EPANET File Utility"), wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self, event):
        self.Close(True)

    def makeColourPanel(self, colour):
        from ColouredPanel import ColouredPanel
        p = wx.Panel(self.control, -1)
        p.win = ColouredPanel(p, colour)
        p.Sizer = wx.BoxSizer(wx.VERTICAL)
        p.Sizer.Add(p.win, 1, wx.GROW)
        return p



class MyProgressDialog(wx.ProgressDialog):
    def __init__(self, maxval):
        self.maxval = 200
        self.rangemin = 0
        self.rangemax = 200
        self.progress = wx.ProgressDialog(
                            _('Loading output file...'),
                            _('Reading output file...'),
                            self.maxval,
                            style = wx.PD_APP_MODAL
                                    | wx.PD_AUTO_HIDE
                                    | wx.PD_ELAPSED_TIME
                                    | wx.PD_ESTIMATED_TIME
                                    | wx.PD_REMAINING_TIME
                                    )

    def SetStepLimits(self, rangemin, rangemax):
        # make sure these limits are in the range 0-maxval
        self.rangemin = max(0, min(self.maxval, rangemin))
        self.rangemax = max(self.rangemin, min(self.maxval, rangemax))
        #print('MyProgress step limits: %d to %d' % (rangemin, rangemax))

    def Update(self, value, newmsg = None):
        # make sure value is in the range 0-100 (%)
        value = max(0, min(100, value))
        value = self.rangemin + int(float(value) *
                float(self.rangemax - self.rangemin) / 100.0)
        #print('MyProgress value: %d' % value)
        self.progress.Update(value, newmsg)
    
    def Hide(self):
        self.progress.Hide()

    def Destroy(self):
        self.progress.Destroy()


class MyListbook(wx.Listbook):
    def __init__(self, parent, id, log):
        wx.Listbook.__init__(self, parent, id, style=
                            #wx.BK_DEFAULT
                            #wx.BK_TOP
                            #wx.BK_BOTTOM
                            wx.BK_LEFT
                            #wx.BK_RIGHT
                            #, size = wx.DefaultSize
                            )
        self.log = log

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print('OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()



version = "0.1.0.0"

if __name__ == '__main__':
    if 'unicode' not in wx.PlatformInfo:
        print(_("\nInstalled wxPython version: %s\nYou need a unicode build of wxPython to run this application.\n")%wx.version())
    else:
        print(_("\n%(EFUver)s, Installed wxPython version: %(wxver)s\n") %
                {'EFUver': version, 'wxver': wx.version()})
        if _hasXLRD:
            print(_("xlrd imported successfully"))
        else:
            print(_("WARNING: can't import xlrd, so Tables option will not work"))

        if _hasXLWT:
            print(_("xlwt imported successfully"))
        else:
            print(_("WARNING: can't import xlwt, so Tables option will not work"))

        if _hasXLUTILS:
            print(_("xlutils imported successfully"))
        else:
            print(_("WARNING: can't import xlutils, so saving tables may not work"))

        main()
