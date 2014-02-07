@REM Run basic tests of EPANETOutputFile tool using EPANET Net1 output file
@setlocal
set LANG=en_AU
if not exist output: mkdir output
del /y output\*.csv
python ..\ReadEPANETOutputFile.py -vpedca -n output\Net1_pnode.csv -l output\Net1_plink.csv -E output\Net1_e.csv -N output\Net1_dnode.csv -L output\Net1_dlink.csv data\Net1.hyd
@endlocal
