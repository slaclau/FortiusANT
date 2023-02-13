#import array
import math
import numpy
import os
import random
import sys
#import threading
import time
import webbrowser
import wx
import wx.lib.agw.speedmeter             as SM

from   fortius_ant.constants             import mode_Power, mode_Grade, OnRaspberry, mile
import fortius_ant.debug                 as debug
import fortius_ant.logfile               as logfile
import fortius_ant.FortiusAntCommand     as cmd
from   fortius_ant.FortiusAntTitle       import githubWindowTitle
import fortius_ant.RadarGraph            as RadarGraph
import fortius_ant.settings              as settings

#-------------------------------------------------------------------------------
# constants
#-------------------------------------------------------------------------------
ForceRefresh        = True  # More stable with self.panel.Refresh()
ForceRefreshDC      = False # add DOT/COMMA to force refresh
_UseStaticText      = False # There appears to be no difference in behaviour
                            # for StaticText() or TextCtrl() with appropriate style

LargeTexts          = True  # 2020-02-07

bg                  = wx.Colour(220,220,220) # Background colour [for self.Speedometers]
colorTacxFortius    = wx.Colour(120,148,227)
Margin              = 4

FixedForDocu        = False

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
    Calibrating = False         # Flag that we're calibrating
    clv        = None
    LastFields = 0  # Time when SetValues() updated the fields
    LastHeart  = 0  # Time when heartbeat image was updated
    IdleDone   = 0  # Counter to warn that callIdleFunction is not redefined
    power      = [] # Array with power-tuples

    StatusLeds   = [False,False,False,False,False]   # 5 True/False flags
    StatusLedsXr = None # Right side of rightmost status-led-label
    StatusLedsYb = None # Bottom of status-led-row
    
    def __init__(self, parent, pclv):
        showSpeed = True
        showRevs = True
        showPower = True
        # ----------------------------------------------------------------------
        # Create frame and panel for TAB-handling
        # (First versions did not use panel, and that's why TABs did not work)
        # ----------------------------------------------------------------------
        wx.Frame.__init__(self, parent, -1, githubWindowTitle())#, style = wx.DEFAULT_FRAME_STYLE & ~ wx.MAXIMIZE_BOX)
        if True:
            self.panel = wx.Panel(self) # Controls on panel for TAB-handling
        else:
            self.panel = self           # Controls directly on the frame window

        # ----------------------------------------------------------------------
        # Save Command Line Variables in the GUI-context
        # ----------------------------------------------------------------------
        self.clv = pclv

        # ----------------------------------------------------------------------
        # Images are either in directory of the .py or embedded in .exe
        # ----------------------------------------------------------------------
        if getattr(sys, 'frozen', False):
            dirname = sys._MEIPASS
        else:
            dirname = os.path.dirname(__file__)

        FortiusAnt_ico = os.path.join(dirname, "FortiusAnt.ico")
        FortiusAnt_jpg = os.path.join(dirname, "FortiusAnt.jpg")
        Heart_jpg      = os.path.join(dirname, "heart.jpg"     )
        settings_bmp   = os.path.join(dirname, "settings.bmp"  )
        sponsor_bmp    = os.path.join(dirname, "sponsor.bmp"   )

        try:
            ico = wx.Icon(FortiusAnt_ico, wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            print('Cannot load '+ FortiusAnt_ico)
            
        # ----------------------------------------------------------------------
        # Default initial actions, bind functions to frame
        # ----------------------------------------------------------------------
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)    # Draw the bitmap
        self.Iconize(False)                            # un-iconize
        #self.Centre() # Too early, do after all controls created

        if True:
            TIMER_ID = 250
            self.timer = wx.Timer(self, TIMER_ID)
            self.Bind(wx.EVT_TIMER, self.OnTimer)
            self.timer.Start(250)
            self.OnTimerEnabled = True

        # ----------------------------`------------------------------------------
        # Thread handling
        # ----------------------------------------------------------------------
        self.RunningSwitch = False
        self.CloseButtonPressed = False

        # ----------------------------------------------------------------------
        # Load Background image
        # ----------------------------------------------------------------------
        self.BackgroundBitmap = False
        BitmapW = 900
        BitmapH = 600
        try:
            self.BackgroundBitmap = wx.Bitmap(FortiusAnt_jpg)       # Image on the window background
            BitmapW = self.BackgroundBitmap.Size.GetWidth()
            BitmapH = self.BackgroundBitmap.Size.GetHeight()
        except:
            print('Cannot load '+ FortiusAnt_jpg)
        # ----------------------------------------------------------------------
        # Load HeartRate image
        # ----------------------------------------------------------------------
        self.HeartRate      = 123
        self.HeartRateWH    = 40
                            # 2020-04-07    # 2020-02-07    # 2020-01-25
        self.HeartRateX     = Margin        # 25            # BitmapW - 25 - self.HeartRateWH
        self.HeartRateY     = BitmapH - 50 - self.HeartRateWH
        self.HeartRateImage = False
        try:
            self.HeartRateImage = wx.Image(Heart_jpg)  # HeartRate

            img           = self.HeartRateImage.Scale(36, 36, wx.IMAGE_QUALITY_HIGH)
            self.bmp36x36 = wx.Bitmap(img)

            img           = self.HeartRateImage.Scale(40, 40, wx.IMAGE_QUALITY_HIGH)
            self.bmp40x40 = wx.Bitmap(img)

        except:
            print('Cannot load ' + Heart_jpg)
            
        # ----------------------------------------------------------------------
        # Calculate location of Cassette image
        # Positioned above HeartRate_img, equally wide/heigh
        # ----------------------------------------------------------------------
        self.CassetteIndex  = self.clv.CassetteStart
        self.CassetteWH     = self.HeartRateWH
        self.CassetteX      = self.HeartRateX
        self.CassetteY      = self.HeartRateY - self.HeartRateWH - Margin
        
        # ----------------------------------------------------------------------
        # Calculate location of Crankset image
        # Positioned above Cassette_img, equally wide/heigh
        # Re-positioned later under txtAntHRM (find self.CranksetY)
        # ----------------------------------------------------------------------
        self.CranksetIndex = self.clv.CranksetStart
        self.CranksetWH    = self.CassetteWH
        self.CranksetX     = self.CassetteX
        self.CranksetY     = self.CassetteY - self.CassetteWH - Margin           
                
        topHBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(topHBoxSizer)
                
        buttonsVBoxSizer = wx.BoxSizer(wx.VERTICAL)
        
        # ----------------------------------------------------------------------
        # Buttons
        # ----------------------------------------------------------------------
        b = wx.Image(settings_bmp)
        b.Rescale(16,16)
        b = wx.Bitmap(b)

        self.btnSettings = wx.BitmapButton(self.panel,bitmap=b, style=wx.NO_BORDER)
        self.btnSettings.SetToolTip ("Modify settings and optionally save for next session")
        self.btnSettings.SetFocus()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnSettings, self.btnSettings)
        buttonsVBoxSizer.Add(self.btnSettings, flag = wx.EXPAND)
        
        self.btnLocateHW = wx.Button(self.panel, label="Locate HW")
        self.btnLocateHW.SetToolTip ("Connect to USB-devices (Tacx trainer and/or ANTdongle)")
        self.btnLocateHW.SetFocus()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnLocateHW, self.btnLocateHW)
        buttonsVBoxSizer.Add(self.btnLocateHW, flag = wx.EXPAND)

        self.btnRunoff   = wx.Button(self.panel, label="Runoff")
        self.btnRunoff.SetToolTip ("Execute runoff-procedure (recommended for magnetic brake trainers)")
        self.btnRunoff.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnRunoff, self.btnRunoff)
        buttonsVBoxSizer.Add(self.btnRunoff, flag = wx.EXPAND)

        self.btnStart    = wx.Button(self.panel, label="Start")
        self.btnStart.SetToolTip ("Start communication with Cycle Training Program")
        self.btnStart.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnStart, self.btnStart)
        buttonsVBoxSizer.Add(self.btnStart, flag = wx.EXPAND)

        self.btnStop     = wx.Button(self.panel, label="Stop")
        self.btnStop.SetToolTip ("Stop FortiusAnt bridge")
        self.btnStop.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnStop, self.btnStop)
        buttonsVBoxSizer.Add(self.btnStop, flag = wx.EXPAND)

        self.btnSponsor  = wx.Button(self.panel, label="Sponsor")
        self.btnSponsor.SetToolTip ("Become a sponsor for FortiusAnt")
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnSponsor, self.btnSponsor)
        buttonsVBoxSizer.Add(self.btnSponsor, flag = wx.EXPAND)

        self.btnHelp     = wx.Button(self.panel, label="Help")
        self.btnHelp.SetToolTip ("Open the manual on github")
        self.Bind(wx.EVT_BUTTON, self.OnClick_btnHelp, self.btnHelp)
        buttonsVBoxSizer.Add(self.btnHelp, flag = wx.EXPAND)
        
        topHBoxSizer.Add(buttonsVBoxSizer)

        # ----------------------------------------------------------------------
        # Speedometer values and colours
        # ----------------------------------------------------------------------
        MiddleTextFontSize  = 10
        TicksFontSize       = 10
        speedmeterSize = buttonsVBoxSizer.GetMinSize().GetHeight()
        print(speedmeterSize)

        # ----------------------------------------------------------------------
        # self.Speedometer
        # ----------------------------------------------------------------------
        speedPanel = wx.Panel(self.panel)
        if showSpeed:
            self.Speed = SM.SpeedMeter(speedPanel, agwStyle=SM.SM_DRAW_HAND|SM.SM_DRAW_GRADIENT|SM.SM_DRAW_MIDDLE_TEXT|SM.SM_DRAW_SECONDARY_TICKS)
            self.Speed.SetSize (0, 0, speedmeterSize, speedmeterSize)
            self.Speed.DisableFocusFromKeyboard()

            self.Speed.SetSpeedBackground(bg)
            self.Speed.SetFirstGradientColour(colorTacxFortius)             # Colours for SM_DRAW_GRADIENT
            self.Speed.SetSecondGradientColour(wx.WHITE)
            self.Speed.DrawExternalArc(True)                                # Do (Not) Draw The External (Container) Arc.
            self.Speed.SetArcColour(wx.BLACK)

            self.Speed.SetAngleRange(-math.pi / 6, 7 * math.pi / 6)         # Set The Region Of Existence Of self.SpeedMeter (Always In Radians!!!!)
            self.Speed.SetHandColour(wx.Colour(255, 50, 0))                    # Set The Colour For The Hand Indicator

            self.Speed.SetMiddleText("Speed")                               # Set The Text In The Center Of self.SpeedMeter
            self.Speed.SetMiddleTextColour(wx.BLUE)                         # Assign The Colour To The Center Text
            self.Speed.SetMiddleTextFont(wx.Font(MiddleTextFontSize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                                                                            # Assign A Font To The Center Text

            Min = 0
            NrIntervals = 10
            Step  = 5
            Max   = Min + Step * NrIntervals
            self.SpeedMax = Max

            intervals = range(Min, Max+1, Step)                             # Create The Intervals That Will Divide Our self.SpeedMeter In Sectors
            self.Speed.SetIntervals(intervals)

            #colours = [wx.BLUE] * NrIntervals                               # Assign The Same Colours To All Sectors (We Simulate A Car Control For self.Speed)
            #self.Speed.SetIntervalColours(colours)

            ticks = [str(interval) for interval in intervals]               # Assign The Ticks: Here They Are Simply The String Equivalent Of The Intervals
            self.Speed.SetTicks(ticks)
            self.Speed.SetTicksColour(wx.WHITE)                             # Set The Ticks/Tick Markers Colour
            self.Speed.SetNumberOfSecondaryTicks(5)                         # We Want To Draw 5 Secondary Ticks Between The Principal Ticks

            self.Speed.SetTicksFont(wx.Font(TicksFontSize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                                                                            # Set The Font For The Ticks Markers
        topHBoxSizer.Add(speedPanel, flag = wx.EXPAND)
        
        # ----------------------------------------------------------------------
        # self.Revs
        # ----------------------------------------------------------------------
        revsPanel = wx.Panel(self.panel)
        if showRevs:
            # SM_ROTATE_TEXT            Draws the ticks rotated: the ticks are rotated accordingly to the tick marks positions.
            # SM_DRAW_SECTORS           Different intervals are painted in differend colours (every sector of the circle has its own colour).
            # SM_DRAW_PARTIAL_SECTORS   Every interval has its own colour, but only a circle corona is painted near the ticks.
            # SM_DRAW_HAND              The hand (arrow indicator) is drawn.
            # SM_DRAW_SHADOW            A shadow for the hand is drawn.
            # SM_DRAW_PARTIAL_FILLER    A circle corona that follows the hand position is drawn near the ticks.
            # SM_DRAW_SECONDARY_TICKS   Intermediate (smaller) ticks are drawn between principal ticks.
            # SM_DRAW_MIDDLE_TEXT       Some text is printed in the middle of the control near the center.
            # SM_DRAW_MIDDLE_ICON       An icon is drawn in the middle of the control near the center.
            # SM_DRAW_GRADIENT          A gradient of colours will fill the control.
            # SM_DRAW_FANCY_TICKS       With this style you can use xml tags to create some custom text and draw it at the ticks position. See lib.fancytext for the tags.
            self.Revs = SM.SpeedMeter(revsPanel, agwStyle=SM.SM_DRAW_GRADIENT | SM.SM_DRAW_PARTIAL_SECTORS | SM.SM_DRAW_HAND | SM.SM_DRAW_SECONDARY_TICKS | SM.SM_DRAW_MIDDLE_TEXT)
            self.Revs.SetSize (0, 0, speedmeterSize, speedmeterSize) # x,y and width, height
            self.Revs.DisableFocusFromKeyboard()

            self.Revs.SetSpeedBackground(bg)
            self.Revs.SetFirstGradientColour(wx.BLUE)                       # Colours for SM_DRAW_GRADIENT
            self.Revs.SetSecondGradientColour(wx.WHITE)
            self.Revs.DrawExternalArc(True)                                 # Do (Not) Draw The External (Container) Arc.
            self.Revs.SetArcColour(wx.BLUE)

            self.Revs.SetAngleRange(-math.pi / 6, 7 * math.pi / 6)          # Set The Region Of Existence Of self.RevsMeter (Always In Radians!!!!)
            self.Revs.SetHandColour(wx.Colour(255, 50, 0))                    # Set The Colour For The Hand Indicator

            self.Revs.SetMiddleText("Cadence")                              # Set The Text In The Center Of self.RevsMeter
            self.Revs.SetMiddleTextColour(wx.BLUE)                          # Assign The Colour To The Center Text
            self.Revs.SetMiddleTextFont(wx.Font(MiddleTextFontSize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                                                                            # Assign A Font To The Center Text

            Min = 0
            NrIntervals = 12
            Step  = 10                                                      # For me, 120/min is enough
            Max   = Min + Step * NrIntervals
            self.RevsMax = Max

            intervals = range(Min, Max+1, Step)                             # Create The Intervals That Will Divide Our self.SpeedMeter In Sectors
            self.Revs.SetIntervals(intervals)

            colours = [wx.BLACK]                                            # Assign colours, per range
            i = 2
            while i <= NrIntervals:
                if i * Step <= 40:                                          # <= 40 is special case for resistance calculation
                    colours.append(wx.BLACK)
                elif i * Step <= 60:
                    colours.append(wx.BLUE)
                elif i * Step <= 90:
                    colours.append(wx.GREEN)
                elif i * Step <= 110:
                    colours.append(wx.Colour(244,144,44))                   # Orange
                else:
                    colours.append(wx.RED)
                i += 1
            self.Revs.SetIntervalColours(colours)

            ticks = [str(interval) for interval in intervals]               # Assign The Ticks: Here They Are Simply The String Equivalent Of The Intervals
            self.Revs.SetTicks(ticks)
            self.Revs.SetTicksColour(wx.WHITE)                                # Set The Ticks/Tick Markers Colour
            self.Revs.SetNumberOfSecondaryTicks(5)                            # We Want To Draw 5 Secondary Ticks Between The Principal Ticks

            self.Revs.SetTicksFont(wx.Font(TicksFontSize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                                                                            # Set The Font For The Ticks Markers
        topHBoxSizer.Add(revsPanel, flag = wx.EXPAND)

        # ----------------------------------------------------------------------
        # self.Power
        # ----------------------------------------------------------------------
        powerPanel = wx.Panel(self.panel)
        if showPower:
            self.Power = SM.SpeedMeter(powerPanel, agwStyle=SM.SM_DRAW_HAND|SM.SM_DRAW_GRADIENT|SM.SM_DRAW_MIDDLE_TEXT|SM.SM_DRAW_SECONDARY_TICKS)
            self.Power.SetSize (0, 0, speedmeterSize, speedmeterSize) # x,y and width, height
            self.Power.DisableFocusFromKeyboard()

            self.Power.SetSpeedBackground(bg)
            self.Power.SetFirstGradientColour(colorTacxFortius)             # Colours for SM_DRAW_GRADIENT
            self.Power.SetSecondGradientColour(wx.WHITE)
            self.Power.DrawExternalArc(True)                                # Do (Not) Draw The External (Container) Arc.
            self.Power.SetArcColour(wx.BLACK)

            self.Power.SetAngleRange(-math.pi / 6, 7 * math.pi / 6)         # Set The Region Of Existence Of self.PowerMeter (Always In Radians!!!!)
            self.Power.SetHandColour(wx.Colour(255, 50, 0))                    # Set The Colour For The Hand Indicator

            self.Power.SetMiddleText("Power")                               # Set The Text In The Center Of self.PowerMeter
            self.Power.SetMiddleTextColour(wx.BLUE)                         # Assign The Colour To The Center Text
            self.Power.SetMiddleTextFont(wx.Font(MiddleTextFontSize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                                                                            # Assign A Font To The Center Text

            Min = 0
            NrIntervals = 10
            Step  = 40
            Max   = Min + Step * NrIntervals
            self.PowerMax = Max
            self.PowerArray = numpy.array([0,0,0,0,0,0,0,0,0,0])            # Array for running everage

            intervals = range(Min, Max+1, Step)                             # Create The Intervals That Will Divide Our self.SpeedMeter In Sectors
            self.Power.SetIntervals(intervals)

#           colours = [wx.BLACK] * NrIntervals                              # Assign The Same Colours To All Sectors (We Simulate A Car Control For self.Speed)
#           self.Power.SetIntervalColours(colours)

            ticks = [str(interval) for interval in intervals]               # Assign The Ticks: Here They Are Simply The String Equivalent Of The Intervals
            self.Power.SetTicks(ticks)
            self.Power.SetTicksColour(wx.WHITE)                                # Set The Ticks/Tick Markers Colour
            self.Power.SetNumberOfSecondaryTicks(5)                            # We Want To Draw 5 Secondary Ticks Between The Principal Ticks

            self.Power.SetTicksFont(wx.Font(TicksFontSize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                                                                            # Set The Font For The Ticks Markers
        topHBoxSizer.Add(powerPanel, flag = wx.EXPAND)

        # ----------------------------------------------------------------------
        # Font sizing for all measurements
        # ----------------------------------------------------------------------
        TextCtrlFont = wx.Font(24, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        #TextCtrlH    = 40
        #TextCtrlW    = int(SpeedWH/2)

        TextCtrlFont2= wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        #TextCtrlH2   = 25
        #_TextCtrlW2  = int(SpeedWH/2)

        # ----------------------------------------------------------------------
        # self.Speed value; speed in km/h or mph (On top of self.Speed)
        # ----------------------------------------------------------------------
        self.txtSpeed = wx.TextCtrl(self.Speed, value="99.9", style=wx.TE_CENTER | wx.TE_READONLY | wx.BORDER_NONE)
        self.txtSpeed.SetBackgroundColour(bg)
        self.txtSpeed.SetFont(TextCtrlFont)
        self.txtSpeed.SetPosition((int((self.Speed.Width - self.txtSpeed.Size[0]) / 2), self.Speed.Height - self.txtSpeed.Size[1]))
        # ----------------------------------------------------------------------
        # self.Revs value;  (On top of self.Revs)
        # ----------------------------------------------------------------------
        self.txtRevs = wx.TextCtrl(self.Revs, value="999/min", style=wx.TE_CENTER | wx.TE_READONLY | wx.BORDER_NONE)
        self.txtRevs.SetBackgroundColour(bg)
        self.txtRevs.SetPosition((int((self.Revs.Width - self.txtRevs.Size[0]) / 2), self.Revs.Height - self.txtRevs.Size[1]))

        # ----------------------------------------------------------------------
        # self.Power values; (On top of self.Power)
        # ----------------------------------------------------------------------
        self.txtPower = wx.TextCtrl(self.Power, value="999 Watt", style=wx.TE_CENTER | wx.TE_READONLY | wx.BORDER_NONE)
        self.txtPower.SetBackgroundColour(bg)
        self.txtPower.SetPosition((int((self.Power.Width - self.txtPower.Size[0]) / 2), self.Power.Height - 2 * self.txtPower.Size[1]))

        self.txtTarget = wx.TextCtrl(self.Power, value="Target=999 Watt", style=wx.TE_LEFT | wx.TE_READONLY | wx.BORDER_NONE)
        self.txtTarget.SetBackgroundColour(bg)
        self.txtTarget.SetPosition((0, self.Power.Height - self.txtTarget.Size[1]))

        self.txtTacx = wx.TextCtrl(self.Power, value="Tacx=9999", style=wx.TE_RIGHT | wx.TE_READONLY | wx.BORDER_NONE)
        self.txtTacx.SetBackgroundColour(bg)
        self.txtTacx.SetPosition((self.Power.Width - self.txtTacx.Size[0], self.txtTarget.Position[1]))


        # ----------------------------------------------------------------------
        # Font setting for all measurements
        # ----------------------------------------------------------------------
        #self.txtSpeed.SetFont(TextCtrlFont)
        self.txtRevs.SetFont(TextCtrlFont)
        self.txtPower.SetFont(TextCtrlFont)
        self.txtTarget.SetFont(TextCtrlFont)
        self.txtTacx.SetFont(TextCtrlFont)
        #self.txtHeartRate.SetFont(TextCtrlFont)
        #self.txtCrankset.SetFont(TextCtrlFont)
        #self.txtCassette.SetFont(TextCtrlFont)

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
    def callSettings(self, RestartApplication, pclv):
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
            for i in range(0,360,int(9)):                           # 9 degrees
                self.power.append((i, random.randint(75, 125)))
            self.RadarGraph.ShowRadarGraph(self.power)

        return True

    def callRunoff(self):
        print("callRunoff not defined by application class")
        f = 1
        while self.RunningSwitch == True:
            t = time.localtime()
            f += 1
            self.SetValues(f/100 * self.SpeedMax, f/100 * self.RevsMax, f/100 * self.PowerMax, t[5], False, t[0] + t[5], 123, 10, random.randint(0,2), random.randint(0,12), 1)
            time.sleep(1/8)                         # sleep 0.125 second (like Tacx2Dongle)
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
        led          = True
        while self.RunningSwitch == True:
            #t = time.localtime()
            r = (90 + random.randint(1,20)) / 100   # 0.9 ... 1.1
#           r = .5
#           self.SetTransparent(tr)                 # frame can be made transparent
#           self.Speed.SetTransparent(tr)           # control on frame cannot be made transparent
#           tr -= 5
#           self.SetValues(r * self.SpeedMax, r * self.RevsMax, r * self.PowerMax, t[5], t[0] + t[5])
            if FixedForDocu: # Fixed value for documentation screen
                #             (km/hr, /min, W,       mode, T=Watt, Grade, Resistance, iHeartRate, Cranck, Cassette, Factor)
                self.SetValues(34.5,  89, 123, mode_Grade,    345,   8.5,       2345,        123,      1,        5,      1)
                #elf.SetValues(34.5,  89, 123, mode_Power,    345,   8.5,       2345,        123,      1,        5,      1)
                self.SetLeds(led, led, led, led, led)
            else:    # Random value for moving GUI test
                self.SetValues(r * 35.6, r * 234, r * 123, mode_Grade, r * 345, r * 19.5, r * 2345, r * 123, random.randint(0,1), random.randint(0,12), 1)
                self.SetLeds(led, not led, led, not led, led)
                led = not led

            if self.clv.PedalStrokeAnalysis:
                for i, p in enumerate(self.power):
                    if FixedForDocu:
                        self.power[i] = (p[0], p[1])
                    else:
                        self.power[i] = (p[0], p[1] + random.uniform(-15, 15))
                self.RadarGraph.ShowRadarGraph(self.power)

            time.sleep(0.250)                       # sleep 0.250 second (like Tacx2Dongle)
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
        dc.DrawBitmap(self.BackgroundBitmap, 0, 0)          # LeftTop in pixels

        # ----------------------------------------------------------------------
        # Draw HeartRate
        #       Image functions done once, instead of every OnPaint()
        # ----------------------------------------------------------------------
        if self.HeartRateImage and self.HeartRate > 40:
#           img = self.HeartRateImage.Scale(self.HeartRateWH, self.HeartRateWH, wx.IMAGE_QUALITY_HIGH)
#           bmp = wx.Bitmap(img)
            if   self.HeartRateWH == 36:
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
            margin    = int((self.CassetteWH - len(self.clv.Cassette) * 3) / 2)
            
            # ------------------------------------------------------------------
            # Draw sprockets, expected 10, 11, 12
            # ------------------------------------------------------------------
            for i in range(0, len(self.clv.Cassette)):
                x = self.CassetteX + margin + i * 3                    # horizontal position
                w = 2                                                               # width
                h = int(self.clv.Cassette[i] / self.clv.CassetteMax * self.CassetteWH )  # height
                y = self.CassetteY + int((self.CassetteWH - h) / 2)   # vertical

                # --------------------------------------------------------------
                # The selected one is red, the other default colour
                # --------------------------------------------------------------
                if i == self.CassetteIndex \
                    or ( i == 0                          and self.CassetteIndex < 0                       )\
                    or ( i == len(self.clv.Cassette) - 1 and self.CassetteIndex >= len(self.clv.Cassette) ):
                    dc.SetPen(wx.Pen(wx.RED))                           # Selected gear
                    ChainX1 = x
                    ChainY1 = y
                else:
                    dc.SetPen(wx.Pen(colorTacxFortius))                 # Other gears

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
            margin    = int((self.CranksetWH - len(self.clv.Crankset) * 4) / 2)
            
            # ------------------------------------------------------------------
            # Draw chainrings, expected 1, 2 or 3
            # ------------------------------------------------------------------
            for i in range(0, len(self.clv.Crankset)):
                x = self.CranksetX + margin + i * 4                    # horizontal position
                w = 2                                                               # width
                h = int(self.clv.Crankset[i] / self.clv.CranksetMax * self.CranksetWH )  # height
                y = self.CranksetY + int((self.CranksetWH - h) / 2)   # vertical

                # --------------------------------------------------------------
                # The selected one is red, the other default colour
                # --------------------------------------------------------------
                if i == self.CranksetIndex \
                    or ( i == 0                           and self.CranksetIndex < 0                        )\
                    or ( i == len(self.clv.Crankset) - 1 and self.CranksetIndex >= len(self.clv.Crankset) ):
                    dc.SetPen(wx.Pen(wx.RED))                           # Selected gear
                    ChainX2 = x
                    ChainY2 = y + h
                else:
                    dc.SetPen(wx.Pen(colorTacxFortius))                 # Other gears

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
        if False: # self.clv.PedalStrokeAnalysis:
            self.RadarGraph.OnPaint(dc)
        # ----------------------------------------------------------------------
        # Draw status leds
        # - If there is no ANT dongle, do not show ANT-led
        # - If there is no BLE interface, do not show BLE-led
        # - Only on Raspberry, not show shutdown-led
        # ----------------------------------------------------------------------
        if False: # True or self.clv.StatusLeds:
            all = FixedForDocu
            x   = self.StatusLedsXr         # Right side of rightmost label
            y   = self.StatusLedsYb - 10    # Upper size of status leds
            r   = 3
            distance = 70

            if all or self.clv.antDeviceID != -1:  # Led 5 = ANT CTP
                x -= distance
                self.DrawLed(dc,   0,   0,255, x, y, r, self.StatusLeds[4], 'ANT CTP'  )

            if all or self.clv.ble:                # Led 4 = Bluetooth CTP
                x -= distance
                self.DrawLed(dc,   0, 255,255, x, y, r, self.StatusLeds[3], 'BLE CTP'  )

            if all or self.clv.Tacx_Cadence:       # Led 3 = Cadence sensor (black because backgroup is white)
                x -= distance
                self.DrawLed(dc,    0,  0,  0, x, y, r, self.StatusLeds[2], 'Cadence'  )

            if all or OnRaspberry:                 # Led 2 = on raspberry only
                x -= distance
                self.DrawLed(dc, 255,   0,  0, x, y, r, self.StatusLeds[1], 'Shutdown' )

            if all or True:                        # Led 1 = Tacx trainer; USB, ANT or Simulated
                x -= distance
                self.DrawLed(dc, 255, 140,  0, x, y, r, self.StatusLeds[0], 'Tacx'     )

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
        if __name__ == "__main__": print ("OnClick_btnSettings()")
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
                    logfile.Console('frmFortiusAntGui.OnClick_btnSettings() unexpected situation')
                    pass
                else:
                    self.Close()                              # Stop program
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
        if __name__ == "__main__": print ("OnClick_btnLocateHW()")

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
        if __name__ == "__main__":  print ("OnClick_btnRunoff()")

        self.btnStop.Enable()
        self.btnStart.Disable()
        self.btnSettings.Disable()
        self.btnRunoff.Disable()
        self.btnStop.SetFocus()

        thread = threading.Thread(target=self.OnClick_btnRunoff_Thread, daemon=True)
        thread.start()

    def OnClick_btnRunoff_Thread(self):
        if __name__ == "__main__": print ("OnClick_btnRunoff_Thread()")

        self.RunningSwitch = True               # callRunoff() will loop
        self.CloseButtonPressed = False
        self.OnTimerEnabled = False
        self.callRunoff()
        wx.CallAfter(self.OnClick_btnRunoff_Done)

    def OnClick_btnRunoff_Done(self):
        self.OnTimerEnabled= True
        self.RunningSwitch = False              # Just to be sure

        self.ResetValues()
        self.btnSettings.Enable()
        self.btnRunoff.Enable()
        self.btnStart.Enable()
        self.btnStop.Disable()
        self.btnRunoff.SetFocus()

        if self.CloseButtonPressed == True:
            self.CloseButtonPressed = False     # Otherwise self.Close() is blocked
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
        if __name__ == "__main__": print ("OnClick_btnStart()")

        self.btnStop.Enable()
        self.btnStart.Disable()
        self.btnSettings.Disable()
        self.btnRunoff.Disable()
        self.btnStop.SetFocus()

        thread = threading.Thread(target=self.OnClick_btnStart_Thread, daemon=True)
        thread.start()

    def OnClick_btnStart_Thread(self):
        if __name__ == "__main__": print ("OnClick_btnStart_Thread()")

        self.RunningSwitch = True               # callTacx2Dongle() will loop
        self.CloseButtonPressed = False
        self.OnTimerEnabled = False
        self.callTacx2Dongle()
        wx.CallAfter(self.OnClick_btnStart_Done)

    def OnClick_btnStart_Done(self):
        self.OnTimerEnabled= True
        self.RunningSwitch = False              # Just to be sure

        self.ResetValues()
        self.btnSettings.Enable()
        self.btnRunoff.Enable()
        self.btnStart.Enable()
        self.btnStop.Disable()
        self.btnStart.SetFocus()

        if self.CloseButtonPressed == True:
            self.CloseButtonPressed = False     # Otherwise self.Close() is blocked
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
        if __name__ == "__main__": print ("OnClick_btnStop()")
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
        if __name__ == "__main__": print ("OnClick_btnSponsor()")
        webbrowser.open_new_tab('https://github.com/sponsors/WouterJD')

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
        if __name__ == "__main__": print ("OnClick_btnHelp()")
        webbrowser.open_new_tab('https://github.com/WouterJD/FortiusANT/blob/master/doc/FortiusANTUserManual.pdf')

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
        if __name__ == "__main__": print("OnClose()")

        if self.RunningSwitch == True:          # Thread is running
            self.RunningSwitch = False          # Stop the thread
                                                # More accurately: ask the thread to finish!
            self.CloseButtonPressed = True      # Indicate to stop program
            # Expected behaviour from the thread:
            # - stop because RunningSwitch == False
            # - check CloseButtonPressed == True and
            #       1. set CloseButtonPressed = False
            #       2. call self.Close()
            # This event will be called again and go through the else and end.
        elif self.CloseButtonPressed:           # Waiting for thread to finish;
                                                # Do not close again!
            print('Please wait for thread to end...')
            pass

        else:                                   # No thread is running;
            event.Skip()                        # Do default actions (stop program)

# ------------------------------------------------------------------------------
# our normal wxApp-derived class, as usual
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    clv = cmd.CommandLineVariables()
    app = wx.App(0)

    frame = frmFortiusAntGui(None, clv)
    app.SetTopWindow(frame)
    frame.Show()
    #frame.Autostart()

    app.MainLoop()