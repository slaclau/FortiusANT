"""Provide interface for communicating as ANT+ heart rate monitor."""
# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2023-04-15"
# 2023-04-15    Improve flake8 compliance
# 2020-12-27    Interleave like antPWR.py
# 2020-05-07    devAntDongle not needed, not used
# 2020-05-07    pylint error free
# 2020-02-18    First version, split-off from FortiusAnt.py
# -------------------------------------------------------------------------------
import time

import fortius_ant.antDongle as ant

Interleave = None
HeartBeatCounter = None
HeartBeatEventTime = None
HeartBeatTime = None
PageChangeToggle = None


def Initialize():
    """Initialize interface."""
    global Interleave, HeartBeatCounter, HeartBeatEventTime
    global HeartBeatTime, PageChangeToggle
    Interleave = 0
    HeartBeatCounter = 0
    HeartBeatEventTime = 0
    HeartBeatTime = 0
    PageChangeToggle = 0


def BroadcastHeartrateMessage(HeartRate):
    """Create next message to be sent.

    Three types of page are sent here:

    * Page 0 - Default or Unknown Data
        This page contains the heart rate
    * Page 2 - Manufacturer Information
    * Page 3 - Product Information

    Parameters
    ----------
    HeartRate : int

    Returns
    -------
    rtn : bytes
        Message to be sent
    """
    global Interleave, HeartBeatCounter, HeartBeatEventTime
    global HeartBeatTime, PageChangeToggle
    if (time.time() - HeartBeatTime) >= (60 / float(HeartRate)):
        HeartBeatCounter += 1  # Increment heart beat count
        HeartBeatEventTime += 60 / float(HeartRate)  # Reset last time of heart beat
        HeartBeatTime = time.time()  # Current time for next processing

        if HeartBeatEventTime >= 64 or HeartBeatCounter >= 256:  # Rollover at 64seconds
            HeartBeatCounter = 0
            HeartBeatEventTime = 0
            HeartBeatTime = 0

    if Interleave % 4 == 0:
        PageChangeToggle ^= 0x80  # toggle bit every 4 counts

    if Interleave % 64 <= 55:  # Transmit 56 times Page 0 = Main data page
        DataPageNumber = 0
        Spec1 = 0xFF  # Reserved
        Spec2 = 0xFF  # Reserved
        Spec3 = 0xFF  # Reserved
        # comment       = "(HR data p0)"

    elif (
        Interleave % 64 <= 59
    ):  # Transmit 4 times (56, 57, 58, 59) Page 2 = Manufacturer info
        DataPageNumber = 2
        Spec1 = ant.Manufacturer_garmin
        Spec2 = ant.SerialNumber_HRM & 0x00FF  # Serial Number LSB
        Spec3 = (
            ant.SerialNumber_HRM & 0xFF00
        ) >> 8  # Serial Number MSB     # 1959-07-05
        # comment       = "(HR data p2)"

    elif (
        Interleave % 64 <= 63
    ):  # Transmit 4 times (60, 61, 62, 63) Page 3 = Product information
        DataPageNumber = 3
        Spec1 = ant.HWrevision_HRM
        Spec2 = ant.SWversion_HRM
        Spec3 = ant.ModelNumber_HRM
        # comment       = "(HR data p3)"

    info = ant.msgPage_Hrm(
        ant.channel_HRM,
        PageChangeToggle | DataPageNumber,
        Spec1,
        Spec2,
        Spec3,
        HeartBeatEventTime,
        HeartBeatCounter,
        HeartRate,
    )
    hrdata = ant.ComposeMessage(ant.msgID_BroadcastData, info)

    # -------------------------------------------------------------------------
    # Prepare for next event
    # -------------------------------------------------------------------------
    Interleave += 1  # Increment and ...
    Interleave = int(Interleave) & 0xFF  # maximize to 255

    # -------------------------------------------------------------------------
    # Return message to be sent
    # -------------------------------------------------------------------------
    return hrdata


# -------------------------------------------------------------------------------
# Main program for module test
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    Initialize()
    fedata = BroadcastHeartrateMessage(123)
    print(fedata)
