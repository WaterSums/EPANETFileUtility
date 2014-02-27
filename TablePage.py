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
    from xlwt import Workbook
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
        self.IDChoice = None
        self.NodeIDChoice = 0
        self.LinkIDChoice = 0
        self.TimestepChoice = None
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
"""Select what the table should contain and press Update table button...
NOTE: SAVING IS NOT YET AVAILABLE."""))
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

            m_update = wx.Button(win, -1, _("Update table"))
            m_update.Bind(wx.EVT_BUTTON, self.OnUpdate)
            gbs.Add(m_update, (5,2), flag = wx.ALL | wx.ALIGN_RIGHT, border=10)

            # TODO allow selection of multiple IDs using a multi-choice
            # dialog MultiChoiceDialog or ItemsPicker
            self.IDChoice = st = wx.Choice(win)
            st.Bind(wx.EVT_CHOICE, self.OnIDChoice)
            gbs.Add(st, (1,3), flag = wx.GROW | wx.RIGHT, border=30)

            # TODO allow selection of multiple timesteps using a multi-choice
            # dialog MultiChoiceDialog or ItemsPicker
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

            self.TablesXLSGrid = st = MyXLSGrid(win)
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

Displaying tables requires the xlrt and xlwt packages.
See http://pypi.python.org/pypi/xlrd
and http://pypi.python.org/pypi/xlwt

