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

        messageFormat = sc.no_alignment + fSynch + fLength + fId + fInfo
        data = struct.pack(messageFormat, 0xA4, len(info), messageID, info)
        # -----------------------------------------------------------------------
        # Add the checksum
        # (antifier added \00\00 after each message for unknown reason)
        # -----------------------------------------------------------------------
        data += _calc_checksum(data)

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


def _calc_checksum(message):
    xor_value = 0
    length = message[1]  # byte 1; length of info
    length += 3  # Add synch, len, id
    for i in range(0, length):  # Process bytes as defined in length
        xor_value = xor_value ^ message[i]

    #   print('checksum', logfile.HexSpace(message), xor_value, bytes([xor_value]))

    return bytes([xor_value])
