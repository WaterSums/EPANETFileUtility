# ex:set ts=4 sw=4: <- for vim
#
# EPANET Output File Tool Plugin support
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
#   options		parsed command line arguments as returned from OptionParser.parse_args()
#   args		any additional command line arguments not processed (including output file name)
#   Prolog		dictionary of entries read from output file Prolog section
#   EnergyUse	dictionary of entries read from output file Energy Use section
#   DynamicResults list of dictionaries of entries read from output file
#   			Dynamic Results section - one per timestep in the file
#   Epilog		dictionary of entries read from output file Epilog section
#   fname		name of file to read
#   f			file we are reading
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

class EOFTPlugin():

    def __init__(self):
        # TODO initialise translations???
        self.parser = None
        self.options = None
        pass    


    # These are the callback messages that can be overridden

    def Init(self, parser):
        ''' Callback message: initialise plugin eg. add command line options (called once in life of plugin) '''
        #print("%s:Init(%s)" % (self.__class__.__name__, parser))
        pass


    def Test(self, eof):
        ''' Callback message: test plugin '''
        #print("%s:Test()" % self.__class__.__name__)


    def FileInit(self, eof, options):
        ''' Callback message: file to read has been specified, but not opened yet, so check args '''
        #print("%s:FileInit(%s, %s)" % (self.__class__.__name__, eof, options))
        self.options = options

    def FileOpen(self, eof, progupdate):
        ''' Callback message: file has been opened so verify. Progress 0-100. '''
        #print("%s:FileOpen(%s)" % (self.__class__.__name__, eof))

    def PrologRead(self, eof, progupdate):
        ''' Callback message: file prolog section has been read. Progress 0-100. '''
        #print("%s:PrologRead(%s)" % (self.__class__.__name__, eof))

    def PrologPrint(self, eof, progupdate):
        ''' Callback message: print prolog section. Progress 0-100. '''
        #print("%s:PrologPrint(%s)" % (self.__class__.__name__, eof))

    def PrologExport(self, eof, progupdate):
        ''' Callback message: export prolog section. Progress 0-100. '''
        #print("%s:PrologExport(%s)" % (self.__class__.__name__, eof))

    def EnergyUsageRead(self, eof, progupdate):
        ''' Callback message: file energy usage section has been read. Progress 0-100. '''
        #print("%s:EnergyUsageRead(%s)" % (self.__class__.__name__, eof))

    def EnergyUsagePrint(self, eof, progupdate):
        ''' Callback message: print file energy usage section. Progress 0-100. '''
        #print("%s:EnergyUsagePrint(%s)" % (self.__class__.__name__, eof))

    def EnergyUsageExport(self, eof, progupdate):
        ''' Callback message: epxort file energy usage section. Progress 0-100. '''
        #print("%s:EnergyUsageExport(%s)" % (self.__class__.__name__, eof))

    def DynamicResultsRead(self, eof, progupdate):
        ''' Callback message: file dynamic results section has been read. Progress 80-89. '''
        #print("%s:DynamicResultsRead(%s)" % (self.__class__.__name__, eof))

    def DynamicResultsPrint(self, eof, progupdate):
        ''' Callback message: print file dynamic results section. Progress 0-100. '''
        #print("%s:DynamicResultsPrint(%s)" % (self.__class__.__name__, eof))

    def DynamicResultsExport(self, eof, progupdate):
        ''' Callback message: export file dynamic results section. Progress 0-100. '''
        #print("%s:DynamicResultsExport(%s)" % (self.__class__.__name__, eof))

    def EpilogRead(self, eof, progupdate):
        ''' Callback message: file epilog section has been read. Progress 0-100. '''
        #print("%s:EpilogRead(%s)" % (self.__class__.__name__, eof))

    def EpilogPrint(self, eof, progupdate):
        ''' Callback message: print file epilog section. Progress 0-100. '''
        #print("%s:EpilogPrint(%s)" % (self.__class__.__name__, eof))

    def EpilogExport(self, eof, progupdate):
        ''' Callback message: export file epilog section. Progress 0-100. '''
        #print("%s:EpilogExport(%s)" % (self.__class__.__name__, eof))

    def FileClose(self, eof, progupdate):
        ''' Callback message: file has been closed. Progress 0-100. '''
        #print("%s:FileClose(%s)" % (self.__class__.__name__, eof))

    def FileTerm(self, eof, progupdate):
        ''' Callback message: file processing is complete. Progress 0-100. '''
        #print("%s:FileTerm(%s)" % (self.__class__.__name__, eof))



