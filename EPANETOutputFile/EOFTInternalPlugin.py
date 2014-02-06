# ex:set ts=4 sw=4: <- for vim
#
# EPANET Output File Tool Internal Plugin which reads EPANET 2.00.12 Output File
#
import EPANETOutputFilePlugin
import struct

class InternalPlugin(EPANETOutputFilePlugin.EOFTPlugin):

    def __init__(self):
        # TODO initialise translations?
        # since this is an internal plugin, we don't need to do this.
        self.parser = None
        self.options = None
        pass

    def Test(self, eof):
        #print("InternalPlugin:Test function")
        pass

    def Init(self, parser):
        #print("%s:Init(%s)" % (self.__class__.__name__, parser))
        parser.add_option('-a','--all',
            action='store_true', dest = 'all', default=False,
            help=_('display all output file sections (default)'))
        parser.add_option('-s','--silent',
            action='store_true', dest = 'silent', default=False,
            help=_('don\'t display any output file sections'))
        parser.add_option('-p','--prolog',
            action='store_true', dest = 'prolog', default=False,
            help=_('display prolog section'))
        parser.add_option('-n','--prolog_node_csv',
            action='store', type='string', dest = 'prolog_node_csv',
            metavar = 'PROLOG_NODE_CSV',
            help=_('write CSV for nodes from prolog to PROLOG_NODE_CSV'))
        parser.add_option('-l','--prolog_link_csv',
            action='store', type='string',
            dest = 'prolog_link_csv', metavar = 'PROLOG_LINK_CSV',
            help=_('write CSV for links from prolog to PROLOG_LINK_CSV'))
        parser.add_option('-e','--energy_use',
            action='store_true', dest = 'energy_use', default=False,
            help=_('display energy use section'))
        parser.add_option('-E','--energy_use_csv',
            action='store', type='string', dest = 'energy_use_csv',
            metavar = 'ENERGY_CSV',
            help=_('write CSV from energy use section to ENERGY_CSV'))
        parser.add_option('-d','--dynamic_results',
            action='store_true', dest = 'dynamic_results', default=False,
            help=_('display dynamic results section'))
        parser.add_option('-N','--dynamic_node_csv',
            action='store', type='string', dest = 'dynamic_node_csv',
            metavar = 'DYNAMIC_NODE_CSV',
            help=_('write CSV for nodes from dynamic results to DYNAMIC_NODE_CSV'))
        parser.add_option('-L','--dynamic_link_csv',
            action='store', type='string', dest = 'dynamic_link_csv',
            metavar = 'DYNAMIC_LINK_CSV',
            help=_('write CSV for links from dynamic results to DYNAMIC_LINK_CSV'))
        parser.add_option('-c','--coda', '--epilog',
            action='store_true', dest = 'epilog', default=False,
            help=_('display file epilog'))

    def FileInit(self, eof, options):
        #print("InternalPlugin:FileInit(%s, %s)" % (eof, options))
        # if user has not specified anything to do, dump everything
        self.options = options
        if (options.prolog == False
                and options.energy_use == False
                and options.dynamic_results == False
                and options.epilog == False
                and options.prolog_node_csv is None
                and options.prolog_link_csv is None
                and options.energy_use_csv is None
                and options.dynamic_node_csv is None
                and options.dynamic_link_csv is None):
            if options.silent == False: options.all = True
        # 'silent' wins over all printing except errors....
        if options.silent == True: options.prolog = False
        if options.silent == True: options.energy_use = False
        if options.silent == True: options.dynamic_results = False
        if options.silent == True: options.epilog = False
        if options.silent == True: options.verbose = False
        if options.verbose:
            if options.prolog == True:
                print(_("User requested display of file prolog section"))
            if options.prolog_node_csv is not None:
                print(_("User requested writing of prolog node info as CSV to: %s") % options.prolog_node_csv)
            if options.prolog_link_csv is not None:
                print(_("User requested writing of prolog link info as CSV to: %s") % options.prolog_link_csv)
            if options.energy_use == True:
                print(_("User requested display of energy use section"))
            if options.energy_use_csv is not None:
                print(_("User requested writing of energy use section as CSV to: %s") % options.energy_use_csv)
            if options.dynamic_results  == True:
                print(_("User requested display of file dynamic results section"))
            if options.dynamic_node_csv is not None:
                print(_("User requested writing of dynamic node info as CSV to: %s") % options.dynamic_node_csv)
            if options.dynamic_link_csv is not None:
                print(_("User requested writing of dynamic link info as CSV to: %s") % options.dynamic_link_csv)
            if options.epilog == True:
                print(_("User requested display of file epilog section"))
            if options.all == True:
                print(_("User requested display of content from all file sections"))


    def FileOpen(self, eof, progupdate):
        '''File has been opened.  No return value.

        Args:

            eof (EPANETOutputFile): output file loading coordinator
            progupdate (None or function):
                called as progupdate(% of task done (0-100), text description of current step)

        '''
        #print("InternalPlugin:FileOpen(%s)" % eof)
        # read some info from end first to verify file type
        if progupdate is not None: progupdate(5,_('Verifying file type...'))
        # read some info from end first
        eof.f.seek(-12,2)
        eof.Epilog['nPeriods'], = struct.unpack('<i', eof.f.read(4))
        eof.Epilog['WarningFlag'], = struct.unpack('<i', eof.f.read(4))
        eof.Epilog['magic'], = magicend, = struct.unpack('<i', eof.f.read(4))

        eof.f.seek(0)
        eof.Prolog['magic'], = magicstart, = struct.unpack('<i', eof.f.read(4))
        if magicstart != magicend:
            print(_('ERROR: magic number in prolog (%(prologmagic)d) does not match magic number in epilog (%(epilogmagic)d)') % {'prologmagic': magicstart, 'epilogmagic': magicend})
            raise Exception(_('ERROR: magic numbers do not match: probably not an EPANET output file'))
        if progupdate is not None: progupdate(100,_('Verified file type.'))


    def ReadProlog(self, eof, f, d, magicend, progupdate):
        '''Read prolog from EPANET output file.  No return value.

        Args:

            f (file):               file in correct position to read prolog data
            d (dictionary):         dictionary provided to store prolog values in
            magicend (int):         magic value read from epilog which should match one in prolog
            progupdate (None or function):
                called as progupdate(% of task done (0-100), text description of current step)

        '''

        if progupdate is not None: progupdate(5,_('Reading prolog info'))
        d['magic'], = struct.unpack('<i', f.read(4))
        if d['magic'] != magicend:
            print(_('ERROR: magic number in prolog (%(prologmagic)d) does not match magic number in epilog (%(epilogmagic)d)') % {'prologmagic': d['magic'], 'epilogmagic': magicend})
            raise Exception(_('ERROR: magic numbers do not match: probably not an EPANET output file'))
        d['version'], = struct.unpack('<i', f.read(4))
        d['nNodes'], = struct.unpack('<i', f.read(4))
        d['nResTanks'], = struct.unpack('<i', f.read(4))
        d['nJunctions'] = d['nNodes'] - d['nResTanks']
        d['nLinks'], = struct.unpack('<i', f.read(4))
        d['nPumps'], = struct.unpack('<i', f.read(4))
        d['nValves'], = struct.unpack('<i', f.read(4))
        d['nPipes'] = d['nLinks'] - d['nPumps'] - d['nValves']
        d['WaterQualityOptNum'], = struct.unpack('<i', f.read(4))
        d['WaterQualityOption'] = eof.getWaterQualityOptionText(d['WaterQualityOptNum'])
        # read source node index and make it 0-based
        d['source_node_index'] = struct.unpack('<i', f.read(4))[0] - 1
        d['FlowUnitsOptNum'], = struct.unpack('<i', f.read(4))
        d['FlowUnitsOption'] = eof.getFlowUnitsOptionText(d['FlowUnitsOptNum'])
        d['PressureUnitsOptNum'], = struct.unpack('<i', f.read(4))
        d['PressureUnitsOption'] = eof.getPressureUnitsOptionText(d['PressureUnitsOptNum'])
        d['TimeStatsOptNum'], = struct.unpack('<i', f.read(4))
        d['TimeStatsOption'] = eof.getTimeStatsOption(d['TimeStatsOptNum'])
        d['StartTime'], = struct.unpack('<i', f.read(4))
        d['ReportTimeStep'], = struct.unpack('<i', f.read(4))
        d['SimulationDuration'], = struct.unpack('<i', f.read(4))
        d['Title1'] = f.read(80).strip('\0')
        d['Title2'] = f.read(80).strip('\0')
        d['Title3'] = f.read(80).strip('\0')
        d['InputFile'] =  f.read(260).strip('\0')
        d['ReportFile'] =  f.read(260).strip('\0')
        d['ChemicalName'] =  f.read(32).strip('\0')
        d['ChemicalConcentrationUnits'] =  f.read(32).strip('\0')
        d['NodeID'] = []
        d['NodeElev'] = []
        d['NodeTankResIndex'] = []
        if progupdate is not None: progupdate(20,_('Reading prolog node info'))
        if eof.options.verbose:
            print(_('Reading Node IDs (%(nNodes)d)...') % {'nNodes': d['nNodes']})
        for i in range (0, d['nNodes']):
            d['NodeID'].append(f.read(32).strip('\0'))
            #print('  Node %d ID: %s' % (i, NodeID[i]))
            d['NodeTankResIndex'].append(-1)

        d['LinkID'] = []
        d['LinkStart'] = []
        d['LinkEnd'] = []
        d['LinkType'] = []
        d['LinkLength'] = []
        d['LinkDiam'] = []

        if progupdate is not None: progupdate(50,_('Reading prolog link info'))
        if eof.options.verbose:
            print(_('Reading Link IDs (%(nLinks)d)...') % {'nLinks': d['nLinks']})
        for i in range (0, d['nLinks']):
            d['LinkID'].append(f.read(32).strip('\0'))
            #print('  Link %d ID: %s' % (i, d['LinkID[i]))
        for i in range (0, d['nLinks']):
            d['LinkStart'].append(struct.unpack('<i', f.read(4))[0]-1)
            #print('  LinkStart %d ID: %d (0-based)' % (i, LinkStart[i]))
        for i in range (0, d['nLinks']):
            d['LinkEnd'].append(struct.unpack('<i', f.read(4))[0]-1)
            #print('  LinkEnd %d ID: %d (0-based)' % (i, LinkEnd[i]))
        for i in range (0, d['nLinks']):
            d['LinkType'].append(struct.unpack('<i', f.read(4))[0])
            #print('  LinkType %d ID: %d' % (i, LinkType[i]))
        d['TankResIndex'] = []
        if eof.options.verbose:
            print(_('Reading Tank/Reservoir indexes (%(nResTanks)d)...') % {'nResTanks': d['nResTanks']})
        for i in range (0, d['nResTanks']):
            # read the index of tank/res and take off 1 to make it zero-based
            d['TankResIndex'].append(struct.unpack('<i', f.read(4))[0] - 1)
            #print('  Node index (0-based) of tank %d: %d' % (i, d['TankResIndex[i]))
            # store index of tank or res in node array
            d['NodeTankResIndex'][d['TankResIndex'][i]] = i
        d['TankResXSectArea'] = []
        if eof.options.verbose:
            print(_('Reading Cross Sectional Areas of Tanks/Reservoirs (%(nResTanks)d)...') % {'nResTanks': d['nResTanks']})
        nReservoirs = 0
        for i in range (0, d['nResTanks']):
            val = struct.unpack('<f', f.read(4))[0]
            if val == 0.0:
                nReservoirs += 1
            d['TankResXSectArea'].append(val)
            #print('  Cross Sectional Area of tank %d: %d' % (i, TankResXSectArea[i]))
        d['nReservoirs'] = nReservoirs
        d['nTanks'] = d['nResTanks'] - nReservoirs

        for i in range (0, d['nNodes']):
            d['NodeElev'].append(struct.unpack('<f', f.read(4))[0])
            #print('  Node %d elevation: %s' % (i, d['NodeElev'][i]))

        if progupdate is not None: progupdate(80,_('Reading prolog extra info'))

        if eof.options.verbose:
            print(_('Reading Link lengths (%(nLinks)d)...') % {'nLinks': d['nLinks']})
        for i in range (0, d['nLinks']):
            d['LinkLength'].append(struct.unpack('<f', f.read(4))[0])
            #print('  Link %d length: %s' % (i, LinkLength[i]))
        if eof.options.verbose:
            print(_('Reading Link diameters (%(nLinks)d)...') % {'nLinks': d['nLinks']})
        for i in range (0, d['nLinks']):
            d['LinkDiam'].append(struct.unpack('<f', f.read(4))[0])
            #print('  Link %d diameter: %s' % (i, LinkDiam[i]))

    def PrologRead(self, eof, progupdate):
        #print("%s:PrologRead(%s)" % (self.__class__.__name__, eof))
        # read prolog (matching magic numbers at start and end already read
        # and checked)
        self.ReadProlog(eof, eof.f, eof.Prolog, eof.Epilog['magic'], progupdate)

    def PrintProlog(self, eof, d):
        '''Print EPANET output file prolog.  No return value.

        Args:
            d (dictionary): Prolog dictionary to print

        '''
        print("")
        headingtext = _("Prolog")
        print(headingtext)
        print('='*len(headingtext))
        print(_('Magic number: %d') % d['magic'])
        print(_('EPANET Version: %d') % d['version'])
        print(_('Number of Nodes: %d') % d['nNodes'])
        print(_('Number of Reservoirs (%(nRes)d) + Tanks (%(nTank)d): %(nResTank)d (so %(nJunc)d Junctions)')
                % { 'nRes': d['nReservoirs'],
                    'nTank': d['nTanks'],
                    'nResTank': d['nResTanks'],
                    'nJunc': d['nJunctions']})
        print(_('Number of Links: %d') % d['nLinks'])
        print(_('Number of Pumps: %d') % d['nPumps'])
        print(_('Number of Valves: %d') % d['nValves'])
        print(_('  (Number of Pipes: %d)') % d['nPipes'])
        print(_('Water Quality Option: %(optnum)d (%(opttext)s)') % {'optnum': d['WaterQualityOptNum'], 'opttext': d['WaterQualityOption']})
        print(_('Index of node for Source Tracing: %d') % d['source_node_index'])
        print(_('Flow Units Option: %(optnum)d (%(opttext)s)') % {'optnum': d['FlowUnitsOptNum'], 'opttext': d['FlowUnitsOption']})
        print(_('Pressure Units Option: %(optnum)d (%(opttext)s)') % {'optnum': d['PressureUnitsOptNum'], 'opttext': d['PressureUnitsOption']})
        print(_('Time Statistics Flag: %(optnum)d (%(opttext)s)') % {'optnum': d['TimeStatsOptNum'], 'opttext': d['TimeStatsOption']})
        print(_('Reporting Start Time: %d') % d['StartTime'])
        print(_('Reporting Time Step: %d') % d['ReportTimeStep'])
        print(_('Simulation Duration: %d') % d['SimulationDuration'])
        print(_('Problem Title1: %s') % d['Title1'])
        print(_('Problem Title2: %s') % d['Title2'])
        print(_('Problem Title3: %s') % d['Title3'])
        print(_('Name of Input File: %s') % d['InputFile'])
        print(_('Name of Report File: %s') % d['ReportFile'])
        print(_('Name of Chemical: %s') % d['ChemicalName'])
        print(_('Chemical Concentration Units: %s') % d['ChemicalConcentrationUnits'])

        print(_('Node details (%d):') % d['nNodes'])
        for i in range (0, d['nNodes']):
            if d['NodeTankResIndex'][i] == -1:
                print(_('  %(index)d: ID %(id)s, elevation: %(elev)f')
                        % {'index': i, 'id': d['NodeID'][i], 'elev': d['NodeElev'][i]})
            elif d['TankResXSectArea'][d['NodeTankResIndex'][i]] == 0.0:
                print(_('  %(index)d: ID %(id)s, elevation: %(elev)f (RESERVOIR)')
                        % {'index': i, 'id': d['NodeID'][i], 'elev': d['NodeElev'][i]})
            else:
                print(_('  %(index)d: ID %(id)s, elevation: %(elev)f, Tank x-sect area: %(xsect)f')
                        % {'index': i, 'id': d['NodeID'][i], 'elev':  d['NodeElev'][i],
                            'xsect': d['TankResXSectArea'][d['NodeTankResIndex'][i]]})

        print(_('Link details (%(nLinks)d):') % {'nLinks': d['nLinks']})
        for i in range (0, d['nLinks']):
            option = eof.getLinkTypeText(d['LinkType'][i])
            # NB: the LinkStart and LinkEnd values are indexes which are
            # zero based, whereas the data file stores them 1-based
            print(_('  %d: ID %s, start: %d, end: %d, type: %d (%s), length: %f, diam: %f') % (i, d['LinkID'][i], d['LinkStart'][i], d['LinkEnd'][i], d['LinkType'][i], option, d['LinkLength'][i], d['LinkDiam'][i]))
        print("")

    def PrologPrint(self, eof, progupdate):
        ''' Callback message: print prolog section. Progress 0-100. '''
        #print("%s:PrologPrint(%s)" % (self.__class__.__name__, eof))
        if eof.options.prolog or eof.options.all:
            self.PrintProlog(eof, eof.Prolog)


    def WritePrologNodeCSV(self, csvname, d):
        '''Export EPANET output file node info to CSV.  No return value.

        Args:
            csvname (string):   name of file in which to write prolog node data in CSV format
            d (dictionary):     prolog dictionary with node data to write 
        '''
        print(_("Writing prolog node info CSV: %s") % csvname)
        csvf = open(csvname,'w')
        csvf.write(_('"ID", "Type", "Elevation", "XSectArea"\n'))
        for i in range (0, d['nNodes']):
            if d['NodeTankResIndex'][i] == -1:
                csvf.write('"%s", "Junction", %f, 0.0\n'
                        % (d['NodeID'][i], d['NodeElev'][i]))
            elif d['TankResXSectArea'][d['NodeTankResIndex'][i]] == 0.0:
                csvf.write('"%s", "Reservoir", %f, 0.0\n'
                        % (d['NodeID'][i], d['NodeElev'][i]))
            else:
                csvf.write('"%s", "Tank", %f, %f\n'
                        % (d['NodeID'][i], d['NodeElev'][i],
                        d['TankResXSectArea'][d['NodeTankResIndex'][i]]))
        csvf.close()

    def WritePrologLinkCSV(self, eof, csvname, d):
        '''Export EPANET output file link info to CSV.  No return value.

        Args:
            csvname (string):   name of file in which to write link data in CSV format
            d (dictionary):     prolog dictionary with link data to write 
        '''
        print(_("Writing prolog link info CSV: %s") % csvname)
        csvf = open(csvname,'w')
        csvf.write(_('"ID", "StartNodeID", "EndNodeID", "Type", "Length", "Diameter"\n'))
        for i in range (0, d['nLinks']):
            option = eof.getLinkTypeText(d['LinkType'][i])
            # NB: the LinkStart and LinkEnd values are indexes which are
            # zero based, whereas the data file stores them 1-based.
            csvf.write('"%s", "%s", "%s", "%s", %f, %f\n'
                    % (d['LinkID'][i], d['NodeID'][d['LinkStart'][i]],
                        d['NodeID'][d['LinkEnd'][i]],
                        option, d['LinkLength'][i], d['LinkDiam'][i]))
        csvf.close()

    def PrologExport(self, eof, progupdate):
        ''' Callback message: export prolog section. Progress 0-100. '''
        #print("%s:PrologExport(%s)" % (self.__class__.__name__, eof))
        if eof.options.prolog_node_csv is not None:
            self.WritePrologNodeCSV(eof.options.prolog_node_csv, eof.Prolog)

        if eof.options.prolog_link_csv is not None:
            self.WritePrologLinkCSV(eof, eof.options.prolog_link_csv, eof.Prolog)


    def ReadEnergyUsage(self, eof, f, Prolog, d, progupdate):
        '''Read energy usage from EPANET output file.  No return value.

        Args:

            f (file):           file in correct position to read energy data
            Prolog (dictionary):prolog data already read from file
            d (dictionary):     dictionary provided to store energy use values in
            progupdate (None or function):
                called as progupdate(% of work done (0-100), text description of current step)

        '''

        if progupdate is not None: progupdate(5,_('Reading energy usage'))

        d['PumpIndex'] = []
        d['PumpUtilization'] = []
        d['PumpAveEfficiency'] = []
        d['PumpAvekWPerVol'] = []
        d['PumpAvekW'] = []
        d['PumpPeakkW'] = []
        d['PumpAveCostPerDay'] = []

        for i in range(0,Prolog['nPumps']):
            d['PumpIndex'].append(struct.unpack('<i', f.read(4))[0]-1) # make 0-based
            d['PumpUtilization'].append(struct.unpack('<f', f.read(4))[0])
            d['PumpAveEfficiency'].append(struct.unpack('<f', f.read(4))[0])
            d['PumpAvekWPerVol'].append(struct.unpack('<f', f.read(4))[0])
            d['PumpAvekW'].append(struct.unpack('<f', f.read(4))[0])
            d['PumpPeakkW'].append(struct.unpack('<f', f.read(4))[0])
            d['PumpAveCostPerDay'].append(struct.unpack('<f', f.read(4))[0])

        # should this be PumpPeakDemandCost?
        d['PumpPeakEnergyUsage'] = struct.unpack('<f', f.read(4))[0]
        if progupdate is not None: progupdate(100,_('Read energy usage'))


    def EnergyUsageRead(self, eof, progupdate):
        #print("%s:EnergyUsageRead(%s)" % (self.__class__.__name__, eof))
        # read energy usage section
        self.ReadEnergyUsage(eof, eof.f, eof.Prolog, eof.EnergyUse, progupdate)


    def PrintEnergyUsage(self, prolog, d):
        '''Print EPANET output file energy usage.  No return value.

        Args:
            prolog (dictionary):    Prolog data
            d (dictionary):         Energy Use dictionary to print

        '''
        print("")
        headingtext = _("Energy Use")
        print(headingtext)
        print('='*len(headingtext))
        print(_("Energy Use for %(nPumps)d Pumps") % {'nPumps': prolog['nPumps']})
        for i in range(0,prolog['nPumps']):
            ind = d['PumpIndex'][i]
            print(_("Pump %d: link %d, util %f%%, effic %f%%, Ave kW/vol %f, Ave %f kW, Peak %f kW, Ave cost/day %f")
                    % (i, ind, d['PumpUtilization'][i],
                        d['PumpAveEfficiency'][i],
                        d['PumpAvekWPerVol'][i], d['PumpAvekW'][i],
                        d['PumpPeakkW'][i], d['PumpAveCostPerDay'][i]))
        print(_("Peak energy usage: %f") % d['PumpPeakEnergyUsage'])
        print("")

    def EnergyUsagePrint(self, eof, progupdate):
        ''' Callback message: print file energy usage section. Progress 0-100. '''
        #print("%s:EnergyUsagePrint(%s)" % (self.__class__.__name__, eof))
        if eof.options.energy_use or eof.options.all:
            self.PrintEnergyUsage(eof.Prolog, eof.EnergyUse)


    def WriteEnergyUseCSV(self, csvname, prolog, d):
        '''Export EPANET output file energy usage info to CSV.  No return value.

        Args:
            csvname (string):       name of file in which to write pump energy use data in CSV format
            prolog (dictionary):    prolog dictionary with link data
            d (dictionary):         energy use dictionary to write data from

        '''
        print(_("Writing energy usage to CSV: %s") % csvname)
        csvf = open(csvname,'w')
        csvf.write(_('"ID", "PumpUtilization", "PumpAveEfficiency", "PumpAvekWPerVol", "PumpAvekW", "PumpPeakkW", "PumpAveCostPerDay"\n'))
        for i in range(0,prolog['nPumps']):
            ind = d['PumpIndex'][i]
            csvf.write( '"%s", %f, %f, %f, %f, %f, %f\n' % (prolog['LinkID'][ind], 
                d['PumpUtilization'][i], d['PumpAveEfficiency'][i],
                d['PumpAvekWPerVol'][i], d['PumpAvekW'][i], d['PumpPeakkW'][i],
                d['PumpAveCostPerDay'][i]))
        csvf.close()


    def EnergyUsageExport(self, eof, progupdate):
        ''' Callback message: epxort file energy usage section. Progress 0-100. '''
        #print("%s:EnergyUsageExport(%s)" % (self.__class__.__name__, eof))
        if eof.options.energy_use_csv is not None:
            self.WriteEnergyUseCSV(eof.options.energy_use_csv, 
                    eof.Prolog, eof.EnergyUse)




    def ReadDynamicResults(self, f, Prolog, nPeriods, DynamicResults, progupdate):
        '''Read dynamic results from EPANET output file.  No return value.

        Args:
            f (file):               file in correct position to read dynamic results
            Prolog (dictionary):    prolog data already read from file
            nPeriods (int):         number of time steps in simulation
            DynamicResults (list):  a dictionary is appended to this list for each time step read
            progupdate (None or function):
                called as progupdate(% of work done (40-79), text description of current step)

        '''

        if progupdate is not None: progupdate(0,_('Reading dynamic results'))

        nNodes = Prolog['nNodes']
        nLinks = Prolog['nLinks']

        # our progress goes from 40 to 79 in nPeriods
        oldprog = 0

        for i in range(0,nPeriods):
            if progupdate is not None:
                newprog = int(100*(float(i)/float(nPeriods)))
                if newprog > oldprog + 2:
                    progupdate(newprog,_('Reading dynamic results timestep %d') % i)
                    oldprog = newprog
            NodeDemand = []
            NodeHead = []
            NodePressure = []
            NodeWaterQuality = []
            LinkFlow = []
            LinkVelocity = []
            LinkHeadloss = []
            LinkAveWaterQuality = []
            LinkStatus = []
            LinkSetting = []
            LinkReactionRate = []
            LinkFrictionFactor = []
            for j in range(0,nNodes):
                NodeDemand.append(struct.unpack('<f', f.read(4))[0])
            for j in range(0,nNodes):
                NodeHead.append(struct.unpack('<f', f.read(4))[0])
            for j in range(0,nNodes):
                NodePressure.append(struct.unpack('<f', f.read(4))[0])
            for j in range(0,nNodes):
                NodeWaterQuality.append(struct.unpack('<f', f.read(4))[0])
            for j in range(0,nLinks):
                LinkFlow.append(struct.unpack('<f', f.read(4))[0])
            for j in range(0,nLinks):
                LinkVelocity.append(struct.unpack('<f', f.read(4))[0])
            for j in range(0,nLinks):
                LinkHeadloss.append(struct.unpack('<f', f.read(4))[0])
            for j in range(0,nLinks):
                LinkAveWaterQuality.append(struct.unpack('<f', f.read(4))[0])
            for j in range(0,nLinks):
                LinkStatus.append(struct.unpack('<f', f.read(4))[0])
            for j in range(0,nLinks):
                LinkSetting.append(struct.unpack('<f', f.read(4))[0])
            for j in range(0,nLinks):
                LinkReactionRate.append(struct.unpack('<f', f.read(4))[0])
            for j in range(0,nLinks):
                LinkFrictionFactor.append(struct.unpack('<f', f.read(4))[0])

            TimeStepD = {}
            TimeStepD['NodeDemand'] = NodeDemand
            TimeStepD['NodeHead'] = NodeHead
            TimeStepD['NodePressure'] = NodePressure
            TimeStepD['NodeWaterQuality'] = NodeWaterQuality
            TimeStepD['LinkFlow'] = LinkFlow
            TimeStepD['LinkVelocity'] = LinkVelocity
            TimeStepD['LinkHeadloss'] = LinkHeadloss
            TimeStepD['LinkAveWaterQuality'] = LinkAveWaterQuality
            TimeStepD['LinkStatus'] = LinkStatus
            TimeStepD['LinkSetting'] = LinkSetting
            TimeStepD['LinkReactionRate'] = LinkReactionRate
            TimeStepD['LinkFrictionFactor'] = LinkFrictionFactor

            DynamicResults.append(TimeStepD)

        if progupdate is not None: progupdate(100,_('Finished reading dynamic results'))


    def DynamicResultsRead(self, eof, progupdate):
        #print("%s:DynamicResultsRead(%s)" % (self.__class__.__name__, eof))
        self.ReadDynamicResults(eof.f, eof.Prolog, eof.Epilog['nPeriods'],
                eof.DynamicResults, progupdate)


    def PrintDynamicResults(self, Prolog, nPeriods, DynamicResults):
        '''Print EPANET output file dynamic results.  No return value.

        Args:
            Prolog (dictionary):    Prolog dictionary
            nPeriods (int):         number of time steps in simulation
            DynamicResults (list):  list of dynamic result dictionaries for printing, one for each timestep

        '''
        print("")
        headingtext = _("Dynamic Results")
        print(headingtext)
        print('='*len(headingtext))
        for i in range(0,nPeriods):
            d = DynamicResults[i]
            print(_("TimeStep %d") % i)
            print(_(" Nodes"))
            for j in range(0,Prolog['nNodes']):
                print(_("  Node %d: demand %f, head %f, pressure %f, water quality %f") % (j, d['NodeDemand'][j], d['NodeHead'][j], d['NodePressure'][j], d['NodeWaterQuality'][j]))
            print(_(" Links"))
            for j in range(0,Prolog['nLinks']):
                print(_("  Link %d: flow %f, velocity %f, headloss %f, ave water qual %f, status %f, react rate %f, frict fact %f") % (j,
                    d['LinkFlow'][j], d['LinkVelocity'][j], d['LinkHeadloss'][j],
                    d['LinkAveWaterQuality'][j], d['LinkStatus'][j],
                    d['LinkReactionRate'][j], d['LinkFrictionFactor'][j]))
            print("")

    def DynamicResultsPrint(self, eof, progupdate):
        ''' Callback message: print file dynamic results section. Progress 0-100. '''
        #print("%s:DynamicResultsPrint(%s)" % (self.__class__.__name__, eof))
        if eof.options.dynamic_results or eof.options.all:
            self.PrintDynamicResults(eof.Prolog, eof.Epilog['nPeriods'],
                    eof.DynamicResults)


    def WriteDynamicNodeCSV(self, csvname, prolog, nPeriods, DynamicResults):
        '''Export EPANET otuput file dynamic results (nodes) to CSV.  No return value.

        Args:
            csvname (string):       name of file in which to write dynamic node data in CSV format
            prolog (dictionary):    prolog dictionary with node data
            nPeriods (int):         number of time steps in simulation
            DynamicResults (list):  list of dictionaries to write, one for each timestep

        '''
        if csvname is not None:
            print(_("Writing dynamic results for nodes to CSV: %s") % csvname)
            nodecsvf = open(csvname,'w')
            nodecsvf.write(_('"TimeStep","Time (sec)","ID", "Demand", "Head", "Pressure (%s)", "WaterQuality (%s)"\n') % (prolog['PressureUnitsOption'], prolog['WaterQualityOption']))
            for i in range(0,nPeriods):
                d = DynamicResults[i]
                for j in range(0,prolog['nNodes']):
                    nodecsvf.write('%d, %d, "%s", %f, %f, %f, %f\n'
                            % (i, prolog['StartTime'] +
                                (i*prolog['ReportTimeStep']),
                                prolog['NodeID'][j], d['NodeDemand'][j],
                                d['NodeHead'][j], d['NodePressure'][j],
                                d['NodeWaterQuality'][j]))
            nodecsvf.close()

    def WriteDynamicLinkCSV(self, csvname, Prolog, nPeriods, DynamicResults):
        '''Export EPANET otuput file dynamic results (links) to CSV.  No return value.

        Args:
            csvname (string):       name of file in which to write dynamic link data in CSV format
            prolog (dictionary):    prolog dictionary with link data
            nPeriods (int):         number of time steps in simulation
            DynamicResults (list):  list of dictionaries to write, one for each timestep

        '''
        print(_("Writing dynamic results for links to CSV: %s") % csvname)
        linkcsvf = open(csvname,'w')
        linkcsvf.write(_('"TimeStep","Time (sec)","ID", "Flow (%s)", "Velocity", "Headloss", "AverageWaterQuality (%s)", "Status", "ReactionRate", "FrictionFactor"\n') % (Prolog['FlowUnitsOption'], Prolog['WaterQualityOption']))
        for i in range(0,nPeriods):
            d = DynamicResults[i]
            for j in range(0,Prolog['nLinks']):
                linkcsvf.write('%d, %d, "%s", %f, %f, %f, %f, %f, %f, %f\n'
                        % (i, Prolog['StartTime'] +
                            (i*Prolog['ReportTimeStep']),
                            Prolog['LinkID'][j], d['LinkFlow'][j],
                            d['LinkVelocity'][j], d['LinkHeadloss'][j],
                            d['LinkAveWaterQuality'][j],
                            d['LinkStatus'][j], d['LinkReactionRate'][j],
                            d['LinkFrictionFactor'][j]))
        linkcsvf.close()


    def DynamicResultsExport(self, eof, progupdate):
        ''' Callback message: export file dynamic results section. Progress 0-100. '''
        #print("%s:DynamicResultsExport(%s)" % (self.__class__.__name__, eof))

        # saving the dynamic node info to CSV
        if eof.options.dynamic_node_csv is not None:
            self.WriteDynamicNodeCSV(eof.options.dynamic_node_csv, 
                    eof.Prolog, eof.Epilog['nPeriods'], eof.DynamicResults)

        # saving the dynamic link info to CSV
        if eof.options.dynamic_link_csv is not None:
            self.WriteDynamicLinkCSV(eof.options.dynamic_link_csv, 
                    eof.Prolog, eof.Epilog['nPeriods'], eof.DynamicResults)


    def ReadEpilog(self, eof, f, d, progupdate):
        '''Read epilog from EPANET output file. No return value.

        Args:
            f (file):       file in correct position to read epilog data
            d (dictionary): dictionary provided to store the epilog data in
            progupdate (None or function):
                called as progupdate(% of task done (0-100), text description of current step)

        '''
        if progupdate is not None: progupdate(5,_('Reading epilog'))
        d['AveBulkReactionRate'], = struct.unpack('<f', f.read(4))
        d['AveWallReactionRate'], = struct.unpack('<f', f.read(4))
        d['AveTankReactionRate'], = struct.unpack('<f', f.read(4))
        d['AveSourceInflowRate'], = struct.unpack('<f', f.read(4))
        #eof.Epilog['nPeriods'], = struct.unpack('<i', f.read(4))
        nPeriods, = struct.unpack('<i', f.read(4))
        if d['nPeriods'] != nPeriods:
            print(_('ERROR: reading epilog nPeriods value again gives a different answer') % (d['nPeriods'],nPeriods))
        d['WarningFlag'], = struct.unpack('<i', f.read(4))
        magic, = struct.unpack('<i', f.read(4))
        if d['magic'] != magic:
            print(_('ERROR: reading epilog magic value again gives a different answer') % (d['magic'],magic))
        if progupdate is not None: progupdate(100,_('Finished reading epilog'))

    def EpilogRead(self, eof, progupdate):
        #print("%s:EpilogRead(%s)" % (self.__class__.__name__, eof))
        # read energy usage section
        self.ReadEpilog(eof, eof.f, eof.Epilog, progupdate)


    def PrintEpilog(self, d):
        '''Print EPANET output file epilog.  No return value.

        Args:
            d (dictonary):  epilog dictionary to print

        '''
        print("")
        headingtext = _("Epilog")
        print(headingtext)
        print('='*len(headingtext))
        print(_("Average Bulk Reaction Rate: %f") % d['AveBulkReactionRate'])
        print(_("Average Wall Reaction Rate: %f") % d['AveWallReactionRate'])
        print(_("Average Tank Reaction Rate: %f") % d['AveTankReactionRate'])
        print(_("Average Source Inflow Rate: %f") % d['AveSourceInflowRate'])
        print(_("Number of reporting periods: %d") % d['nPeriods'])
        if d['WarningFlag'] == 0:
            print(_('Analysis generated no errors or warnings'))
        else:
            print(_('Analysis generated warning(s)'))
        print(_('Magic number: %d') % d['magic'])
        print("")


    def EpilogPrint(self, eof, progupdate):
        ''' Callback message: print file epilog section. Progress 0-100. '''
        #print("%s:EpilogPrint(%s)" % (self.__class__.__name__, eof))
        if eof.options.epilog or eof.options.all:
            self.PrintEpilog(eof.Epilog)


    #def EpilogExport(self, eof, progupdate):
        #''' Callback message: export file epilog section. Progress 0-100. '''
        #print("%s:EpilogExport(%s)" % (self.__class__.__name__, eof))
        # Nothing for us to do

    def FileClose(self, eof, progupdate):
        ''' Callback message: file has been closed. Progress 0-100. '''
        #print("%s:FileClose(%s)" % (self.__class__.__name__, eof))



def Initialize():
    #print("InternalPlugin.py: Initialize()")
    return InternalPlugin()
