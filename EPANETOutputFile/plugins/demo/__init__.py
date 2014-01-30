# ex:set ts=4 sw=4: <- for vim
#
# Plugins can listen to messages from the coordinating process and do whatever
# is necessary.
# 
# Messages are sent by calling specific functions in the plugin.
# This class defines all the functions and their arguments.
# A plugin inheriting from this class can override the messages
# as required.
# 
# Variables available in our 'parent' EPANETOutputFile class are:
#   options     parsed command line arguments as returned from OptionParser.parse_args()
#   args        any additional command line arguments not processed (including output file name)
#   Prolog      dictionary of entries read from output file Prolog section
#   EnergyUse   dictionary of entries read from output file Energy Use section
#   DynamicResults list of dictionaries of entries read from output file
#               Dynamic Results section - one per timestep in the file
#   Epilog      dictionary of entries read from output file Epilog section
#   fname       name of file to read
#   f           file we are reading
#
# If a plugin adds dictionary entries, use the plug name followed by an
# underscore '_' as a prefix to the key to make sure names remain unique.
#
# The Init function is called when the plugin is first loaded.
# This function initialises the plugin eg. adding command line options to
# the parser provided.  Extra command line options should only be given
# a long option which should be prefixed with the plugin name followed
# by an underscore '_' to make sure options remain unique.
#
# Command line options for a plugin should be added in a group.
# First we need the following import
#
# from optparse import OptionGroup
#
# then create the option group in the Init function
#
#        group = OptionGroup(parser, "Demo Plugin Options",
#                    "Extra output file and summary infomation.")
#
#        ...add the option groups...
#
#        parser.add_option_group(group)
#
# For example, if a demo plugin wants to
# add a logging option, the command line option might be '--demo_logging'
# using code something like:
#
#     group.add_option('--demo_logging', action='store_true',
#               dest = 'demo_logging', default=False,
#               help=_('enable logging'))
#
# If command line options use metavars, prefix these also with the plugin
# name followed by an underscore '_' to make sure they remain unique.
# For example, a logging option which allows a file name to be specified
# might use code such as:
#
#     group.add_option('--demo_logging', action='store', type='string',
#               dest = 'demo_logging', metavar = 'DEMO_LOGFILE',
#               help=_('enable logging to DEMO_LOGFILE'))
#
#
# The other messages are sent in the following order:
# - Test: called after Init, but before any other callbacks
# - FileInit file has been specified, but is not yet opened for reading
# - FileOpen file has been opened for reading, but no reading yet
# - PrologRead: the prolog section has been read
# - PrologPrint: the prolog section has been read
# - PrologExport: the prolog section has been read
# - EnergyUsageRead: the energy usage section has been read
# - EnergyUsagePrint: print the energy usage section
# - EnergyUsageExport: export the energy usage section
# - DynamicResultsRead: the dynamic results section has been read
# - DynamicResultsPrint: print the dynamic results section
# - DynamicResultsExport: export the dynamic results section
# - EpilogRead: the epilog section has been read
# - EpilogPrint: print the epilog section
# - EpilogExport: export the epilog section
# - FileClose: file has been closed after reading
# - FileTerm: file has been read and closed
#
#
#
# When the progress monitor update function is passed (ie is not None),
# progress updates can be done within the plugins.  The available progress
# range which can be used is given for each message.
# To set the progress bar use the following code:
# (changing the percentage and the comment as appropriate)
#
# if progupdate is not None: progupdate(33,_('One third done'))
#
# Most of the progress values are used by the internal plugin which
# does the actual reading of the EPANET output file.
#

import os
import struct
from optparse import OptionGroup

#print(dir())
if __name__.startswith('EPANETOutputFile'):
    from ... import EPANETOutputFilePlugin
else:
    import EPANETOutputFilePlugin

