from mypy.typeshed.stdlib.builtins import staticmethod
import struct
import fortius_ant.structConstants as sc


class AntMessage(struct):
    """A message to be sent over an ANT+ interface."""

    @staticmethod
    def Compose(messageID: int, info: struct) -> AntMessage:
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
        data += CalcChecksum(data)

        return data

    @staticmethod
    def Decompose(message) -> tuple(int):
        """Decompose a message into its constituent parts."""
        synch = 0
        length = 0
        id = 0
        checksum = 0
        info = binascii.unhexlify("")  # NULL-string bytes
        rest = ""  # No remainder (normal)

        if len(message) > 0:
            synch = message[0]  # Carefull approach
        if len(message) > 1:
            length = message[1]
        if len(message) > 2:
            id = message[2]
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

        if id == msgID_BurstData:
            _SequenceNumber = (Channel & 0b11100000) >> 5  # Upper 3 bits
            Channel = Channel & 0b00011111  # Lower 5 bits

        return synch, length, id, info, checksum, rest, Channel, DataPageNumber


def CalcChecksum(message):
    xor_value = 0
    length = message[1]  # byte 1; length of info
    length += 3  # Add synch, len, id
    for i in range(0, length):  # Process bytes as defined in length
        xor_value = xor_value ^ message[i]

    #   print('checksum', logfile.HexSpace(message), xor_value, bytes([xor_value]))

    return bytes([xor_value])
