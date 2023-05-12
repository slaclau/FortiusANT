"""Provide an inheritable class for implemented an ANT+ device."""

__version__ = "2023-04-16"
# 2023-04-16    Rewritten in class based fashion

from fortius_ant.ant.dongle import (
    default_network_key,
    ant_plus_frequency,
    power_0db,
    ChannelType,
    TransmissionType,
)

print_debug = False


class AntInterface:
    """Interface for communicating as an ANT+ device."""

    interleave = 0
    interleave_reset: int
    channel: int
    device_type_id: int
    device_number: int

    master: bool
    paired = False
    gui = None
    clv = None
    trainer = None
    received_data: ReceivedData | None = None

    network_key = default_network_key
    frequency = ant_plus_frequency
    transmit_power = power_0db
    
    channel_period = 32768 / 4
    channel_frequency = 57
    
    master_channel_type = ChannelType.BidirectionalTransmit.value
    slave_channel_type = ChannelType.BidirectionalReceive.value
    channel_type = None
 
    master_transmission_type = TransmissionType.INDEPENDENT
    slave_transmission_type = TransmissionType.PAIRING
    transmission_type = None

    def __init__(self, master=True):
        self.master = master

        self.p71_LastReceivedCommandID = 255
        self.p71_SequenceNr = 255
        self.p71_CommandStatus = 255
        self.p71_Data1 = 0xFF
        self.p71_Data2 = 0xFF
        self.p71_Data3 = 0xFF
        self.p71_Data4 = 0xFF

        if self.master:
            self.channel_type = self.master_channel_type
            self.transmission_type = self.master_transmission_type
        else:
            self.channel_type = self.slave_channel_type
            self.transmission_type = self.slave_transmission_type
         

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

    def _broadcast_message(self, interleave: int, *args):
        raise NotImplementedError

    def handle_received_info(
        self, channel: int, message_id: int, data_page_number: int, info: bytes
    ):
        """Handle data received over ANT."""
        if channel != self.channel:
            raise WrongChannel
        return self._handle_received_info(message_id, data_page_number, info)

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
            self._handle_acknowledged_message(data_page_number, info)
        elif message_id == msgID_BurstData:
            self._handle_burst_data(info)
        else:
            raise UnknownMessageID(info, message_id, type(self).__name__)

    def _handle_channel_id_message(self, info: bytes):
        (
            Channel,
            DeviceNumber,
            DeviceTypeID,
            _TransmissionType,
        ) = Message51.unmessage(info)

        if DeviceNumber == 0:  # No device paired, ignore
            pass

        elif Channel == self.channel and DeviceTypeID == self.device_type_id:
            self.paired = True

    def _handle_channel_response_message(self, info: bytes):
        channel = info[0]
        initiating_id = info[1]
        code = info[2]
        if print_debug:
            print(
                f"Channel response on channel {channel} initiated by {initiating_id} "
                f"with code {code}"
            )

    def _handle_burst_data(self, info: bytes):
        pass

    def _handle_broadcast_message(self, data_page_number: int, info: bytes):
        raise NotImplementedError

    def _handle_acknowledged_message(self, data_page_number, info):
        raise NotImplementedError


class WrongChannel(Exception):
    """Raise when attempting to handle messages on the wrong channel."""


class UnknownMessageID(Exception):
    """Raise when attempting to handle an unknown message ID."""

    def __init__(self, info: bytes, message_id: int, interface: str):
        self.info = info
        self.message_id = message_id
        self.interface = interface
        self.message = f"Message id {message_id} is not known by {interface}"


class UnknownDataPage(Exception):
    """Raise when attempting to handle an unknown data page."""

    def __init__(self, info: bytes = b"", page_number: int = -1):
        self.info = info
        self.page_number = page_number
        self.message = f"Page {page_number} is not known"


class UnsupportedPage(Exception):
    """Raise when an unsupported page is requested."""

    def __init__(self, info: bytes = b"", page_number: int = -1):
        self.info = info
        self.page_number = page_number
        self.message = f"Page {page_number} is not supported"
