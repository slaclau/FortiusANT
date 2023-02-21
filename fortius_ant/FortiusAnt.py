"""Public module for FortiusANT."""
import argparse
import glob
import multiprocessing
import os
import pickle
import platform
import random
import struct
import sys
import threading
import time
from datetime import datetime

import numpy
import usb.core

from fortius_ant import FortiusAntBody
from fortius_ant import FortiusAntCommand as cmd
from fortius_ant import TCXexport, antCTRL
from fortius_ant import antDongle as ant
from fortius_ant import antFE as fe
from fortius_ant import antHRM as hrm
from fortius_ant import antPWR as pwr
from fortius_ant import antSCS as scs
from fortius_ant import (
    bleBless,
    bleBlessClass,
    bleDongle,
    constants,
    debug,
    logfile,
    raspberry,
    settings,
)
from fortius_ant import structConstants as sc
from fortius_ant import usbTrainer
from fortius_ant.constants import (
    OnRaspberry,
    UseBluetooth,
    UseGui,
    UseMultiProcessing,
    mile,
    mode_Grade,
    mode_Power,
)
from fortius_ant.FortiusAntTitle import githubWindowTitle

if UseGui:
    import wx

    from fortius_ant import FortiusAntGui as gui
    from fortius_ant import RadarGraph as RadarGraph
# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2022-03-08"
# 2022-03-08    bleBless, bleBlessClass added
# 2021-04-29    If no hrm used (-H-1) thgen do not show on console.
#               Leds shown on console
# 2021-03-22    Added; SetLeds
# 2021-03-03    Change 2020-12-16 undone; modification moved to GUI itself
#                   so that raspberry can powerdown.
# 2021-03-01    raspberry added
# 2021-02-25    Console message modified to fit on one line
# 2021-02-18    FortiusAntBody.Initialize() not called in the GUI-process
#               FortiusAntBody.Terminate()  before ending main()
# 2021-01-10    Digital gearbox changed to front/rear index
# 2021-01-06    settings added (+ missing other files for version check)
# 2020-12-24    usage of UseGui implemented
# 2020-12-20    Constants used from constants.py
# 2020-11-18    Logfile shows what version is started; windows exe or python
# 2020-12-16    Stopping the program is no longer possible from the head unit
#                   (#164 - to restart you have to get off your bike)
# 2020-11-13    Logfile was not closed on end
# 2020-11-05    New files added, githubWindowTitle() used
# 2020-05-24    WindowTitle in logfile
# 2020-04-23    First version; core functions separated into FortiusAntBody.py
#               This module contains program startup, GUI-binding and
#               multi-processing functionality only
# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
# Directives for this module
# -------------------------------------------------------------------------------
testMode = False  # Production version should be False

# -------------------------------------------------------------------------------
# Constants between the two processes, exchanged through the pipe
# -------------------------------------------------------------------------------
cmd_EndExecution = 19590  # Child->Main; No response expected
"""Command from child to main to end execution. No response expected."""
cmd_Idle = 19591  # Child->Main; Response = Buttons
"""Command from child to main to idle. Responds with the buttons pressed."""
cmd_LocateHW = 19592  # Child->Main; Response = True/False for success/failure
"""Command from child to main to locate hardware. Responds with True/False."""
cmd_Runoff = 19593  # Child->Main; Response = True
"""Command from child to main to start runoff. Responds with True."""
cmd_Tacx2Dongle = 19594  # Child->Main; Response = True
"""Command from child to main. Responds with true"""
cmd_StopButton = 19595  # Child->Main; Response = True
"""Command from child to main on pressing :guilabel:`Stop`. Responds with True."""
cmd_Settings = 19596  # Child->Main; Response = True
"""Command from child to main on pressing :guilabel:`Settings`. Responds with True."""

cmd_SetMessages = 19596  # Main->Child; No response expected
"""Command from main to child to set messages. No response expected"""
cmd_SetValues = 19597  # Main->Child; No response expected
"""Command from main to child to set values. No response expected"""
cmd_PedalStrokeAnalysis = 19598  # Main->Child; No response expected
"""Command from main to child to set Pedal Stroke Analysis. No response expected"""
cmd_SetLeds = 19599  # Main->Child; No response expected
"""Command from main to child to set LEDs. No response expected"""

# ------------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------------
clv = None
"""Command line variables in use."""
RestartApplication = None
"""Flag if application is to be restarted."""