The xlutils package may be required later.
See http://pypi.python.org/pypi/xlutils"""))
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
                _('Water Quality')
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
                6,      #'Water Quality'
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
                _('Water Quality'),
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
                10,     # 'Water Quality',
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

    def OnUpdate(self, event):
        """ Update table """
        print('Updating table')
        fname, sname = self.GenerateTable()

        book = xlrd.open_workbook(fname, formatting_info=1)

        sheet = book.sheet_by_name(sname)
        rows, cols = sheet.nrows, sheet.ncols

        comments, texts = xlsg.ReadExcelCOM(fname, sname, rows, cols)

        self.TablesXLSGrid.PopulateGrid(book, sheet, texts, comments)


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

        #fname, sname = self.GenerateTable()
        #book = xlrd.open_workbook(fname, formatting_info=1)
        #sheet = book.sheet_by_name(sname)
        #rows, cols = sheet.nrows, sheet.ncols
        #comments, texts = xlsg.ReadExcelCOM(fname, sname, rows, cols)
        #self.TablesXLSGrid.PopulateGrid(book, sheet, texts, comments)

    def GenerateTable(self):
        book = Workbook()
        fname = 'simple.xls'
        sname ='Sheet 1'
        sheet1 = book.add_sheet(sname)

        if self.TimestepIndex == 0:
            tmin = 0
            tmax = self.epanetoutputfile().Epilog['nPeriods']
        else:
            tmin = self.TimestepIndex-1 # (-1 since we offer 'All' option)
            tmax = self.TimestepIndex

        heading_xf = xlwt.easyxf('font: bold on; align: wrap on, vert centre, horiz center')
        if self.TableNodeRadioButton.GetValue() == True:
            # generate a node table
            if self.NodeIDChoice == 0:
                # generate table for all node IDs
                idmin = 0
                idmax = len(self.epanetoutputfile().Prolog['NodeID'])
            else:
                # generate table for selected node ID
                idmin = self.NodeIDChoice-1 # (-1 since we offer 'All' option)
                idmax = self.NodeIDChoice

            rownum = 0
            
            cols = self.NodeColumnList()
            sheet1.write(rownum,0,_('Timestep'),heading_xf)
            sheet1.col(0).width = 3000
            sheet1.write(rownum,1,_('ID'),heading_xf)
            sheet1.col(1).width = 3000
            for i in range(len(self.NodeCurrentColumns)):
                sheet1.write(rownum,i+2,cols[self.NodeCurrentColumns[i]],heading_xf)
                sheet1.col(i+2).width = 4000

            rownum = 1
            for i in range(tmin, tmax):
                t = self.epanetoutputfile().DynamicResults[i]
                p = self.epanetoutputfile().Prolog
                for j in range(idmin, idmax):
					# format with 0 decimal places
                    sheet1.write(rownum,0,i,
						xlwt.easyxf(num_format_str='#,##0'))
                    sheet1.write(rownum,1,
                        self.epanetoutputfile().Prolog['NodeID'][j])
                    for k in range(len(self.NodeCurrentColumns)):
                        if self.NodeCurrentColumns[k] == 0:   # Elevation
                            sheet1.write(rownum,k+2,p['NodeElev'][j])
                        elif self.NodeCurrentColumns[k] == 1: # Base Demand
                            pass
                        elif self.NodeCurrentColumns[k] == 2: # Initial Quality
                            pass
                        elif self.NodeCurrentColumns[k] == 3: # Demand
                            sheet1.write(rownum,k+2,t['NodeDemand'][j])
                        elif self.NodeCurrentColumns[k] == 4: # Head
                            sheet1.write(rownum,k+2,t['NodeHead'][j])
                        elif self.NodeCurrentColumns[k] == 5: # Pressure
                            sheet1.write(rownum,k+2,t['NodePressure'][j])
                        elif self.NodeCurrentColumns[k] == 6: # Water Quality
                            sheet1.write(rownum,k+2,t['NodeWaterQuality'][j])
                    rownum += 1
                    if rownum >= 65536:
                        break
                if rownum >= 65536:
                    break
        else:
            # generate a link table
            if self.LinkIDChoice == 0:
                # generate table for all IDs
                idmin = 0
                idmax = len(self.epanetoutputfile().Prolog['LinkID'])
            else:
                # generate table for selected link ID
                idmin = self.LinkIDChoice-1 # (-1 since we offer 'All' option)
                idmax = self.LinkIDChoice

            rownum = 0

            cols = self.LinkColumnList()
            sheet1.write(rownum,0,_('Timestep'),heading_xf)
            sheet1.col(0).width = 3000
            sheet1.write(rownum,1,_('ID'),heading_xf)
            sheet1.col(1).width = 3000
            for i in range(len(self.LinkCurrentColumns)):
                sheet1.write(rownum,i+2,cols[self.LinkCurrentColumns[i]],heading_xf)
                sheet1.col(i+2).width = 4000

            rownum = 1
            for i in range(tmin, tmax):
                t = self.epanetoutputfile().DynamicResults[i]
                p = self.epanetoutputfile().Prolog
                for j in range(idmin, idmax):
					# format with 0 decimal places
                    sheet1.write(rownum,0,i,
						xlwt.easyxf(num_format_str='#,##0'))
                    sheet1.write(rownum,1,
                        self.epanetoutputfile().Prolog['LinkID'][j])
                    for k in range(len(self.LinkCurrentColumns)):
                        if self.LinkCurrentColumns[k] == 0:   # Length
                            sheet1.write(rownum,k+2,p['LinkLength'][j])
                        elif self.LinkCurrentColumns[k] == 1: # Diameter
                            sheet1.write(rownum,k+2,p['LinkDiam'][j])
                        elif self.LinkCurrentColumns[k] == 2: # Roughness
                            pass
                        elif self.LinkCurrentColumns[k] == 3: # Bulk Coeff.
                            pass
                        elif self.LinkCurrentColumns[k] == 4: # Wall Coeff.
                            pass
                        elif self.LinkCurrentColumns[k] == 5: # Flow
                            sheet1.write(rownum,k+2,t['LinkFlow'][j])
                        elif self.LinkCurrentColumns[k] == 6: # Velocity
                            sheet1.write(rownum,k+2,t['LinkVelocity'][j])
                        elif self.LinkCurrentColumns[k] == 7: # Unit Headloss
                            sheet1.write(rownum,k+2,t['LinkHeadloss'][j])
                        elif self.LinkCurrentColumns[k] == 8: # Friction Factor
                            sheet1.write(rownum,k+2,t['LinkFrictionFactor'][j])
                        elif self.LinkCurrentColumns[k] == 9: # Reaction Rate
                            sheet1.write(rownum,k+2,t['LinkReactionRate'][j])
                        elif self.LinkCurrentColumns[k] == 10: # Water Quality
                            sheet1.write(rownum,k+2,t['LinkAveWaterQuality'][j])
                        elif self.LinkCurrentColumns[k] == 11: # Status
                            sheet1.write(rownum,k+2,t['LinkStatus'][j])
                    rownum += 1
                    if rownum >= 65536:
                        break
                if rownum >= 65536:
                    break

        if rownum >= 65536:
            errdlg = wx.MessageDialog(self,
                    _('Sorry, but a maximum of 65,536 rows can be displayed in the table page.  With the current table configuration, it should contain %(numrows)d rows.\n\nThe table has been truncated.') %
                    {'numrows': ((tmax-tmin)*(idmax-idmin))+1},
                    _('Error'), style=wx.OK | wx.ICON_ERROR)
            errdlg.ShowModal()
            errdlg.Destroy()

        book.save(fname)
        return (fname, sname)



class MyXLSGrid(xlsg.XLSGrid):

    def __init__(self, parent):
        xlsg.XLSGrid.__init__(self, parent)

    def Save():
        print('Save is not yet supported')


