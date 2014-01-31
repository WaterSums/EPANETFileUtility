Python EPANETFileUtility
========================

EPANET file utility planned to read/load different types of EPANET files.

Written for Python 2.6 and 2.7.

Current functionality
---------------------

Functionality for reading other EPANET files is planned for
the future, but at the moment, the only type of file read is:

1. EPANET toolkit 2.00.12 binary output file


Details
-------


1. EPANET toolkit 2.00.12 binary output file reader
   Loads binary output file (from EPANET toolkit hydraulic analysis) 
   and displays contents or exports contents to CSV files.
   Supports plugins for extending functionality.
   Can be run as a standalone program as detailed below
   or imported to load files into memory for other uses.
   More details will be available in the doc/ directory soon.

        Usage: python ReadEPANETOutputFile.py [Options] <outputfilename>

        Options:
        --version             show program's version number and exit
        -h, --help            show this help message and exit
        -a, --all             display all output file sections (default)
        -s, --silent          don't display any output file sections
        -p, --prolog          display prolog section,
        -n PROLOG_NODE_CSV, --prolog_node_csv=PROLOG_NODE_CSV
                              write CSV for nodes from prolog to PROLOG_NODE_CSV
        -l PROLOG_LINK_CSV, --prolog_link_csv=PROLOG_LINK_CSV
                              write CSV for links from prolog to PROLOG_LINK_CSV
        -e, --energy_use      display energy use section
        -E ENERGY_CSV, --energy_use_csv=ENERGY_CSV
                              write CSV from energy use section to ENERGY_CSV
        -d, --dynamic_results
                              display dynamic results section
        -N DYNAMIC_NODE_CSV, --dynamic_node_csv=DYNAMIC_NODE_CSV
                              write CSV for nodes from dynamic results to
                              DYNAMIC_NODE_CSV
        -L DYNAMIC_LINK_CSV, --dynamic_link_csv=DYNAMIC_LINK_CSV
                              write CSV for links from dynamic results to
                              DYNAMIC_LINK_CSV
        -c, --coda, --epilog  display file epilog
        -v, --verbose         display verbose output

How to get an EPANET output file:

1. With [EPANET](http://www.epa.gov/nrmrl/wswrd/dw/epanet.html):
   analyse the model with the settings required.  
   Do NOT close EPANET.
   Look in the `%TEMP%` directory for the newest file having a name
   starting with `en` and ending with `.tmp`.  Copy this file
   somewhere useful with a meaningful name.
2. With [WaterSums](http://www.WaterSums.com): analyse the model with
   the settings required.
   The EPANET output file will be written to the same directory
   as the network file with the extension changed to `.hyd`.
   This file is overwritten each time the analysis is performed,
   so if you want to keep a set of results, copy the file somewhere
   else.
3. Use the [EPANET Toolkit](http://www.epa.gov/nrmrl/wswrd/dw/epanet.html#toolkit)
   to generate an output file.

EPANET output files can be large files.  Their structure is described
in the EPANET Toolkit Windows Help File.

