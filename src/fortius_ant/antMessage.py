"""Provide a class structure for ANT+ messages."""

__version__ = "2023-04-16"
# 2023-04-16    Rewritten in class based fashion

import binascii
import struct

import fortius_ant.structConstants as sc
from fortius_ant.antPage import AntPage

msgID_RF_EVENT = 0x01

msgID_ANTversion = 0x3E
msgID_BroadcastData = 0x4E
msgID_AcknowledgedData = 0x4F
msgID_ChannelResponse = 0x40
msgID_Capabilities = 0x54

msgID_UnassignChannel = 0x41
msgID_AssignChannel = 0x42
msgID_ChannelPeriod = 0x43
msgID_ChannelSearchTimeout = 0x44
msgID_ChannelRfFrequency = 0x45
msgID_SetNetworkKey = 0x46
msgID_ResetSystem = 0x4A
msgID_OpenChannel = 0x4B
msgID_RequestMessage = 0x4D

msgID_ChannelID = 0x51  # Set, but also receive master channel - but how/when?
msgID_ChannelTransmitPower = 0x60

msgID_StartUp = 0x6F

msgID_BurstData = 0x50

# Manufacturer ID       see FitSDKRelease_21.20.00 profile.xlsx
Manufacturer_garmin = 1
Manufacturer_dynastream = 15
Manufacturer_tacx = 89
Manufacturer_trainer_road = 281
Manufacturer_dev = 255


class AntMessage(bytes):
    """A message to be sent over an ANT+ interface."""

    def __init__(self, data: bytes):
        super(bytes, data)

    @classmethod
    def compose(cls, messageID: int, info: AntPage):
        """Compose a message from its id and contents."""
        fSynch = sc.unsigned_char
        fLength = sc.unsigned_char
        fId = sc.unsigned_char
        fInfo = str(len(info)) + sc.char_array  # 9 character string

        messagemessage_format = sc.no_alignment + fSynch + fLength + fId + fInfo
        data = struct.pack(messagemessage_format, 0xA4, len(info), messageID, info)
        # -----------------------------------------------------------------------
        # Add the checksum
        # (antifier added \00\00 after each message for unknown reason)
        # -----------------------------------------------------------------------
        data += calc_checksum(data)

        return cls(data)

    @classmethod
    def decompose(cls, message) -> tuple:
        """Decompose a message into its constituent parts."""
        synch = 0
        length = 0
        messageID = 0
        checksum = 0
        info = binascii.unhexlify("")  # NULL-string bytes
        rest = ""  # No remainder (normal)

        if len(message) > 0:
            synch = message[0]  # Carefull approach
        if len(message) > 1:
            length = message[1]
        if len(message) > 2:
            messageID = message[2]
        if len(message) > 3 + length:
            if length:
                info = message[3 : 3 + length]  # Info, if length > 0
            checksum = message[3 + length]  # Character after info
        if len(message) > 4 + length:
            rest = message[4 + length :]  # Remainder (should not occur)

        Channel = -1
        DataPageNumber = -1
        if length >= 1:
            Channel = message[3]
        if length >= 2:
            DataPageNumber = message[4]

        # ---------------------------------------------------------------------------
        # Special treatment for Burst data
        # Note that SequenceNumber is not returned and therefore lost, which is to
        #      be implemented as soon as we will use msgID_BurstData
        # ---------------------------------------------------------------------------

        if messageID == msgID_BurstData:
            _SequenceNumber = (Channel & 0b11100000) >> 5  # Upper 3 bits # noqa: F841
            Channel = Channel & 0b00011111  # Lower 5 bits

        return synch, length, messageID, info, checksum, rest, Channel, DataPageNumber


def calc_checksum(message):
    xor_value = 0
    length = message[1]  # byte 1; length of info
    length += 3  # Add synch, len, id
    for i in range(0, length):  # Process bytes as defined in length
        xor_value = xor_value ^ message[i]

    #   print('checksum', logfile.HexSpace(message), xor_value, bytes([xor_value]))

    return bytes([xor_value])


