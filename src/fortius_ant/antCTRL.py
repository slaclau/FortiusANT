"""Provide interface for communicating with ANT+ controls."""
# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2023-04-16"
# 2023-04-16    Rewritten in class based fashion
# 2023-04-15    Improve flake8 compliance
# 2020-12-27    Interleave like antPWR.py
# 2020-12-14    First version, obtained from switchable
# -------------------------------------------------------------------------------

from fortius_ant.antInterface import AntInterface
from fortius_ant.antMessage import AntMessage, Manufacturer_dev, msgID_BroadcastData
from fortius_ant.antPage import Page2, Page80, Page81
from fortius_ant.usbTrainer import clsTacxTrainer

ModelNumber_CTRL = 1234  # short
SerialNumber_CTRL = 19590709  # int   1959-7-9
HWrevision_CTRL = 1  # char
SWrevisionMain_CTRL = 1  # char
SWrevisionSupp_CTRL = 1  # char

channel_CTRL = 6  # ANT+ Channel for Remote Control
DeviceTypeID_control = 16

# ---------------------------------------------------------------------------
# ANT+ Control command codes
# D00001307_-_ANT+_Device_Profile_-_Controls_-_2.0.pdf
# Table 9-8.
# ---------------------------------------------------------------------------
MenuUp = 0
MenuDown = 1
MenuSelect = 2
MenuBack = 3
Home = 4
Start = 32
Stop = 33
Reset = 34
Length = 35
Lap = 36
NoAction = 65535  # None is reserved

CommandName = {
    MenuUp: "MenuUp",
    MenuDown: "MenuDown",
    MenuSelect: "MenuSelect",
    MenuBack: "MenuBack",
    Home: "Home",
    Start: "Start",
    Stop: "Stop",
    Reset: "Reset",
    Length: "Length",
    Lap: "Lap",
    NoAction: "NoAction",
}


class antCTRL(AntInterface):
    """Interface for communicating as an ANT+ control."""

    interleave_reset = 129
    channel = channel_CTRL
    device_type_id = DeviceTypeID_control

    def broadcast_message_from_trainer(self, TacxTrainer: clsTacxTrainer):
        return broadcast_message()

    def _broadcast_message(self, interleave: int, *args):
        if interleave == 64:
            page = Page80.page(
                channel_CTRL,
                0xFF,
                0xFF,
                HWrevision_CTRL,
                Manufacturer_dev,
                ModelNumber_CTRL,
            )
        elif interleave == 129:
            page = Page81.page(
                channel_CTRL,
                0xFF,
                SWrevisionSupp_CTRL,
                SWrevisionMain_CTRL,
                SerialNumber_CTRL,
            )
        else:
            page = Page2.page(channel_CTRL, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10)
        return AntMessage.compose(msgID_BroadcastData, page)


ctrl = antCTRL()
Interleave = ctrl.interleave


def BroadcastControlMessage():
    """Used for compatibility with old implementation, to be updated."""
    global Interleave
    ctrl.interleave = Interleave
    rtn = ctrl.broadcast_message()
    Interleave = ctrl.interleave
    return rtn


def Initialize():
    ctrl.initialize()
