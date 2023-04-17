"""Provide interface for communicating as ANT+ heart rate monitor."""
# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2023-04-16"
# 2023-04-16    Rewritten in class based fashion
# 2023-04-15    Improve flake8 compliance
# 2020-12-27    Interleave like antPWR.py
# 2020-05-07    devAntDongle not needed, not used
# 2020-05-07    pylint error free
# 2020-02-18    First version, split-off from FortiusAnt.py
# -------------------------------------------------------------------------------
import time

from fortius_ant.antInterface import AntInterface
from fortius_ant.antMessage import AntMessage, Manufacturer_garmin, msgID_BroadcastData
from fortius_ant.antPage import HRMPage

ModelNumber_HRM = 0x33  # char  antifier-value
SerialNumber_HRM = 5975  # short 1959-7-5
HWrevision_HRM = 1  # char
SWversion_HRM = 1  # char

channel_HRM = 1  # ANT+ channel for Heart Rate Monitor


class AntHRM(AntInterface):
    """Interface for communicating as an ANT+ HRM."""

    interleave_reset = 256

    def __init__(self):
        self.interleave = None
        self.heart_beat_counter = None
        self.heart_beat_event_time = None
        self.heart_beat_time = None
        self.page_change_toggle = None
        self.initialize()

    def initialize(self):
        super().initialize()
        self.interleave = 0
        self.heart_beat_counter = 0
        self.heart_beat_event_time = 0
        self.heart_beat_time = 0
        self.page_change_toggle = 0

    def _broadcast_message(self, interleave: int, HeartRate):
        if (time.time() - self.heart_beat_time) >= (60 / float(HeartRate)):
            self.heart_beat_counter += 1  # Increment heart beat count
            self.heart_beat_event_time += 60 / float(
                HeartRate
            )  # Reset last time of heart beat
            self.heart_beat_time = time.time()  # Current time for next processing

            if (
                self.heart_beat_event_time >= 64 or self.heart_beat_counter >= 256
            ):  # Rollover at 64seconds
                self.heart_beat_counter = 0
                self.heart_beat_event_time = 0
                self.heart_beat_time = 0

        if self.interleave % 4 == 0:
            self.page_change_toggle ^= 0x80  # toggle bit every 4 counts

        if self.interleave % 64 <= 55:  # Transmit 56 times Page 0 = Main data page
            DataPageNumber = 0
            Spec1 = 0xFF  # Reserved
            Spec2 = 0xFF  # Reserved
            Spec3 = 0xFF  # Reserved
            # comment       = "(HR data p0)"

        elif (
            self.interleave % 64 <= 59
        ):  # Transmit 4 times (56, 57, 58, 59) Page 2 = Manufacturer info
            DataPageNumber = 2
            Spec1 = Manufacturer_garmin
            Spec2 = SerialNumber_HRM & 0x00FF  # Serial Number LSB
            Spec3 = (
                SerialNumber_HRM & 0xFF00
            ) >> 8  # Serial Number MSB     # 1959-07-05
            # comment       = "(HR data p2)"

        elif (
            self.interleave % 64 <= 63
        ):  # Transmit 4 times (60, 61, 62, 63) Page 3 = Product information
            DataPageNumber = 3
            Spec1 = HWrevision_HRM
            Spec2 = SWversion_HRM
            Spec3 = ModelNumber_HRM
            # comment       = "(HR data p3)"

        page = HRMPage.page(
            self.page_change_toggle | DataPageNumber,
            channel_HRM,
            Spec1,
            Spec2,
            Spec3,
            self.heart_beat_event_time,
            self.heart_beat_counter,
            int(HeartRate),
        )
        return AntMessage.compose(msgID_BroadcastData, page)


hrm = AntHRM()
Interleave = hrm.interleave


def BroadcastHeartrateMessage(HeartRate):
    """Used for compatibility with old implementation, to be updated."""
    global Interleave
    hrm.interleave = Interleave
    rtn = hrm.broadcast_message(HeartRate)
    Interleave = hrm.interleave
    return rtn


def Initialize():
    hrm.initialize()