class DemoPlugin(EPANETOutputFilePlugin.EOFTPlugin):

    def __init__(self):
        self.parser = None
        self.options = None
        pass

    # These are the callback messages that can be overridden

    def Init(self, parser):
        ''' Callback message: initialise plugin eg. add command line options (called once in life of plugin) '''
        self.parser = parser


        group = OptionGroup(parser, "Demo Plugin Options",
                    "Extra output file and summary infomation.")


        group.add_option('--demo_info',
            action='store_true', dest = 'demo_info', default=False,
            help=_('display extra info about output file'))
        group.add_option('--demo_prolog_info',
            action='store_true', dest = 'demo_prolog_info', default=False,
            help=_('display extra prolog info'))
        group.add_option('--demo_dynamic_results_info',
            action='store_true', dest = 'demo_dynamic_results_info',
            default=False, help=_('display extra dynamic results info'))
        group.add_option('--demo_plugin_info',
            action='store_true', dest = 'demo_plugin_info', default=False,
            help=_('display info about plugins loaded'))
        group.add_option('--demo_verbose',
            action='store_true', dest = 'demo_verbose', default=False,
            help=_('display plugin messages'))
        group.add_option('--demo_all',
            action='store_true', dest = 'demo_all', default=False,
            help=_('display all demo plugin info'))

        parser.add_option_group(group)

        #print("%s:Init(%s)" % (self.__class__.__name__, parser))
        pass

    # These are the callback messages sent for each file that can be overridden

    def Test(self, eof):
        ''' Callback message: test plugin '''
        if self.options and self.options.demo_verbose:
            print("DEMO: %s:Test()" % self.__class__.__name__)


    def FileInit(self, eof, options):
        ''' Callback message: file to read has been specified, but not opened yet, so check args '''

        self.options = options
        self.filesize = os.path.getsize(eof.fname)

        if options.demo_all:
            options.demo_info = True
            options.demo_verbose = True
            options.demo_plugin_info = True
            options.demo_prolog_info = True
            options.demo_dynamic_results_info = True

        if self.options.demo_verbose:
            print("DEMO: %s:FileInit(eof, %s)" % (self.__class__.__name__, options))
        if self.options.demo_plugin_info:
            print("DEMO: EPANETOutputFile loaded plugins:")
            for p in eof.GetEOFTPluginDirs():
                print("DEMO:   %s" % p)
            print("DEMO: File %s, size %d" % (eof.fname, self.filesize))

    def FileOpen(self, eof, progupdate):
        ''' Callback message: file has been opened so verify. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:FileOpen(eof)" % self.__class__.__name__)
            if progupdate is None:
                print("DEMO: No progress bar to update")
        if self.options.demo_info:
            if progupdate:
                progupdate(100,_('Demo plugin FileOpen starting.'))
            # if we have been called , the file has been verified to some
            # extent by the internal plugin.
            # we want to display the file section sizes, so we need to know:
            # 1. number of nodes (from prolog - 8 bytes in)
            # 2. number of links (from prolog - 16 bytes in)
            # 3. number of tanks and reservoirs (from prolog - 12 bytes in)
            # 4. number of pumps (from prolog - 20 bytes in)
            # 5. number of periods (use eof.Epilog['nPeriods'])
            # Prolog size: 884 + 36*Nnodes + 52*Nlinks + 8*Ntanks
            # Energy use size: 28*Npumps + 4
            # Dynamic results size: (16*Nnodes + 32*Nlinks)*Nperiods
            # Epilog size: 28
            eof.f.seek(8)
            Nnodes, = struct.unpack('<i', eof.f.read(4))
            Ntanks, = struct.unpack('<i', eof.f.read(4))
            Nlinks, = struct.unpack('<i', eof.f.read(4))
            Npumps, = struct.unpack('<i', eof.f.read(4))
            Nperiods = eof.Epilog['nPeriods']
            PrologSize = 884 + 36*Nnodes + 52*Nlinks + 8*Ntanks
            EnergyUseSize = 28*Npumps + 4
            DynamicResultsSize = (16*Nnodes + 32*Nlinks)*Nperiods
            EpilogSize = 28
            TotalSize = PrologSize + EnergyUseSize + DynamicResultsSize + EpilogSize
            eof.f.seek(0)
            print('DEMO: File section size definitions:')
            print('DEMO:   Prolog size: 884 + 36*Nnodes + 52*Nlinks + 8*Ntanks')
            print('DEMO:   Energy use size: 28*Npumps + 4')
            print('DEMO:   Dynamic results size: (16*Nnodes + 32*Nlinks)*Nperiods')
            print('DEMO:   Epilog size: 28')

            print('DEMO: Network data:')
            print('DEMO:   Nnodes=%d' % Nnodes)
            print('DEMO:   Ntanks=%d (actually reservoirs and tanks)' % Ntanks)
            print('DEMO:   Nlinks=%d' % Nlinks)
            print('DEMO:   Npumps=%d' % Npumps)
            print('DEMO:   Nperiods=%d' % Nperiods)
            print('DEMO: Caclulated file section sizes:')
            print('DEMO:   Prolog size: 884 + 36*%d + 52*%d + 8*%d = %d (%.2f%%)' %
                    (Nnodes,Nlinks,Ntanks, PrologSize,
                        (PrologSize*100.0/TotalSize)))
            print('DEMO:   Energy use size: 28*%d + 4 = %d (%.2f%%)' % (Npumps, EnergyUseSize, (EnergyUseSize*100.0/TotalSize)))
            print('DEMO:   Dynamic results size: (16*%d + 32*%d)*%d = %d (%.2f%%)' %
                    (Nnodes, Nlinks, Nperiods, DynamicResultsSize,
                        (DynamicResultsSize*100.0/TotalSize)))
            print('DEMO:   Epilog size: 28 (%.2f%%)' % (EpilogSize*100.0/TotalSize))
            print('DEMO: Total file size: %d' % TotalSize)
            if self.filesize == TotalSize:
                print('DEMO: Actual file size matches calculated file size')
            else:
                print('DEMO: ERROR actual file size (%d) does not match calculated file size (%d)' % (self.filesize, TotalSize))
            if progupdate is not None: progupdate(100,_('Demo plugin FileOpen finished.'))

    def PrologRead(self, eof, progupdate):
        ''' Callback message: file prolog section has been read. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:PrologRead(eof)" % self.__class__.__name__)
        if self.options.demo_prolog_info:
            d = eof.Prolog
            NodeElevTotal = 0.0
            for i in range (0, d['nNodes']):
                NodeElevTotal += d['NodeElev'][i]
            d['demo_NodeElevAve'] = NodeElevTotal / d['nNodes']

            LinkLengthTotal = 0.0
            for i in range (0, d['nLinks']):
                LinkLengthTotal += d['LinkLength'][i]
            d['demo_LinkLengthAve'] = LinkLengthTotal / d['nLinks']

    def PrologPrint(self, eof, progupdate):
        ''' Callback message: print prolog section. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:PrologPrint(eof)" % self.__class__.__name__)
        if self.options.demo_prolog_info:
            d = eof.Prolog
            print('DEMO: Node elevation Average=%f' % d['demo_NodeElevAve'])
            print('DEMO: Link length Average=%f' % d['demo_LinkLengthAve'])

    def PrologExport(self, eof, progupdate):
        ''' Callback message: export prolog section. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:PrologExport(eof)" % self.__class__.__name__)

    def EnergyUsageRead(self, eof, progupdate):
        ''' Callback message: file energy usage section has been read. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:EnergyUsageRead(eof)" % self.__class__.__name__)

    def EnergyUsagePrint(self, eof, progupdate):
        ''' Callback message: print file energy usage section. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:EnergyUsagePrint(eof)" % self.__class__.__name__)

    def EnergyUsageExport(self, eof, progupdate):
        ''' Callback message: epxort file energy usage section. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:EnergyUsageExport(eof)" % self.__class__.__name__)

    def DynamicResultsRead(self, eof, progupdate):
        ''' Callback message: file dynamic results section has been read. Progress 80-89. '''
        if self.options.demo_verbose:
            print("DEMO: %s:DynamicResultsRead(eof)" % self.__class__.__name__)
        if self.options.demo_dynamic_results_info:
            nNodes = eof.Prolog['nNodes']
            minMinPress = float("+inf")
            maxMaxPress = float("-inf")
            for i in range (0, eof.Epilog['nPeriods']):
                minPress = float("+inf")
                maxPress = float("-inf")
                d = eof.DynamicResults[i]
                for j in range (0, nNodes):
                    if d['NodePressure'][j] < minPress:
                        minPress = d['NodePressure'][j]
                    if d['NodePressure'][j] > maxPress:
                        maxPress = d['NodePressure'][j]
                d['demo_NodePressureMin'] = minPress
                d['demo_NodePressureMax'] = maxPress
                if minPress < minMinPress:
                    minMinPress = minPress
                if maxPress > maxMaxPress:
                    maxMaxPress = maxPress

            # save the answers
            self.minMinPress = minMinPress
            self.maxMaxPress = maxMaxPress

            nLinks = eof.Prolog['nLinks']
            minMinVel = float("+inf")
            maxMaxVel = float("-inf")
            for i in range (0, eof.Epilog['nPeriods']):
                minVel = float("+inf")
                maxVel = float("-inf")
                d = eof.DynamicResults[i]
                for j in range (0, nLinks):
                    if d['LinkVelocity'][j] < minVel:
                        minVel = d['LinkVelocity'][j]
                    if d['LinkVelocity'][j] > maxVel:
                        maxVel = d['LinkVelocity'][j]
                d['demo_LinkVelocityMin'] = minVel
                d['demo_LinkVelocityMax'] = maxVel
                if minVel < minMinVel:
                    minMinVel = minVel
                if maxVel > maxMaxVel:
                    maxMaxVel = maxVel

            # save the answers
            self.minMinVel = minMinVel
            self.maxMaxVel = maxMaxVel

    def DynamicResultsPrint(self, eof, progupdate):
        ''' Callback message: print file dynamic results section. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:DynamicResultsPrint(eof)" % self.__class__.__name__)
        if self.options.demo_dynamic_results_info:
            for i in range (0, eof.Epilog['nPeriods']):
                d = eof.DynamicResults[i]
                print(_("DEMO: TimeStep %d") % i)
                print(_('DEMO:   Minimum node pressure %f, Maximum node pressure %f' % (d['demo_NodePressureMin'], d['demo_NodePressureMax'])))
                print(_('DEMO:   Minimum link velocity %f, Maximum link velocity %f' % (d['demo_LinkVelocityMin'], d['demo_LinkVelocityMax'])))
            print(_("DEMO: Overall min/max"))
            print(_('DEMO:   Minimum node pressure %f, Maximum node pressure %f' % (self.minMinPress, self.maxMaxPress)))
            print(_('DEMO:   Minimum link velocity %f, Maximum link velocity %f' % (self.minMinVel, self.maxMaxVel)))

    def DynamicResultsExport(self, eof, progupdate):
        ''' Callback message: export file dynamic results section. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:DynamicResultsExport(eof)" % self.__class__.__name__)

    def EpilogRead(self, eof, progupdate):
        ''' Callback message: file epilog section has been read. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:EpilogRead(eof)" % self.__class__.__name__)

    def EpilogPrint(self, eof, progupdate):
        ''' Callback message: print file epilog section. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:EpilogPrint(eof)" % self.__class__.__name__)

    def EpilogExport(self, eof, progupdate):
        ''' Callback message: export file epilog section. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:EpilogExport(eof)" % self.__class__.__name__)

    def FileClose(self, eof, progupdate):
        ''' Callback message: file has been closed. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:FileClose(eof)" % self.__class__.__name__)

    def FileTerm(self, eof, progupdate):
        ''' Callback message: file processing is complete. Progress 0-100. '''
        if self.options.demo_verbose:
            print("DEMO: %s:FileTerm(eof)" % self.__class__.__name__)



def Initialize():
    print("demo.__init__.py: Initialize()")
    return DemoPlugin()
