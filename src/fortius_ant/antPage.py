"""Provide a class structure for ANT+ data pages."""
import struct

import fortius_ant.structConstants as sc


class AntPage(bytes):
    """Base class for ANT+ data pages."""

    message_format: str
    data_page_number: int

    def __init__(self, data: bytes):
        super(bytes, data)

    @classmethod
    def page(cls, *args):
        """Convert the supplied data to a data page."""
        args = (
            args[0],
            cls.data_page_number,
        ) + args[1:]
        return cls(struct.pack(cls.message_format, *args))

    @classmethod
    def unpage(cls, page) -> tuple:
        """Convert the supplied page to a tuple of its data."""
        return struct.unpack(cls.message_format, page)


class Page2(AntPage):
    """Page 2 contains control information."""

    data_page_number = 2

    fChannel = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fCurrentNotifications = sc.unsigned_char
    fReserved1 = sc.unsigned_char
    fReserved2 = sc.unsigned_char
    fReserved3 = sc.unsigned_char
    fReserved4 = sc.unsigned_char
    fReserved5 = sc.unsigned_char
    fDeviceCapabilities = sc.unsigned_char

    message_format = (
        sc.no_alignment
        + fChannel
        + fDataPageNumber
        + fCurrentNotifications
        + fReserved1
        + fReserved2
        + fReserved3
        + fReserved4
        + fReserved5
        + fDeviceCapabilities
    )


class FEPage16(AntPage):
    """Page 16 contains generic trainer information."""

    data_page_number = 16
    EquipmentType = 0x19  # Trainer

    # Old: Capabilities = 0x30 | 0x03 | 0x00 | 0x00 # IN_USE | HRM | Distance | Speed
    #               bit  7......0   #185 Rewritten as below for better documenting bit-pattern
    HRM = 0b00000011  # 0b____ __xx bits 0-1  3 = hand contact sensor    (2020-12-28: Unclear why this option chosen)
    Distance = 0b00000000  # 0b____ _x__ bit 2     0 = No distance in byte 3  (2020-12-28: Unclear why this option chosen)
    VirtualSpeedFlag = 0b00000000  # 0b____ x___ bit 3     0 = Real speed in byte 4/5 (2020-12-28: Could be virtual speed)
    FEstate = 0b00110000  # 0b_xxx ____ bits 4-6  3 = IN USE
    LapToggleBit = 0b00000000  # 0bx___ ____ bit 7     0 = No lap toggle

    Capabilities = HRM | Distance | VirtualSpeedFlag | FEstate | LapToggleBit

    fChannel = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fEquipmentType = sc.unsigned_char
    fElapsedTime = sc.unsigned_char
    fDistanceTravelled = sc.unsigned_char
    fSpeed = sc.unsigned_short
    fHeartRate = sc.unsigned_char
    fCapabilities = sc.unsigned_char

    message_format = (
        sc.no_alignment
        + fChannel
        + fDataPageNumber
        + fEquipmentType
        + fElapsedTime
        + fDistanceTravelled
        + fSpeed
        + fHeartRate
        + fCapabilities
    )


class FEPage25(AntPage):
    """Page 25 contains specific trainer information."""

    data_page_number = 25

    Flags = 0x30  # Hmmm.... leave as is but do not understand the value

    fChannel = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fEvent = sc.unsigned_char
    fCadence = sc.unsigned_char
    fAccPower = sc.unsigned_short
    fInstPower = sc.unsigned_short  # The first four bits have another meaning!!
    fFlags = sc.unsigned_char

    format = (
        sc.no_alignment
        + fChannel
        + fDataPageNumber
        + fEvent
        + fCadence
        + fAccPower
        + fInstPower
        + fFlags
    )

    @classmethod
    def page(cls, *args):
        args = args + (cls.Flags)
        return super(FEPage25, cls).page()


class Page80(AntPage):
    """Page 80 contains manufacturer information."""

    data_page_number = 80

    fChannel = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fReserved1 = sc.unsigned_char
    fReserved2 = sc.unsigned_char
    fHWrevision = sc.unsigned_char
    fManufacturerID = sc.unsigned_short
    fModelNumber = sc.unsigned_short

    message_format = (
        sc.no_alignment
        + fChannel
        + fDataPageNumber
        + fReserved1
        + fReserved2
        + fHWrevision
        + fManufacturerID
        + fModelNumber
    )


class Page81(AntPage):
    """Page 81 contains device information."""

    data_page_number = 81

    fChannel = sc.unsigned_char  # First byte of the ANT+ message content
    fDataPageNumber = sc.unsigned_char  # First byte of the ANT+ datapage (payload)
    fReserved1 = sc.unsigned_char
    fSWrevisionSupp = sc.unsigned_char
    fSWrevisionMain = sc.unsigned_char
    fSerialNumber = sc.unsigned_int

    message_format = (
        sc.no_alignment
        + fChannel
        + fDataPageNumber
        + fReserved1
        + fSWrevisionSupp
        + fSWrevisionMain
        + fSerialNumber
    )
