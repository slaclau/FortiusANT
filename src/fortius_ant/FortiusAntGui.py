# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2023-04-28"
# 2023-04-28    Implemented GUI using sizers etc.
# 2022-01-05    MinHeigth/MinWidth replaced by Size() for consistency
# 2022-01-04    text-fields on top of other controls were flickering, because
#                    the parent was not the on-top control #353
# 2021-04-22    centre() done when all controls created
# 2021-04-13    clv.imperial: speed in mph
# 2021-04-12    Status leds are fixed part of GUI, clv.StatusLeds is for Raspberry only
# 2021-03-22    Status leds added to screen; SetLeds() added
# 2021-03-02    Buttons enlarged for Raspberry rendering
# 2021-02-22    Button correction removed from timer
# 2021-02-03    Test values updated in callTacx2Dongle(self)
#               When no heartrate shown, cassette/cranckset
# 2021-01-28    During calibration, the Cadence speedometer will display
#               "Calibration countdown"
#               Help and Sponsor button added (#189)
# 2021-01-25    Random cranckset was 0...2; should be 0..1
#
#               SetValues(), SetMessages() and PedalStrokeAnalysis() made
#               thread safe, using wx.CallAfter(). See issue #216.
#               Ref: https://www.blog.pythonlibrary.org/2010/05/22/wxpython-and-threads/
#
#               Also, after thread-completion (Runoff and Tacx2Dongle), wx.CallAfter()
#               called to perform the post-thread actions in the GUI.
#
#               And as a reference for multi-threading (unchanged in this version):
#                    https://wiki.wxpython.org/LongRunningTasks
#
#               Although the threads should properly end, "daemon=True" is
#               added so that the threads will be killed when the main
#               program stops, just as back-stop to avoid hangups.
#               Ref: https://docs.python.org/3/library/threading.html#thread-objects
#
#               Now that the threads work properly ForceRefreshDC=False can be used.
#               ForceRefreshDC=True was used untill now and remains True, because the
#                                   screen is more stable.
#               Little test: there seems to be no difference between StaticText and
#                            TextCtrl() from screen-stability point of view
#
# 2021-01-18    When Setvalues() is called with zeroes, default transmission
# 2021-01-16    Value of cassette was displayed incorrectly
# 2021-01-08    Buttons spaced and Panel used for TAB-handling
#               Drawing done on the panel and speedometers 'disable focus'
#               #120 cranckset added for virtual front/read shifting
#               Shifting changed to setting the indexes (front/rear)
#                   SetValues() parameter-change
# 2021-01-06    settings added
# 2020-12-20    Constants moved to constants.py
# 2020-12-16    Force refresh when main inputs zero
# 2020-11-04    WindowTitle separated into FortiusAntTitle.py
# 2020-10-01    Version 3.2.2:
#               - Enable manual mode withoout ANT dongle
#               - Correct runoff procedure
# 2020-05-17    Version 3.2.1; two crashes solved
# 2020-05-12    Version 3.2 with SCS and PWR profile
# 2020-05-24    Initial GUI messages made more general
#               TargetResistance not displayed when zero (for i-Vortex)
# 2020-05-15    Window title adjusted to version 3.0, comment on teeth.
# 2020-05-11    Small corrections
# 2020-04-30    Pedal stroke analysis added
#               form class requires clv to be provided when created
#               Occasional crash in OnClose() resolved
# 2020-04-29    Speedmeter optimizations removed (no need due to child-process)
#               StaticValues class removed, fields moved to frmFortiusAntGui.
# 2020-04-27    OnTimer() event restarts too early, OnTimerEnabled flag added.
# 2020-04-20    txtAntHRM added, message size reduced
# 2020-04-07    Messages enlarged to improve readability
#               Message with PowerFactor is no longer displayed
#                   PowerFactor is an antifier inherited way of calibrating
#                   which is not used anymore, although still suppported.
#                   Since the value is not dynamic, the message is obsolete.
#               Digital Gearbox display as a graphic in number of teeth,
#                   as if enlarging/reducing the cassette of the bicycle.
# 2020-03-29    PowercurveFactor added to console
# 2020-02-09    Suffix to refresh text-fields removed (?(
# 2020-02-07    Text resized; as large as possible. Units abbreviated
#               Heartrate positioned left
# 2020-01-24    ico and jpg can be embedded in pyinstaller executable
# 2020-01-22    In GradeMode, TargetPower is also displayed for reference
# 2020-01-01    SetValues, TargetMode added
# 2019-12-30    Version 2.1
#               SetValues() input: TargetPower/TargetGrade to be inline with
#                   FortiusAnt.py itself.
# 2019-12-24    Heartbeat performance optimized
#               "Target x Watt" or "Target grade x %"
# 2019-12-11    Icon added
# 2019-12-06    Frame not resizable, no maximize button
# 2019-12-05    Buttons are enabled and SetFocus in the button event.
#               If done in the thread(), the SetFocus seems not working.
#
#               Also, text fields are flickering, therefore updated every second
# -------------------------------------------------------------------------------
import array
import math
import os
import random
import sys
import threading
import time
import webbrowser

import numpy
import wx
import wx.lib.agw.speedmeter as SM

import fortius_ant.debug as debug
import fortius_ant.FortiusAntCommand as cmd
import fortius_ant.logfile as logfile
import fortius_ant.RadarGraph as RadarGraph
import fortius_ant.settings as settings
from fortius_ant.constants import OnRaspberry, mile, mode_Grade, mode_Power
from fortius_ant.FortiusAntTitle import githubWindowTitle

# -------------------------------------------------------------------------------
# constants
# -------------------------------------------------------------------------------
ForceRefresh = True  # More stable with self.panel.Refresh()
ForceRefreshDC = False  # add DOT/COMMA to force refresh
_UseStaticText = False  # There appears to be no difference in behaviour
# for StaticText() or TextCtrl() with appropriate style

LargeTexts = True  # 2020-02-07

bg = wx.Colour(220, 220, 220)  # Background colour [for self.Speedometers]
colorTacxFortius = wx.Colour(120, 148, 227)
hand_colour = wx.Colour(255, 50, 0)
Margin = 4

FixedForDocu = False


