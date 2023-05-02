"""Provide interface for communicating as ANT+ fitness equipment."""
# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2023-04-16"
# 2023-04-16    Rewritten in class based fashion
# 2023-04-15    Improve flake8 compliance
# 2020-12-28    accumulated_power not negative
# 2020-12-27    Interleave and EventCount more according specification
#               see comment in antPWR.py for more info.
# 2020-05-07    devAntDongle not needed, not used
# 2020-05-07    pylint error free
# 2020-02-18    First version, split-off from FortiusAnt.py
# -------------------------------------------------------------------------------
import time

from fortius_ant.antInterface import AntInterface
from fortius_ant.antMessage import AntMessage, Manufacturer_tacx, msgID_BroadcastData
from fortius_ant.antPage import Page80, Page81, FEPage16, FEPage25
from fortius_ant.usbTrainer import clsTacxTrainer

ModelNumber_FE = 2875  # short antifier-value=0x8385, Tacx Neo=2875
SerialNumber_FE = 19590705  # int   1959-7-5
HWrevision_FE = 1  # char
SWrevisionMain_FE = 1  # char
SWrevisionSupp_FE = 1  # char

channel_FE = 0  # ANT+ channel for Fitness Equipment


class antFE(AntInterface):
    """Interface for communicating as an ANT+ Fitness Equipment."""

    interleave_reset = 256

    def __init__(self):
        self.interleave = None
        self.event_count = None
        self.accumulated_power = None
        self.accumulated_time = None
        self.distance_travelled = None
        self.accumulated_last_time = None
        self.initialize()

    def initialize(self):
        super().initialize()
        self.interleave = 0
        self.event_count = 0
        self.accumulated_power = 0
        self.accumulated_time = 0
        self.distance_travelled = 0
        self.accumulated_last_time = time.time()
        
    def broadcast_message(self, *args):
        """Assemble the message to be sent."""
        message = self._broadcast_message(self.interleave, *args)
        self.interleave += 1
        if self.interleave == self.interleave_reset:
            self.interleave = 0
        return message
        
    def broadcast_message_from_trainer(self, TacxTrainer: clsTacxTrainer):
        return broadcast_message(TacxTrainer.Cadence, TacxTrainer.Power, TacxTrainer.SpeedKmh, TacxTrainer.HeartRate)

    def _broadcast_message(
        self, interleave: int, Cadence, CurrentPower, SpeedKmh, HeartRate
    ):
        CurrentPower = max(0, CurrentPower)  # Not negative
        CurrentPower = min(4093, CurrentPower)  # Limit to 4093
        Cadence = min(253, Cadence)  # Limit to 253

        if interleave % 64 in (
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
            page = Page80.page(
                channel_FE,
                0xFF,
                0xFF,
                HWrevision_FE,
                Manufacturer_tacx,
                ModelNumber_FE,
            )

        elif interleave % 64 in (
            62,
            63,
        ):  # After 10 blocks of three messages, then 2 = 32 messages
            # -----------------------------------------------------------------------
            # Send first and second product info packet
            # -----------------------------------------------------------------------
            # comment = "(Product info packet)"
            page = Page81.page(
                channel_FE,
                0xFF,
                SWrevisionSupp_FE,
                SWrevisionMain_FE,
                SerialNumber_FE,
            )

        elif interleave % 3 == 0:
            # -----------------------------------------------------------------------
            # Send general fe data every 3 packets
            # -----------------------------------------------------------------------
            t = time.time()
            ElapsedTime = t - self.accumulated_last_time  # time since previous event
            self.accumulated_last_time = t
            self.accumulated_time += ElapsedTime * 4  # in 0.25s

            Speed = SpeedKmh * 1000 / 3600  # convert SpeedKmh to m/s
            Speed = Speed * 1000
            Speed = int(min(0xFFFF, Speed))
            Distance = ElapsedTime * Speed  # meters
            self.distance_travelled += Distance  # meters
            HeartRate = int(min(0xFF, HeartRate))

            self.accumulated_time = (
                int(self.accumulated_time) & 0xFF
            )  # roll-over at 255 (64 seconds)
            self.distance_travelled = (
                int(self.distance_travelled) & 0xFF
            )  # roll-over at 255

            # comment = "(General fe data)"
            page = FEPage16.page(
                channel_FE,
                self.accumulated_time,
                self.distance_travelled,
                Speed,
                HeartRate,
            )

        else:
            self.event_count += 1
            self.accumulated_power += max(0, CurrentPower)  # No decrement allowed

            self.event_count = int(self.event_count) & 0xFF  # roll-over at 255
            self.accumulated_power = (
                int(self.accumulated_power) & 0xFFFF
            )  # roll-over at 65535

            # -----------------------------------------------------------------------
            # Send specific trainer data
            # -----------------------------------------------------------------------
            # comment = "(Specific trainer data)"
            page = FEPage25.page(
                channel_FE,
                self.event_count,
                Cadence,
                self.accumulated_power,
                CurrentPower,
            )
        # -------------------------------------------------------------------------
        # Return message to be sent
        # -------------------------------------------------------------------------
        return AntMessage.compose(msgID_BroadcastData, page)


fe = antFE()
Interleave = fe.interleave


def BroadcastTrainerDataMessage(*args):
    """Used for compatibility with old implementation, to be updated."""
    global Interleave
    fe.interleave = Interleave
    rtn = fe.broadcast_message(*args)
    Interleave = fe.interleave
    return rtn


def Initialize():
    fe.initialize()
