@REM Run basic tests of EPANETOutputFile tool using EPANET Net1 output file
@setlocal
set LANG=en_AU
if not exist output: mkdir output
del /y output\*.csv output\Net*.txt
python ..\ReadEPANETOutputFile.py --demo_all -vpedca -n output\Net1_pnode.csv -l output\Net1_plink.csv -E output\Net1_e.csv -N output\Net1_dnode.csv -L output\Net1_dlink.csv data\Net1.hyd > output\Net1.txt 2>&1
fc output\Net1.txt known_output\Net1.txt
fc output\Net1_pnode.csv known_output\Net1_pnode.csv
fc output\Net1_plink.csv known_output\Net1_plink.csv
fc output\Net1_e.csv known_output\Net1_e.csv
fc output\Net1_dnode.csv known_output\Net1_dnode.csv
fc output\Net1_dlink.csv known_output\Net1_dlink.csv
python ..\ReadEPANETOutputFile.py --demo_all -vpedca -n output\Net2_pnode.csv -l output\Net2_plink.csv -E output\Net2_e.csv -N output\Net2_dnode.csv -L output\Net2_dlink.csv data\Net2.hyd > output\Net2.txt 2>&1
fc output\Net2.txt known_output\Net2.txt
fc output\Net2_pnode.csv known_output\Net2_pnode.csv
fc output\Net2_plink.csv known_output\Net2_plink.csv
fc output\Net2_e.csv known_output\Net2_e.csv
fc output\Net2_dnode.csv known_output\Net2_dnode.csv
fc output\Net2_dlink.csv known_output\Net2_dlink.csv
python ..\ReadEPANETOutputFile.py --demo_all -vpedca -n output\Net3_pnode.csv -l output\Net3_plink.csv -E output\Net3_e.csv -N output\Net3_dnode.csv -L output\Net3_dlink.csv data\Net3.hyd > output\Net3.txt 2>&1
fc output\Net3.txt known_output\Net3.txt
fc output\Net3_pnode.csv known_output\Net3_pnode.csv
fc output\Net3_plink.csv known_output\Net3_plink.csv
fc output\Net3_e.csv known_output\Net3_e.csv
fc output\Net3_dnode.csv known_output\Net3_dnode.csv
fc output\Net3_dlink.csv known_output\Net3_dlink.csv
@endlocal
