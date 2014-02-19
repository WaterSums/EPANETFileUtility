#!/bin/sh
# Run basic tests of EPANETOutputFile tool using EPANET Net[123],hyd output file
mkdir -p output
rm output/*.csv output/Net*.txt
LANG=en_AU python ../ReadEPANETOutputFile.py --demo_all -vpedca -n output/Net1_pnode.csv -l output/Net1_plink.csv -E output/Net1_e.csv -N output/Net1_dnode.csv -L output/Net1_dlink.csv data/Net1.hyd > output/Net1.txt 2>&1
diff output/Net1.txt known_output/
diff output/Net1_pnode.csv known_output/
diff output/Net1_plink.csv known_output/
diff output/Net1_e.csv known_output/
diff output/Net1_dnode.csv known_output/
diff output/Net1_dlink.csv known_output/
LANG=en_AU python ../ReadEPANETOutputFile.py --demo_all -vpedca -n output/Net2_pnode.csv -l output/Net2_plink.csv -E output/Net2_e.csv -N output/Net2_dnode.csv -L output/Net2_dlink.csv data/Net2.hyd > output/Net2.txt 2>&1
diff output/Net2.txt known_output/
diff output/Net2_pnode.csv known_output/
diff output/Net2_plink.csv known_output/
diff output/Net2_e.csv known_output/
diff output/Net2_dnode.csv known_output/
diff output/Net2_dlink.csv known_output/
LANG=en_AU python ../ReadEPANETOutputFile.py --demo_all -vpedca -n output/Net3_pnode.csv -l output/Net3_plink.csv -E output/Net3_e.csv -N output/Net3_dnode.csv -L output/Net3_dlink.csv data/Net3.hyd > output/Net3.txt 2>&1
diff output/Net3.txt known_output/
diff output/Net3_pnode.csv known_output/
diff output/Net3_plink.csv known_output/
diff output/Net3_e.csv known_output/
diff output/Net3_dnode.csv known_output/
diff output/Net3_dlink.csv known_output/
