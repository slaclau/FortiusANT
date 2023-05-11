"""Provide a class structure for ANT+ messages."""

__version__ = "2023-04-16"
# 2023-04-16    Rewritten in class based fashion

import binascii
from enum import Enum
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


class Id(Enum):
    """Message ID enum."""

    RF_EVENT = 0x01

    ANTversion = 0x3E
    BroadcastData = 0x4E
    AcknowledgedData = 0x4F
    ChannelResponse = 0x40
    Capabilities = 0x54

    UnassignChannel = 0x41
    AssignChannel = 0x42
    ChannelPeriod = 0x43
    ChannelSearchTimeout = 0x44
    ChannelRfFrequency = 0x45
    SetNetworkKey = 0x46
    ResetSystem = 0x4A
    OpenChannel = 0x4B
    RequestMessage = 0x4D

    ChannelID = 0x51  # Set, but also receive master channel - but how/when?
    ChannelTransmitPower = 0x60

    StartUp = 0x6F

    BurstData = 0x50


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

        message_format = sc.no_alignment + fSynch + fLength + fId + fInfo
        data = struct.pack(message_format, 0xA4, len(info), messageID, info)
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

    @classmethod
    def decompose_to_dict(cls, message) -> dict:
        """Decompose message into dictionary."""
        rtn = {}
        response = cls.decompose(message)
        rtn["synch"] = response[0]
        rtn["length"] = response[1]
        rtn["id"] = response[2]
        rtn["info"] = response[3]
        rtn["checksum"] = response[4]
        rtn["rest"] = response[5]
        rtn["channel"] = response[6]
        rtn["page_number"] = response[7]

        if rtn["synch"] != 0xA4:
            raise ValueError
        # if rtn["checksum"] != calc_checksum(message[0:-1]):
        #    raise ValueError

        return rtn


def calc_checksum(message):
    """Calculate checksum."""
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
    message_format: str
    info: bytes

    @classmethod
    def _parse_args(cls, **kwargs) -> bytes:
        raise NotImplementedError

    @classmethod
    def create(cls, **kwargs):
        """Create message."""
        info = cls._parse_args(**kwargs)
        return cls.compose(cls.message_id, info)

    @classmethod
    def to_dict(cls, message):
        """Convert message to dict."""
        raise NotImplementedError

    @classmethod
    def _get_content(cls, message):
        info = cls._get_info(message)
        return struct.unpack(cls.message_format, info)

    @classmethod
    def _get_info(cls, message):
        message_id = cls.decompose_to_dict(message)["id"]
        if message_id != cls.message_id:
            raise WrongMessageId(message_id, cls.message_id)
        return cls.decompose_to_dict(message)["info"]


class UnassignChannelMessage(SpecialMessage):
    """Unassign channel."""

    message_id = msgID_UnassignChannel
    message_format = sc.no_alignment + sc.unsigned_char

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        return struct.pack(cls.message_format, channel)


class AssignChannelMessage(SpecialMessage):
    """Assign channel."""

    message_id = msgID_AssignChannel
    message_format = (
        sc.no_alignment + sc.unsigned_char + sc.unsigned_char + sc.unsigned_char
    )

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        channel_type = kwargs["type"]
        network = kwargs["network"]
        return struct.pack(cls.message_format, channel, channel_type, network)


class Message43(SpecialMessage):
    """Set period."""

    message_id = msgID_ChannelPeriod
    message_format = sc.no_alignment + sc.unsigned_char + sc.unsigned_short

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        period = kwargs["period"]
        return struct.pack(cls.message_format, channel, period)


class Message44(SpecialMessage):
    """Set search timeoute."""

    message_id = msgID_ChannelSearchTimeout
    message_format = sc.no_alignment + sc.unsigned_char + sc.unsigned_short

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        timeout = kwargs["timeout"]
        return struct.pack(cls.message_format, channel, timeout)


class Message45(SpecialMessage):
    """Set channel RF frequency."""

    message_id = msgID_ChannelRfFrequency
    message_format = sc.no_alignment + sc.unsigned_char + sc.unsigned_char

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        frequency = kwargs["frequency"]
        return struct.pack(cls.message_format, channel, frequency)


