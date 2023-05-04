"""Provide an inheritable class for implemented an ANT+ device."""

__version__ = "2023-04-16"
# 2023-04-16    Rewritten in class based fashion

from fortius_ant.FortiusAntBody import ReceivedData
from fortius_ant.FortiusAntCommand import CommandLineVariables
from fortius_ant.usbTrainer import clsTacxTrainer
from fortius_ant.antDongle import (
    clsAntDongle,
    unmsg51_ChannelID,
)
from fortius_ant.antMessage import (
    msgID_AcknowledgedData,
    msgID_BroadcastData,
    msgID_ChannelID,
    msgID_ChannelResponse,
    msgID_BurstData,
)


class AntInterface:
    """Interface for communicating as an ANT+ device."""

    interleave = 0
    interleave_reset: int
    channel: int
    device_type_id: int
    ant_dongle: clsAntDongle
    master: bool
    paired = False
    gui = None
    clv = None
    trainer = None
    received_data: ReceivedData = None

    def __init__(self, master=True):
        self.master = master

    def set_gui(self, gui):
        """Assign a GUI instance to the interface."""
        self.gui = gui

    def set_clv(self, clv: CommandLineVariables):
        """Assign a clv instance to the interface."""
        self.clv = clv

    def set_trainer(self, trainer: clsTacxTrainer):
        """Assign a trainer instance to the interface."""
        self.trainer = trainer

    def set_received_data(self, received_data: ReceivedData):
        """Assign a :class:`ReceivedData` instance to the interface."""
        self.received_data = received_data

    def initialize(self):
        """Initialize interface."""
        self.interleave = 0

    def broadcast_message(self, *args):
        """Assemble the message to be sent."""
        message = self._broadcast_message(self.interleave, *args)
        if self.interleave == self.interleave_reset:
            self.interleave = 0
        self.interleave += 1
        return message

    def broadcast_message_from_trainer(self):
        """Assemble the message to be sent given a trainer."""
        raise NotImplementedError

    def _broadcast_message(self, interleave: int, *args):
        raise NotImplementedError

    def handle_received_info(
        self, channel: int, message_id: int, data_page_number: int, info: bytes
    ):
        """Handle data received over ANT."""
        if channel != self.channel:
            raise WrongChannel
        self._handle_received_info(message_id, data_page_number, info)

    def _handle_received_info(
        self, message_id: int, data_page_number: int, info: bytes
    ):
        if message_id == msgID_ChannelID:
            self._handle_channel_id_message(info)
        elif message_id == msgID_ChannelResponse:
            self._handle_channel_response_message(info)
        elif message_id == msgID_BroadcastData:
            self._handle_broadcast_message(data_page_number, info)
        elif message_id == msgID_AcknowledgedData:
            self._handle_aknowledged_message(data_page_number, info)
        elif message_id == msgID_BurstData:
            self._handle_burst_data(info)
        else:
            raise UnknownMessageID

    def _handle_channel_id_message(self, info: bytes):
        (
            Channel,
            DeviceNumber,
            DeviceTypeID,
            _TransmissionType,
        ) = unmsg51_ChannelID(info)

        if DeviceNumber == 0:  # No device paired, ignore
            pass

        elif Channel == self.channel and DeviceTypeID == self.device_type_id:
            self.paired = True

    def _handle_channel_response_message(self, info: bytes):
        pass

    def _handle_burst_data(self, info: bytes):
        pass

    def _handle_broadcast_message(self, data_page_number: int, info: bytes):
        raise NotImplementedError

    def _handle_aknowledged_message(self, data_page_number, info):
        raise NotImplementedError


class WrongChannel(Exception):
    """Raise when attempting to handle messages on the wrong channel."""


class UnknownMessageID(Exception):
    """Raise when attempting to handle an unknown message ID."""


class UnknownDataPage(Exception):
    """Raise when attempting to handle an unknown data page."""


class UnsupportedPage(Exception):
    """Raise when an unsupported page is requested."""