# ==============================================================================
# The following functions are called from the GUI, Console or multi-processing
# parent process.
# The functions are used to test the multi-processing and/or GUI without
# being bothered by the actual FortiusAntBody/usbTrainer/antDongle functionality.
# ==============================================================================
def Settings(self, pRestartApplication: bool, pclv: cmd.CommandLineVariables):
    """Call FortiusAntBody.Settings and return its result.

    In test mode only write to console.

    Parameters
    ----------
    pRestartApplication : bool
        Application restart state to be set to :data:`RestartApplication`
    pclv : FortiusAntCommand.CommandLineVariables
        Command line variables to be set to :data:`clv`

    Returns
    -------
    rtn : bool
        True
    """
    global RestartApplication, clv
    RestartApplication = pRestartApplication
    clv = pclv

    if debug.on(debug.Function):
        logfile.Write("FortiusAnt.Settings(%s, %s)" % (pRestartApplication, pclv.debug))

    if testMode:
        print("")
        logfile.Console("Transfer settings")
        time.sleep(1)
        logfile.Console("Done")
        rtn = True
    else:
        rtn = FortiusAntBody.Settings(self, pRestartApplication, pclv)
    return rtn


def IdleFunction(self):
    """Call FortiusAntBody.IdleFunction and return its result.

    In test mode only write to console.
    """
    if testMode:
        print("i", end="")
        sys.stdout.flush()
        s = time.gmtime().tm_sec
        if s % 4 == 0:
            Buttons = usbTrainer.DownButton
        else:
            Buttons = 0
    else:
        Buttons = FortiusAntBody.IdleFunction(self)
    return Buttons


def LocateHW(self):
    """Call FortiusAntBody.LocateHW and return its result.

    In test mode only write to console.

    Returns
    -------
    rtn : bool
        True if hardware located
    """
    if testMode:
        print("")
        logfile.Console("Checking for HW")
        time.sleep(1)
        logfile.Console("Done")
        rtn = True
    else:
        rtn = FortiusAntBody.LocateHW(self)
    return rtn


def Runoff(self):
    """Call FortiusAntBody.Runoff and return its result.

    In test mode only write to console.

    Returns
    -------
    rtn : bool
        True if runoff successful
    """
    if testMode:
        print("")
        while self.RunningSwitch:
            logfile.Console("Doing runoff")
            self.SetMessages(
                "Doing runoff",
                datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S"),
                str(time.gmtime().tm_sec),
            )
            self.SetValues(0, 1, time.gmtime().tm_sec, 3, 4, 5, 6, 7, 8, 9, 10)
            time.sleep(1)
        logfile.Console("Runoff done")
        rtn = True
    else:
        rtn = FortiusAntBody.Runoff(self)
    return rtn


def Tacx2Dongle(self):
    """Call FortiusAntBody.Tacx2Dongle and return its result.

    In test mode only write to console.

    Returns
    -------
    rtn : bool
        True
    """
    if testMode:
        print("")
        while self.RunningSwitch:
            logfile.Console("Translate Tacx 2 Dongle")
            self.SetMessages(
                "Translate Tacx 2 Dongle",
                datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S"),
                str(time.gmtime().tm_sec),
            )
            self.SetValues(0, 1, time.gmtime().tm_sec, 3, 4, 5, 6, 7, 8, 9, 10)
            time.sleep(1)
        logfile.Console("Tacx2Dongle done")
        rtn = True
    else:
        rtn = FortiusAntBody.Tacx2Dongle(self)
    return rtn


# ==============================================================================
# Subclass FortiusAnt GUI with our directly called functions
# ------------------------------------------------------------------------------
# Called:       IdleFunction, LocateHW(), Runoff() and Tacx2Dongle() are called
#                    to provide the required functionality.
# ==============================================================================
if UseGui:

    class frmFortiusAnt(gui.frmFortiusAntGui):
        """This class extends the base GUI class with direct function calls."""

        def callSettings(self, RestartApplication, pclv):
            """Call FortiusAnt.Settings and return its result.

            Parameters
            ----------
            RestartApplication : bool
                Application restart state to be set
            pclv : FortiusAntCommand.CommandLineVariables
                Command line variables to be set

            Returns
            -------
            bool
                True
            """
            return Settings(self, RestartApplication, pclv)

        def callIdleFunction(self):
            """Call FortiusAnt.IdleFunction and act on its result.

            Returns
            -------
            bool
                True
            """
            Buttons = IdleFunction(self)
            # ----------------------------------------------------------------------
            # IdleFunction checks trainer for headunit button press
            # Since the GUI does not know the usbTrainer, we do this here
            # ----------------------------------------------------------------------
            if Buttons == usbTrainer.EnterButton:
                self.Navigate_Enter()
            elif Buttons == usbTrainer.DownButton:
                self.Navigate_Down()
            elif Buttons == usbTrainer.UpButton:
                self.Navigate_Up()
            elif Buttons == usbTrainer.CancelButton:
                self.Navigate_Back()
            else:
                pass
            return True

        def callLocateHW(self):
            """Call FortiusAnt.LocateHW and return its result.

            Returns
            -------
            bool
                True if hardware located
            """
            return LocateHW(self)

        def callRunoff(self):
            """Call FortiusAnt.LocateHW and return its result.

            Returns
            -------
            bool
                True if runoff successful
            """
            return Runoff(self)

        def callTacx2Dongle(self):
            """Call FortiusAnt.LocateHW and return its result.

            Returns
            -------
            bool
                True
            """
            return Tacx2Dongle(self)


