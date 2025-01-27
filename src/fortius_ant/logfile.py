# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2022-12-28"
# 2022-12-28    PythonLogger.info() error in Write() avoided by disabling.
# 2022-04-07    Comment typo corrected
# 2022-03-28    Traceback() added
# 2022-03-24    fLogfile is set to None, so that modules can check it
#               Print() given a new implementation (since PythonLogging)
# 2022-03-16    python.logging implemented, using PythonLogging=True
#               The "Old" logging remains present, just in case...
# 2022-02-22    HexSpace() now also supports bytearray
# 2020-11-25    Small textual modifications (time->Time)
#               .utcnow() replaced by .now()
# 2020-11-19    json PedalEcho added and time-format made JAVA-style
# 2020-11-13    json logfile added
# 2020-04-28    Logfile flushed as well
# 2020-04-17    Open() provides suffix option
# 2020-04-16    Console() introduced
# 2020-04-15    HexSpace() supports int
# 2020-04-13    Print() added
# 2020-03-24    Resolve crash when non-bytes input to HexSpace()
# 2020-02-12    Write() flushes stdout
#               No error when fLogfile not opened (sometimes raised w/o reason)
# 2020-02-02    Open() has optional parameter for logfile-prefix
# -------------------------------------------------------------------------------
import binascii
import json
import os
import sys
import time
import traceback
from datetime import datetime

import fortius_ant.debug as debug
from fortius_ant.constants import UsePythonLogging

global LogfileCreated
LogfileCreated = False

if UsePythonLogging:
    import logging


