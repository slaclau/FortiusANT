"""Provide interface for communicating as ANT+ speed and cadence sensor."""
# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2023-04-15"
# 2023-04-15    Improve flake8 compliance
# 2020-12-27    Rollover more according specification
# 2020-06-16    Modified: device-by-zero due to zero Cadence/SpeedKmh
# 2020-06-09    First version, based upon antHRM.py
# -------------------------------------------------------------------------------
import time

import fortius_ant.antDongle as ant
from fortius_ant import logfile

PedalEchoPreviousCount = None  # There is no previous
CadenceEventTime = None  # Initiate the even variables
CadenceEventCount = None
SpeedEventTime = None
SpeedEventCount = None


def Initialize():
    """Initialize interface."""
    global PedalEchoPreviousCount, CadenceEventTime, CadenceEventCount
    global SpeedEventTime, SpeedEventCount
    PedalEchoPreviousCount = 0  # There is no previous
    CadenceEventTime = 0  # Initiate the even variables
    CadenceEventCount = 0
    SpeedEventTime = 0
    SpeedEventCount = 0


def BroadcastMessage(_PedalEchoTime, PedalEchoCount, SpeedKmh, Cadence):
    """Create next message to be sent as speed and cadence sensor.

    Parameters
    ----------
    PedalEchoCount : int
    SpeedKmh : int
    Cadence : int

    Returns
    -------
    rtn : bytes
        Message to be sent
    """
    global PedalEchoPreviousCount, CadenceEventTime, CadenceEventCount
    global SpeedEventTime, SpeedEventCount

    # -------------------------------------------------------------------------
    # If pedal passed the magnet, calculate new values
    # Otherwise repeat previous message
    # Avoid devide-by-zero!
    # -------------------------------------------------------------------------
    if PedalEchoCount != PedalEchoPreviousCount and Cadence > 0 and SpeedKmh > 0:
        # ---------------------------------------------------------------------
        # Cadence variables
        # Based upon the number of pedal-cycles that are done and the given
        # cadence, calculate the elapsed time.
        # _PedalEchoTime is not used, because that give rounding errors and
        # an instable reading.
        # ---------------------------------------------------------------------
        PedalCycles = PedalEchoCount - PedalEchoPreviousCount
        ElapsedTime = (
            PedalCycles / Cadence * 60
        )  # count / count/min * seconds/min = seconds
        CadenceEventTime += ElapsedTime * 1024  # 1/1024 seconds
        CadenceEventCount += PedalCycles

        # ---------------------------------------------------------------------
        # Speed variables
        # First calculate how many wheel-cycles can be done
        # Then (based upon rounded #of cycles) calculate the elapsed time
        # ---------------------------------------------------------------------
        Circumference = 2.096  # Note: SimulANT has 2.070 as default
        WheelCadence = (
            SpeedKmh / 3.6 / Circumference
        )  # km/hr / kseconds/hr / meters  = cycles/s
        WheelCycles = round(
            ElapsedTime * WheelCadence, 0
        )  # seconds * /s                  = cycles

        ElapsedTime = WheelCycles / SpeedKmh * 3.6 * Circumference
        SpeedEventTime += ElapsedTime * 1024
        SpeedEventCount += WheelCycles

    # -------------------------------------------------------------------------
    # Rollover after 0xffff
    # -------------------------------------------------------------------------
    CadenceEventTime = int(CadenceEventTime) & 0xFFFF  # roll-over at 65535 = 64 seconds
    CadenceEventCount = int(CadenceEventCount) & 0xFFFF  # roll-over at 65535
    SpeedEventTime = int(SpeedEventTime) & 0xFFFF  # roll-over at 65535 = 64 seconds
    SpeedEventCount = int(SpeedEventCount) & 0xFFFF  # roll-over at 65535

    # -------------------------------------------------------------------------
    # Prepare for next event
    # -------------------------------------------------------------------------
    PedalEchoPreviousCount = PedalEchoCount

    # -------------------------------------------------------------------------
    # Compose message
    # -------------------------------------------------------------------------
    info = ant.msgPage_SCS(
        ant.channel_SCS,
        CadenceEventTime,
        CadenceEventCount,
        SpeedEventTime,
        SpeedEventCount,
    )
    rtn = ant.ComposeMessage(ant.msgID_BroadcastData, info)

    # -------------------------------------------------------------------------
    # Return message to be sent
    # -------------------------------------------------------------------------
    return rtn


# -------------------------------------------------------------------------------
# Main program for module test
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    Initialize()
    time.sleep(1)
    scsdata = BroadcastMessage(0, 1, 45.6, 123)
    print(logfile.HexSpace(scsdata))
