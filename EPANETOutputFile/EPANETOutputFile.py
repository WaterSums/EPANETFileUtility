# ex:set ts=4 sw=4: <- for vim
#
# EPANET Output File Tool (EOFT):
#
# Utility to read information from EPANET Toolkit output file (EPANET 2.00.12)
# (note that the EPANET output file format changed in EPANET 2.00.12
# so this utility will not read output files written by earlier versions of the
# EPANET Toolkit or EPANET for Windows).
#
# This utility supports plugins which can do extra processing.
# Plugin are installed in the 'plugins' directory. Each plugin must
# be a package and the __init__.py file must do any initialisation necessary
# to register listeners to the messages sent by the coordinating process.
#
# Note that indexes in the output file are 1-based, whereas Python is 0-based
# so these need to be handled carefully.
#
# Usage: python ReadEPANETOutputFile.py [Options] <outputfilename>
#
# Options:
#   --version             show program's version number and exit
#   -h, --help            show this help message and exit
#   -a, --all             display all output file sections (default)
#   -s, --silent          don't display any output file sections
#   -p, --prolog          display prolog section
#   -n PROLOG_NODE_CSV, --prolog_node_csv=PROLOG_NODE_CSV
#                         write CSV for nodes from prolog to PROLOG_NODE_CSV
#   -l PROLOG_LINK_CSV, --prolog_link_csv=PROLOG_LINK_CSV
#                         write CSV for links from prolog to PROLOG_LINK_CSV
#   -e, --energy_use      display energy use section
#   -E ENERGY_CSV, --energy_use_csv=ENERGY_CSV
#                         write CSV from energy use section to ENERGY_CSV
#   -d, --dynamic_results
#                         display dynamic results section
#   -N DYNAMIC_NODE_CSV, --dynamic_node_csv=DYNAMIC_NODE_CSV
#                         write CSV for nodes from dynamic results to
#                         DYNAMIC_NODE_CSV
#   -L DYNAMIC_LINK_CSV, --dynamic_link_csv=DYNAMIC_LINK_CSV
#                         write CSV for links from dynamic results to
#                         DYNAMIC_LINK_CSV
#   -c, --coda, --epilog  display file epilog
#   -v, --verbose         display verbose output
# 
# Available translations/locales:
# en_US.UTF-8
# en_AU.UTF-8
# 
# The EPANET help describes the output file as: "an unformatted binary file" and
# uses it "to store both hydraulic and water quality results at uniform
# reporting intervals. Data written to the file is either 4-byte integers,
# 4-byte floats, # or fixed-size strings whose size is a multiple of 4 bytes.
# This allows the file to be divided conveniently into 4-byte records.
# The file consists of four sections of the following sizes in bytes:
#
# Section         Size in Bytes 
# Prolog          884 + 36*Nnodes + 52*Nlinks + 8*Ntanks 
# Energy Use      28*Npumps + 4 
# Dynamic Results (16*Nnodes + 32*Nlinks)*Nperiods 
# Epilog          28 
# 
# where
# Nnodes = number of nodes (junctions + reservoirs + tanks) 
# Nlinks = number of links (pipes + pumps + valves) 
# Ntanks = number of tanks and reservoirs 
# Npumps = number of pumps 
# Nperiods = number of reporting periods 
# and all of these counts are themselves written to the file's
# prolog or epilog sections."
#
# Please note that the output file format changed in Version 2.00.12
# when IDs changed from 15 to 31 characters/numbers.  The size of the
# prolog section for EPANET 2.00.11 and earlier was:
# Prolog          852 + 20*Nnodes + 36*Nlinks + 8*Ntanks
# This utility does NOT read this earlier format.
#
#
# How to get an EPANET output file:
# 1. with EPANET: Analyse the model with the settings required.  
#    Do NOT close EPANET.
#    Look in the %TEMP% directory for the newest file having a name
#    starting with 'en' and ending with '.tmp'.  Copy this file
#    somewhere useful with a meaningful name.
# 2. with WaterSums, analyse the model with the settings required.
#    The EPANET output file will be written to the same directory
#    as the network file with the extension changed to '.hyd'.
#    This file is overwritten each time the analysis is performed,
#    so if you want to keep a set of results, copy the file somewhere
#    else.
# 3. use the EPANET Toolkit commands to generate the output file.
#
# EPANET output files can be large files.
#
#
# PLUGINS
# =======
# Plugins can listen to messages from the coordinating process and do whatever
# is necessary.
# The following messages are sent:
# - Init file has been specified, but is not yet opened for reading
# - FileOpen file has been opened for reading
# - PreReadProlog
# - PostReadProlog
# - PreReadEnergyUsage
#   - one call per pump
# - PostReadEnergyUsage
# - PreReadDynamicResults
#   - one call per timestep
# - PostReadDynamicResults
# - PreReadEpilog
# - PostReadEpilog
# - FileClose file has been closed after reading
# - Term file has been read and closed
#
# The existing output reading will use the same framework which will also
# all the support of reading the earlier version of EPANET files if anyone
# wanted to bother.
#
#
# Tentative TODO list:
#
# Item 1: # When dumping dynamic data to CSV, we could:
# 1. for Nodes:
#    (a) dump one time step with an ID column [and time column], OR
#    (b) dump one link with [an ID column and] a time step column
# 2. for Links it is the same:
#    (a) dump one time step with an ID column [and time column], OR
#    (b) dump one link with [an ID column and] a time step column
# One consistent format for Nodes and one for Links is best, so we might as
# well include both the ID and time columns even when the user has specified
# an ID or time.
#
# Item 2: How about:
# -i ID which specifies one node for prolog, dynamic results or power
# -I ID which specifies one link for prolog, dynamic results or power
# (probably best to work out what the ID relates to ASAP)
# -t time in seconds
# -T TimeStep count (0-based since it starts at initial conditions)
#
# Item 3 How about allowing including static information in the dynamic
# output for each time step ie. everything included in the prolog report could
# also be included in the dynamic report
#
# Note that we also include lots of redundant information since we include
# the start/end nodes for each link at each time step.
# One option would be to have an HTML output which would use expandable nodes
# to collect the data for each node or timestep.  Of course, it could then
# include graphs using SVG.