class Message46(SpecialMessage):
    """Set network key."""

    message_id = msgID_SetNetworkKey
    message_format = sc.no_alignment + sc.unsigned_char + sc.unsigned_long_long

    @classmethod
    def _parse_args(cls, **kwargs):
        network = kwargs["network"] if "network" in kwargs else 0x00
        key = kwargs["key"] if "key" in kwargs else 0x45C372BDFB21A5B9
        return struct.pack(cls.message_format, network, key)


class Message4A(SpecialMessage):
    """Reset system."""

    message_id = msgID_ResetSystem
    message_format = sc.no_alignment + sc.unsigned_char

    @classmethod
    def _parse_args(cls, **kwargs):
        return struct.pack(cls.message_format, 0x00)


class Message4B(SpecialMessage):
    """Open channel."""

    message_id = msgID_OpenChannel
    message_format = sc.no_alignment + sc.unsigned_char

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        return struct.pack(cls.message_format, channel)


class Message4D(SpecialMessage):
    """Request message."""

    message_id = msgID_RequestMessage
    message_format = sc.no_alignment + sc.unsigned_char + sc.unsigned_char

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"] if "channel" in kwargs else 0
        requested_id = kwargs["id"]
        print(channel)
        print(requested_id)
        return struct.pack(cls.message_format, channel, requested_id)


class Message51(SpecialMessage):
    """Set channel ID."""

    message_id = msgID_ChannelID
    message_format = (
        sc.no_alignment
        + sc.unsigned_char
        + sc.unsigned_short
        + sc.unsigned_char
        + sc.unsigned_char
    )

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        device_number = kwargs["device_number"]
        device_type_id = kwargs["device_type_id"]
        transmission_type = kwargs["transmission_type"]
        return struct.pack(
            cls.message_format,
            channel,
            device_number,
            device_type_id,
            transmission_type,
        )


class Message50(SpecialMessage):
    """Set transmit power."""

    message_id = msgID_ChannelTransmitPower
    message_format = sc.no_alignment + sc.unsigned_char + sc.unsigned_char

    @classmethod
    def _parse_args(cls, **kwargs):
        channel = kwargs["channel"]
        power = kwargs["power"]
        return struct.pack(cls.message_format, channel, power)


class ChannelResponseMessage(SpecialMessage):
    """Sent by the dongle in response to channel events."""

    message_id = msgID_ChannelResponse
    message_format = (
        sc.no_alignment + sc.unsigned_char + sc.unsigned_char + sc.unsigned_char
    )

    @classmethod
    def to_dict(cls, message):
        """Return breakdown of channel response message."""
        info = cls._get_info(message)
        rtn = {}
        rtn["channel"] = info[0]
        rtn["id"] = Id(info[1])
        rtn["code"] = cls.Code(info[2])

        return rtn

    class Code(Enum):
        """Response codes enum."""

        RESPONSE_NO_ERROR = 0
        UNKNOWN = 1


class StartupMessage(SpecialMessage):
    """Sent by dongle on startup."""

    message_id = msgID_StartUp
    message_format = sc.no_alignment + sc.unsigned_char

    @classmethod
    def to_dict(cls, message):
        """Return bit field of startup reason."""
        info = cls._get_info(message)
        rtn = {}
        bits = bin(info[0])[2:]
        bits = "0" * (8 - len(bits)) + bits
        rtn["bits"] = bits

        reset_type = ""
        reset_type = "POWER_ON_RESET" if bits == "00000000" else ""
        reset_type = "COMMAND_RESET" if bits[7 - 5] == "1" else ""

        rtn["type"] = reset_type
        return rtn


class CapabilitiesMessage(SpecialMessage):
    """Sent by dongle with capabilities."""

    message_id = msgID_Capabilities

    @classmethod
    def to_dict(cls, message) -> dict:
        """Return max channels and networks."""
        info = cls._get_info(message)
        rtn = {}
        rtn["max_channels"] = info[0]
        rtn["max_networks"] = info[1]
        return rtn


class VersionMessage(SpecialMessage):
    """Sent by dongle with capabilities."""

    message_id = msgID_ANTversion

    @classmethod
    def to_dict(cls, message) -> dict:
        """Return version."""
        info = cls._get_info(message)
        version = bytes(info[0:-1]).decode("utf-8")
        return {"version": version}


class WrongMessageId(Exception):
    """Raise when trying to parse the wrong type of message."""

    def __init__(self, received, expected):
        self.received = received
        self.expected = expected
        self.message = f"Received {received} and expected {expected}."