class SpecialMessage(AntMessage):
    """Special case messages."""

    message_id: int
    info: bytes

    @classmethod
    def _parse_args(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def create(cls, **kwargs):
        """Create message."""
        cls._parse_args(**kwargs)
        return cls.compose(cls.message_id, cls.info)


class Message41(SpecialMessage):
    """Unassign channel."""

    message_id = msgID_UnassignChannel

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        message_format = sc.no_alignment + sc.unsigned_char
        cls.info = struct.pack(message_format, channel)


class Message42(SpecialMessage):
    """Assign channel."""

    message_id = msgID_AssignChannel

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        channel_type = kwargs["type"]
        network = kwargs["network"]
        message_format = (
            sc.no_alignment + sc.unsigned_char + sc.unsigned_char + sc.unsigned_char
        )
        cls.info = struct.pack(message_format, channel, channel_type, network)


class Message43(SpecialMessage):
    """Set period."""

    message_id = msgID_ChannelPeriod

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        period = kwargs["period"]
        message_format = sc.no_alignment + sc.unsigned_char + sc.unsigned_short
        cls.info = struct.pack(message_format, channel, period)


class Message44(SpecialMessage):
    """Set search timeoute."""

    message_id = msgID_ChannelSearchTimeout

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        timeout = kwargs["timeout"]
        message_format = sc.no_alignment + sc.unsigned_char + sc.unsigned_short
        cls.info = struct.pack(message_format, channel, timeout)


class Message45(SpecialMessage):
    """Set channel RF frequency."""

    message_id = msgID_ChannelRfFrequency

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        frequency = kwargs["frequency"]
        message_format = sc.no_alignment + sc.unsigned_char + sc.unsigned_char
        cls.info = struct.pack(message_format, channel, frequency)


class Message46(SpecialMessage):
    """Set network key."""

    message_id = msgID_SetNetworkKey

    @classmethod
    def _parse_args(cls, **kwargs):
        network = kwargs["network"] if "network" in kwargs else 0x00
        key = kwargs["key"] if "key" in kwargs else 0x45C372BDFB21A5B9
        message_format = sc.no_alignment + sc.unsigned_char + sc.unsigned_long_long
        cls.info = struct.pack(message_format, network, key)


class Message4A(SpecialMessage):
    """Reset system."""

    message_id = msgID_ResetSystem

    @classmethod
    def _parse_args(cls, **kwargs):
        message_format = sc.no_alignment + sc.unsigned_char
        cls.info = struct.pack(message_format, 0x00)


class Message4B(SpecialMessage):
    """Open channel."""

    message_id = msgID_OpenChannel

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        message_format = sc.no_alignment + sc.unsigned_char
        cls.info = struct.pack(message_format, channel)


class Message4D(SpecialMessage):
    """Request message."""

    message_id = msgID_RequestMessage

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        requested_id = kwargs["id"]
        message_format = sc.no_alignment + sc.unsigned_char + sc.unsigned_char
        cls.info = struct.pack(message_format, channel, requested_id)


class Message51(SpecialMessage):
    """Set channel ID."""

    message_id = msgID_ChannelID

    @classmethod
    def _parse_args(cls, **kwargs):
        message_format = (
            sc.no_alignment
            + sc.unsigned_char
            + sc.unsigned_short
            + sc.unsigned_char
            + sc.unsigned_char
        )
        cls.info = struct.pack(
            message_format, ChannelNumber, DeviceNumber, DeviceTypeID, TransmissionType
        )


class Message50(SpecialMessage):
    """Set transmit power."""

    message_id = msgID_ChannelTransmitPower

    @classmethod
    def _parse_args(cls, **kwargs):
        message_format = sc.no_alignment + sc.unsigned_char + sc.unsigned_char
        cls.info = struct.pack(message_format, ChannelNumber, TransmitPower)