# -------------------------------------------------------------------------------
# c l s L o g f i l e J s o n
# -------------------------------------------------------------------------------
# Create()  create JSON logfile, with same filename as logfile
# Write()   add info
# Close()   close JSON logfile
# -------------------------------------------------------------------------------
class clsLogfileJson:
    def __init__(self, filename):
        self.first = True  # Comma preceeds next record (not the 1st)
        self.jsonFile = None  # Not opened yet
        self.NrTrackpoints = None  # To detect new trackpoint
        self.PedalCycle = 0  # 0 or 50 during one pedal cycle
        self.LastPedalEcho = 0  # Previous pedalecho from TacxTrainer
        # Create JSON file
        self.jsonFile = open(filename, "w+")
        self.jsonFile.write("[\n")

    def Write(self, QuarterSecond, TacxTrainer, tcx, HeartRate):
        if self.first:
            self.first = False
        else:
            self.jsonFile.write(",")

        # -----------------------------------------------------------------------
        # The json file is intended to analyze the data
        # It is interesting to see what measurements are done per pedal rotation
        # PedalCycle is set to 50, so it can be displayed on the speed-scale
        #
        # PedalCycle changes when PedalEcho goes from 0 --> 1
        # -----------------------------------------------------------------------
        if self.LastPedalEcho == 0 and TacxTrainer.PedalEcho == 1:
            if self.PedalCycle == 0:
                self.PedalCycle = 50
            else:
                self.PedalCycle = 0
        self.LastPedalEcho = TacxTrainer.PedalEcho
        # -----------------------------------------------------------------------
        # Add all usefull variables
        # -----------------------------------------------------------------------
        # datetime.now() is not understood by Excel.
        # "2012-04-23T18:25:43.511Z" is not understood either (altough 'standard')
        # time.time() / (24 * 3600) is excel-style, but offset is different
        #       We add 25569 so that Excel understands it.
        #       It' does not account for summer/wintertime...
        # -----------------------------------------------------------------------
        # = '{"Time"                : "%s",' % datetime.now()                       + \
        # = '{"Time"                : "%s",' % datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ") + \
        s = (
            '{"Time"                :  %s ,' % ((time.time() / (24 * 3600)) + 25569)
            + ' "QuarterSecond"       : "%s",' % QuarterSecond
            + ' "HeartRate"           :  %s ,' % HeartRate
            + ' "Target"              : "|" ,'
            + ' "TargetMode"          :  %s ,' % TacxTrainer.TargetMode
            + ' "TargetGrade"         :  %s ,' % TacxTrainer.TargetGrade
            + ' "TargetPower"         :  %s ,' % TacxTrainer.TargetPower
            + ' "TargetResistance"    :  %s ,' % TacxTrainer.TargetResistance
            + ' "TacxTrainer"         : "|" ,'
            + ' "Cadence"             :  %s ,' % TacxTrainer.Cadence
            + ' "CurrentPower"        :  %s ,' % TacxTrainer.CurrentPower
            + ' "CurrentResistance"   :  %s ,' % TacxTrainer.CurrentResistance
            + ' "SpeedKmh"            :  %s ,' % TacxTrainer.SpeedKmh
            + ' "VirtualSpeedKmh"     :  %s ,' % TacxTrainer.VirtualSpeedKmh
            + ' "CalculatedSpeedKmh"  :  %s ,' % TacxTrainer.CalculatedSpeedKmh
            + ' "PedalEcho"           :  %s ,' % TacxTrainer.PedalEcho
            + ' "PedalCycle"          :  %s ,' % self.PedalCycle
        )

        # -----------------------------------------------------------------------
        # TCX only when active
        # -----------------------------------------------------------------------
        if tcx != None and tcx.NrTrackpoints != self.NrTrackpoints:
            self.NrTrackpoints = tcx.NrTrackpoints
            s += (
                ' "TCX"                 : "|" ,'
                + ' "NrTrackpoints"       :  %s ,' % tcx.NrTrackpoints
                + ' "TotalDistance"       :  %s ,' % tcx.TotalDistance
                + ' "TrackpointTime"      : "%s",' % tcx.TrackpointTime
                + ' "ElapsedTime"         :  %s ,' % tcx.ElapsedTime
                + ' "Distance"            :  %s ,' % tcx.Distance
                + ' "TrackpointDistance"  :  %s ,' % tcx.TrackpointDistance
                + ' "TrackpointAltitude"  :  %s ,' % tcx.TrackpointAltitude
                + ' "TrackpointHeartRate" :  %s ,' % tcx.TrackpointHeartRate
                + ' "TrackpointCadence"   :  %s ,' % tcx.TrackpointCadence
                + ' "TrackpointCurrentPower":%s ,' % tcx.TrackpointCurrentPower
                + ' "TrackpointSpeedKmh"  :  %s ,' % tcx.TrackpointSpeedKmh
            )

        s += ' "End"                 : "|" ' + "}\n"
        self.jsonFile.write(s.replace(" ", ""))

    def Close(self):
        self.jsonFile.write("]\n")
        self.jsonFile.close


