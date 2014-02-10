#!/bin/sh
# Run basic tests of EPANETOutputFile tool using EPANET Net1 output file
export LANG=en_AU
mkdir -p output
rm output/*.csv
python ../ReadEPANETOutputFile.py -vpedca -n output/Net1_pnode.csv -l output/Net1_plink.csv -E output/Net1_e.csv -N output/Net1_dnode.csv -L output/Net1_dlink.csv data/Net1.hyd
