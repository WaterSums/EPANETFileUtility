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
import traceback

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
    

class ColouredPanel(wx.Window):
    def __init__(self, parent, colour):
        wx.Window.__init__(self, parent, -1, style = wx.SIMPLE_BORDER)
        self.SetBackgroundColour(colour)
        if wx.Platform == '__WXGTK__':
            self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

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
        self.treesizer = None
        self.Pnodetree = None
        self.Plinktree = None
        self.Epumptree = None
        self.Dnodetree = None
        self.Dlinktree = None
        self.currentpage = 0
        self.dirname = None
        self.filename = None
        self.exportdirname = None

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
            win = self.makeColourPanel(colour)
            title = titleList[i]
            self.control.AddPage(win, title, imageId=imageIdGenerator.next())

            if i == 3:
                sizer = wx.BoxSizer(wx.VERTICAL)
                win.win.SetSizer(sizer)
                topsizer = wx.BoxSizer(wx.HORIZONTAL)
                sizer.Add(topsizer, 1, wx.GROW)

                bitmap = wx.Bitmap('images/200px-Text-csv-text.svg.png')
                imgcontrol = wx.StaticBitmap(win.win, -1, bitmap)
                topsizer.Add(imgcontrol, 0, wx.GROW | wx.ALL, 10)

                st = wx.StaticText(win.win, -1,
                      _(
"Some of the values stored in an output file can be exported "
"in a tabular form to Comma Separated Values (CSV) files."
"""

"""
"Normally, these export files are written in the same directory as the output "
"file, each with the same base name as the output file and with a different "
"suffix.  The .csv extension is appended.  If necessary, the base name and "
"directory can be specified below."
)
                      )
                topsizer.Add(st, 0, wx.GROW | wx.ALL, 10)

                midsizer = wx.BoxSizer(wx.HORIZONTAL)
                sizer.Add(midsizer, 1, wx.GROW)

                midleftsizer = wx.BoxSizer(wx.VERTICAL)
                midsizer.Add(midleftsizer, 1, wx.GROW)

                midrightsizer = wx.BoxSizer(wx.VERTICAL)
                midsizer.Add(midrightsizer, 1, wx.GROW)
                groupbox = wx.StaticBox(win.win, -1, 'Naming')
                groupsizer = wx.StaticBoxSizer(groupbox, wx.VERTICAL)
                st = wx.StaticText(win.win, -1, _("Base name"))
                groupsizer.Add(st, 0, wx.GROW)
                self.BaseNameTextCtrl = st = wx.TextCtrl(win.win)
                groupsizer.Add(st, 0, wx.GROW)

                m_dir = wx.Button(win.win, -1, "Directory...")
                m_dir.Bind(wx.EVT_BUTTON, self.OnDirectoryClick)
                groupsizer.Add(m_dir, 0, wx.TOP, 30)
                midrightsizer.Add(groupsizer, 1, wx.GROW)

                groupbox = wx.StaticBox(win.win, -1, 'Prolog')
                groupsizer = wx.StaticBoxSizer(groupbox, wx.VERTICAL)
                midleftsizer.Add(groupsizer, 1, wx.GROW)
                self.PrologNodeCSVCheckBox = st = wx.CheckBox(win.win, -1, _('Nodes analysed') + '  (<Base name>_pnode.csv)')
                st.SetValue(True)
                groupsizer.Add(st, 1, wx.GROW)
                self.PrologLinkCSVCheckBox = st = wx.CheckBox(win.win, -1, _('Links analysed') + '  (<Base name>_plink.csv)')
                st.SetValue(True)
                groupsizer.Add(st, 1, wx.GROW)

                groupbox = wx.StaticBox(win.win, -1, 'Energy Usage')
                groupsizer = wx.StaticBoxSizer(groupbox, wx.VERTICAL)
                midleftsizer.Add(groupsizer, 1, wx.GROW)
                self.EnergyUsageCSVCheckBox = st = wx.CheckBox(win.win, -1, _('Pump energy usage') + '  (<Base name>_e.csv)')
                st.SetValue(True)
                groupsizer.Add(st, 1, wx.GROW)

                groupbox = wx.StaticBox(win.win, -1, 'Dynamic Results')
                groupsizer = wx.StaticBoxSizer(groupbox, wx.VERTICAL)
                midleftsizer.Add(groupsizer, 1, wx.GROW)
                self.DynamicResultsNodeCSVCheckBox = st = wx.CheckBox(win.win, -1, _('Node dynamic results') + '  (<Base name>_dnode.csv)')
                st.SetValue(True)
                groupsizer.Add(st, 1, wx.GROW)
                self.DynamicResultsLinkCSVCheckBox = st = wx.CheckBox(win.win, -1, _('Link dynamic results') + '  (<Base name>_dlink.csv)')
                st.SetValue(True)
                groupsizer.Add(st, 1, wx.GROW)
                m_export = wx.Button(win.win, -1, "Export")
                m_export.Bind(wx.EVT_BUTTON, self.OnExport)
                sizer.Add(m_export, 0, wx.ALL | wx.ALIGN_RIGHT, 20)
                
                topsizer.Layout()
                sizer.Layout()
            else:
                st = wx.StaticText(win.win, -1,
                          _("EPANET File Utility."),
                          wx.Point(10, 10))

            #win = self.makeColourPanel(colour)
            #st = wx.StaticText(win.win, -1, "this is a sub-page", (10,10))
            #self.control.AddSubPage(win, 'a sub-page', imageId=imageIdGenerator.next())

        self.control.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.control.OnPageChanged)
        self.control.Bind(wx.EVT_LISTBOOK_PAGE_CHANGING, self.control.OnPageChanging)

        # A Statusbar in the bottom of the window used with menu help text, # etc.
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

    def OnDirectoryClick(self, event):
        """ Select directory for export """
        dlg = wx.DirDialog(self, _("Choose an export directory"), self.dirname)
        try:
            dlg.SetPath(self.exportdirname)
            result = dlg.ShowModal()
            if result == wx.ID_OK:
                self.exportdirname = dlg.GetPath()

        except Exception as ex:
            print(ex)
            errdlg = wx.MessageDialog(self, str(ex), _('Error'), style=wx.OK | wx.ICON_ERROR)
            errdlg.ShowModal()
            errdlg.Destroy()
        finally:
            dlg.Destroy()

    def OnExport(self, event):
        """ Export CSV file(s)"""
        try:
            options = {}
            files = []
            dname = self.exportdirname
            base = self.BaseNameTextCtrl.GetValue()
            pre = '%s%s%s' % (dname, os.sep, base)
            if self.PrologNodeCSVCheckBox.IsChecked():
                fname = '%s_pnode.csv' % pre
                files.append(fname)
                options["prolog_node_csv"] = fname
            if self.PrologLinkCSVCheckBox.IsChecked():
                fname = '%s_plink.csv' % pre
                files.append(fname)
                options["prolog_link_csv"] = fname
            if self.EnergyUsageCSVCheckBox.IsChecked():
                fname = '%s_e.csv' % pre
                files.append(fname)
                options["energy_use_csv"] = fname
            if self.DynamicResultsNodeCSVCheckBox.IsChecked():
                fname = '%s_dnode.csv' % pre
                files.append(fname)
                options["dynamic_node_csv"] = fname
            if self.DynamicResultsLinkCSVCheckBox.IsChecked():
                fname = '%s_dlink.csv' % pre
                files.append(fname)
                options["dynamic_link_csv"] = fname
            flist = ''
            fcnt = 0
            for name in files:
                if os.path.exists(name):
                    flist += name + '\n'
                    fcnt += 1
            if fcnt:
                tmpstr = gettext.ngettext(
                    'The following file already exists:\n\n%(fname)s\n\nOverwrite?',
                    'The following %(fcount)d files already exist:\n\n%(fnames)s\n\nOverwrite?',
                    fcnt)
                if '%(fcount)d' in tmpstr:
                    tmpstr %= {'fcount': fcnt, 'fnames': flist}
                else:
                    tmpstr %= {'fnames': flist}
                warndlg = wx.MessageDialog(self, tmpstr, _('Overwrite?'), style=wx.YES_NO | wx.ICON_EXCLAMATION)
                result = warndlg.ShowModal()
                warndlg.Destroy()
                if result == wx.ID_NO:
                    # don't overwrite
                    return

            self.epanetoutputfile.Export(options)
        except Exception, e:
            print("ERROR exporting: %s" % e)
            traceback.print_exc()

    def AddCategory(self, page, str):
        return page.Append(wxpg.PropertyCategory(str))

    def AddBool(self, page, str, val):
        return page.Append(wxpg.BoolProperty(str,value=val))

    def AddInt(self, page, str, val, name=None):
        if name is None:
            return page.Append(wxpg.IntProperty(str,value=val))
        return page.Append(wxpg.IntProperty(str, name, val))

    def AddFloat(self, page, str, val):
        return page.Append(wxpg.FloatProperty(str,value=val))

    def AddString(self, page, str, val):
        return page.Append(wxpg.StringProperty(str,value=val))

    # Build or rebuild Dynamic Results node tree
    # This tree is semi-lazy: a branch is added for each timestep,
    # but the branches are not filled in until they are expanded.
    # This make the loading of the tree quick.
    def BuildDynamicResultsNodeTree(self):
        Dnodetree = self.Dnodetree
        eof = self.epanetoutputfile
        p = eof.Prolog
        DynamicResults = eof.DynamicResults
        c = eof.Epilog
        nPeriods = c['nPeriods']

        if Dnodetree.GetColumnCount() > 0:
            Dnodetree.DeleteAllItems()
        else:
            # TODO Idea: use properties in Dynamic Results page to control
            # display of columns
            Dnodetree.AddColumn(_('Timestep'))
            Dnodetree.AddColumn(_('Node index'))
            #Dnodetree.AddColumn(_('ID'))
            Dnodetree.AddColumn(_('Demand'))
            Dnodetree.AddColumn(_('Head'))
            Dnodetree.AddColumn(_('Pressure'))
            Dnodetree.AddColumn(_('Water Quality'))
            #Dnodetree.AddRoot(_("Timesteps (%d): Nodes (%d)") % (nPeriods, p['nNodes']))
            Dnodetree.AddRoot(_("Nodes (%d)") % p['nNodes'])

        for i in range(nPeriods):
            d = DynamicResults[i]
            t = Dnodetree.AppendItem(Dnodetree.RootItem,_('Timestep %d') % i)
            # set data to say branch has not been expanded and tell tree it has children
            Dnodetree.SetPyData(t,('timestep',i,False))
            Dnodetree.SetItemHasChildren(t)
            # the timestep branches are filled in when they
            # are expanded in OnDnodeTreeItemExpanding()

        Dnodetree.Expand(Dnodetree.RootItem)

    def OnDNodeTreeItemExpanding(self, event):
        t = event.GetItem()
        if t.IsOk():
            #print("Expanding node: %s" % self.Dnodetree.GetItemText(t))
            # Item data is in the form ( nodetype (text), timestep number, expanded (True/False)
            # If branch type is 'timestep' and expanded == True
            data = self.Dnodetree.GetPyData(t)
            if data is not None:
                branchtype, tstep, expanded = data
                if branchtype == 'timestep' and expanded == False:
                    #print("Adding node information as we expand %s" % self.Dnodetree.GetItemText(t))
                    # add the node info for this timestep
                    Dnodetree = self.Dnodetree
                    eof = self.epanetoutputfile
                    p = eof.Prolog
                    DynamicResults = eof.DynamicResults
                    c = eof.Epilog
                    nPeriods = c['nPeriods']
                    i = tstep
                    d = DynamicResults[i]
                    for j in range (0, p['nNodes']):
                        n = Dnodetree.AppendItem(t,str(i))
                        Dnodetree.SetItemText(n, str(j), 1)
                        Dnodetree.SetItemText(n, str(d['NodeDemand'][j]), 2)
                        Dnodetree.SetItemText(n, str(d['NodeHead'][j]), 3)
                        Dnodetree.SetItemText(n, str(d['NodePressure'][j]), 4)
                        Dnodetree.SetItemText(n, str(d['NodeWaterQuality'][j]), 5)
                    Dnodetree.SetPyData(t,(branchtype, tstep, True))

    # Build or rebuild Dynamic Results link tree
    # This tree is semi-lazy: a branch is added for each timestep,
    # but the branches are not filled in until they are expanded.
    # This make the loading of the tree quick.
    def BuildDynamicResultsLinkTree(self):
        Dlinktree = self.Dlinktree
        eof = self.epanetoutputfile
        p = eof.Prolog
        DynamicResults = eof.DynamicResults
        c = eof.Epilog
        nPeriods = c['nPeriods']

        if Dlinktree.GetColumnCount() > 0:
            Dlinktree.DeleteAllItems()
        else:
            # TODO Idea: use properties in Dynamic Results page to control
            # display of columns
            Dlinktree.AddColumn(_('Timestep'))
            Dlinktree.AddColumn(_('Link index'))
            #Dlinktree.AddColumn(_('ID'))
            Dlinktree.AddColumn(_('Flow'))
            Dlinktree.AddColumn(_('Velocity'))
            Dlinktree.AddColumn(_('Head loss'))
            Dlinktree.AddColumn(_('Ave Water Quality'))
            Dlinktree.AddColumn(_('Status'))
            Dlinktree.AddColumn(_('React. rate'))
            Dlinktree.AddColumn(_('Frict. factor'))
            #Dlinktree.AddRoot(_("Timesteps (%d): Links (%d)") % (nPeriods, p['nLinks']))
            Dlinktree.AddRoot(_("Links (%d)") % p['nLinks'])


        for i in range(nPeriods):
            d = DynamicResults[i]
            t = Dlinktree.AppendItem(Dlinktree.RootItem,_('Timestep %d') % i)
            Dlinktree.SetPyData(t,('timestep',i,False))
            Dlinktree.SetItemHasChildren(t)
            # the timestep branches are filled in when they
            # are expanded in OnDlinkTreeItemExpanding()

        Dlinktree.Expand(Dlinktree.RootItem)

    def OnDLinkTreeItemExpanding(self, event):
        t = event.GetItem()
        if t.IsOk():
            #print("Expanding node: %s" % self.Dlinktree.GetItemText(t))
            # Item data is in the form ( nodetype (text), timestep number, expanded (True/False)
            # If branch type is 'timestep' and expanded == True
            data = self.Dlinktree.GetPyData(t)
            if data is not None:
                branchtype, tstep, expanded = data
                if branchtype == 'timestep' and expanded == False:
                    # add the link info for this timestep
                    #print("Adding link information as we expand %s" % self.Dlinktree.GetItemText(t))
                    Dlinktree = self.Dlinktree
                    eof = self.epanetoutputfile
                    p = eof.Prolog
                    DynamicResults = eof.DynamicResults
                    c = eof.Epilog
                    nPeriods = c['nPeriods']
                    i = tstep
                    d = DynamicResults[i]
                    for j in range (0, p['nLinks']):
                        n = Dlinktree.AppendItem(t,str(i))
                        Dlinktree.SetItemText(n, str(j), 1)
                        Dlinktree.SetItemText(n, str(d['LinkFlow'][j]), 2)
                        Dlinktree.SetItemText(n, str(d['LinkVelocity'][j]), 3)
                        Dlinktree.SetItemText(n, str(d['LinkHeadloss'][j]), 4)
                        Dlinktree.SetItemText(n, str(d['LinkAveWaterQuality'][j]), 5)
                        Dlinktree.SetItemText(n, str(d['LinkStatus'][j]), 6)
                        Dlinktree.SetItemText(n, str(d['LinkReactionRate'][j]), 7)
                        Dlinktree.SetItemText(n, str(d['LinkFrictionFactor'][j]), 8)
                    Dlinktree.SetPyData(t,(branchtype, tstep, True))

    def OnPageChanged(self, event):
        # Property Grid page changed
        panel = self.control.GetPage(0)
        panel.win.Freeze()
        newindex = panel.win.GetSelectedPage()
        #print('Changed to page %d (old page was %d)' % (newindex,
        #    self.currentpage))

        if newindex == 0:
            # add the node and link trees and hide the others
            self.treesizer.Show(self.Pnodetree)
            self.treesizer.Show(self.Plinktree)
            self.treesizer.Hide(self.Epumptree)
            self.treesizer.Hide(self.Dnodetree)
            self.treesizer.Hide(self.Dlinktree)
        elif newindex == 1:
            # show the pump tree and hide the rest
            self.treesizer.Hide(self.Pnodetree)
            self.treesizer.Hide(self.Plinktree)
            self.treesizer.Show(self.Epumptree)
            self.treesizer.Hide(self.Dnodetree)
            self.treesizer.Hide(self.Dlinktree)
        elif newindex == 2:
            # show the node and link trees for dynamic results
            self.treesizer.Hide(self.Pnodetree)
            self.treesizer.Hide(self.Plinktree)
            self.treesizer.Hide(self.Epumptree)
            self.treesizer.Show(self.Dnodetree)
            self.treesizer.Show(self.Dlinktree)
            # populate the trees iff we need to
            if self.Dnodetree.GetColumnCount() == 0:
                self.BuildDynamicResultsNodeTree()
            if self.Dlinktree.GetColumnCount() == 0:
                self.BuildDynamicResultsLinkTree()


        elif newindex == 3:
            # nothing to show - hide everything
            self.treesizer.Hide(self.Pnodetree)
            self.treesizer.Hide(self.Plinktree)
            self.treesizer.Hide(self.Epumptree)
            self.treesizer.Hide(self.Dnodetree)
            self.treesizer.Hide(self.Dlinktree)
        else:
            print(_('Unexpected property grid page number %d') % newindex)

        panel.Sizer.Layout()
        self.currentpage = newindex
        panel.win.Thaw()

        event.Skip()

    def OnStartup(self, event):
        self.Unbind(wx.EVT_IDLE)
        self.OnOpen(event)
        event.Skip()

    def OnOpen(self, event):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, _("Choose a file"), self.dirname, "", "*", wx.OPEN)
        try:
            result = dlg.ShowModal()
            if result == wx.ID_OK:
                self.filename = dlg.GetFilename()
                self.dirname = dlg.GetDirectory()
                self.exportdirname = self.dirname
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

                    panel = self.control.GetPage(0)

                    # remove the old contents (coloured panel or PropertyGridManager)
                    panel.Sizer.Remove(panel.win)
                    panel.win.Destroy()
                    if self.treesizer is not None:
                        self.treesizer.Remove(self.Pnodetree)
                        self.treesizer.Remove(self.Plinktree)
                        self.treesizer.Remove(self.Epumptree)
                        self.treesizer.Remove(self.Dnodetree)
                        self.treesizer.Remove(self.Dlinktree)
                        self.Pnodetree.Destroy()
                        self.Plinktree.Destroy()
                        self.Epumptree.Destroy()
                        self.Dnodetree.Destroy()
                        self.Dlinktree.Destroy()
                        self.Pnodetree = None
                        self.Plinktree = None
                        self.Epumptree = None
                        self.Dnodetree = None
                        self.Dlinktree = None

                    panel.Freeze()

                    pg = wxpg.PropertyGridManager(
                        panel,
                        style = wxpg.PG_SPLITTER_AUTO_CENTER
                                #| wx.FULL_REPAINT_ON_RESIZE
                                #| wxpg.PG_DESCRIPTION
                                #| wxpg.PG_SPLITTER_ALL_PAGES
                                | wxpg.PGMAN_DEFAULT_STYLE
                                | wxpg.PG_TOOLBAR)
                    # Show help as tooltips
                    pg.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
                    pg.Bind(wxpg.EVT_PG_PAGE_CHANGED, self.OnPageChanged)
                    pg.GetGrid().DedicateKey(wx.WXK_UP)
                    pg.GetGrid().DedicateKey(wx.WXK_DOWN)
                    pg.GetGrid().AddActionTrigger(wxpg.PG_ACTION_NEXT_PROPERTY, wx.WXK_RETURN)
                    pg.GetGrid().DedicateKey(wx.WXK_RETURN)

                    # put in the new contents
                    panel.win = pg
                    panel.Sizer.Prepend(panel.win, 1, wx.GROW)

                    # new horizontal sizer for five switchable trees
                    if self.treesizer is None:
                        self.treesizer = wx.BoxSizer(wx.HORIZONTAL)
                        panel.Sizer.Add(self.treesizer, 0.7, wx.GROW)
                    # create the trees
                    self.Pnodetree = Pnodetree = wx.gizmos.TreeListCtrl(panel,-1,
                            style = wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
                    self.Plinktree = Plinktree = wx.gizmos.TreeListCtrl(panel,-1,
                            style = wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
                    self.Epumptree = Epumptree = wx.gizmos.TreeListCtrl(panel,-1,
                            style = wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
                    self.Dnodetree = Dnodetree = wx.gizmos.TreeListCtrl(panel,-1,
                            style = wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
                    self.Dlinktree = Dlinktree = wx.gizmos.TreeListCtrl(panel,-1,
                            style = wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
                    # add the trees to the sizer and hide the ones we don't need yet
                    self.treesizer.Add(self.Pnodetree, 1, wx.GROW)
                    self.treesizer.Add(self.Plinktree, 1, wx.GROW)
                    self.treesizer.Add(self.Epumptree, 1, wx.GROW)
                    self.treesizer.Hide(self.Epumptree)
                    self.treesizer.Add(self.Dnodetree, 1, wx.GROW)
                    self.treesizer.Hide(self.Dnodetree)
                    self.treesizer.Add(self.Dlinktree, 1, wx.GROW)
                    self.treesizer.Hide(self.Dlinktree)

                    self.Dnodetree.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnDNodeTreeItemExpanding)
                    self.Dlinktree.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnDLinkTreeItemExpanding)

                    panel.Layout()


                    p = eof.Prolog
                    e = eof.EnergyUse
                    d = eof.DynamicResults
                    c = eof.Epilog

                    # this sets the number of columns, but how do we set multiple
                    # values in the second and third columns?
                    #pg.SetColumnCount(3)

                    p1 = pg.AddPage(_("Prolog"))
                    self.AddCategory(p1, _('1 - General'))
                    self.AddInt(p1, _('Magic number'),p['magic'])
                    self.AddInt(p1, _('EPANET version'), p['version'])
                    self.AddCategory(p1, _('2 - Network Statistics'))
                    self.AddInt(p1, _('Number of Nodes (Junctions+Reservoirs+Tanks)'),p['nNodes'])
                    self.AddInt(p1, _('Number of Reservoirs + Tanks'),p['nResTanks'])
                    self.AddInt(p1, _('(Number of Junctions (type 0))'),p['nJunctions'])
                    self.AddInt(p1, _('(Number of Reservoirs (type 1))'),p['nReservoirs'])
                    self.AddInt(p1, _('(Number of Tanks (type 2))'),p['nTanks'])
                    self.AddInt(p1, _('Number of Links'),p['nLinks'])
                    self.AddInt(p1, _('(Number of Pipes (type 3))'),p['nPipes'])
                    self.AddInt(p1, _('Number of Pumps  (type 4)'),p['nPumps'])
                    self.AddInt(p1, _('Number of Valves (type 5)'),p['nValves'])
                    self.AddCategory(p1, _('3 - Configuration'))
                    self.AddInt(p1, _('Water quality option'),p['WaterQualityOptNum'])
                    self.AddString(p1, _('Water quality option meaning'),p['WaterQualityOption'])
                    self.AddInt(p1, _('Source node index'),p['source_node_index'])
                    self.AddInt(p1, _('Flow units'),p['FlowUnitsOptNum'])
                    self.AddString(p1, _('Flow units meaning'),p['FlowUnitsOption'])
                    self.AddInt(p1, _('Presssure units'),p['PressureUnitsOptNum'])
                    self.AddString(p1, _('Presssure units meaning'),p['PressureUnitsOption'])
                    self.AddInt(p1, _('Time statistics'),p['TimeStatsOptNum'])
                    self.AddString(p1, _('Time statistics meaning'),p['TimeStatsOption'])
                    self.AddInt(p1, _('Start time'),p['StartTime'])
                    self.AddInt(p1, _('Report time step'),p['ReportTimeStep'])
                    self.AddInt(p1, _('Simulation duration'),p['SimulationDuration'])
                    self.AddString(p1, _('Problem Title (line 1)'),p['Title1'])
                    self.AddString(p1, _('Problem Title (line 2)'),p['Title2'])
                    self.AddString(p1, _('Problem Title (line 3)'),p['Title3'])
                    self.AddString(p1, _('Name of input file'),p['InputFile'])
                    self.AddString(p1, _('Name of report file'),p['ReportFile'])
                    self.AddString(p1, _('Chemical name'),p['ChemicalName'])
                    self.AddString(p1, _('Chemical concentration units'),p['ChemicalConcentrationUnits'])

                    #self.AddCategory(p1, '4 - Nodes')
                    #self.AddInt(p1, 'Number of nodes',p['nNodes'])
                    #p1.Append( wxpg.EnumProperty("Display format","Enum",
                    #                             ['Default'],
                    #                             [0],
                    #                             0) )

                    progress.Update(20,_('Displaying prolog node data'))

                    Pnodetree.AddColumn(_('Index'))
                    Pnodetree.AddColumn(_('Node Type'))
                    Pnodetree.AddColumn(_('ID'))
                    Pnodetree.AddColumn(_('Elevation'))
                    Pnodetree.AddColumn(_('Tank X-sect Area'))
                    Pnodetree.AddRoot(_("Nodes (%d)") % p['nNodes'])
                    for i in range (0, p['nNodes']):
                        n = Pnodetree.AppendItem(Pnodetree.RootItem,str(i+1))
                        if p['NodeTankResIndex'][i] == -1:
                            Pnodetree.SetItemText(n, _("Junction"),1)
                            Pnodetree.SetItemText(n,p['NodeID'][i],2)
                            Pnodetree.SetItemText(n,str(p['NodeElev'][i]),3)
                        elif p['TankResXSectArea'][p['NodeTankResIndex'][i]] == 0.0:
                            Pnodetree.SetItemText(n, _("Reservoir"),1)
                            Pnodetree.SetItemText(n,p['NodeID'][i],2)
                            Pnodetree.SetItemText(n,str(p['NodeElev'][i]),3)
                        else:
                            Pnodetree.SetItemText(n, _("Tank"),1)
                            Pnodetree.SetItemText(n,p['NodeID'][i],2)
                            Pnodetree.SetItemText(n,str(p['NodeElev'][i]),3)
                            Pnodetree.SetItemText(n,
                                    str(p['TankResXSectArea'][p['NodeTankResIndex'][i]]), 4)
                    Pnodetree.Expand(Pnodetree.RootItem)

                    progress.Update(40,_('Displaying prolog link data'))

                    #self.AddCategory(p1, '5 - Links')
                    Plinktree.AddColumn(_('Index'))
                    Plinktree.AddColumn(_('Link Type'))
                    Plinktree.AddColumn(_('ID'))
                    Plinktree.AddColumn(_('Start node'))
                    Plinktree.AddColumn(_('End node'))
                    Plinktree.AddColumn(_('Length'))
                    Plinktree.AddColumn(_('Diameter'))
                    Plinktree.AddRoot(_("Links (%d)") % p['nLinks'])

                    # add the link tree content
                    for i in range (0, p['nLinks']):
                        n = Plinktree.AppendItem(Plinktree.RootItem,str(i))
                        option = eof.getLinkTypeText(p['LinkType'][i])
                        Plinktree.SetItemText(n,option,1)
                        Plinktree.SetItemText(n,str(p['LinkID'][i]),2)
                        Plinktree.SetItemText(n,str(p['LinkStart'][i]),3)
                        Plinktree.SetItemText(n,str(p['LinkEnd'][i]),4)
                        Plinktree.SetItemText(n,str(p['LinkLength'][i]),5)
                        Plinktree.SetItemText(n,str(p['LinkDiam'][i]),6)
                    Plinktree.Expand(Plinktree.RootItem)


                    p1.SetPropertyReadOnly(p1.GetRoot(),True)

                    p2 = pg.AddPage(_("Energy Usage"))
                    Epumptree.AddColumn(_('Index'))
                    Epumptree.AddColumn(_('ID'))
                    Epumptree.AddColumn(_('Link Index'))
                    Epumptree.AddColumn(_('Utilization'))
                    Epumptree.AddRoot(_("Pumps (%d)") % p['nPumps'])

                    for i in range(p['nPumps']):
                        n = Epumptree.AppendItem(Epumptree.RootItem,str(i))
                        index = e['PumpIndex'][i]
                        Epumptree.SetItemText(n,str(p['LinkID'][index]),1)
                        Epumptree.SetItemText(n,str(index),2)
                        Epumptree.SetItemText(n, str(e['PumpUtilization'][i]), 3)
                        #ID = p['LinkID'][index]
                        #self.AddCategory(p2, 'Pump %d: Link Index %d, ID: %s' % (i,index, ID))
                        #self.AddInt(p2, 'Link Index (%s)' % ID,index)
                        #self.AddFloat(p2, 'Pump utilization (%s)' % ID,e['PumpUtilization'][i])
                    Epumptree.Expand(Epumptree.RootItem)

                    self.AddCategory(p2, _('Summary'))
                    self.AddFloat(p2, _('Pump Peak Energy Usage'),e['PumpPeakEnergyUsage'])
                    p2.SetPropertyReadOnly(p2.GetRoot(),True)

                    progress.Update(60,_('Displaying dynamic results data'))

                    p3 = pg.AddPage(_("Dynamic Results"))
                    self.AddCategory(p3, _('1 - Analysis'))
                    nPeriods = c['nPeriods']
                    self.AddInt(p3, _('Number of time periods'), nPeriods)
                    self.AddInt(p3, _('Number of nodes'), p['nNodes'])
                    self.AddInt(p3, _('Number of links'), p['nLinks'])

                    # add some dynamic results summary information
                    # if demo plugin has been loaded
                    # TODO - this should really be moved into a GUI plugin itself
                    if 'demo' in eof.GetEOFTPluginDirs():
                        try:
                            dp = eof.GetEOFTPlugins()[eof.GetEOFTPluginDirs().index('demo')]
                            self.AddCategory(p3, _('2 - Nodes'))
                            self.AddString(p3, _('Minimum demand'), "%f (timestep %d, node index %d)" % (dp.minMinDemand, dp.minMinDemandContext[0], dp.minMinDemandContext[1]))
                            self.AddString(p3, _('Maximum demand'), "%f (timestep %d, node index %d)" % (dp.maxMaxDemand, dp.maxMaxDemandContext[0], dp.maxMaxDemandContext[1]))
                            self.AddString(p3, _('Minimum head'), "%f (timestep %d, node index %d)" % (dp.minMinHead, dp.minMinHeadContext[0], dp.minMinHeadContext[1]))
                            self.AddString(p3, _('Maximum head'), "%f (timestep %d, node index %d)" % (dp.maxMaxHead, dp.maxMaxHeadContext[0], dp.maxMaxHeadContext[1]))
                            self.AddString(p3, _('Minimum pressure'), "%f (timestep %d, node index %d)" % (dp.minMinPress, dp.minMinPressContext[0], dp.minMinPressContext[1]))
                            self.AddString(p3, _('Maximum pressure'), "%f (timestep %d, node index %d)" % (dp.maxMaxPress, dp.maxMaxPressContext[0], dp.maxMaxPressContext[1]))
                            self.AddString(p3, _('Minimum water quality'), "%f (timestep %d, node index %d)" % (dp.minMinWaterQ, dp.minMinWaterQContext[0], dp.minMinWaterQContext[1]))
                            self.AddString(p3, _('Maximum water quality'), "%f (timestep %d, node index %d)" % (dp.maxMaxWaterQ, dp.maxMaxWaterQContext[0], dp.maxMaxWaterQContext[1]))

                            self.AddCategory(p3, _('3 - Links'))
                            self.AddString(p3, _('Minimum velocity'), "%f (timestep %d, link index %d)" % (dp.minMinVel, dp.minMinVelContext[0], dp.minMinVelContext[1]))
                            self.AddString(p3, _('Maximum velocity'), "%f (timestep %d, link index %d)" % (dp.maxMaxVel, dp.maxMaxVelContext[0], dp.maxMaxVelContext[1]))

                        except:
                            print('Could not get data from the demo plugin')


                    p3.SetPropertyReadOnly(p3.GetRoot(),True)

                    progress.Update(90,_('Displaying epilog data'))

                    p4 = pg.AddPage("Epilog")
                    self.AddFloat(p4, _("Average Bulk Reaction Rate"), c['AveBulkReactionRate'])
                    self.AddFloat(p4, _("Average Wall Reaction Rate"), c['AveWallReactionRate'])
                    self.AddFloat(p4, _("Average Tank Reaction Rate"), c['AveTankReactionRate'])
                    self.AddFloat(p4, _("Average Source Inflow Rate"), c['AveSourceInflowRate'])
                    self.AddInt(p4, _("Number of reporting periods"), c['nPeriods'])
                    self.AddBool(p4, _('Analysis generated errors?'), c['WarningFlag'])
                    #p4.SetPropertyAttribute("Analysis generated errors?", "UseCheckbox", True)
                    self.AddInt(p4, _('Magic number'), c['magic'])

                    p4.SetPropertyReadOnly(p4.GetRoot(),True)

                    # no such function...
                    #pg.ShowHeader()
                    # causes a crash if called too early
                    # and doesn't seem to work without a
                    # refresh - it displays the default values initially
                    # pg.SetColumnTitle(idx=0,title="'Scription")

                    panel.Thaw()

                    #panel.SetAutoLayout(True)

                    #self.SetAutoLayout(True)
                    self.Layout()

                    progress.Update(100,_('Done'))

                #except Exception as ex:
                #    #print(ex)
                #    raise ex
                finally:
                    progress.Hide()
                    progress.Destroy()

                self.BaseNameTextCtrl.SetValue(os.path.splitext(self.filename)[0])
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

    def OnReserved(self, event):
        pass

    def OnAbout(self, event):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, _("EPANET File Utility by Mark Morgan, WaterSums."), _("About EPANET File Utility"), wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self, event):
        self.Close(True)

    def makeColourPanel(self, colour):
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
        print(_("\n%s, Installed wxPython version: %s\n")%(version,wx.version()))
        main()