# -------------------------------------------------------------------------------
# module l o g f i l e
# -------------------------------------------------------------------------------
# functions:    Open, Write(), Close
#
# description:  One central logfile to trace program-execution
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# O p e n
# -------------------------------------------------------------------------------
def Open(prefix="FortiusAnt", suffix=""):
    global fLogfile, LogfileJson, LogfileCreated, UsePythonLogging, PythonLogger

    fLogfile = None
    if debug.on():
        # -----------------------------------------------------------------------
        # Create filename for logging
        # -----------------------------------------------------------------------
        if len(suffix) > 0 and suffix[0] != ".":
            suffix = "." + suffix
        filename = (
            prefix
            + "."
            + datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            + suffix
            + ".log"
        )

        # -----------------------------------------------------------------------
        # Open the file
        # - either using the logging module
        # - or creating the file ourselves (then other modules will not log)
        # -----------------------------------------------------------------------
        l = 0
        if UsePythonLogging:
            # If BLE-logging is requested, then logging is set to DEBUG
            # because bless and bleak use logging.
            if debug.on(debug.Ble):
                l = logging.DEBUG  # If BLE logging, DEBUG is default

            # If multiple values are defined, the one that generates most output takes precedence
            if debug.on(debug.logging_CRITICAL):
                l = logging.CRITICAL
            if debug.on(debug.logging_ERROR):
                l = logging.ERROR
            if debug.on(debug.logging_WARNING):
                l = logging.WARNING
            if debug.on(debug.logging_INFO):
                l = logging.INFO
            if debug.on(debug.logging_DEBUG):
                l = logging.DEBUG

            # So  -db       implies DEBUG
            # and -dbC      logs CRITICAL only
            # and -dbCW     logs WARNING, ERROR and CRITICAL

        # -----------------------------------------------------------------------
        # logging_CRITICAL... is for the OTHER modules, since we have our own
        # flags. If no such logging is requested, use our own method.
        # Alternative would be to define another logging_level...
        # -----------------------------------------------------------------------
        if UsePythonLogging and l:
            # -------------------------------------------------------------------
            # Open logging file
            # Create PythonLogger for FortiusAnt logging
            # -------------------------------------------------------------------
            logging.basicConfig(
                filename=filename,
                level=l,
                format="%(asctime)s: [%(name)s, %(levelname)s] %(message)s",
            )
            # Note that   datefmt='%Y-%m-%d %H:%M:%S'   has no milliseconds!
            PythonLogger = logging.getLogger("FortiusAnt")  # Tag as our message
            PythonLogger.setLevel(logging.DEBUG)  # No filtering
            if False:
                # ---------------------------------------------------------------
                # The idea is that the fortiusant-logging is different from
                # the 'standard' logging, but it's not (yet) succesful...
                #
                # Standard:   format='%(asctime)s: [%(name)s %(levelname)s] %(message)s'
                # FortiusAnt: format='%(message)s' (since the time is already there)
                # ---------------------------------------------------------------

                # create NULL handler to format our messages
                h = logging.NullHandler()
                h.setLevel(l)

                # create formatter
                # f = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                f = logging.Formatter("===> %(message)s")  ##  Dit lukt nog niet erg

                # add formatter to handler
                h.setFormatter(f)

                # add handler to logger
                PythonLogger.addHandler(h)

        else:
            UsePythonLogging = False  # No python logging, use our own format
            fLogfile = open(filename, "w+")

        LogfileCreated = True

        # -----------------------------------------------------------------------
        # If requested, create the json log
        # -----------------------------------------------------------------------
        if debug.on(debug.LogfileJson) and prefix == "FortiusAnt":
            LogfileJson = clsLogfileJson(filename.replace(".log", ".json"))


def IsOpen():
    return LogfileCreated


# -------------------------------------------------------------------------------
# P r i n t   t o   l o g f i l e
# -------------------------------------------------------------------------------
# https://stackoverflow.com/questions/14630288/unicodeencodeerror-charmap-codec-cant-encode-character-maps-to-undefined
# -------------------------------------------------------------------------------
def Print(*objects, sep=" ", end="\n"):
    global fLogfile, PythonLogger

    if UsePythonLogging:
        if False:  # Disabled because sometimes fails, on encoding error.
            s = ""
            for obj in objects:
                if s != "":
                    s += " "  # Add space between each object
                s += str(obj)  # Add object as string
            Write(s)  # Write all objects on one line

    else:
        if IsOpen():
            enc = fLogfile.encoding
            if enc == "UTF-8":
                print(*objects, sep=sep, end=end, file=fLogfile)
            else:
                f = (
                    lambda obj: str(obj)
                    .encode(enc, errors="backslashreplace")
                    .decode(enc)
                )
                print(*map(f, objects), sep=sep, end=end, file=fLogfile)


