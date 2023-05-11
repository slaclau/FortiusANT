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

from fortius_ant.antDongle import (
    msgUnpage73_GenericCommand,
    msgUnpage70_RequestDataPage,
    msgPage71_CommandStatus,
)
from fortius_ant.ant.interface import AntInterface, UnknownDataPage, UnsupportedPage
from fortius_ant.ant.message import AntMessage, Manufacturer_dev, msgID_BroadcastData
from fortius_ant.antPage import Page2, Page80, Page81
from fortius_ant import debug, logfile

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


class AntCTRL(AntInterface):
    """Interface for communicating as an ANT+ control."""

    interleave_reset = 129
    channel = channel_CTRL
    device_type_id = DeviceTypeID_control

    def broadcast_message_from_trainer(self):
        """Broadcast controllable message."""
        return self.broadcast_message()

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

    def _handle_broadcast_message(self, data_page_number: int, info: bytes):
        pass

    def _handle_acknowledged_message(self, data_page_number, info):
        if data_page_number == 73:
            (
                ctrl_SlaveSerialNumber,
                ctrl_SlaveManufacturerID,
                SequenceNr,
                ctrl_CommandNr,
            ) = msgUnpage73_GenericCommand(info)

            # Update "last command" data in case page 71 is requested later
            self.p71_LastReceivedCommandID = data_page_number
            self.p71_SequenceNr = SequenceNr
            self.p71_CommandStatus = 0  # successfully processed
            self.p71_Data1 = ctrl_CommandNr & 0x00FF
            self.p71_Data2 = (ctrl_CommandNr & 0xFF00) >> 8
            self.p71_Data3 = 0xFF
            self.p71_Data4 = 0xFF

            # ---------------------------------------------------
            # Commands should not overwrite, therefore stored
            # in a table as tuples.
            # ---------------------------------------------------
            self.received_data.ctrl_commands.append(
                (
                    ctrl_SlaveManufacturerID,
                    ctrl_SlaveSerialNumber,
                    ctrl_CommandNr,
                )
            )
            command_name = CommandName.get(ctrl_CommandNr, "Unknown")
            if debug.on(debug.Application):
                logfile.Print(
                    f"ANT+ Control {ctrl_SlaveManufacturerID} {ctrl_SlaveSerialNumber}:"
                    f" Received command {ctrl_CommandNr} = {command_name} "
                )

            return None

        # -------------------------------------------------------
        # Data page 70 Request data page
        # -------------------------------------------------------
        if data_page_number == 70:
            (
                _SlaveSerialNumber,
                _DescriptorByte1,
                _DescriptorByte2,
                _AckRequired,
                NrTimes,
                RequestedPageNumber,
                _CommandType,
            ) = msgUnpage70_RequestDataPage(info)

            info = False
            if RequestedPageNumber == 71:
                info = msgPage71_CommandStatus(
                    self.channel,
                    self.p71_LastReceivedCommandID,
                    self.p71_SequenceNr,
                    self.p71_CommandStatus,
                    self.p71_Data1,
                    self.p71_Data2,
                    self.p71_Data3,
                    self.p71_Data4,
                )
            else:
                raise UnsupportedPage

            if info is not False:
                data = []
                d = AntMessage.compose(msgID_BroadcastData, info)
                while NrTimes:
                    data.append(d)
                    NrTimes -= 1
                return (data, False, True, True)
            return None
        # -------------------------------------------------------
        # Other data pages
        # -------------------------------------------------------
        raise UnknownDataPage


ctrl = AntCTRL()
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
