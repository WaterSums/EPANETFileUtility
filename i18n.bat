@REM python "c:\Program Files (x86)\Python27\Tools\i18n\pygettext.py" -van -d EPANETOutputFile -p EPANETOutputFile EPANETOutputFile\EPANETOutputFile.py EPANETOutputFile\EPANETOutputFilePlugin.py EPANETOutputFile\EOFTInternalPlugin.py
@REM "c:\Program Files (x86)\GnuWin32\bin\xgettext.exe" --copyright-holder="Mark Morgan" --package-name="WaterSums" --package-version="1.0.0" -n -d EPANETOutputFile -p EPANETOutputFile -o EPANETOutputFile.pot -L Python EPANETOutputFile\EPANETOutputFile.py EPANETOutputFile\EPANETOutputFilePlugin.py EPANETOutputFile\EOFTInternalPlugin.py
"c:\Program Files (x86)\GnuWin32\bin\xgettext.exe" --copyright-holder="Mark Morgan" -n -d EPANETOutputFile -p EPANETOutputFile -o EPANETOutputFile.pot -L Python EPANETOutputFile\EPANETOutputFile.py EPANETOutputFile\EPANETOutputFilePlugin.py EPANETOutputFile\EOFTInternalPlugin.py EPANETOutputFile\plugins\demo\__init__.py
copy EPANETOutputFile\EPANETOutputFile.pot locale\
@REM copy EPANETOutputFile\EPANETOutputFile.pot locale\en_AU\LC_MESSAGES\EPANETOutputFile.po
"c:\Program Files (x86)\GnuWin32\bin\xgettext.exe" --copyright-holder="Mark Morgan" -n -d EPANETFileUtility -o EPANETFileUtility.pot -L Python EPANETFileUtility.py DataPage.py TablePage.py ExportPage.py
copy EPANETFileUtility.pot locale\
@REM copy EPANETFileUtility.pot locale\en_AU\LC_MESSAGES\EPANETFileUtility.po
@REM python "c:\Program Files (x86)\Python27\Tools\i18n\msgfmt.py" locale\en_AU\LC_MESSAGES\EPANETFileUtility.po