import os
import platform
import codecs

import sys
# from 2.7 on, optparse is deprecated, use argparse instead
# however we support 2.6 and 2.7...
from optparse import OptionParser
import gettext
from datetime import datetime
import struct
from types import ModuleType

import os
#print('Current file: %s' % os.path.realpath(__file__))
# look first for a locale directory in same directory as this file
localedir = os.path.dirname(os.path.realpath(__file__)) + '/locale'
print('looking for locale directory: %s' % localedir)
if os.path.exists(localedir) == False or os.path.isdir(localedir) == False:
    # next try up a directory
    localedir = os.path.dirname(os.path.realpath(__file__)) + '/../locale'
    print('looking for locale directory: %s' % localedir)
    if os.path.exists(localedir) == False or os.path.isdir(localedir) == False:
        # and finally we look for it in the current working directory
        localedir = os.getcwd() + '/locale'
        print('looking for locale directory: %s' % localedir)
#print('using locale directory: %s' % localedir)
gettext.install('EPANETOutputFile', localedir, unicode=1)

EOFTusage = _("%prog [options] filename")
EOFTparser = OptionParser(version=_('%prog 1.0.0'), usage=EOFTusage)
# set up the command line option parsing
EOFTparser.add_option('-v','--verbose',
        action='store_true', dest = 'verbose', default=False,
        help=_('display verbose output'))


'''
Install Internal 'plugin' which the coordinator calls before any
of the other plugins and actually reads the file.
This plugin also adds more command line options for export to CSV.
'''
import EOFTInternalPlugin
EOFTInternalPlugin = EOFTInternalPlugin.Initialize()
#print(EOFTInternalPlugin)


'''
Install Plugins
'''

# our empty plugins list
EOFTPlugins = []

