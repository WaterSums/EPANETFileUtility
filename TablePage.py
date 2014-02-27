# ex:set ts=4 sw=4: <- for vim
#
# EPANET File Utility - Table page
#
# Dependencies:
# - Python 2.6 or 2.7 (32- or 64-bit)
# - wxPython 3.0.0 (32- or 64-bit to match installed version of Python)
# - EPANETOutputFile/EPANETOutputFile.py
#
# Available translations/locales:
# en_AU.UTF-8

import wx
from ColouredPanel import ColouredPanel

_loadedXLSGRID = True
try:
    import wx.lib.agw.xlsgrid as xlsg
    #_loadedXLSGRID = False
except ImportError:
    _loadedXLSGRID = False


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



class TablePage(wx.Panel):
    """ We simply derive a new class of Panel. """


    def __init__(self, frame, listbook, colour):

        # initialise ourselves as a panel belonging to the listbook
        wx.Panel.__init__(self, listbook)

        # save the main program frame
        self.MainWindow = frame
        self.TablesXLSGrid = None
        self.NodeCurrentColumns = None
        self.LinkCurrentColumns = None
        self.NodeIDChoice = 0
        self.LinkIDChoice = 0
        self.TimestepIndex = 0

        # add a coloured panel inside
        self.win = win = ColouredPanel(self, colour)
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(win, 1, wx.GROW)

        if _hasXLRD and _hasXLWT and _hasXLUTILS and _loadedXLSGRID:

            sizer = wx.BoxSizer(wx.VERTICAL)
            win.SetSizer(sizer)


            # now put some content in the coloured panel
            topsizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(topsizer, 1, wx.GROW)
            st = wx.StaticText(win, -1,
                      _(
"""NOT YET COMPLETE.  TABLE DISPLAY/SAVING IS NOT AVAILABLE.
Select what the table should contain..."""))
            topsizer.Add(st, 17, wx.ALL, 10)

            groupbox = wx.StaticBox(win, -1, _('Configure table contents'))
            groupsizer = wx.StaticBoxSizer(groupbox, wx.HORIZONTAL)

            # Use a GridBagSizer 6 rows, 5 columns
            gbs = wx.GridBagSizer(6,5)

            st = wx.StaticText(win, -1,_('Select Nodes or Links:'))
            f = st.GetFont()
            f.SetWeight(wx.BOLD)
            st.SetFont(f)
            gbs.Add(st, (0,0), flag = wx.RIGHT, border=10)

            self.TableNodeRadioButton = radio1 = wx.RadioButton(win, -1, _("Nodes"))
            radio1.SetValue(True)
            radio1.Bind(wx.EVT_RADIOBUTTON, self.OnTableNodeSelect)
            
            gbs.Add(radio1, (1,0), flag = wx.RIGHT, border=30)
            self.TableLinkRadioButton = radio2 = wx.RadioButton( win, -1, _("Links"))
            radio2.Bind(wx.EVT_RADIOBUTTON, self.OnTableLinkSelect)
            gbs.Add(radio2, (2,0), flag = wx.RIGHT, border=30)

