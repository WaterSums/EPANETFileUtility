# ex:set ts=4 sw=4: <- for vim
#
# Coloured panel class
#
# Dependencies:
# - Python 2.6 or 2.7 (32- or 64-bit)
# - wxPython 3.0.0 (32- or 64-bit to match installed version of Python)
#

import wx

class ColouredPanel(wx.Window):
    def __init__(self, parent, colour):
        wx.Window.__init__(self, parent, -1, style = wx.SIMPLE_BORDER)
        self.SetBackgroundColour(colour)
        if wx.Platform == '__WXGTK__':
            self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

