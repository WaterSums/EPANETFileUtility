#!/bin/sh
#xgettext -n -d EPANETOutputFile -p EPANETOutputFile -o EPANETOutputFile.pot -L Python EPANETOutputFile/EPANETOutputFile.py EPANETOutputFile/EPANETOutputFilePlugin.py EPANETOutputFile/EOFTInternalPlugin.py EPANETOutputFile/plugins/demo/__init__.py
xgettext --copyright-holder="Mark Morgan" --package-name="EPANETOutputFile" --package-version="1.0.0" -n -d EPANETOutputFile -p EPANETOutputFile -o EPANETOutputFile.pot -L Python EPANETOutputFile/EPANETOutputFile.py EPANETOutputFile/EPANETOutputFilePlugin.py EPANETOutputFile/EOFTInternalPlugin.py EPANETOutputFile/plugins/demo/__init__.py
cp EPANETOutputFile/EPANETOutputFile.pot locale
xgettext --copyright-holder="Mark Morgan" --package-name="EPANETFileUtility" --package-version="0.0.1" -n -d EPANETFileUtility -o EPANETFileUtility.pot -L Python EPANETFileUtility.py
cp EPANETFileUtility.pot locale