# ==============================================================================
# Class to create a Console-GUI
# ------------------------------------------------------------------------------
# Functions:    Autostart() is similar to frmFortiusAntGui.autostart
#                   and executes all program-functionality
#               SetValues() and SetMessages() to show the progress on the console
#
# Called:       LocateHW() and Tacx2Dongle() are called to provide the required
#               functionality.
# ==============================================================================
class clsFortiusAntConsole:
    """This class provides a console GUI.

    Attributes
    ----------
    RunningSwitch : bool
    LastTime : float
    leds : string
    StatusLeds : list[bool]
    """

    def __init__(self):
        """Initialize console with sensible defaults."""
        self.RunningSwitch = False
        self.LastTime = 0
        self.leds = "- - -"  # Remember leds for SetValues() on console
        self.StatusLeds = [False, False, False, False, False]  # 5 True/False flags

    def Autostart(self):
        """Start the program automatically."""
        if LocateHW(self):
            self.RunningSwitch = True
            Tacx2Dongle(self)

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
    ):
        """Set values to display on the console once per second."""
        global clv
        # ----------------------------------------------------------------------
        # Console: Update current readings, once per second
        # ----------------------------------------------------------------------
        delta = time.time() - self.LastTime  # Delta time since previous
        if delta >= 1 and (not clv.gui or debug.on(debug.Application)):
            self.LastTime = time.time()  # Time in seconds

            if clv.imperial:
                s1 = fSpeed / mile
                s2 = "mph"
            else:
                s1 = fSpeed
                s2 = "km/h"

            if iTargetMode == mode_Power:
                sTarget = "%3.0fW" % iTargetPower
            elif iTargetMode == mode_Grade:
                sTarget = "%3.1f%%" % fTargetGrade
                if iTargetPower > 0:  # 2020-01-22
                    sTarget += (
                        "(%iW)" % iTargetPower
                    )  # Target power added for reference
            else:
                sTarget = "None"

            if clv.hrm == -1:
                h = ""
            else:
                h = "hr=%3.0f " % iHeartRate

            all = False
            self.leds = ""
            if all or True:  # Led 1 = Tacx trainer; USB, ANT or Simulated
                self.leds += "t" if self.StatusLeds[0] else "-"

            if all or OnRaspberry:  # Led 2 = on raspberry only
                self.leds += "s" if self.StatusLeds[1] else "-"

            if (
                all or clv.Tacx_Cadence
            ):  # Led 3 = Cadence sensor (black because backgroup is white)
                self.leds += "c" if self.StatusLeds[2] else "-"

            if all or clv.ble:  # Led 4 = Bluetooth CTP
                self.leds += "b" if self.StatusLeds[3] else "-"

            if all or clv.antDeviceID != -1:  # Led 5 = ANT CTP
                self.leds += "a" if self.StatusLeds[4] else "-"

            msg = "Target=%s %4.1f%s %sCurrent=%3.0fW Cad=%3.0f r=%4.0f %3s%% %s" % (
                sTarget,
                s1,
                s2,
                h,
                iPower,
                iRevs,
                iTacx,
                int(fReduction * 100),
                self.leds,
            )
            logfile.Console(msg)

    def SetMessages(self, Tacx=None, Dongle=None, HRM=None):
        """Set messages to display on the console."""
        if Tacx is not None:
            logfile.Console("Tacx   - " + Tacx)

        if Dongle is not None:
            logfile.Console("Dongle - " + Dongle)

        if HRM is not None:
            logfile.Console("AntHRM - " + HRM)

    def SetLeds(self, ANT=None, BLE=None, Cadence=None, Shutdown=None, Tacx=None):
        """Set LEDs to show state."""
        if self.leds != "":
            self.leds = (
                ""  # leds only change after that the are displayed in SetValues()
            )
            # print (ANT, BLE, Cadence, Shutdown, Tacx, self.StatusLeds)
            if Tacx is not None:
                self.StatusLeds[0] = not self.StatusLeds[0] if Tacx else False
            if Shutdown is not None:
                self.StatusLeds[1] = not self.StatusLeds[1] if Shutdown else False
            if Cadence is not None:
                self.StatusLeds[2] = not self.StatusLeds[2] if Cadence else False
            if BLE is not None:
                self.StatusLeds[3] = not self.StatusLeds[3] if BLE else False
            if ANT is not None:
                self.StatusLeds[4] = not self.StatusLeds[4] if ANT else False