# -------------------------------------------------------------------------------
# W r i t e   and   C o n s o l e
#
# Refer https://strftime.org/ for format codes
# hh:mm:ss,ddd is 12 characters (%f for microseconds provides 6 digits)
# -------------------------------------------------------------------------------
# In the beginning, Write() replaced print() AND writes all printed messages to
# logfile. Then Write() was used to fill the logfile, taking for granted that
# all written messages are also printed on the console.
#
# Therefore Console() is introduced: prints AND writes
#           Write()   does NOT print to console anymore, unless requested.
# -------------------------------------------------------------------------------
def Console(logText):
    Write(logText, True)


def Write(logText, console=False):
    global fLogfile, PythonLogger

    logTextDT = datetime.now().strftime("%H:%M:%S,%f")[0:12] + ": " + logText
    if console:
        print(logTextDT)
    sys.stdout.flush()

    if debug.on():
        if not LogfileCreated:
            Open()  # if module not initiated, open implicitly

    try:
        if debug.on():
            if UsePythonLogging:
                PythonLogger.info(logText)  # Format is defined in PythonLogger
            else:
                fLogfile.write(logTextDT + "\n")  # \r\n
                fLogfile.flush()
    except:
        #       print ("logfile.Write (" + logText + ") called, but logfile is not opened.")
        pass


def WriteJson(QuarterSecond, TacxTrainer, tcx, HeartRate):
    if debug.on(debug.LogfileJson):
        LogfileJson.Write(QuarterSecond, TacxTrainer, tcx, HeartRate)


# -------------------------------------------------------------------------------
# T r a c e b a c k
# -------------------------------------------------------------------------------
# input         exception
#
# description   Print stack trace to logfile with provided exception
#
#               Example:
#                   try:
#                       ....
#                   except Exception as e:
#                       Traceback(e)
#
#               Note: line could be processed to remove \n so that one logrecord
#                   is written instead of multiples; but this is more readable
#                   I do not assume there will be automated interpretation of
#                   the logfile and then we can still change...
#
# output        stacktrace added to logfile through Write()
# -------------------------------------------------------------------------------
def Traceback(exception):
    for line in traceback.format_exception(
        exception.__class__, exception, exception.__traceback__
    ):
        Write(line)


# -------------------------------------------------------------------------------
# C l o s e
# -------------------------------------------------------------------------------
def Close():
    try:
        if debug.on():
            if UsePythonLogging:
                pass
            else:
                fLogfile.close

            if debug.on(debug.LogfileJson):
                LogfileJson.Close()

    except:
        pass


# -------------------------------------------------------------------------------
# HexSpace
# -------------------------------------------------------------------------------
# input         buffer;         e.g. "\01\02\03\04"
#
# description   convert buffer into readable string
#
# returns       string          e.g. "01 02 03 04"
# -------------------------------------------------------------------------------
def HexSpace(info):
    if type(info) in (bytes, bytearray):
        s = binascii.hexlify(info).decode("utf-8")
        rtn = '"'
        for i in range(0, len(s)):
            if i > 0 and i % 2 == 0:
                rtn += " "
            rtn += s[i]
        rtn += '"'
    elif type(info) is int:
        rtn = '"' + hex(info)[2:].zfill(2) + '"'
    else:
        rtn = '"' + str(info) + '"'
    return rtn


def HexSpaceL(list):
    rtn = "["
    comma = ""
    for l in list:
        rtn += comma + HexSpace(l)
        comma = ", "
    rtn += "]"
    return rtn


# -------------------------------------------------------------------------------
# Main program to test the previous functions
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    global LogfileJson
    print("Test of wdLogfile")
    Write("This logrecord cannot be written")  # Not open yet
    debug.activate()
    Open()  # This is normal
    Write("This is a logrecord")  # ..

    Print("This is a logrecord by Print()")  # ..
    Print("functions:", Console, Write, Print)  # ..

    print("json tests")
    LogfileJson.Close()

    Close()  # ..
    print("Test of wdLogfile done")
    print(HexSpace(binascii.unhexlify("203031")))
    print(HexSpace("False"))
    print(HexSpace(False))


else:
    pass  # We're included so do not take action!