# ------------------------------------------------------------------------------
# Create the FortiusAnt frame
# ------------------------------------------------------------------------------
# Execute:      If this file is executed as main, the user-interface can be
#                   tested without the program functionality
#               If this file is included, the following functions must be defined:
#
# Functions:    Autostart
#               SetValues, ResetValues
#               SetMessages
#
# Folowing functions to be provided:
#               callSettings(self)
#               callIdleFunction(self)
#               callLocateHW(self)          returns True/False
#               callRunoff(self)
#               callTacx2Dongle(self)
# ------------------------------------------------------------------------------
class frmFortiusAntGui(wx.Frame):
    Calibrating = False  # Flag that we're calibrating
    clv = None
    LastFields = 0  # Time when SetValues() updated the fields
    LastHeart = 0  # Time when heartbeat image was updated
    IdleDone = 0  # Counter to warn that callIdleFunction is not redefined
    power = []  # Array with power-tuples

    StatusLeds = [False, False, False, False, False]  # 5 True/False flags
    StatusLedsXr = None  # Right side of rightmost status-led-label
    StatusLedsYb = None  # Bottom of status-led-row

    def __init__(self, parent, pclv):
        wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX)
        self.SetSize((1000, 700))
        self.SetTitle(githubWindowTitle())
        middle_text_font_size = 10
        ticks_font_size = 10
        control_text_font_size = 20
        message_font_size = 12
        lower_control_font_size = 24
        middle_text_font = wx.Font(
            middle_text_font_size,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
        )
        ticks_font = wx.Font(
            ticks_font_size,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
        )
        control_text_font = wx.Font(
            control_text_font_size,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
            0,
            "",
        )
        message_font = wx.Font(
            message_font_size,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
            0,
            "",
        )
        lower_control_font = wx.Font(
            lower_control_font_size,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
            0,
            "",
        )

        # ----------------------------------------------------------------------
        # Save Command Line Variables in the GUI-context
        # ----------------------------------------------------------------------
        self.clv = pclv

        # ----------------------------------------------------------------------
        # Images are either in directory of the .py or embedded in .exe
        # ----------------------------------------------------------------------
        if getattr(sys, "frozen", False):
            dirname = sys._MEIPASS
        else:
            dirname = os.path.dirname(__file__)

        FortiusAnt_ico = os.path.join(dirname, "FortiusAnt.ico")
        self.FortiusAnt_jpg = os.path.join(dirname, "FortiusAnt.jpg")
        Heart_jpg = os.path.join(dirname, "heart.jpg")
        settings_bmp = os.path.join(dirname, "settings.bmp")
        sponsor_bmp = os.path.join(dirname, "sponsor.bmp")

        try:
            ico = wx.Icon(FortiusAnt_ico, wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            print("Cannot load " + FortiusAnt_ico)
            pass

        self.panel = wx.Panel(self, wx.ID_ANY)

        main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_vertical_sizer.Add(top_sizer, 1, wx.ALL | wx.EXPAND, Margin)

        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(buttons_sizer, 0, wx.EXPAND, Margin)

        self.btnSettings = wx.Button(self.panel, wx.ID_ANY, "Settings")
        buttons_sizer.Add(self.btnSettings, 0, wx.ALL | wx.EXPAND, Margin)

        self.btnLocateHW = wx.Button(self.panel, wx.ID_ANY, "Locate HW")
        buttons_sizer.Add(self.btnLocateHW, 0, wx.ALL | wx.EXPAND, Margin)

        self.btnRunoff = wx.Button(self.panel, wx.ID_ANY, "Runoff")
        buttons_sizer.Add(self.btnRunoff, 0, wx.ALL | wx.EXPAND, Margin)

        self.btnStart = wx.Button(self.panel, wx.ID_ANY, "Start")
        buttons_sizer.Add(self.btnStart, 0, wx.ALL | wx.EXPAND, Margin)

        self.btnStop = wx.Button(self.panel, wx.ID_ANY, "Stop")
        buttons_sizer.Add(self.btnStop, 0, wx.ALL | wx.EXPAND, Margin)

        self.buttons_spacer = wx.Panel(self.panel, wx.ID_ANY)
        buttons_sizer.Add(self.buttons_spacer, 1, wx.EXPAND, Margin)

        self.btnSponsor = wx.Button(self.panel, wx.ID_ANY, "Sponsor")
        buttons_sizer.Add(self.btnSponsor, 0, wx.ALL | wx.EXPAND, Margin)

        self.btnHelp = wx.Button(self.panel, wx.ID_ANY, "Help")
        buttons_sizer.Add(self.btnHelp, 0, wx.ALL | wx.EXPAND, Margin)

        self.btnSettings.SetToolTip(
            "Modify settings and optionally save for next session"
        )
        self.btnSettings.SetFocus()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnSettings, self.btnSettings)

        self.btnLocateHW.SetToolTip(
            "Connect to USB-devices (Tacx trainer and/or ANTdongle)"
        )
        self.btnLocateHW.SetFocus()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnLocateHW, self.btnLocateHW)

        self.btnRunoff.SetToolTip(
            "Execute runoff-procedure (recommended for magnetic brake trainers)"
        )
        self.btnRunoff.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnRunoff, self.btnRunoff)

        self.btnStart.SetToolTip("Start communication with Cycle Training Program")
        self.btnStart.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnStart, self.btnStart)

        self.btnStop.SetToolTip("Stop FortiusAnt bridge")
        self.btnStop.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnStop, self.btnStop)

        self.btnSponsor.SetToolTip("Become a sponsor for FortiusAnt")
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnSponsor, self.btnSponsor)

        self.btnHelp.SetToolTip("Open the manual on github")
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnHelp, self.btnHelp)

        self.speed_panel = wx.Panel(self.panel, wx.ID_ANY)
        self.speed_panel.SetBackgroundColour(bg)
        top_sizer.Add(self.speed_panel, 1, wx.ALL | wx.EXPAND, Margin)

        speed_sizer = wx.BoxSizer(wx.VERTICAL)

        self.Speed = wx.lib.agw.speedmeter.SpeedMeter(
            self.speed_panel,
            wx.ID_ANY,
            agwStyle=SM.SM_DRAW_HAND
            | SM.SM_DRAW_MIDDLE_TEXT
            | SM.SM_DRAW_SECONDARY_TICKS,
        )
        try:
            self.Speed.DisableFocusFromKeyboard()
        except AttributeError:
            pass
        self.Speed.SetSpeedBackground(bg)
        self.Speed.DrawExternalArc(True)  # Do (Not) Draw The External (Container) Arc.
        self.Speed.SetArcColour(wx.BLACK)
        self.Speed.SetAngleRange(
            -math.pi / 6, 7 * math.pi / 6
        )  # Set The Region Of Existence Of self.SpeedMeter (Always In Radians!!!!)
        self.Speed.SetHandColour(hand_colour)  # Set The Colour For The Hand Indicator

        self.Speed.SetMiddleText(
            "Speed"
        )  # Set The Text In The Center Of self.SpeedMeter
        self.Speed.SetMiddleTextColour(wx.BLUE)  # Assign The Colour To The Center Text
        self.Speed.SetMiddleTextFont(middle_text_font)
        # Assign A Font To The Center Text
        Min = 0
        NrIntervals = 10
        Step = 5
        Max = Min + Step * NrIntervals
        self.SpeedMax = Max
        intervals = range(
            Min, Max + 1, Step
        )  # Create The Intervals That Will Divide Our self.SpeedMeter In Sectors
        self.Speed.SetIntervals(intervals)

        ticks = [
            str(interval) for interval in intervals
        ]  # Assign The Ticks: Here They Are Simply The String Equivalent Of The Intervals
        self.Speed.SetTicks(ticks)
        self.Speed.SetTicksColour(wx.BLACK)  # Set The Ticks/Tick Markers Colour
        self.Speed.SetNumberOfSecondaryTicks(
            5
        )  # We Want To Draw 5 Secondary Ticks Between The Principal Ticks
        self.Speed.SetTicksFont(ticks_font)
        # Set The Font For The Ticks Markers
        speed_sizer.Add(self.Speed, 1, wx.EXPAND, Margin)

        self.text_ctrl_filler = wx.TextCtrl(
            self.speed_panel,
            wx.ID_ANY,
            "",
            style=wx.BORDER_NONE | wx.TE_CENTRE | wx.TE_READONLY,
        )
        self.text_ctrl_filler.SetBackgroundColour(bg)
        self.text_ctrl_filler.SetFont(control_text_font)
        speed_sizer.Add(self.text_ctrl_filler, 0, wx.EXPAND, Margin)

        self.txtSpeed = wx.TextCtrl(
            self.speed_panel,
            wx.ID_ANY,
            "99.9",
            style=wx.BORDER_NONE | wx.TE_CENTRE | wx.TE_READONLY,
        )
        self.txtSpeed.SetBackgroundColour(bg)
        self.txtSpeed.SetFont(control_text_font)
        speed_sizer.Add(self.txtSpeed, 0, wx.EXPAND, Margin)

        self.revs_panel = wx.Panel(self.panel, wx.ID_ANY)
        self.revs_panel.SetBackgroundColour(bg)
        top_sizer.Add(self.revs_panel, 1, wx.ALL | wx.EXPAND, Margin)

        revs_sizer = wx.BoxSizer(wx.VERTICAL)

        self.Revs = wx.lib.agw.speedmeter.SpeedMeter(
            self.revs_panel,
            wx.ID_ANY,
            agwStyle=SM.SM_DRAW_HAND
            | SM.SM_DRAW_PARTIAL_SECTORS
            | SM.SM_DRAW_MIDDLE_TEXT
            | SM.SM_DRAW_SECONDARY_TICKS,
        )
        try:
            self.Revs.DisableFocusFromKeyboard()
        except AttributeError:
            pass
        self.Revs.SetSpeedBackground(bg)
        self.Revs.DrawExternalArc(True)  # Do (Not) Draw The External (Container) Arc.
        self.Revs.SetArcColour(wx.BLACK)
        self.Revs.SetAngleRange(
            -math.pi / 6, 7 * math.pi / 6
        )  # Set The Region Of Existence Of self.SpeedMeter (Always In Radians!!!!)
        self.Revs.SetHandColour(hand_colour)  # Set The Colour For The Hand Indicator

        self.Revs.SetMiddleText(
            "Cadence"
        )  # Set The Text In The Center Of self.SpeedMeter
        self.Revs.SetMiddleTextColour(wx.BLUE)  # Assign The Colour To The Center Text
        self.Revs.SetMiddleTextFont(middle_text_font)
        # Assign A Font To The Center Text
        Min = 0
        NrIntervals = 12
        Step = 10
        Max = Min + Step * NrIntervals
        self.RevsMax = Max
        intervals = range(
            Min, Max + 1, Step
        )  # Create The Intervals That Will Divide Our self.SpeedMeter In Sectors
        self.Revs.SetIntervals(intervals)
        colours = [wx.WHITE]  # Assign colours, per range
        i = 2
        while i <= NrIntervals:
            if i * Step <= 40:  # <= 40 is special case for resistance calculation
                colours.append(wx.WHITE)
            elif i * Step <= 60:
                colours.append(wx.BLUE)
            elif i * Step <= 90:
                colours.append(wx.GREEN)
            elif i * Step <= 110:
                colours.append(wx.Colour(244, 144, 44))  # Orange
            else:
                colours.append(wx.RED)
            i += 1
        self.Revs.SetIntervalColours(colours)
        ticks = [
            str(interval) for interval in intervals
        ]  # Assign The Ticks: Here They Are Simply The String Equivalent Of The Intervals
        self.Revs.SetTicks(ticks)
        self.Revs.SetTicksColour(wx.BLACK)  # Set The Ticks/Tick Markers Colour
        self.Revs.SetNumberOfSecondaryTicks(
            5
        )  # We Want To Draw 5 Secondary Ticks Between The Principal Ticks
        self.Revs.SetTicksFont(ticks_font)
        # Set The Font For The Ticks Markers
        revs_sizer.Add(self.Revs, 1, wx.EXPAND, Margin)

        self.text_ctrl_filler_2 = wx.TextCtrl(
            self.revs_panel,
            wx.ID_ANY,
            "",
            style=wx.BORDER_NONE | wx.TE_CENTRE | wx.TE_READONLY,
        )
        self.text_ctrl_filler_2.SetBackgroundColour(bg)
        self.text_ctrl_filler_2.SetFont(control_text_font)
        revs_sizer.Add(self.text_ctrl_filler_2, 0, wx.EXPAND, Margin)

        self.txtRevs = wx.TextCtrl(
            self.revs_panel,
            wx.ID_ANY,
            "999/min",
            style=wx.BORDER_NONE | wx.TE_CENTRE | wx.TE_READONLY,
        )
        self.txtRevs.SetBackgroundColour(bg)
        self.txtRevs.SetFont(control_text_font)
        revs_sizer.Add(self.txtRevs, 0, wx.EXPAND, Margin)

        self.power_panel = wx.Panel(self.panel, wx.ID_ANY)
        self.power_panel.SetBackgroundColour(bg)
        top_sizer.Add(self.power_panel, 1, wx.ALL | wx.EXPAND, Margin)

        power_sizer = wx.BoxSizer(wx.VERTICAL)

        self.Power = wx.lib.agw.speedmeter.SpeedMeter(
            self.power_panel,
            wx.ID_ANY,
            agwStyle=SM.SM_DRAW_HAND
            | SM.SM_DRAW_MIDDLE_TEXT
            | SM.SM_DRAW_SECONDARY_TICKS,
        )
        try:
            self.Power.DisableFocusFromKeyboard()
        except AttributeError:
            pass
        self.Power.SetSpeedBackground(bg)
        self.Power.DrawExternalArc(True)  # Do (Not) Draw The External (Container) Arc.
        self.Power.SetArcColour(wx.BLACK)
        self.Power.SetAngleRange(
            -math.pi / 6, 7 * math.pi / 6
        )  # Set The Region Of Existence Of self.SpeedMeter (Always In Radians!!!!)
        self.Power.SetHandColour(hand_colour)  # Set The Colour For The Hand Indicator

        self.Power.SetMiddleText(
            "Power"
        )  # Set The Text In The Center Of self.SpeedMeter
        self.Power.SetMiddleTextColour(wx.BLUE)  # Assign The Colour To The Center Text
        self.Power.SetMiddleTextFont(middle_text_font)
        # Assign A Font To The Center Text
        Min = 0
        NrIntervals = 10
        Step = 40
        Max = Min + Step * NrIntervals
        self.PowerMax = Max
        self.PowerArray = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        intervals = range(
            Min, Max + 1, Step
        )  # Create The Intervals That Will Divide Our self.SpeedMeter In Sectors
        self.Power.SetIntervals(intervals)

        ticks = [
            str(interval) for interval in intervals
        ]  # Assign The Ticks: Here They Are Simply The String Equivalent Of The Intervals
        self.Power.SetTicks(ticks)
        self.Power.SetTicksColour(wx.BLACK)  # Set The Ticks/Tick Markers Colour
        self.Power.SetNumberOfSecondaryTicks(
            5
        )  # We Want To Draw 5 Secondary Ticks Between The Principal Ticks
        self.Power.SetTicksFont(ticks_font)
        # Set The Font For The Ticks Markers
        power_sizer.Add(self.Power, 1, wx.EXPAND, Margin)

        self.txtPower = wx.TextCtrl(
            self.power_panel,
            wx.ID_ANY,
            "999 Watt",
            style=wx.BORDER_NONE | wx.TE_CENTRE | wx.TE_READONLY,
        )
        self.txtPower.SetBackgroundColour(bg)
        self.txtPower.SetFont(control_text_font)
        power_sizer.Add(self.txtPower, 0, wx.EXPAND, Margin)

        power_control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        power_sizer.Add(power_control_sizer, 0, wx.EXPAND, Margin)

        self.txtTarget = wx.TextCtrl(
            self.power_panel,
            wx.ID_ANY,
            "999 Watt",
            style=wx.BORDER_NONE | wx.TE_LEFT | wx.TE_READONLY,
        )
        self.txtTarget.SetBackgroundColour(bg)
        self.txtTarget.SetFont(control_text_font)
        power_control_sizer.Add(self.txtTarget, 1, wx.EXPAND, Margin)

        self.txtTacx = wx.TextCtrl(
            self.power_panel,
            wx.ID_ANY,
            "9999",
            style=wx.BORDER_NONE | wx.TE_READONLY | wx.TE_RIGHT,
        )
        self.txtTacx.SetBackgroundColour(bg)
        self.txtTacx.SetFont(control_text_font)
        power_control_sizer.Add(self.txtTacx, 1, wx.EXPAND, Margin)

        message_horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_vertical_sizer.Add(message_horizontal_sizer, 0, wx.EXPAND, Margin)

        message_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        message_horizontal_sizer.Add(message_vertical_sizer, 3, wx.EXPAND, Margin)

        self.txtUsbTrainer = wx.TextCtrl(
            self.panel, wx.ID_ANY, "999 Watt", style=wx.TE_LEFT | wx.TE_READONLY
        )
        self.txtUsbTrainer.SetBackgroundColour(bg)
        self.txtUsbTrainer.SetFont(message_font)
        message_vertical_sizer.Add(self.txtUsbTrainer, 0, wx.ALL | wx.EXPAND, Margin)

        self.txtAntDongle = wx.TextCtrl(
            self.panel, wx.ID_ANY, "999 Watt", style=wx.TE_LEFT | wx.TE_READONLY
        )
        self.txtAntDongle.SetBackgroundColour(bg)
        self.txtAntDongle.SetFont(message_font)
        message_vertical_sizer.Add(self.txtAntDongle, 0, wx.ALL | wx.EXPAND, Margin)

        self.txtAntHRM = wx.TextCtrl(
            self.panel, wx.ID_ANY, "999 Watt", style=wx.TE_LEFT | wx.TE_READONLY
        )
        self.txtAntHRM.SetBackgroundColour(bg)
        self.txtAntHRM.SetFont(message_font)
        message_vertical_sizer.Add(self.txtAntHRM, 0, wx.ALL | wx.EXPAND, Margin)

        self.panel_7 = wx.Panel(self.panel, wx.ID_ANY)
        message_horizontal_sizer.Add(self.panel_7, 1, wx.EXPAND, Margin)

        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_vertical_sizer.Add(bottom_sizer, 0, wx.EXPAND, Margin)

        grid_sizer = wx.FlexGridSizer(3, 2, 0, 0)
        bottom_sizer.Add(grid_sizer, 1, wx.EXPAND, Margin)

        self.crankset_panel = wx.Panel(self.panel, wx.ID_ANY)
        self.crankset_panel.SetMinSize((48, 48))
        grid_sizer.Add(self.crankset_panel, 1, wx.EXPAND, Margin)

        self.txtCrankset = wx.TextCtrl(
            self.panel, wx.ID_ANY, "456", style=wx.TE_LEFT | wx.TE_READONLY
        )
        self.txtCrankset.SetBackgroundColour(bg)
        self.txtCrankset.SetFont(lower_control_font)
        grid_sizer.Add(self.txtCrankset, 0, wx.ALL | wx.EXPAND, Margin)

        self.cassette_panel = wx.Panel(self.panel, wx.ID_ANY)
        self.cassette_panel.SetMinSize((48, 48))
        grid_sizer.Add(self.cassette_panel, 1, wx.EXPAND, Margin)

        self.txtCassette = wx.TextCtrl(
            self.panel, wx.ID_ANY, "789", style=wx.TE_LEFT | wx.TE_READONLY
        )
        self.txtCassette.SetBackgroundColour(bg)
        self.txtCassette.SetFont(lower_control_font)
        grid_sizer.Add(self.txtCassette, 0, wx.ALL | wx.EXPAND, Margin)

        self.heartrate_panel = wx.Panel(self.panel, wx.ID_ANY)
        self.heartrate_panel.SetMinSize((48, 48))
        grid_sizer.Add(self.heartrate_panel, 1, wx.EXPAND, Margin)

        self.txtHeartRateShown = True
        self.txtHeartRate = wx.TextCtrl(
            self.panel, wx.ID_ANY, "123", style=wx.TE_LEFT | wx.TE_READONLY
        )
        self.txtHeartRate.SetBackgroundColour(bg)
        self.txtHeartRate.SetFont(lower_control_font)
        grid_sizer.Add(self.txtHeartRate, 0, wx.ALL | wx.EXPAND, Margin)

        self.radar_graph_panel = wx.Panel(self.panel, wx.ID_ANY)
        bottom_sizer.Add(self.radar_graph_panel, 1, wx.EXPAND, Margin)

        self.panel_6 = wx.Panel(self.panel, wx.ID_ANY)
        bottom_sizer.Add(self.panel_6, 1, wx.EXPAND, Margin)

        self.power_panel.SetSizer(power_sizer)

        self.revs_panel.SetSizer(revs_sizer)

        self.speed_panel.SetSizer(speed_sizer)

        self.panel.SetSizer(main_vertical_sizer)

        self.Layout()

        # ----------------------------------------------------------------------
        # Frame resizes based upon the created controls, so center here!
        # ----------------------------------------------------------------------
        self.Centre()

        # ----------------------------------------------------------------------
        # Set initial values
        # ----------------------------------------------------------------------
        self.ResetValues()
        self.SetMessages(Tacx="Tacx Trainer")
        self.SetMessages(Dongle="ANT+ Dongle")
        self.SetMessages(HRM="ANT+ Heart Rate Monitor")

        self.SetDoubleBuffered(True)

        # ----------------------------------------------------------------------
        # Default initial actions, bind functions to frame
        # ----------------------------------------------------------------------
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)  # Draw the bitmap
        self.Iconize(False)  # un-iconize
        # self.Centre() # Too early, do after all controls created

        if True:
            TIMER_ID = 250
            self.timer = wx.Timer(self, TIMER_ID)
            self.Bind(wx.EVT_TIMER, self.OnTimer)
            self.timer.Start(250)
            self.OnTimerEnabled = True

        # ----------------------------------------------------------------------
        # Thread handling
        # ----------------------------------------------------------------------
        self.RunningSwitch = False
        self.CloseButtonPressed = False

        # ----------------------------------------------------------------------
        # Load Background image
        # ----------------------------------------------------------------------
        self.BackgroundBitmap = False
        try:
            self.BackgroundBitmap = wx.Bitmap(
                self.FortiusAnt_jpg
            )  # Image on the window background
        except:
            print("Cannot load " + self.FortiusAnt_jpg)
        # ----------------------------------------------------------------------
        # Load HeartRate image
        # ----------------------------------------------------------------------
        self.HeartRate = 123
        self.HeartRateX = self.heartrate_panel.GetPosition().x + Margin
        self.HeartRateY = self.heartrate_panel.GetPosition().y + Margin
        self.HeartRateWH = 40
        self.HeartRateImage = False
        try:
            self.HeartRateImage = wx.Image(Heart_jpg)  # HeartRate

            img = self.HeartRateImage.Scale(36, 36, wx.IMAGE_QUALITY_HIGH)
            self.bmp36x36 = wx.Bitmap(img)

            img = self.HeartRateImage.Scale(40, 40, wx.IMAGE_QUALITY_HIGH)
            self.bmp40x40 = wx.Bitmap(img)

        except:
            # print('Cannot load ' + Heart_jpg)
            pass
        # ----------------------------------------------------------------------
        # Calculate location of Cassette image
        # Positioned above HeartRate_img, equally wide/heigh
        # ----------------------------------------------------------------------
        self.CassetteWH = self.HeartRateWH
        self.CassetteX = self.cassette_panel.GetPosition().x + Margin
        self.CassetteY = self.cassette_panel.GetPosition().y + Margin
        self.CassetteIndex = self.clv.CassetteStart

        # ----------------------------------------------------------------------
        # Calculate location of Crankset image
        # Positioned above Cassette_img, equally wide/heigh
        # Re-positioned later under txtAntHRM (find self.CranksetY)
        # ----------------------------------------------------------------------
        self.CranksetWH = self.HeartRateWH
        self.CranksetX = self.crankset_panel.GetPosition().x + Margin
        self.CranksetY = self.crankset_panel.GetPosition().y + Margin
        self.CranksetIndex = self.clv.CranksetStart

        self.StatusLedsXr = self.panel.GetPosition().x + self.panel.GetSize().x
        self.StatusLedsYb = self.panel.GetPosition().y + self.panel.GetSize().y

        x = self.radar_graph_panel.GetPosition().x + Margin
        y = self.radar_graph_panel.GetPosition().y + Margin
        wh = self.radar_graph_panel.GetSize().y - 2 * Margin
        if self.clv.PedalStrokeAnalysis:
            self.RadarGraph = RadarGraph.clsRadarGraph(
                self.radar_graph_panel, "Pedal stroke analysis", x, y, wh
            )

    # --------------------------------------------------------------------------
    # F u n c t i o n s  --  to be provided by subclass.
    #
    # The structure is as follows:
    # - The user interface calls "callXYZ" which is to be provided
    # - The form class defines the functions and calls the function
    # - The function being called is independant of the user interface
    #
    # The code below provides functionality so that the GUI works and can be tested
    # --------------------------------------------------------------------------
    def callSettings(self, pRestartApplication, pclv):
        print("callSettings not defined by application class")
        return True

    def callIdleFunction(self):
        if self.IdleDone < 10:
            print("callIdleFunction not defined by application class")
            self.IdleDone += 1
        return True

    def callLocateHW(self):
        print("callLocateHW not defined by application class")

        if self.clv.PedalStrokeAnalysis:
            # Fill list and show it
            for i in range(0, 360, int(9)):  # 9 degrees
                self.power.append((i, random.randint(75, 125)))
            self.RadarGraph.ShowRadarGraph(self.power)

        return True

    def callRunoff(self):
        print("callRunoff not defined by application class")
        f = 1
        while self.RunningSwitch == True:
            t = time.localtime()
            f += 1
            self.SetValues(
                f / 100 * self.SpeedMax,
                f / 100 * self.RevsMax,
                f / 100 * self.PowerMax,
                t[5],
                False,
                t[0] + t[5],
                123,
                10,
                random.randint(0, 2),
                random.randint(0, 12),
                1,
            )
            time.sleep(1 / 8)  # sleep 0.125 second (like Tacx2Dongle)
            if f > 100:
                self.RunningSwitch == False

            if self.clv.PedalStrokeAnalysis:
                for i, p in enumerate(self.power):
                    self.power[i] = (p[0], p[1] + random.uniform(-15, 15))
                self.RadarGraph.ShowRadarGraph(self.power)

        self.ResetValues()
        return True

    def callTacx2Dongle(self):
        print("callTacx2Dongle not defined by application class")
        #       tr = 255                                    # experimental purpose only
        led = True
        while self.RunningSwitch == True:
            # t = time.localtime()
            r = (90 + random.randint(1, 20)) / 100  # 0.9 ... 1.1
            #           r = .5
            #           self.SetTransparent(tr)                 # frame can be made transparent
            #           self.Speed.SetTransparent(tr)           # control on frame cannot be made transparent
            #           tr -= 5
            #           self.SetValues(r * self.SpeedMax, r * self.RevsMax, r * self.PowerMax, t[5], t[0] + t[5])
            if FixedForDocu:  # Fixed value for documentation screen
                #             (km/hr, /min, W,       mode, T=Watt, Grade, Resistance, iHeartRate, Cranck, Cassette, Factor)
                self.SetValues(34.5, 89, 123, mode_Grade, 345, 8.5, 2345, 123, 1, 5, 1)
                # elf.SetValues(34.5,  89, 123, mode_Power,    345,   8.5,       2345,        123,      1,        5,      1)
                self.SetLeds(led, led, led, led, led)
            else:  # Random value for moving GUI test
                self.SetValues(
                    r * 35.6,
                    r * 234,
                    r * 123,
                    mode_Grade,
                    r * 345,
                    r * 19.5,
                    r * 2345,
                    r * 123,
                    random.randint(0, 1),
                    random.randint(0, 12),
                    1,
                )
                self.SetLeds(led, not led, led, not led, led)
                led = not led

            if self.clv.PedalStrokeAnalysis:
                for i, p in enumerate(self.power):
                    if FixedForDocu:
                        self.power[i] = (p[0], p[1])
                    else:
                        self.power[i] = (p[0], p[1] + random.uniform(-15, 15))
                self.RadarGraph.ShowRadarGraph(self.power)

            time.sleep(0.250)  # sleep 0.250 second (like Tacx2Dongle)
        return True

    # --------------------------------------------------------------------------
    # A u t o s t a r t
    # --------------------------------------------------------------------------
    # input:        None
    #
    # Description:  Press two buttons: [LocateHW] and [Start]
    #               Button-press simulate so that buttons are enabled/disabled
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def Autostart(self):
        if self.OnClick_btnLocateHW():
            self.OnClick_btnStart()

    # --------------------------------------------------------------------------
    # N a v i g a t e
    # --------------------------------------------------------------------------
    # input:        None
    #
    # Description:  Enter-button on headunit is pressed.
    #               Simulate click on active button
    #
    #               Note: when btnLocateHW is enabled, we do not have a trainer
    #                     yet and therefore no Enter button to find the trainer
    #                     will ever be recieved.
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def Navigate_Enter(self):
        if self.btnLocateHW.HasFocus():
            self.OnClick_btnLocateHW(self)  # Will never occur
        elif self.btnRunoff.HasFocus():
            self.OnClick_btnRunoff(self)
        elif self.btnStart.HasFocus():
            self.OnClick_btnStart(self)
        elif self.btnStop.HasFocus():
            self.OnClick_btnStop(self)
        else:
            pass

    def Navigate_Up(self):
        if self.btnLocateHW.HasFocus():
            pass  # is first button
        elif self.btnRunoff.HasFocus():
            pass  # previous cannot be enabled
        elif self.btnStart.HasFocus():
            self.btnRunoff.SetFocus()
        elif self.btnStop.HasFocus():
            pass  # stop first
        else:
            pass

    def Navigate_Down(self):
        if self.btnLocateHW.HasFocus():
            pass  # must be done first
        elif self.btnRunoff.HasFocus():
            self.btnStart.SetFocus()
        elif self.btnStart.HasFocus():
            pass  # must start first
        elif self.btnStop.HasFocus():
            pass  # is last button
        else:
            pass

    def Navigate_Back(self):
        if self.RunningSwitch == True:
            self.RunningSwitch = False  # Stop running thread
            self.CloseButtonPressed = False  # Do not stop the program
        else:
            self.Close()  # Stop program
            pass

    # --------------------------------------------------------------------------
    # S e t L e d s
    # --------------------------------------------------------------------------
    # input:        Tacx, Shutdown, Cadence, BLE, ANT
    #
    # Description:  Modify the leds according the inputs
    #
    # Output:       self.StatusLeds
    # --------------------------------------------------------------------------
    def SetLeds(
        self, ANT=None, BLE=None, Cadence=None, Shutdown=None, Tacx=None
    ):  # Thread safe
        wx.CallAfter(self.SetLedsGUI, ANT, BLE, Cadence, Shutdown, Tacx)

    def SetLedsGUI(self, ANT=None, BLE=None, Cadence=None, Shutdown=None, Tacx=None):
        # print (ANT, BLE, Cadence, Shutdown, Tacx, self.StatusLeds)
        if Tacx != None:
            self.StatusLeds[0] = not self.StatusLeds[0] if Tacx else False
        if Shutdown != None:
            self.StatusLeds[1] = not self.StatusLeds[1] if Shutdown else False
        if Cadence != None:
            self.StatusLeds[2] = not self.StatusLeds[2] if Cadence else False
        if BLE != None:
            self.StatusLeds[3] = not self.StatusLeds[3] if BLE else False
        if ANT != None:
            self.StatusLeds[4] = not self.StatusLeds[4] if ANT else False
        self.panel.Refresh()

    # --------------------------------------------------------------------------
    # S e t V a l u e s
    # --------------------------------------------------------------------------
    # input:        User interface values
    #               fSpeed          Actual speed in km/hr
    #               iRevs           Revolutions in /min
    #               iPower          Actual Power in Watts
    #               iTargetMode     basic, power or grade
    #               iTargetPower    Target Power in Watts
    #               fTargetGrade    Target Grade in %
    #               iTacx           Target resistance for the Tacx
    #               iHeartRate      Heartrate in beats/min
    #               iCranksetIndex, iCassetteIndex
    #                               Index position of the virtual gearbox.
    #
    # Description:  Show the values in SpeedoMeter and text-fields
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def ResetValues(self):
        self.SetValues(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    def SetValues(
        self,
        fSpeed,
        iRevs,
        iPower,
        iTargetMode,
        iTargetPower,
        fTargetGrade,
        iTacx,
        iHeartRate,
        iCranksetIndex,
        iCassetteIndex,
        fReduction,
    ):  # Tread safe
        wx.CallAfter(
            self.SetValuesGUI,
            fSpeed,
            iRevs,
            iPower,
            iTargetMode,
            iTargetPower,
            fTargetGrade,
            iTacx,
            iHeartRate,
            iCranksetIndex,
            iCassetteIndex,
            fReduction,
        )

    def SetValuesGUI(
        self,
        fSpeed,
        iRevs,
        iPower,
        iTargetMode,
        iTargetPower,
        fTargetGrade,
        iTacx,
        iHeartRate,
        iCranksetIndex,
        iCassetteIndex,
        fReduction,
    ):
        # ----------------------------------------------------------------------
        # When zero, display default setting
        # ----------------------------------------------------------------------
        if fReduction == 0:
            fReduction = 1  # Aviod DivideByZero
            iCranksetIndex = self.clv.CranksetStart
            iCassetteIndex = self.clv.CassetteStart

        # ----------------------------------------------------------------------
        # Average power over the last 10 readings
        # ----------------------------------------------------------------------
        self.PowerArray = numpy.append(
            self.PowerArray, iPower
        )  # Add new value to array
        self.PowerArray = numpy.delete(self.PowerArray, 0)  # Remove oldest from array
        iPowerMean = int(numpy.mean(self.PowerArray))  # Calculate average

        # ----------------------------------------------------------------------
        # Force refresh to avoid ghost values at end-of-loop
        # ----------------------------------------------------------------------
        if fSpeed == 0 and iRevs == 0 and iPower == 0:
            iPowerMean = 0  # Avoid that meter remains > 0
            self.LastFields = 0  # Force refresh

        # ----------------------------------------------------------------------
        # Values are needed on OnPaint() event
        # ----------------------------------------------------------------------
        if iHeartRate > 40:
            self.HeartRate = iHeartRate
        else:
            self.HeartRate = 0

        if iTargetMode in (
            mode_Grade,
            mode_Power,
        ):  # issue #195 asked for power-mode as well
            self.CranksetIndex = iCranksetIndex
            self.CassetteIndex = iCassetteIndex
            self.Reduction = fReduction
        else:
            self.CranksetIndex = None  # Not valid in other modes
            self.CassetteIndex = None
            self.Reduction = 1

        # ----------------------------------------------------------------------
        # Update measurements once per second only (otherwise too much flicker)
        # .SetSpeedValue requires quite some processing, but since we are in our
        #   own process since 29-4-2020 refresh all, no optimize needed.
        # ----------------------------------------------------------------------
        delta = time.time() - self.LastFields  # Delta time since previous
        if delta >= 1:  # Refresh once per second
            self.LastFields = time.time()  # Time in seconds

            if self.Calibrating:
                self.Revs.SetMiddleText("Calibration countdown")
            else:
                self.Revs.SetMiddleText("Cadence")
            self.Speed.SetSpeedValue(float(min(max(0, fSpeed), self.SpeedMax)))
            self.Revs.SetSpeedValue(float(min(max(0, iRevs), self.RevsMax)))
            self.Power.SetSpeedValue(float(min(max(0, iPowerMean), self.PowerMax)))

            if ForceRefreshDC:
                # Alternating suffix makes the texts being refreshed
                suffix1 = "."  # str(0x32) # space
                suffix2 = ","  # str(0xa0) # no break space
                suffix = self.txtSpeed.Value[-1:]
                suffix = suffix2 if suffix == suffix1 else suffix1
            else:
                # Such a measurement is not needed (anymore)
                suffix = ""

            # 2020-02-07: LargeTexts implemented
            if LargeTexts:
                if self.clv.imperial:
                    self.txtSpeed.SetValue(("%4.1fmph" % (fSpeed / mile)) + suffix)
                else:
                    self.txtSpeed.SetValue("%4.1fkm/h" % fSpeed + suffix)

                if self.Calibrating:
                    self.txtRevs.SetValue("%i" % iRevs + suffix)
                else:
                    self.txtRevs.SetValue("%i/min" % iRevs + suffix)

                self.txtPower.SetValue("%iW" % iPower + suffix)

                if iTacx == 0:
                    self.txtTacx.SetValue("")
                else:
                    self.txtTacx.SetValue("%i" % iTacx + suffix)
                fTargetPower = "%iW"
            else:
                if self.clv.imperial:
                    self.txtSpeed.SetValue(("%4.1f mph" % (fSpeed / mile)) + suffix)
                else:
                    self.txtSpeed.SetValue("%4.1f km/h" % fSpeed + suffix)
                self.txtRevs.SetValue("%i revs/min" % iRevs + suffix)
                self.txtPower.SetValue("%i Watt" % iPower + suffix)
                self.txtTacx.SetValue("Tacx=%i" % iTacx + suffix)
                fTargetPower = "%i Watt"

            if iTargetMode == mode_Power:
                self.txtTarget.SetValue(fTargetPower % iTargetPower + suffix)

            elif iTargetMode == mode_Grade:
                s = "%2.0f%%" % fTargetGrade
                s += "%iW" % iTargetPower  # Target power added for reference
                # Can be negative!
                self.txtTarget.SetValue(s + suffix)

            else:
                self.txtTarget.SetValue("No target" + suffix)

            if logfile.IsOpen() and debug.on(debug.Data1 | debug.Data2):
                Elapsed = time.time() - self.LastFields
                logfile.Write("SetValues() done in %s ms" % int(Elapsed * 1000))

        # ----------------------------------------------------------------------
        # If there is a HeartRate, bounce the image
        # We pass here every 0.250 second = 400 times/minute
        # Do not process more often than heartbeat
        # ----------------------------------------------------------------------
        bRefreshRequired = False
        delta = time.time() - self.LastHeart  # Delta time since previous
        if delta >= 60 / max(
            60, self.HeartRate * 2
        ):  # At HeartRate, not slower than 1/second
            # *2 because one heartbeat = 2 cycles
            self.LastHeart = time.time()  # Time in seconds
            if self.HeartRate > 0:
                if not self.txtHeartRate.IsShown():
                    # If txtHeartrate not shown; move the cassette/crankset up
                    self.txtHeartRate.Show()
                    self.txtHeartRateShown = True
                self.txtHeartRate.SetValue("%i" % self.HeartRate)

                if self.HeartRateWH == 40:  # Show 36x36 on every other passage
                    self.HeartRateWH = 36
                    self.HeartRateX += 2  # center in the 40x40 area
                    self.HeartRateY += 2  # center in the 40x40 area
                    bRefreshRequired = True

                elif self.HeartRateWH == 36:  # Show 40x40 on every other passage
                    self.HeartRateWH = 40
                    self.HeartRateX -= 2  # use the 40x40 area
                    self.HeartRateY -= 2  # use the 40x40 area
                    bRefreshRequired = True

            else:
                if self.txtHeartRate.IsShown():
                    # If txtHeartrate not shown; move the cassette/crankset down
                    self.txtHeartRate.Hide()
                    self.txtHeartRateShown = False
                    bRefreshRequired = True

        # ----------------------------------------------------------------------
        # Gearbox
        # Show the size of the selected sprocket & chainring.
        # The cassette and cranckset are displayed in OnPaint()!
        # ----------------------------------------------------------------------
        if self.CranksetIndex != None:
            if not self.txtCrankset.IsShown():
                self.txtCrankset.Show()

            self.txtCrankset.SetValue("%i" % self.clv.Crankset[self.CranksetIndex])
            bRefreshRequired = True  # So that Crankset is painted

        else:
            if self.txtCrankset.IsShown():
                self.txtCrankset.Hide()
                bRefreshRequired = True

        if self.CassetteIndex != None:
            if not self.txtCassette.IsShown():
                self.txtCassette.Show()

            if self.CassetteIndex < 0:  # IF out of bounds: Reduction <> 1
                teeth = self.clv.Cassette[0]
            elif self.CassetteIndex >= len(self.clv.Cassette):
                teeth = self.clv.Cassette[len(self.clv.Cassette) - 1]
            else:
                teeth = self.clv.Cassette[self.CassetteIndex]

            self.txtCassette.SetValue("%i" % int(round(teeth / self.Reduction)))
            bRefreshRequired = True  # So that Cassette is painted

        else:
            if self.txtCassette.IsShown():
                self.txtCassette.Hide()
                bRefreshRequired = True

        # ----------------------------------------------------------------------
        # Refresh if required; so that JPGs are drawn in the OnPaint() event
        # ----------------------------------------------------------------------
        if ForceRefresh and bRefreshRequired:
            self.panel.Refresh()

    def SetMessages(self, Tacx=None, Dongle=None, HRM=None):  # Tread safe
        wx.CallAfter(self.SetMessagesGUI, Tacx, Dongle, HRM)

    def SetMessagesGUI(self, Tacx=None, Dongle=None, HRM=None):
        if Tacx != None:
            if Tacx[:4] == "* * ":  # We're calibrating!
                self.Calibrating = True
                self.txtUsbTrainer.SetForegroundColour(wx.BLUE)
            else:
                self.Calibrating = False
                self.txtUsbTrainer.SetForegroundColour(wx.BLACK)
            self.txtUsbTrainer.SetValue(Tacx)

        if Dongle != None:
            self.txtAntDongle.SetValue(Dongle)

        if HRM != None:
            self.txtAntHRM.SetValue(HRM)

    # --------------------------------------------------------------------------
    # P e d a l S t r o k e A n a l y s i s
    # --------------------------------------------------------------------------
    # input:        User interface values
    #               info = list of tuples(Time,  Power)
    #
    # Description:  Show the Pedal Stroke Analysis in the RadarGraph
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def PedalStrokeAnalysis(self, info, Cadence):  # Tread safe
        wx.CallAfter(self.RadarGraph.PedalStrokeAnalysis, info, Cadence)

    # --------------------------------------------------------------------------
    # O n P a i n t
    # --------------------------------------------------------------------------
    # input:        None
    #
    # Description:  Paint the frame, the bitmap and the HeartRate
    #               Ref: http://zetcode.com/wxpython/gdi/
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnPaint(self, event):
        # ----------------------------------------------------------------------
        # Draw background (to be done on every OnPaint() otherwise disappears!
        # ----------------------------------------------------------------------
        dc = wx.PaintDC(self.panel)
        dc.DrawBitmap(self.BackgroundBitmap, 0, 0)  # LeftTop in pixels

        # ----------------------------------------------------------------------
        # Draw HeartRate
        #       Image functions done once, instead of every OnPaint()
        # ----------------------------------------------------------------------
        if self.HeartRateImage and self.HeartRate > 40:
            #           img = self.HeartRateImage.Scale(self.HeartRateWH, self.HeartRateWH, wx.IMAGE_QUALITY_HIGH)
            #           bmp = wx.Bitmap(img)
            if self.HeartRateWH == 36:
                dc.DrawBitmap(self.bmp36x36, self.HeartRateX, self.HeartRateY)
            elif self.HeartRateWH == 40:
                dc.DrawBitmap(self.bmp40x40, self.HeartRateX, self.HeartRateY)
            else:
                logfile.Write("Unsupported image size")
        else:
            pass

        # ----------------------------------------------------------------------
        # Draw Digital Crankset and Cassette with Max 12 sprockets since 12*3
        # pixels fits in the 40x40 area we have chosen to use
        # ----------------------------------------------------------------------
        ChainX1 = False
        ChainY1 = False
        ChainX2 = False
        ChainY1 = False
        # ----------------------------------------------------------------------
        # Draw Cassette
        # ----------------------------------------------------------------------
        if self.CassetteIndex != None:
            # ------------------------------------------------------------------
            # The sprocket is 2 pixels wide, 1 space = 3 per sprocket
            # With 40 pixels and 13 sprockets: 3 * 13 = 39 which fits
            # ------------------------------------------------------------------
            margin = int((self.CassetteWH - len(self.clv.Cassette) * 3) / 2)

            # ------------------------------------------------------------------
            # Draw sprockets, expected 10, 11, 12
            # ------------------------------------------------------------------
            for i in range(0, len(self.clv.Cassette)):
                x = self.CassetteX + margin + i * 3  # horizontal position
                w = 2  # width
                h = int(
                    self.clv.Cassette[i] / self.clv.CassetteMax * self.CassetteWH
                )  # heigth
                y = self.CassetteY + int((self.CassetteWH - h) / 2)  # vertical

                # --------------------------------------------------------------
                # The selected one is red, the other default colour
                # --------------------------------------------------------------
                if (
                    i == self.CassetteIndex
                    or (i == 0 and self.CassetteIndex < 0)
                    or (
                        i == len(self.clv.Cassette) - 1
                        and self.CassetteIndex >= len(self.clv.Cassette)
                    )
                ):
                    dc.SetPen(wx.Pen(wx.RED))  # Selected gear
                    ChainX1 = x
                    ChainY1 = y
                else:
                    dc.SetPen(wx.Pen(colorTacxFortius))  # Other gears

                # --------------------------------------------------------------
                # Draw the chainring
                # --------------------------------------------------------------
                dc.DrawRectangle(int(x), int(y), int(w), int(h))

        # ----------------------------------------------------------------------
        # Draw Crankset
        # ----------------------------------------------------------------------
        if self.CranksetIndex != None:
            # ------------------------------------------------------------------
            # The chainring is 2 pixels wide, 2 space = 4 per chainring
            # Since max 3 chainrings, this always fits
            # ------------------------------------------------------------------
            margin = int((self.CranksetWH - len(self.clv.Crankset) * 4) / 2)

            # ------------------------------------------------------------------
            # Draw chainrings, expected 1, 2 or 3
            # ------------------------------------------------------------------
            for i in range(0, len(self.clv.Crankset)):
                x = self.CranksetX + margin + i * 4  # horizontal position
                w = 2  # width
                h = int(
                    self.clv.Crankset[i] / self.clv.CranksetMax * self.CranksetWH
                )  # heigth
                y = self.CranksetY + int((self.CranksetWH - h) / 2)  # vertical

                # --------------------------------------------------------------
                # The selected one is red, the other default colour
                # --------------------------------------------------------------
                if (
                    i == self.CranksetIndex
                    or (i == 0 and self.CranksetIndex < 0)
                    or (
                        i == len(self.clv.Crankset) - 1
                        and self.CranksetIndex >= len(self.clv.Crankset)
                    )
                ):
                    dc.SetPen(wx.Pen(wx.RED))  # Selected gear
                    ChainX2 = x
                    ChainY2 = y + h
                else:
                    dc.SetPen(wx.Pen(colorTacxFortius))  # Other gears

                # --------------------------------------------------------------
                # Draw the chainring
                # --------------------------------------------------------------
                dc.DrawRectangle(int(x), int(y), int(w), int(h))

                # --------------------------------------------------------------
                # If cassette and chainring selected, draw chain
                # --------------------------------------------------------------
                if ChainX1 and ChainX2:
                    dc.DrawLine(int(ChainX1), int(ChainY1), int(ChainX2), int(ChainY2))
                    ChainX1 = False

        else:
            pass
        # ----------------------------------------------------------------------
        # Draw Pedal Stroke Analysis
        # ----------------------------------------------------------------------
        if self.clv.PedalStrokeAnalysis:
            self.RadarGraph.OnPaint(dc)
        # ----------------------------------------------------------------------
        # Draw status leds
        # - If there is no ANT dongle, do not show ANT-led
        # - If there is no BLE interface, do not show BLE-led
        # - Only on Raspberry, not show shutdown-led
        # ----------------------------------------------------------------------
        if True or self.clv.StatusLeds:
            all = FixedForDocu
            x = self.StatusLedsXr  # Right side of rightmost label
            y = self.StatusLedsYb - 10  # Upper size of status leds
            r = 3
            distance = 70

            if all or self.clv.antDeviceID != -1:  # Led 5 = ANT CTP
                x -= distance
                self.DrawLed(dc, 0, 0, 255, x, y, r, self.StatusLeds[4], "ANT CTP")

            if all or self.clv.ble:  # Led 4 = Bluetooth CTP
                x -= distance
                self.DrawLed(dc, 0, 255, 255, x, y, r, self.StatusLeds[3], "BLE CTP")

            if (
                all or self.clv.Tacx_Cadence
            ):  # Led 3 = Cadence sensor (black because backgroup is white)
                x -= distance
                self.DrawLed(dc, 0, 0, 0, x, y, r, self.StatusLeds[2], "Cadence")

            if all or OnRaspberry:  # Led 2 = on raspberry only
                x -= distance
                self.DrawLed(dc, 255, 0, 0, x, y, r, self.StatusLeds[1], "Shutdown")

            if all or True:  # Led 1 = Tacx trainer; USB, ANT or Simulated
                x -= distance
                self.DrawLed(dc, 255, 140, 0, x, y, r, self.StatusLeds[0], "Tacx")

            self.OnResize(event)

    # --------------------------------------------------------------------------
    # D r a w L e d
    # --------------------------------------------------------------------------
    def DrawLed(self, dc, r, g, b, x, y, radius, on, label):
        c = wx.Colour(r, g, b)  # pylint: disable=maybe-no-member
        dc.SetPen(wx.Pen(c))  # Circle line, pylint: disable=maybe-no-member
        if on == True or FixedForDocu:
            dc.SetBrush(wx.Brush(c))  # Circle fill, pylint: disable=maybe-no-member
        else:
            dc.SetBrush(wx.TRANSPARENT_BRUSH)  # Circle fill transparent
        dc.DrawCircle(x, y, radius)
        led_font_size = 8
        led_font = wx.Font(
            led_font_size,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
        )
        dc.SetFont(led_font)
        dc.DrawText(label, x + radius + 2, y - 7)

    def OnResize(self, event):
        event.Skip()
        self.HeartRateX = self.heartrate_panel.GetPosition().x + Margin
        self.HeartRateY = self.heartrate_panel.GetPosition().y + Margin

        self.CassetteX = self.cassette_panel.GetPosition().x + Margin
        self.CassetteY = self.cassette_panel.GetPosition().y + Margin

        self.CranksetX = self.crankset_panel.GetPosition().x + Margin
        self.CranksetY = self.crankset_panel.GetPosition().y + Margin

        self.StatusLedsXr = self.panel.GetPosition().x + self.panel.GetSize().x
        self.StatusLedsYb = self.panel.GetPosition().y + self.panel.GetSize().y

        w = self.panel.GetSize().x
        h = self.panel.GetSize().y

        ww = w / 1.5
        size = int(min(ww, h))

        try:
            self.BackgroundBitmap = wx.Bitmap(
                self.FortiusAnt_jpg
            )  # Image on the window background
            image = self.BackgroundBitmap.ConvertToImage()
            image = image.Scale(int(size * 1.5), size, wx.IMAGE_QUALITY_HIGH)
            self.BackgroundBitmap = wx.Bitmap(image)
        except Exception as e:
            print(e)
            print("Cannot load " + self.FortiusAnt_jpg)

        self.RadarGraph = None
        x = self.radar_graph_panel.GetPosition().x + Margin
        y = self.radar_graph_panel.GetPosition().y + Margin
        wh = self.radar_graph_panel.GetSize().y - 2 * Margin
        if self.clv.PedalStrokeAnalysis:
            self.RadarGraph = RadarGraph.clsRadarGraph(
                self.radar_graph_panel, "Pedal stroke analysis", x, y, wh
            )

    # --------------------------------------------------------------------------
    # O n T i m e r
    # --------------------------------------------------------------------------
    # input:        None
    #
    # Description:  Is called every second; if we are IDLE, use function called
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnTimer(self, event):
        if self.OnTimerEnabled:
            self.callIdleFunction()

    # --------------------------------------------------------------------------
    # O n C l i c k _ b t n S e t t i n g s
    # --------------------------------------------------------------------------
    # input:        [Settings] pressed
    #
    # Description:  Modify FortiusAnt settings
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnClick_btnSettings(self, event=False):
        if __name__ == "__main__":
            print("OnClick_btnSettings()")
        self.OnTimerEnabled = False
        # app is not available here, use None
        RestartApplication, clvReturned = settings.OpenDialog(None, self, self.clv)
        self.OnTimerEnabled = True
        if RestartApplication != None:
            # ------------------------------------------------------------------
            # Inform that clv is changed and that application has to be restarted
            # ------------------------------------------------------------------
            self.clv = clvReturned
            self.callSettings(RestartApplication, self.clv)
            # ------------------------------------------------------------------
            # If application must be restarted, end the GUI
            # We do not expect that a thread is running!!
            # ------------------------------------------------------------------
            if RestartApplication == True:
                if self.RunningSwitch == True:
                    logfile.Console(
                        "frmFortiusAntGui.OnClick_btnSettings() unexpected situation"
                    )
                    pass
                else:
                    self.Close()  # Stop program

    # --------------------------------------------------------------------------
    # O n C l i c k _ b t n L o c a t e H W
    # --------------------------------------------------------------------------
    # input:        [Locate HW] pressed
    #
    # Description:  Enable [RUNOFF], [START]
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnClick_btnLocateHW(self, event=False):
        if __name__ == "__main__":
            print("OnClick_btnLocateHW()")

        self.OnTimerEnabled = False
        rtn = self.callLocateHW()
        self.OnTimerEnabled = True
        if rtn:
            self.btnRunoff.Enable()
            self.btnStart.Enable()
            self.btnSettings.Disable()
            self.btnLocateHW.Disable()
            self.btnStart.SetFocus()
        return rtn

    # --------------------------------------------------------------------------
    # O n C l i c k _ b t n R u n o f f
    # --------------------------------------------------------------------------
    # input:        [RUNOFF] pressed
    #
    # Description:  Start RunoffThread
    #               Enable [STOP], Disable [SETTINGS], [START] and [RUNOFF]
    #               If CloseButtonPressed, stop the program after the thread
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnClick_btnRunoff(self, event):
        if __name__ == "__main__":
            print("OnClick_btnRunoff()")

        self.btnStop.Enable()
        self.btnStart.Disable()
        self.btnSettings.Disable()
        self.btnRunoff.Disable()
        self.btnStop.SetFocus()

        thread = threading.Thread(target=self.OnClick_btnRunoff_Thread, daemon=True)
        thread.start()

    def OnClick_btnRunoff_Thread(self):
        if __name__ == "__main__":
            print("OnClick_btnRunoff_Thread()")

        self.RunningSwitch = True  # callRunoff() will loop
        self.CloseButtonPressed = False
        self.OnTimerEnabled = False
        self.callRunoff()
        wx.CallAfter(self.OnClick_btnRunoff_Done)

    def OnClick_btnRunoff_Done(self):
        self.OnTimerEnabled = True
        self.RunningSwitch = False  # Just to be sure

        self.ResetValues()
        self.btnSettings.Enable()
        self.btnRunoff.Enable()
        self.btnStart.Enable()
        self.btnStop.Disable()
        self.btnRunoff.SetFocus()

        if self.CloseButtonPressed == True:
            self.CloseButtonPressed = False  # Otherwise self.Close() is blocked
            self.Close()

    # --------------------------------------------------------------------------
    # O n C l i c k _ b t n S t a r t
    # --------------------------------------------------------------------------
    # input:        [START] pressed
    #
    # Description:  Start RunningThread
    #               Enable [STOP], Disable [SETTINGS], [START] and [RUNOFF]
    #               If CloseButtonPressed, stop the program after the thread
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnClick_btnStart(self, event=False):
        if __name__ == "__main__":
            print("OnClick_btnStart()")

        self.btnStop.Enable()
        self.btnStart.Disable()
        self.btnSettings.Disable()
        self.btnRunoff.Disable()
        self.btnStop.SetFocus()

        thread = threading.Thread(target=self.OnClick_btnStart_Thread, daemon=True)
        thread.start()

    def OnClick_btnStart_Thread(self):
        if __name__ == "__main__":
            print("OnClick_btnStart_Thread()")

        self.RunningSwitch = True  # callTacx2Dongle() will loop
        self.CloseButtonPressed = False
        self.OnTimerEnabled = False
        self.callTacx2Dongle()
        wx.CallAfter(self.OnClick_btnStart_Done)

    def OnClick_btnStart_Done(self):
        self.OnTimerEnabled = True
        self.RunningSwitch = False  # Just to be sure

        self.ResetValues()
        self.btnSettings.Enable()
        self.btnRunoff.Enable()
        self.btnStart.Enable()
        self.btnStop.Disable()
        self.btnStart.SetFocus()

        if self.CloseButtonPressed == True:
            self.CloseButtonPressed = False  # Otherwise self.Close() is blocked
            self.Close()

    # --------------------------------------------------------------------------
    # O n C l i c k _ b t n S t o p
    # --------------------------------------------------------------------------
    # input:        [STOP] pressed
    #
    # Description:  Stop RunningThread; when that was not running, no effect
    #
    # Output:       self.RunningSwitch
    # --------------------------------------------------------------------------
    def OnClick_btnStop(self, event=False):
        if __name__ == "__main__":
            print("OnClick_btnStop()")
        self.RunningSwitch = False
        self.btnStop.Disable()

    # --------------------------------------------------------------------------
    # O n C l i c k _ b t n S p o n s o r
    # --------------------------------------------------------------------------
    # input:        [SPONSOR] pressed
    #
    # Description:  Open sponsor page
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnClick_btnSponsor(self, event=False):
        if __name__ == "__main__":
            print("OnClick_btnSponsor()")
        webbrowser.open_new_tab("https://github.com/sponsors/WouterJD")

    # --------------------------------------------------------------------------
    # O n C l i c k _ b t n H e l p
    # --------------------------------------------------------------------------
    # input:        [Help] pressed
    #
    # Description:  Open manual
    #
    # Output:       None
    # --------------------------------------------------------------------------
    def OnClick_btnHelp(self, event=False):
        if __name__ == "__main__":
            print("OnClick_btnHelp()")
        webbrowser.open_new_tab(
            "https://github.com/WouterJD/FortiusANT/blob/master/doc/FortiusANTUserManual.pdf"
        )

    # --------------------------------------------------------------------------
    # O n C l o s e
    # --------------------------------------------------------------------------
    # input:        ALT-F4 is pressed
    #
    # Description:  if the thread is running, stop thread and indicate to stop
    #                   the program after the thread
    #               if the thread is NOT running, stop immediatly
    #
    # Output:       self.RunningSwitch
    #               self.CloseButtonPressed
    # --------------------------------------------------------------------------
    def OnClose(self, event):
        if __name__ == "__main__":
            print("OnClose()")

        if self.RunningSwitch == True:  # Thread is running
            self.RunningSwitch = False  # Stop the thread
            # More accurately: ask the thread to finish!
            self.CloseButtonPressed = True  # Indicate to stop program
            # Expected behaviour from the thread:
            # - stop because RunningSwitch == False
            # - check CloseButtonPressed == True and
            #       1. set CloseButtonPressed = False
            #       2. call self.Close()
            # This event will be called again and go through the else and end.
        elif self.CloseButtonPressed:  # Waiting for thread to finish;
            # Do not close again!
            print("Please wait for thread to end...")
            pass

        else:  # No thread is running;
            event.Skip()  # Do default actions (stop program)


# ------------------------------------------------------------------------------
# our normal wxApp-derived class, as usual
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    clv = cmd.CommandLineVariables()
    app = wx.App(0)

    frame = frmFortiusAntGui(None, clv)
    app.SetTopWindow(frame)
    frame.Show()
    frame.Autostart()

    app.MainLoop()
