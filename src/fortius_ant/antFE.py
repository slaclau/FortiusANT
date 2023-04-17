"""Provide interface for communicating as ANT+ fitness equipment."""
# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2023-04-15"
# 2023-04-15    Improve flake8 compliance
# 2020-12-28    AccumulatedPower not negative
# 2020-12-27    Interleave and EventCount more according specification
#               see comment in antPWR.py for more info.
# 2020-05-07    devAntDongle not needed, not used
# 2020-05-07    pylint error free
# 2020-02-18    First version, split-off from FortiusAnt.py
# -------------------------------------------------------------------------------
import time

import fortius_ant.antDongle as ant

Interleave = None
EventCount = None
AccumulatedPower = None
AccumulatedTime = None
DistanceTravelled = None
AccumulatedLastTime = None


def Initialize():
    """Initialize interface."""
    global Interleave, EventCount, AccumulatedPower, AccumulatedTime
    global DistanceTravelled, AccumulatedLastTime
    Interleave = 0
    EventCount = 0
    AccumulatedPower = 0
    AccumulatedTime = 0
    DistanceTravelled = 0
    AccumulatedLastTime = time.time()


# ------------------------------------------------------------------------------
# B r o a d c a s t T r a i n e r D a t a M e s s a g e
# ------------------------------------------------------------------------------
# input:        Cadence, CurrentPower, SpeedKmh, HeartRate
#
# Description:  Create next message to be sent for FE-C device. Refer to
#               D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
#
# Output:       Interleave, AccumulatedPower, AccumulatedTime, DistanceTravelled
#
# Returns:      fedata; next message to be broadcasted on ANT+ channel
# ------------------------------------------------------------------------------
def BroadcastTrainerDataMessage(Cadence, CurrentPower, SpeedKmh, HeartRate):
    """Create next message to be sent to FE-C device.

    Four types of page are sent here:

    * Page 80 - Manufacturer’s Identification
    * Page 81 - Product Information
    * Page 16 - GeneralFE Data
        This page contains the following information:

        * Elapsed time
        * Distance travelled
        * Speed
        * Heart rate
    * Page 25 - Specific Trainer/Stationary BikeData
        This page contains the following information:

        * Instantaneous cadence
        * Accumulated power
        * Instantaneous power

    Parameters
    ----------
    Cadence : int
    CurrentPower : int
    SpeedKmh : float
    HeartRate : int

    Returns
    -------
    rtn : bytes
        Message to be sent
    """
    global Interleave, EventCount, AccumulatedPower, AccumulatedTime
    global DistanceTravelled, AccumulatedLastTime
    # ---------------------------------------------------------------------------
    # Prepare data to be sent to ANT+
    # ---------------------------------------------------------------------------
    CurrentPower = max(0, CurrentPower)  # Not negative
    CurrentPower = min(4093, CurrentPower)  # Limit to 4093
    Cadence = min(253, Cadence)  # Limit to 253
    Cadence = max(0, Cadence) # Not negative

    if Interleave % 64 in (
        30,
        31,
    ):  # After 10 blocks of three messages, then 2 = 32 messages
        # -----------------------------------------------------------------------
        # Send first and second manufacturer's info packet
        #      FitSDKRelease_20.50.00.zip
        #      profile.xlsx
        #      D00001198_-_ANT+_Common_Data_Pages_Rev_3.1%20.pdf
        #      page 28 byte 4,5,6,7- 15=dynastream, 89=tacx
        # -----------------------------------------------------------------------
        # comment = "(Manufacturer's info packet)"
        info = ant.msgPage80_ManufacturerInfo(
            ant.channel_FE,
            0xFF,
            0xFF,
            ant.HWrevision_FE,
            ant.Manufacturer_tacx,
            ant.ModelNumber_FE,
        )
        rtn = ant.ComposeMessage(ant.msgID_BroadcastData, info)

    elif Interleave % 64 in (
        62,
        63,
    ):  # After 10 blocks of three messages, then 2 = 32 messages
        # -----------------------------------------------------------------------
        # Send first and second product info packet
        # -----------------------------------------------------------------------
        # comment = "(Product info packet)"
        info = ant.msgPage81_ProductInformation(
            ant.channel_FE,
            0xFF,
            ant.SWrevisionSupp_FE,
            ant.SWrevisionMain_FE,
            ant.SerialNumber_FE,
        )
        rtn = ant.ComposeMessage(ant.msgID_BroadcastData, info)

    elif Interleave % 3 == 0:
        # -----------------------------------------------------------------------
        # Send general fe data every 3 packets
        # -----------------------------------------------------------------------
        t = time.time()
        ElapsedTime = t - AccumulatedLastTime  # time since previous event
        AccumulatedLastTime = t
        AccumulatedTime += ElapsedTime * 4  # in 0.25s

        Speed = SpeedKmh * 1000 / 3600  * 1000 # convert SpeedKmh to mm/s
        Speed = max(Speed, 0)
        Speed = min(Speed, 65535)
        Heartrate = max(Heartrate, 0)
        Heartrate = min(Speed, 255)
        Distance = ElapsedTime * Speed  # meters
        DistanceTravelled += Distance  # meters

        AccumulatedTime = int(AccumulatedTime) & 0xFF  # roll-over at 255 (64 seconds)
        DistanceTravelled = int(DistanceTravelled) & 0xFF  # roll-over at 255

        # comment = "(General fe data)"
        info = ant.msgPage16_GeneralFEdata(
            ant.channel_FE, AccumulatedTime, DistanceTravelled, Speed * 1000, HeartRate
        )
        rtn = ant.ComposeMessage(ant.msgID_BroadcastData, info)

    else:
        EventCount += 1
        AccumulatedPower += max(0, CurrentPower)  # No decrement allowed

        EventCount = int(EventCount) & 0xFF  # roll-over at 255
        AccumulatedPower = int(AccumulatedPower) & 0xFFFF  # roll-over at 65535

        # -----------------------------------------------------------------------
        # Send specific trainer data
        # -----------------------------------------------------------------------
        # comment = "(Specific trainer data)"
        info = ant.msgPage25_TrainerData(
            ant.channel_FE, EventCount, Cadence, AccumulatedPower, CurrentPower
        )
        rtn = ant.ComposeMessage(ant.msgID_BroadcastData, info)

    # -------------------------------------------------------------------------
    # Prepare for next event
    # -------------------------------------------------------------------------
    Interleave += 1  # Increment and ...
    Interleave &= 0xFF  # maximize to 255

    # -------------------------------------------------------------------------
    # Return message to be sent
    # -------------------------------------------------------------------------
    return rtn


# -------------------------------------------------------------------------------
# Main program for module test
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    Initialize()
    fedata = BroadcastTrainerDataMessage(98, 234, 35.6, 123)
    print(fedata)
