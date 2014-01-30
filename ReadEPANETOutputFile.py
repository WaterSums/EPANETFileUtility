# ex:set ts=4 sw=4: <- for vim
#
# EPANET Output File Tool (EOFT):
#
# Utility to read information from EPANET Toolkit output file (EPANET 2.00.12)
# (note that the EPANET output file format changed in EPANET 2.00.12
# so this utility will not read output files written by earlier versions of the
# EPANET Toolkit or EPANET for Windows).
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
#   -v, --verbose         display verbouse output
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
from datetime import datetime
from EPANETOutputFile import EPANETOutputFile

start_time = datetime.now()
epanetoutput = EPANETOutputFile.EPANETOutputFile()
end_time = datetime.now()
dt = end_time - start_time
print(_("Time taken: %s") % dt)