# read all the directories in the plugins directory
# each one is to be a package which we can import and which will also
# return us a plugin class object when we Initialize() it
EOFTPluginDirs = []
if hasattr(sys, 'frozen'):
    #Py2EXE gets paths wrong
    #print('cwd=%s' % os.getcwd())
    #path = os.path.dirname(sys.argv[0])
    #print('dir=%s' % path)
    #if path:
    #    os.chdir(path)
    #else:
    #    path = '.'
    #pluginsdir = os.path.join(path,u'plugins')
    print("Can't import plugins after using Py2exe")
else:    
    path = os.path.dirname(os.path.realpath(__file__))
    pluginsdir = os.path.join(path,u'plugins')
    # unfortunately, to make this work we need to go back to ASCII...
    EOFTPluginDirs = [name.encode('ascii','replace') for name in os.listdir(pluginsdir)
            if os.path.isdir(os.path.join(pluginsdir, name))]
EOFTPluginPackages = []


'''
Import any plugins found
One-off initialising of plugin modules:
call must return a plugin object we can call later
'''
#print(EOFTPluginDirs)
#print (dir())
#print ('__name__="%s"' % __name__)
for p in EOFTPluginDirs:
    if __name__ == '__main__':
        if hasattr(sys, 'frozen'):
            tmp = __import__(('plugins.%s' % p), fromlist=[p])
        else:
            tmp = __import__(('plugins.%s' % p), fromlist=[p])
    else:
        tmp = __import__('EPANETOutputFile.plugins.%s' % p, fromlist=[p])
    # store it so that we can call the Terminate function also
    EOFTPluginPackages.append(tmp)
    a = tmp.Initialize()
    #print(a)
    # store it so that we can send the messages to the plugins
    EOFTPlugins.append(a)


'''
Utilities for working with the plugins
'''

'''Message IDs '''
EOFTPLUGIN_TEST=0
EOFTPLUGIN_INIT=1
EOFTPLUGIN_FILEINIT=2
EOFTPLUGIN_FILEOPEN=3
EOFTPLUGIN_PROLOGREAD=10
EOFTPLUGIN_PROLOGPRINT=11
EOFTPLUGIN_PROLOGEXPORT=12
EOFTPLUGIN_ENERGYUSAGEREAD=20
EOFTPLUGIN_ENERGYUSAGEPRINT=21
EOFTPLUGIN_ENERGYUSAGEEXPORT=22
EOFTPLUGIN_DYNAMICRESULTSREAD=30
EOFTPLUGIN_DYNAMICRESULTSPRINT=31
EOFTPLUGIN_DYNAMICRESULTSEXPORT=32
EOFTPLUGIN_EPILOGREAD=40
EOFTPLUGIN_EPILOGPRINT=41
EOFTPLUGIN_EPILOGEXPORT=42

EOFTPLUGIN_FILECLOSE=99
EOFTPLUGIN_FILETERM=100
# no EOFTPLUGIN_TERM to match EOFTPLUGIN_INIT - no way of sending it

def SetStepLimits(progress, rangemin, rangemax):
    if progress is not None:
        progress.SetStepLimits(rangemin, rangemax)