# ==============================================================================
# Subclass FortiusAnt GUI with our multi-processing functions
# ------------------------------------------------------------------------------
# Description:  This class is functionally identical to frmFortiusAnt, with that
#               difference that the required functions are not called, but
#               requested through the multiprocessing pipe.
#
# Called:       cmd_IdleFunction, cmd_LocateHW, cmd_Runoff and cmd_Tacx2Dongle
#               are sent to the main process for execution and the response is
#               received.
#
# Functions:    For this purpose, GuiMessageToMain() is available.
# ==============================================================================
if UseGui:

    class frmFortiusAntChild(gui.frmFortiusAntGui):
        """This class extends the base GUI class with multiprocessing function calls.

        Parameters
        ----------
        conn : multiprocessing.connection.Connection
            GUI end of multiprocessing pipe
        pclv : FortiusAntCommand.CommandLineVariables
            Command line variables to be set
        """

        # --------------------------------------------------------------------------
        # gui_conn is the child-connection to the parent process
        # --------------------------------------------------------------------------
        def __init__(self, parent, conn, pclv):
            """Init.

            Parameters
            ------------
            conn : multiprocessing.connection.Connection
                GUI end of multiprocessing pipe
            pclv : FortiusAntCommand.CommandLineVariables
                Command line variables to be set
            """
            self.gui_conn = conn
            super(frmFortiusAntChild, self).__init__(parent, pclv)

        def GuiMessageToMain(self, command, wait=True, p1=None, p2=None):
            """Send a command to the main process.

            If a response command is received then it is carried out.

            Parameters
            ----------
            command : int
                This command is taken from a list of constants in this module. It
                should be refactored as an enum.
            wait : bool, default True
                Whether to wait for the command to return a response.
            p1 : object, default None
                Parameter 1 for command
            p2 : object, default None
                Parameter 2 for command

            Returns
            -------
            rtn : object
                The response from the command unless `wait` is `False` in which case
                we return `True`.
            """
            # ----------------------------------------------------------------------
            # Step 1. GUI sends a command to main
            # ----------------------------------------------------------------------
            if debug.on(debug.MultiProcessing) and not command == cmd_Idle:
                logfile.Write(
                    "mp-GuiMessageToMain(conn, %s, %s, %s, %s)"
                    % (command, wait, p1, p2)
                )
            self.gui_conn.send((command, p1, p2))

            rtn = True
            while wait:
                # ------------------------------------------------------------------
                # Check if requested command is ended
                # OR that information is received from Main
                # ------------------------------------------------------------------
                # Will be more efficient than self.gui_conn.poll() / sleep loop...
                # ------------------------------------------------------------------
                # Step 4. GUI receives the response (command, rtn)
                # ------------------------------------------------------------------
                msg = self.gui_conn.recv()
                cmd = msg[0]
                rtn = msg[1]
                if debug.on(debug.MultiProcessing) and not (
                    command == cmd_Idle and rtn == 0
                ):
                    logfile.Write(
                        "mp-GuiAnswerFromMain(conn) returns (%s, %s)" % (cmd, rtn)
                    )

                # ------------------------------------------------------------------
                # We wait for the response on the command
                # and in the meantime receive data to displayed
                #
                # cmd_StopButton is treated differently, since that command is sent
                # while we are waiting for the response on cmd_Runoff or cmd_Tacx2Dongle
                # we ignore the response here and cmd_StopButton does not start
                # wait-loop to avoid some sort of nesting or so.
                # ------------------------------------------------------------------
                if cmd == command:
                    break  # command is ready
                elif cmd == cmd_StopButton:
                    pass
                elif cmd == cmd_SetValues:
                    self.SetValues(
                        rtn[0],
                        rtn[1],
                        rtn[2],
                        rtn[3],
                        rtn[4],
                        rtn[5],
                        rtn[6],
                        rtn[7],
                        rtn[8],
                        rtn[9],
                        rtn[10],
                    )  # rtn is tuple
                elif cmd == cmd_SetMessages:
                    self.SetMessages(
                        rtn[0], rtn[1], rtn[2]
                    )  # rtn is (Tacx, Dongle, HRM) tuple
                elif cmd == cmd_PedalStrokeAnalysis:
                    self.PedalStrokeAnalysis(
                        rtn[0], rtn[1]
                    )  # rtn is (info, Cadence) tuple
                elif cmd == cmd_SetLeds:
                    self.SetLeds(
                        rtn[0], rtn[1], rtn[2], rtn[3], rtn[4]
                    )  # rtn is (ANT, BLE, Cadence, Shutdown, Tacx) tuple
                else:
                    logfile.Console(
                        "%s active but unknown response received (%s, %s); "
                        "the message is ignored." % (command, cmd, rtn)
                    )
                    break
            return rtn

        # --------------------------------------------------------------------------
        # Multiprocessing;
        #     a command is sent to the parent process and the function waits for
        #     a response.
        #     Idle/LocateHW: the only response expected is the answer from the function
        #     Runoff/Tacx2Dongle: the main process can also send information to be
        #     displayed!
        # --------------------------------------------------------------------------
        def callSettings(self, RestartApplication, pclv):
            """Call :func:`GuiMessageToMain` with :const:`cmd_Settings`.

            Parameters
            ----------
            RestartApplication : bool
                Application restart state to be set
            pclv : FortiusAntCommand.CommandLineVariables
                Command line variables to be set

            Returns
            -------
            rtn : object
                The value returned by :func:`GuiMessageToMain`
            """
            rtn = self.GuiMessageToMain(
                cmd_Settings, True, RestartApplication, self.clv
            )
            return rtn

        def callIdleFunction(self):
            """Call :func:`GuiMessageToMain` with :const:`cmd_Idle`.

            Returns
            -------
            bool
                True
            """
            Buttons = self.GuiMessageToMain(cmd_Idle)  # Send command and wait response
            # ----------------------------------------------------------------------
            # IdleFunction checks trainer for headunit button press
            # Since the GUI does not know the usbTrainer, we do this here
            # ----------------------------------------------------------------------
            if Buttons == usbTrainer.EnterButton:
                self.Navigate_Enter()
            elif Buttons == usbTrainer.DownButton:
                self.Navigate_Down()
            elif Buttons == usbTrainer.UpButton:
                self.Navigate_Up()
            elif Buttons == usbTrainer.CancelButton:
                self.Navigate_Back()
            else:
                pass
            return True

        def callLocateHW(self):
            """Call :func:`GuiMessageToMain` with :const:`cmd_LocateHW`.

            Returns
            -------
            rtn : object
                The value returned by :func:`GuiMessageToMain`
            """
            rtn = self.GuiMessageToMain(cmd_LocateHW)  # Send command and wait response
            return rtn

        def callRunoff(self):
            """Call :func:`GuiMessageToMain` with :const:`cmd_Runoff`.

            Returns
            -------
            rtn : object
                The value returned by :func:`GuiMessageToMain`
            """
            rtn = self.GuiMessageToMain(cmd_Runoff)
            return rtn

        def callTacx2Dongle(self):
            """Call :func:`GuiMessageToMain` with :const:`cmd_Tacx2Dongle`.

            Returns
            -------
            rtn : object
                The value returned by :func:`GuiMessageToMain`
            """
            rtn = self.GuiMessageToMain(cmd_Tacx2Dongle)
            return rtn

        def OnClick_btnStop(self, event=False):
            """:guilabel:`Stop` pressed."""
            gui.frmFortiusAntGui.OnClick_btnStop(self, event)
            self.GuiMessageToMain(cmd_StopButton, False)

        def OnClose(self, event):
            """Frame closed."""
            if self.RunningSwitch is True:  # Thread is running
                self.GuiMessageToMain(cmd_StopButton, False)
            gui.frmFortiusAntGui.OnClose(self, event)