# Vertical separator, but it doesn't work, on MacOS at least:
#                    gbs.Add( wx.StaticLine(win, style=wx.LI_VERTICAL),
#                            (0,1), (6,1), flag = wx.LEFT | wx.RIGHT, border=10)

            st = wx.StaticText(win, -1,_('Any filtering:'))
            f = st.GetFont()
            f.SetWeight(wx.BOLD)
            st.SetFont(f)
            gbs.Add(st, (0,2), (1,2), flag = wx.LEFT, border=10)

            st = wx.StaticText(win, -1,_('ID'))
            gbs.Add(st, (1,2), flag = wx.ALIGN_RIGHT | wx.LEFT, border=10)
            st = wx.StaticText(win, -1,_('Timestep'))
            gbs.Add(st, (2,2), flag = wx.ALIGN_RIGHT | wx.LEFT, border=10)

            gbs.AddGrowableRow(2)

            self.IDChoice = st = wx.Choice(win)
            st.Bind(wx.EVT_CHOICE, self.OnIDChoice)

            gbs.Add(st, (1,3), flag = wx.GROW | wx.RIGHT, border=30)
            self.TimestepChoice = st = wx.Choice(win)
            st.Bind(wx.EVT_CHOICE, self.OnTimestepChoice)
            gbs.Add(st, (2,3), flag = wx.GROW | wx.RIGHT, border=30)
            gbs.AddGrowableCol(3)

            self.NodeCurrentColumns = self.NodeDefaultColumns()
            self.LinkCurrentColumns = self.LinkDefaultColumns()

            st = wx.StaticText(win, -1,_('Columns to include:'))
            f = st.GetFont()
            f.SetWeight(wx.BOLD)
            st.SetFont(f)
            gbs.Add(st, (0,4), flag = wx.ALIGN_BOTTOM | wx.LEFT, border=10)

            self.TableColumnListBox = lb = wx.CheckListBox(win,
                    choices=self.NodeColumnList())
            lb.Bind(wx.EVT_LISTBOX, self.OnColumnListEvent)
            lb.Bind(wx.EVT_CHECKLISTBOX, self.OnColumnListCheckEvent)
            lb.SetChecked(self.NodeCurrentColumns)
            lb.SetSelection(0)
            gbs.Add(lb, (1,4), (5,1), flag = wx.GROW | wx.LEFT | wx.RIGHT, border=10)

            groupsizer.Add(gbs, 0, wx.GROW | wx.ALL, 10)
            topsizer.Add(groupsizer, 83, wx.GROW | wx.ALL, 10)


            midsizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(midsizer, 1, wx.GROW)

            self.TablesXLSGrid = st = xlsg.XLSGrid(win)
            midsizer.Add(st, 1, wx.GROW)

            m_tabsave = wx.Button(win, -1, _("Save..."))
            m_tabsave.Bind(wx.EVT_BUTTON, self.OnSave)
            sizer.Add(m_tabsave, 0, wx.ALL | wx.ALIGN_RIGHT, 20)

        else:
            sizer = wx.BoxSizer(wx.VERTICAL)
            win.SetSizer(sizer)
            st = wx.StaticText(win, -1,
                      _(
"""EPANET File Utility

Displaying tables requires the xlrt, xlwt and xlutils packages.
See http://pypi.python.org/pypi/xlrd
and http://pypi.python.org/pypi/xlwt
and http://pypi.python.org/pypi/xlutils"""))
            sizer.Add(st, 1, wx.GROW | wx.ALL, 10)

    def epanetoutputfile(self):
        eof = None
        if self.MainWindow is not None:
            eof = self.MainWindow.epanetoutputfile
        return eof

    def NodeColumnList(self):
        return [
                _('Elevation'),         # static
                _('Base Demand'),       # static
                _('Intial Quality'),    # static
                _('Demand'),
                _('Head'),
                _('Pressure'),
                _('Chlorine')
            ]

    def GetNodeIDChoices(self):
        return [ _('All nodes') ] + self.epanetoutputfile().Prolog['NodeID']

    def NodeDefaultColumns(self):
        return [
                #0,     #'Elevation',       # static
                #1,     #'Base Demand',     # static
                #2,     #'Intial Quality',  # static
                3,      #'Demand',
                4,      #'Head',
                5,      #'Pressure',
                6,      #'Chlorine'
            ]

    def LinkColumnList(self):
        return [
                _('Length'),            # static
                _('Diameter'),          # static
                _('Roughness'),         # static
                _('Bulk Coeff.'),       # static
                _('Wall Coeff.'),       # static
                _('Flow'),
                _('Velocity'),
                _('Unit Headloss'),
                _('Friction Factor'),
                _('Reaction Rate'),
                _('Chlorine'),
                _('Status')
            ]

    def LinkDefaultColumns(self):
        return [
                #0,     # 'Length',         # static
                #1,     # 'Diameter',       # static
                #2,     # 'Roughness',      # static
                #3,     # 'Bulk Coeff.',    # static
                #4,     # 'Wall Coeff.',    # static
                5,      # 'Flow',
                6,      # 'Velocity',
                7,      # 'Unit Headloss',
                8,      # 'Friction Factor',
                9,      # 'Reaction Rate',
                10,     # 'Chlorine',
                11,     # 'Status'
            ]

    def GetLinkIDChoices(self):
        return [ _('All links') ] + self.epanetoutputfile().Prolog['LinkID']

    def GetTimestepChoices(self):
        return [ _('All timesteps') ] + [ str(i) for i in range(self.epanetoutputfile().Epilog['nPeriods']) ]

    def OnTableNodeSelect(self, event):
        """ Node radio button selected """
        # this is unnecessary - works automatically!
        #self.TableNodeRadioButton.SetValue(True)
        #self.TableLinkRadioButton.SetValue(False)
        self.TableColumnListBox.SetItems(self.NodeColumnList())
        self.TableColumnListBox.SetChecked(self.NodeCurrentColumns)
        self.IDChoice.SetItems(self.GetNodeIDChoices())
        self.IDChoice.SetSelection(self.NodeIDChoice)

    def OnTableLinkSelect(self, event):
        """ Link radio button selected """
        # this is unnecessary - works automatically!
        #self.TableNodeRadioButton.SetValue(False)
        #self.TableLinkRadioButton.SetValue(True)
        self.TableColumnListBox.SetItems(self.LinkColumnList())
        self.TableColumnListBox.SetChecked(self.LinkCurrentColumns)
        self.IDChoice.SetItems(self.GetLinkIDChoices())
        self.IDChoice.SetSelection(self.LinkIDChoice)

    def OnIDChoice(self, event):
        #print('Selected item index %d' % self.IDChoice.GetSelection())
        if self.TableNodeRadioButton.GetValue() == True:
            self.NodeIDChoice = self.IDChoice.GetSelection()
        else:
            self.LinkIDChoice = self.IDChoice.GetSelection()

    def OnTimestepChoice(self, event):
        self.TimestepIndex = self.TimestepChoice.GetSelection()
        #print('Selected timestep index %d' % self.TimestepIndex)

    def OnColumnListEvent(self, event):
        #print('Column list event: %s' % event.GetString())
        pass

    def OnColumnListCheckEvent(self, event):
        index = event.GetSelection()
        self.TableColumnListBox.SetSelection(index)
        if self.TableNodeRadioButton.GetValue() == True:
            self.NodeCurrentColumns = self.TableColumnListBox.GetChecked()
        else:
            self.LinkCurrentColumns = self.TableColumnListBox.GetChecked()

    def OnSave(self, event):
        """ Save table """
        errdlg = wx.MessageDialog(self,
                _('Saving of tables is not yet supported.'),
                _('Error'),
                style=wx.OK | wx.ICON_ERROR)
        errdlg.ShowModal()
        errdlg.Destroy()


    def OnOpen(self, event, progress):
        """ Open a file"""

        # configure the tables panel - report all nodes, timesteps
        self.IDChoice.SetItems(self.GetNodeIDChoices())
        self.NodeIDChoice = 0
        self.IDChoice.SetSelection(self.NodeIDChoice)
        self.LinkIDChoice = 0
        self.TimestepChoice.SetItems(self.GetTimestepChoices())
        self.TimestepIndex = 0
        self.TimestepChoice.SetSelection(self.TimestepIndex)



class MyXLSGrid(xlsg.XLSGrid):

    def __init__(self, parent):
        xlsg.XLSGrid.__init__(self, parent)

    def Save():
        print('Save is not yet supported')