def CallInternalPlugin(msg, *args):
    ''' Pass message with *args to internal plugin

        Args:
            message (int)   ID specifying which plugin function to call.
            *args           arguments to pass to the plugin

        Any return values from plugin is ignored.
    '''
    if msg == EOFTPLUGIN_TEST:
        EOFTInternalPlugin.Test(*args)
    elif msg == EOFTPLUGIN_INIT:
        EOFTInternalPlugin.Init(*args)
    elif msg == EOFTPLUGIN_FILEINIT:
        EOFTInternalPlugin.FileInit(*args)
    elif msg == EOFTPLUGIN_FILEOPEN:
        EOFTInternalPlugin.FileOpen(*args)
    elif msg == EOFTPLUGIN_PROLOGREAD:
        EOFTInternalPlugin.PrologRead(*args)
    elif msg == EOFTPLUGIN_PROLOGPRINT:
        EOFTInternalPlugin.PrologPrint(*args)
    elif msg == EOFTPLUGIN_PROLOGEXPORT:
        EOFTInternalPlugin.PrologExport(*args)
    elif msg == EOFTPLUGIN_ENERGYUSAGEREAD:
        EOFTInternalPlugin.EnergyUsageRead(*args)
    elif msg == EOFTPLUGIN_ENERGYUSAGEPRINT:
        EOFTInternalPlugin.EnergyUsagePrint(*args)
    elif msg == EOFTPLUGIN_ENERGYUSAGEEXPORT:
        EOFTInternalPlugin.EnergyUsageExport(*args)
    elif msg == EOFTPLUGIN_DYNAMICRESULTSREAD:
        EOFTInternalPlugin.DynamicResultsRead(*args)
    elif msg == EOFTPLUGIN_DYNAMICRESULTSPRINT:
        EOFTInternalPlugin.DynamicResultsPrint(*args)
    elif msg == EOFTPLUGIN_DYNAMICRESULTSEXPORT:
        EOFTInternalPlugin.DynamicResultsExport(*args)
    elif msg == EOFTPLUGIN_EPILOGREAD:
        EOFTInternalPlugin.EpilogRead(*args)
    elif msg == EOFTPLUGIN_EPILOGPRINT:
        EOFTInternalPlugin.EpilogPrint(*args)
    elif msg == EOFTPLUGIN_EPILOGEXPORT:
        EOFTInternalPlugin.EpilogExport(*args)
    elif msg == EOFTPLUGIN_FILECLOSE:
        EOFTInternalPlugin.FileClose(*args)
    elif msg == EOFTPLUGIN_FILETERM:
        EOFTInternalPlugin.FileTerm(*args)
    else:
        print(_('Invalid message %d passed to CallInternalPlugin') % msg)


def CallUserPlugins(msg, progress, *args):
    ''' Pass message with *args to all loaded user plugins

        Args:
            message (int)   ID specifying which plugin function to call.
            *args           arguments to pass to the plugin

        Any return values from plugins are ignored.
    '''
    if progress is not None:
        # as we loop, we need to adjust the progress bounds
        rangemin = float(progress.rangemin)
        rangemax = float(progress.rangemax)
        rangestep = (rangemax - rangemin) / float(len(EOFTPlugins))
        prangemin = rangemin
        prangemax = rangemin+rangestep
        progress.SetStepLimits(prangemin, prangemax)

    for p in EOFTPlugins:

        if msg == EOFTPLUGIN_TEST:
            p.Test(*args)
        elif msg == EOFTPLUGIN_INIT:
            p.Init(*args)
        elif msg == EOFTPLUGIN_FILEINIT:
            p.FileInit(*args)
        elif msg == EOFTPLUGIN_FILEOPEN:
            p.FileOpen(*args)
        elif msg == EOFTPLUGIN_PROLOGREAD:
            p.PrologRead(*args)
        elif msg == EOFTPLUGIN_PROLOGPRINT:
            p.PrologPrint(*args)
        elif msg == EOFTPLUGIN_PROLOGEXPORT:
            p.PrologExport(*args)
        elif msg == EOFTPLUGIN_ENERGYUSAGEREAD:
            p.EnergyUsageRead(*args)
        elif msg == EOFTPLUGIN_ENERGYUSAGEPRINT:
            p.EnergyUsagePrint(*args)
        elif msg == EOFTPLUGIN_ENERGYUSAGEEXPORT:
            p.EnergyUsageExport(*args)
        elif msg == EOFTPLUGIN_DYNAMICRESULTSREAD:
            p.DynamicResultsRead(*args)
        elif msg == EOFTPLUGIN_DYNAMICRESULTSPRINT:
            p.DynamicResultsPrint(*args)
        elif msg == EOFTPLUGIN_DYNAMICRESULTSEXPORT:
            p.DynamicResultsExport(*args)
        elif msg == EOFTPLUGIN_EPILOGREAD:
            p.EpilogRead(*args)
        elif msg == EOFTPLUGIN_EPILOGPRINT:
            p.EpilogPrint(*args)
        elif msg == EOFTPLUGIN_EPILOGEXPORT:
            p.EpilogExport(*args)
        elif msg == EOFTPLUGIN_FILECLOSE:
            p.FileClose(*args)
        elif msg == EOFTPLUGIN_FILETERM:
            p.FileTerm(*args)
        else:
            print(_('Invalid message %d passed to CallUserPlugins') % msg)

        if progress is not None:
            prangemin = prangemax
            prangemax += rangestep
            progress.SetStepLimits(prangemin, prangemax)

    if progress is not None:
        progress.SetStepLimits(rangemin, rangemax)