# ==============================================================================
# Class to create a parent-process
# ------------------------------------------------------------------------------
# Description:  This class creates the parent, which receives commands from the
#               GUI child process, calls the required function and returns the
#               result.
#
# Called:       cmd_IdleFunction, cmd_LocateHW, cmd_Runoff and cmd_Tacx2Dongle
#               are called and the response is sent to the child process.
#
# Functions:    For this purpose, MainCommandFromGui() and MainRespondToGUI()
#               are available.
#
#               SetMessages() and SetValues() are called by the functions and
#               send the data to be displayed to the child, not awaiting an
#               answer.
#
#               RunoffThread() and Tacx2DongleThread() act as function to create
#               a thread to execute the functions, whilst not blocking the
#               the process to receive messages from the GUI client, which can
#               order to stop.
# ==============================================================================
class clsFortiusAntParent:
    """Main process when multiprocessing is used.

    Attributes
    ----------
    RunningSwitch : bool
        Whether the program is running
    app_conn : multiprocessing.connection.Connection
    LastTime : float
    PreviousMessages : tuple[bool]
    """

    def __init__(self, app_conn):
        """Initialize parent with sensible defaults."""
        self.RunningSwitch = False
        self.app_conn = app_conn
        self.LastTime = 0
        self.PreviousMessages = None

    def MainCommandFromGui(self):
        """Receive command from child process.

        Returns
        -------
        tuple
        """
        msg = self.app_conn.recv()
        command = msg[0]
        p1 = msg[1]
        p2 = msg[2]
        if debug.on(debug.MultiProcessing) and not command == cmd_Idle:
            logfile.Write(
                "mp-MainCommandFromGui() returns (%s, %s, %s)" % (command, p1, p2)
            )
        return command, p1, p2

    def MainRespondToGUI(self, command, rtn):
        """Send command to child process.

        Parameters
        ----------
        command : int
        rtn
        """
        if debug.on(debug.MultiProcessing) and not (command == cmd_Idle and rtn == 0):
            logfile.Write("mp-MainRespondToGUI(%s, %s)" % (command, rtn))
        self.app_conn.send((command, rtn))

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
    ):
        """Set values to display on the GUI once per second."""
        delta = time.time() - self.LastTime  # Delta time since previous call
        if delta >= 1:  # Do not send faster than once per second
            self.LastTime = time.time()  # Time in seconds
            if debug.on(debug.MultiProcessing):
                logfile.Write(
                    "mp-MainDataToGUI(%s, (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s))"
                    % (
                        cmd_SetValues,
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
                )
            self.app_conn.send(
                (
                    cmd_SetValues,
                    (
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
                    ),
                )
            )

    def SetMessages(self, Tacx=None, Dongle=None, HRM=None):
        """Set messages to display on the GUI."""
        newMessages = (Tacx, Dongle, HRM)
        if newMessages != self.PreviousMessages:  # Send immediatly if changed
            self.PreviousMessages = newMessages
            if debug.on(debug.MultiProcessing):
                logfile.Write(
                    "mp-MainDataToGUI(%s, (%s, %s, %s))"
                    % (cmd_SetMessages, Tacx, Dongle, HRM)
                )
            self.app_conn.send(
                (cmd_SetMessages, (Tacx, Dongle, HRM))
            )  # x. Main sends messages to GUI; no response expected

    def PedalStrokeAnalysis(self, info, Cadence):
        """Display pedal stroke analysis."""
        if debug.on(debug.MultiProcessing):
            logfile.Write(
                "mp-MainDataToGUI(%s, (info, %s))" % (cmd_PedalStrokeAnalysis, Cadence)
            )
        self.app_conn.send(
            (cmd_PedalStrokeAnalysis, (info, Cadence))
        )  # x. Main sends messages to GUI; no response expected

    def SetLeds(self, ANT=None, BLE=None, Cadence=None, Shutdown=None, Tacx=None):
        """Set LEDs to display on the GUI."""
        if debug.on(debug.MultiProcessing):
            logfile.Write(
                "mp-MainDataToGUI(%s, (%s, %s, %s, %d, %s))"
                % (cmd_SetLeds, Tacx, Shutdown, Cadence, BLE, ANT)
            )
        self.app_conn.send(
            (cmd_SetLeds, (ANT, BLE, Cadence, Shutdown, Tacx))
        )  # x. Main sends messages to GUI; no response expected

    def RunoffThread(self):
        """Call FortiusAnt.Runoff."""
        rtn = Runoff(self)
        self.MainRespondToGUI(cmd_Runoff, rtn)

    def Tacx2DongleThread(self):
        """Call FortiusAnt.Tacx2Dongle."""
        rtn = Tacx2Dongle(self)
        self.MainRespondToGUI(cmd_Tacx2Dongle, rtn)

    def ListenToChild(self):
        """Poll child process."""
        while True:
            gui_command, gui_p1, gui_p2 = self.MainCommandFromGui()

            if gui_command == cmd_EndExecution:
                break

            elif gui_command == cmd_Settings:
                rtn = Settings(self, gui_p1, gui_p2)
                self.MainRespondToGUI(cmd_Settings, rtn)

            elif gui_command == cmd_Idle:
                rtn = IdleFunction(self)
                self.MainRespondToGUI(cmd_Idle, rtn)

            elif gui_command == cmd_LocateHW:
                rtn = LocateHW(self)
                self.MainRespondToGUI(cmd_LocateHW, rtn)

            elif gui_command == cmd_Runoff:
                self.RunningSwitch = True
                thread = threading.Thread(target=self.RunoffThread)
                thread.start()

            elif gui_command == cmd_Tacx2Dongle:
                self.RunningSwitch = True
                thread = threading.Thread(target=self.Tacx2DongleThread)
                thread.start()

            elif gui_command == cmd_StopButton:
                if testMode:
                    print("")
                    logfile.Console("Stop button pressed")
                self.RunningSwitch = False
                self.MainRespondToGUI(cmd_StopButton, True)

            else:
                logfile.Console("Unexpected command from GUI: %s" % gui_command)
                rtn = False


# ------------------------------------------------------------------------------
# F o r t i u s A n t C h i l d
# ------------------------------------------------------------------------------
# Input:        clv     Command line variables
#               conn    the child-side of the multiprocessing pipe
#
# Description:  Here the user-interface is created.
#               The user-interface will call the callback functions as defined
#               above.
#
# Output:       none
# ------------------------------------------------------------------------------
def FortiusAntChild(clv, conn):
    """Initialize the child process.

    This function creates the GUI in a child process as an instance of
    :class:`~frmFortiusAntChild` and also creates a
    logfile for the GUI.

    Parameters
    ----------
    clv: FortiusAntCommand.CommandLineVariables
        Command line variables to be set
    conn: multiprocessing.connection.Connection
        GUI end of multiprocessing pipe
    """
    # --------------------------------------------------------------------------
    # Initialize the child process, create our own logfile
    # --------------------------------------------------------------------------
    debug.activate(clv.debug)
    if debug.on(debug.Any):
        logfile.Open("FortiusAntGUI")
        logfile.Console("FortiusAnt GUI started in child-process")

    # --------------------------------------------------------------------------
    # Start the user-interface
    # --------------------------------------------------------------------------
    app = wx.App(0)
    frame = frmFortiusAntChild(None, conn, clv)
    app.SetTopWindow(frame)
    frame.Show()
    if clv.autostart:
        frame.Autostart()
    app.MainLoop()

    # --------------------------------------------------------------------------
    # Signal parent that we're done
    # --------------------------------------------------------------------------
    frame.GuiMessageToMain(cmd_EndExecution, False)
    if debug.on(debug.Any):
        logfile.Console("FortiusAnt GUI ended")


# ==============================================================================
# Main program
# ==============================================================================
def mainProgram():
    """Run the application."""
    global RestartApplication, clv

    # --------------------------------------------------------------------------
    # Initialize
    # --------------------------------------------------------------------------
    debug.deactivate()
    if not RestartApplication:
        clv = cmd.CommandLineVariables()
    debug.activate(clv.debug)
    FortiusAntBody.Initialize(clv)

    if debug.on(debug.Any):
        logfile.Open()
        logfile.Console("FortiusANT started")
        logfile.Write("    Restart=%s debug=%s" % (RestartApplication, clv.debug))
        clv.print()
        logfile.Console("------------------")

    RestartApplication = False

    # -------------------------------------------------------------------------------
    # Component info
    # -------------------------------------------------------------------------------
    if debug.on(debug.Any):
        # ----------------------------------------------------------------------
        if getattr(sys, "frozen", False):
            logfile.Write("Windows executable started")
        else:
            logfile.Write("Python version started")
        # ----------------------------------------------------------------------
        logfile.Write("Version info for the components")
        logfile.Write(githubWindowTitle())
        s = " %20s = %s"
        logfile.Write(s % ("FortiusAnt", __version__))
        logfile.Write(s % ("antCTRL", antCTRL.__version__))
        logfile.Write(s % ("antDongle", ant.__version__))
        logfile.Write(s % ("antFE", fe.__version__))
        logfile.Write(s % ("antHRM", hrm.__version__))
        logfile.Write(s % ("antPWR", pwr.__version__))
        logfile.Write(s % ("antSCS", scs.__version__))
        logfile.Write(s % ("bleBless", bleBless.__version__))
        logfile.Write(s % ("bleBlessClass", bleBlessClass.__version__))
        logfile.Write(s % ("bleDongle", bleDongle.__version__))
        logfile.Write(s % ("constants", constants.__version__))
        logfile.Write(s % ("debug", debug.__version__))
        logfile.Write(s % ("FortiusAntBody", FortiusAntBody.__version__))
        logfile.Write(s % ("FortiusAntCommand", cmd.__version__))
        if UseGui:
            logfile.Write(s % ("FortiusAntGui", gui.__version__))
        logfile.Write(s % ("logfile", logfile.__version__))
        if UseGui:
            logfile.Write(s % ("RadarGraph", RadarGraph.__version__))
        logfile.Write(s % ("raspberry", raspberry.__version__))
        logfile.Write(s % ("settings", settings.__version__))
        logfile.Write(s % ("structConstants", sc.__version__))
        logfile.Write(s % ("TCXexport", TCXexport.__version__))
        logfile.Write(s % ("usbTrainer", usbTrainer.__version__))

        logfile.Write(s % ("argparse", argparse.__version__))
        logfile.Write(s % ("numpy", numpy.__version__))
        logfile.Write(s % ("os", os.name))
        if os.name == "nt":
            v = sys.getwindowsversion()
            logfile.Write((s + ".%s") % ("windows", v.major, v.minor))
        logfile.Write(s % ("pickle", pickle.format_version))
        logfile.Write(s % ("platform", platform.__version__))
        logfile.Write(s % ("glob", glob.__version__))
        logfile.Write(s % ("random", random.__version__))
        logfile.Write(s % ("sys (python)", sys.version))
        logfile.Write(s % ("struct", struct.__version__))
        logfile.Write(s % ("threading", threading.__version__))
        logfile.Write(s % ("time", time.__version__))
        logfile.Write(s % ("usb", usb.__version__))
        if UseGui:
            logfile.Write(s % ("wx", wx.__version__))

        logfile.Write("FortiusANT code flags")
        logfile.Write(s % ("UseMultiProcessing", UseMultiProcessing))
        logfile.Write(s % ("UseGui", UseGui))
        logfile.Write(s % ("UseBluetooth", UseBluetooth))
        logfile.Write("------------------")

    # -------------------------------------------------------------------------------
    # Modify ANT deviceNumbers if requested
    # -------------------------------------------------------------------------------
    if clv.DeviceNumberBase:
        ant.DeviceNumberBase(clv.DeviceNumberBase)
    if clv.SettingsOnly:
        app = wx.App(0)

        settings.OpenDialog(None, None, clv)
    elif not clv.gui:
        # --------------------------------------------------------------------------
        # Console only, no multiprocessing required to separate GUI
        # --------------------------------------------------------------------------
        Console = clsFortiusAntConsole()
        Console.Autostart()

    elif not UseMultiProcessing:
        # --------------------------------------------------------------------------
        # No multiprocessing wanted, start GUI immediatly
        # --------------------------------------------------------------------------
        clv.PedalStrokeAnalysis = False
        app = wx.App(0)
        frame = frmFortiusAnt(None, clv)
        app.SetTopWindow(frame)
        frame.Show()
        if clv.autostart:
            frame.Autostart()
        app.MainLoop()

    else:
        # --------------------------------------------------------------------------
        # Multiprocessing wanted, start GUI in it's own process
        # --------------------------------------------------------------------------
        # https://docs.python.org/3/library/multiprocessing.html
        # Create queue and sub-process
        # --------------------------------------------------------------------------
        app_conn, gui_conn = multiprocessing.Pipe(True)
        pChild = multiprocessing.Process(target=FortiusAntChild, args=(clv, gui_conn))
        pChild.start()

        # --------------------------------------------------------------------------
        # Poll child-process untill done
        # --------------------------------------------------------------------------
        parent = clsFortiusAntParent(app_conn)  # The child process has the GUI
        parent.ListenToChild()

        # --------------------------------------------------------------------------
        # Wait for child-process to complete
        # --------------------------------------------------------------------------
        pChild.join()

    # ------------------------------------------------------------------------------
    # We're done
    # ------------------------------------------------------------------------------
    FortiusAntBody.Terminate()

    if debug.on(debug.Any):
        logfile.Console("FortiusAnt ended")
        logfile.Close()


# -----------------------------------------------------------------------------------
# Main program; when restart is required due to new parameters we will loop
# -----------------------------------------------------------------------------------
def main():
    """Loop :meth:`mainProgram` unless :data:`RestartApplication` is False on return."""
    multiprocessing.freeze_support()
    global RestartApplication, clv

    RestartApplication = False
    while True:
        mainProgram()
        if not RestartApplication:
            break

    # ------------------------------------------------------------------------------
    # If so requested, shutdown Raspberry pi
    # ------------------------------------------------------------------------------
    if OnRaspberry:
        raspberry.ShutdownIfRequested()


if __name__ == "__main__":
    main()
