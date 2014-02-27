# ex:set ts=4 sw=4: <- for vim
#
# EPANET File Utility - Export page
#
# Dependencies:
# - Python 2.6 or 2.7 (32- or 64-bit)
# - wxPython 3.0.0 (32- or 64-bit to match installed version of Python)
# - EPANETOutputFile/EPANETOutputFile.py
#
# Available translations/locales:
# en_AU.UTF-8

import wx
import os
import gettext
from ColouredPanel import ColouredPanel


class ExportPage(wx.Panel):
    """ We simply derive a new class of Panel. """


    def __init__(self, frame, listbook, colour):

        # initialise ourselves as a panel belonging to the listbook
        wx.Panel.__init__(self, listbook)

        # save the main program frame
        self.MainWindow = frame

        self.exportdirname = None

        # add a coloured panel inside
        self.win = win = ColouredPanel(self, colour)
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(win, 1, wx.GROW)

        # now put some content in the coloured panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        win.SetSizer(sizer)

        topsizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(topsizer, 1, wx.GROW)

        bitmap = wx.Bitmap('images/200px-Text-csv-text.svg.png')
        imgcontrol = wx.StaticBitmap(win, -1, bitmap)
        topsizer.Add(imgcontrol, 0, wx.GROW | wx.ALL, 10)

        st = wx.StaticText(win, -1,
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
        groupbox = wx.StaticBox(win, -1, _('Naming'))
        groupsizer = wx.StaticBoxSizer(groupbox, wx.VERTICAL)
        st = wx.StaticText(win, -1, _("Base name"))
        groupsizer.Add(st, 0, wx.GROW)
        self.BaseNameTextCtrl = st = wx.TextCtrl(win)
        groupsizer.Add(st, 0, wx.GROW)

        m_dir = wx.Button(win, -1, _("Directory..."))
        m_dir.Bind(wx.EVT_BUTTON, self.OnDirectoryClick)
        groupsizer.Add(m_dir, 0, wx.TOP, 30)
        midrightsizer.Add(groupsizer, 1, wx.GROW)

        groupbox = wx.StaticBox(win, -1, _('Prolog'))
        groupsizer = wx.StaticBoxSizer(groupbox, wx.VERTICAL)
        midleftsizer.Add(groupsizer, 1, wx.GROW)
        self.PrologNodeCSVCheckBox = st = wx.CheckBox(win, -1, _('Nodes analysed') + '  (<Base name>_pnode.csv)')
        st.SetValue(True)
        groupsizer.Add(st, 1, wx.GROW)
        self.PrologLinkCSVCheckBox = st = wx.CheckBox(win, -1, _('Links analysed') + '  (<Base name>_plink.csv)')
        st.SetValue(True)
        groupsizer.Add(st, 1, wx.GROW)

        groupbox = wx.StaticBox(win, -1, _('Energy Usage'))
        groupsizer = wx.StaticBoxSizer(groupbox, wx.VERTICAL)
        midleftsizer.Add(groupsizer, 1, wx.GROW)
        self.EnergyUsageCSVCheckBox = st = wx.CheckBox(win, -1, _('Pump energy usage') + '  (<Base name>_e.csv)')
        st.SetValue(True)
        groupsizer.Add(st, 1, wx.GROW)

        groupbox = wx.StaticBox(win, -1, _('Dynamic Results'))
        groupsizer = wx.StaticBoxSizer(groupbox, wx.VERTICAL)
        midleftsizer.Add(groupsizer, 1, wx.GROW)
        self.DynamicResultsNodeCSVCheckBox = st = wx.CheckBox(win, -1, _('Node dynamic results') + '  (<Base name>_dnode.csv)')
        st.SetValue(True)
        groupsizer.Add(st, 1, wx.GROW)
        self.DynamicResultsLinkCSVCheckBox = st = wx.CheckBox(win, -1, _('Link dynamic results') + '  (<Base name>_dlink.csv)')
        st.SetValue(True)
        groupsizer.Add(st, 1, wx.GROW)
        m_export = wx.Button(win, -1, _("Export"))
        m_export.Bind(wx.EVT_BUTTON, self.OnExport)
        sizer.Add(m_export, 0, wx.ALL | wx.ALIGN_RIGHT, 20)
        
        topsizer.Layout()
        sizer.Layout()


    def epanetoutputfile(self):
        eof = None
        if self.MainWindow is not None:
            eof = self.MainWindow.epanetoutputfile
        return eof


    def OnDirectoryClick(self, event):
        """ Select directory for export """
        dlg = wx.DirDialog(self, _("Choose an export directory"),
                self.exportdirname)
        try:
            #dlg.SetPath(self.exportdirname)
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

            self.epanetoutputfile().Export(options)

        except Exception, e:
            import traceback
            print("ERROR exporting: %s" % e)
            traceback.print_exc()


    def OnOpen(self, event, progress):
        """ Open a file"""

        if self.exportdirname is None:
            self.exportdirname = self.MainWindow.dirname
        self.BaseNameTextCtrl.SetValue(os.path.splitext(self.MainWindow.filename)[0])


