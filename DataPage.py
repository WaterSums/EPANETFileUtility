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
from ColouredPanel import ColouredPanel


class DataPage(wx.Panel):
    """ We simply derive a new class of Panel. """


    def __init__(self, frame, listbook, colour):

        # initialise ourselves as a panel belonging to the listbook
        wx.Panel.__init__(self, listbook)

        # add a coloured panel inside
        self.win = win = ColouredPanel(self, colour)
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(win, 1, wx.GROW)

        # save the main program frame
        self.MainWindow = frame

        self.currentpage = 0
        self.treesizer = None
        self.Pnodetree = None
        self.Plinktree = None
        self.Epumptree = None
        self.Dnodetree = None
        self.Dlinktree = None


    def epanetoutputfile(self):
        eof = None
        if self.MainWindow is not None:
            eof = self.MainWindow.epanetoutputfile
        return eof


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
        eof = self.epanetoutputfile()
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
                    eof = self.epanetoutputfile()
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
        eof = self.epanetoutputfile()
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
                    eof = self.epanetoutputfile()
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
        panel = self
        panel.win.Freeze()
        newindex = panel.win.GetSelectedPage()
        #print('Changed to property page %d (old page was %d)' % (newindex,
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

    def OnOpen(self, event, progress):
        """ Open a file"""

        panel = self

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


        eof = self.epanetoutputfile()
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
        #panel.Layout()

        progress.Update(100,_('Done'))