def CallPlugins(msg, progress, *args):
    CallInternalPlugin(msg, *args)
    CallUserPlugins(msg, progress, *args)

'''
One-off initialising of plugin objects
Plugins can add any command line arguments they wish to support
NB: called once per session (when this module is imported),
    not once per EPANETOutputFile() call
'''
CallPlugins(EOFTPLUGIN_INIT, None, EOFTparser)


class EPANETOutputFile():


    # The data file has 4 sections, so we store our data in one dictionary
    # for each section:
    #   Prolog
    #   EnergyUse
    #   DynamicResults (this one is a list of dictionaries - 1 for each timestep)
    #   Epilog

    def __init__(self, args = sys.argv[1:], progress = None):
        '''Constructor: Read an EPANET output file into formatted memory

        Args:
            args (list):    arguments in command line format
            progress (None or progress bar dialog with 2 functions):
                progress.SetStepLimits(rangemin, rangemax)
                progress.Update(% of work done (0-100), text description of current step)
        Raises:
            Exception('ERROR: magic numbers do not match: probably not an EPANET output file')

        '''

        # options output from optparse option parsing
        # args remaining arguments that could not be parsed
        (options, args) = EOFTparser.parse_args(args)

        if len(args) != 1:
            if len(args) == 0:
                EOFTparser.error(_('No EPANET output file specified.'))
            else:
                # we could easily cope with this, but it doesn't
                # seem worthwhile - the output is too likely to get
                # confused very easily
                EOFTparser.error(_('More than one EPANET output file specified.'))

        self.options = options
        self.args = args
        self.Prolog = {}
        self.EnergyUse = {}
        self.DynamicResults = []
        self.Epilog = {}

        self.fname = fname = args[0]
        if options.verbose: print(_("Loading EPANET output file %s") % fname)

        CallPlugins(EOFTPLUGIN_TEST, None, self)

        CallPlugins(EOFTPLUGIN_FILEINIT, None, self, options)

        self.f = f = open(fname,'rb')

        progupdate = None 
        if progress is not None: progupdate = progress.Update
        SetStepLimits(progress, 2, 5)
        CallInternalPlugin(EOFTPLUGIN_FILEOPEN, self, progupdate)
        SetStepLimits(progress, 6, 9)
        CallUserPlugins(EOFTPLUGIN_FILEOPEN, progress, self, progupdate)

        # Progress updates could be done better using file size and basing progress
        # on number of bytes read, but the current process does not do this.

        self.readFile(f, progress)

    def GetEOFTPlugins(self):
        return EOFTPlugins

    def GetEOFTPluginDirs(self):
        return EOFTPluginDirs

    def readFile(self, f, progress):
        '''Read EPANET output file.  No return value.

        Args:
            f (file):   file to read Prolog, Energy Use, Dynamic Results and Epilog data from
            progress (None or progress bar dialog with 2 functions):
                progress.SetStepLimits(rangemin, rangemax)
                progress.Update(% of work done (0-100), text description of current step)
                TODO Progress updates could be done better using file size and basing progress
                on number of bytes read, but the current process does not do this.

        '''

        if self.Epilog['nPeriods'] != 1:
            pstr = 's'
        else:
            pstr = ''
        if self.options.verbose:
            print(gettext.ngettext(
                'Analysis had one reporting period',
                'Analysis had %d reporting periods',
                self.Epilog['nPeriods']) %
                self.Epilog['nPeriods'])

            if self.Epilog['WarningFlag'] == 0:
                print(_('Analysis generated no errors or warnings'))
            else:
                print(_('Analysis generated warning(s)'))

        f.seek(0)


        progupdate = None 
        if progress is not None: progupdate = progress.Update

        # read, print and export prolog
        # (matching magic numbers at start and end already read by internal plugin)
        SetStepLimits(progress, 10, 14)
        CallInternalPlugin(EOFTPLUGIN_PROLOGREAD, self, progupdate)
        SetStepLimits(progress, 15, 16)
        CallUserPlugins(EOFTPLUGIN_PROLOGREAD, progress, self, progupdate)
        SetStepLimits(progress, 16, 17)
        CallInternalPlugin(EOFTPLUGIN_PROLOGPRINT, self, progupdate)
        SetStepLimits(progress, 17, 18)
        CallUserPlugins(EOFTPLUGIN_PROLOGPRINT, progress, self, progupdate)
        SetStepLimits(progress, 18, 20)
        CallInternalPlugin(EOFTPLUGIN_PROLOGEXPORT, self, progupdate)
        SetStepLimits(progress, 20, 21)
        CallUserPlugins(EOFTPLUGIN_PROLOGEXPORT, progress, self, progupdate)


        # read, print and export energy use section
        SetStepLimits(progress, 21, 22)
        CallInternalPlugin(EOFTPLUGIN_ENERGYUSAGEREAD, self, progupdate)
        SetStepLimits(progress, 22, 23)
        CallUserPlugins(EOFTPLUGIN_ENERGYUSAGEREAD, progress, self, progupdate)

        SetStepLimits(progress, 23, 24)
        CallInternalPlugin(EOFTPLUGIN_ENERGYUSAGEPRINT, self, progupdate)
        SetStepLimits(progress, 24, 25)
        CallUserPlugins(EOFTPLUGIN_ENERGYUSAGEPRINT, progress, self, progupdate)

        SetStepLimits(progress, 25, 26)
        CallInternalPlugin(EOFTPLUGIN_ENERGYUSAGEEXPORT, self, progupdate)
        SetStepLimits(progress, 26, 27)
        CallUserPlugins(EOFTPLUGIN_ENERGYUSAGEEXPORT, progress, self, progupdate)


        # read, print and export dynamic results section
        SetStepLimits(progress, 27, 75)
        CallInternalPlugin(EOFTPLUGIN_DYNAMICRESULTSREAD, self, progupdate)
        SetStepLimits(progress, 75, 83)
        CallUserPlugins(EOFTPLUGIN_DYNAMICRESULTSREAD, progress, self, progupdate)

        SetStepLimits(progress, 83, 84)
        CallInternalPlugin(EOFTPLUGIN_DYNAMICRESULTSPRINT, self, progupdate)
        SetStepLimits(progress, 84, 85)
        CallUserPlugins(EOFTPLUGIN_DYNAMICRESULTSPRINT, progress, self, progupdate)

        SetStepLimits(progress, 85, 87)
        CallInternalPlugin(EOFTPLUGIN_DYNAMICRESULTSEXPORT, self, progupdate)
        SetStepLimits(progress, 87, 89)
        CallUserPlugins(EOFTPLUGIN_DYNAMICRESULTSEXPORT, progress, self, progupdate)


        # read, print and export epilog
        SetStepLimits(progress, 90, 92)
        CallInternalPlugin(EOFTPLUGIN_EPILOGREAD, self, progupdate)
        SetStepLimits(progress, 92, 93)
        CallUserPlugins(EOFTPLUGIN_EPILOGREAD, progress, self, progupdate)

        SetStepLimits(progress, 93, 94)
        CallInternalPlugin(EOFTPLUGIN_EPILOGPRINT, self, progupdate)
        SetStepLimits(progress, 94, 95)
        CallUserPlugins(EOFTPLUGIN_EPILOGPRINT, progress, self, progupdate)

        SetStepLimits(progress, 95, 96)
        CallInternalPlugin(EOFTPLUGIN_EPILOGEXPORT, self, progupdate)
        SetStepLimits(progress, 96, 97)
        CallUserPlugins(EOFTPLUGIN_EPILOGEXPORT, progress, self, progupdate)

        #if progupdate is not None: progupdate(90,_('Reading epilog'))
        #self.ReadEpilog(f, self.Epilog)

        # print epilog
        #if self.options.epilog or self.options.all:
        #    self.PrintEpilog(self.Epilog)

        if self.options.silent == False: print(_('Done.'))

        if progupdate is not None: progupdate(100,_('Finished reading file'))

        SetStepLimits(progress, 97, 98)
        CallInternalPlugin(EOFTPLUGIN_FILECLOSE, self, progupdate)
        SetStepLimits(progress, 98, 99)
        CallUserPlugins(EOFTPLUGIN_FILECLOSE, progress, self, progupdate)
        f.close()


    def getWaterQualityOptionText(self, optnum):
        """Get descriptive text for specified option.

        Args:
            optnum (int):   enum value for which to return the text description

        Returns:
            (string) text description of enum value given or 'unknown' if not recognised

        """
        if optnum == 0:
            option = _('none')
        elif optnum == 1:
            option = _('chemical')
        elif optnum == 2:
            option = _('age')
        elif optnum == 3:
            option = _('source trace')
        else:
            option = _('unknown')
        return option

    def getFlowUnitsOptionText(self, optnum):
        """Get descriptive text for specified option.

        Args:
            optnum (int):   enum value for which to return the text description

        Returns:
            (string) text description of enum value given or 'unknown' if not recognised

        """
        if optnum == 0:
            option = _('cubic feet/second')
        elif optnum == 1:
            option = _('gallons/minute')
        elif optnum == 2:
            option = _('million gallons/day')
        elif optnum == 3:
            option = _('Imperial million gallons/day')
        elif optnum == 4:
            option = _('acre-ft/day')
        elif optnum == 5:
            option = _('liters/second')
        elif optnum == 6:
            option = _('liters/minute')
        elif optnum == 7:
            option = _('megaliters/day')
        elif optnum == 8:
            option = _('cubic meters/hour')
        elif optnum == 9:
            option = _('cubic meters/day')
        else:
            option = _('unknown')
        return option

    def getPressureUnitsOptionText(self, optnum):
        """Get descriptive text for specified option.

        Args:
            optnum (int):   enum value for which to return the text description

        Returns:
            (string) text description of enum value given or 'unknown' if not recognised

        """
        if optnum == 0:
            option = _('pounds/square inch')
        elif optnum == 1:
            option = _('meters')
        elif optnum == 2:
            option = _('kiloPascals')
        else:
            option = _('unknown')
        return option

    def getTimeStatsOption(self, optnum):
        """Get descriptive text for specified option.

        Args:
            optnum (int):   enum value for which to return the text description

        Returns:
            (string) text description of enum value given or 'unknown' if not recognised

        """
        if optnum == 0:
            option = _('none (report time series)')
        elif optnum == 1:
            option = _('report time-averaged values')
        elif optnum == 2:
            option = _('report minimum values')
        elif optnum == 3:
            option = _('report maximum values')
        elif optnum == 4:
            option = _('report ranges')
        else:
            option = _('unknown')
        return option

    def getLinkTypeText(self, optnum):
        """Get descriptive text for specified option.

        Args:
            optnum (int):   enum value for which to return the text description

        Returns:
            (string) text description of enum value given or 'unknown' if not recognised

        """
        if optnum == 0:
            option = _('Pipe with CV')
        elif optnum == 1:
            option = _('Pipe')
        elif optnum == 2:
            option = _('Pump')
        elif optnum == 3:
            option = _('PRV')
        elif optnum == 4:
            option = _('PSV')
        elif optnum == 5:
            option = _('PBV')
        elif optnum == 6:
            option = _('FCV')
        elif optnum == 7:
            option = _('TCV')
        elif optnum == 8:
            option = _('GPV')
        else:
            option = _('unknown')
        return option



def main():
    #sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))
    # the constructor uses the sys.argv by default
    epanetoutput = EPANETOutputFile()
    #print epanetoutput.options
    #print epanetoutput.args


if __name__ == '__main__':
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    dt = end_time - start_time
    print(_("Time taken: %(deltat)s") % {deltat: dt})

