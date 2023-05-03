"""Provide interface for communicating as ANT+ power sensor."""
# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2023-04-16"
# 2023-04-16    Rewritten in class based fashion
# 2023-04-15    Improve flake8 compliance
# 2020-12-28    AccumulatedPower not negative
# 2020-12-27    Interleave and EventCount improved according
#               D00001086_ANT+Device_Profile-_Bicycle_Power_Rev_5.1.pdf
#               Implementation fitted to the definitions in the profile:
#               7.1 Power only sensors
#                   page 0x50 - Interleave every 121 messages
#                   page 0x51 - Interleave every 121 messages
#                   page 0x52 - Interleave every  61 messages
#               8.1 Update Event Count
#                   The update event count field is incremented each time the
#                   information in the message is updated.
#                   ...
#                   The Power-only page... must be sent each time the update
#                   event counter is incremented.
#               8.4 Accumulated power
#                   The accumulated power field rolls over at 65.535kW
#               Refer to (regarding roll over values):
#                   D000001231_-_ANT+_Device_Profile_-_Fitness_Equipment_-_Rev_5.0_(6).pdf
#                   9.1.1 Calculating accumulated values
#                       NOTE: All accumulating message fields must use only positive values. # noqa: E501 W505 PLC301
#                   9.1.2 Receiving and Calculating Data from Accumulated Values
#               Most important change: Interleave counting is separate from
#                   the AccumulatedPower related EventCount.
# 2020-06-11    First version, based upon antHRM.py
# -------------------------------------------------------------------------------
from fortius_ant.antInterface import AntInterface
from fortius_ant.antMessage import AntMessage, Manufacturer_garmin, msgID_BroadcastData
from fortius_ant.antPage import Page80, Page81, Page82, PWRPage16
from fortius_ant.usbTrainer import clsTacxTrainer

ModelNumber_PWR = 2161  # Garmin Vector 2 (profile.xlsx, garmin_product)
SerialNumber_PWR = 19570702  # int   1957-7-2
HWrevision_PWR = 1  # char
SWrevisionMain_PWR = 1  # char
SWrevisionSupp_PWR = 1  # char

channel_PWR = 2  # ANT+ Channel for Power Profile
DeviceTypeID_bike_power = 11

class AntPWR(AntInterface):
    """Interface for communicating as an ANT+ power sensor."""

    interleave_reset = 121
    
    channel = channel_PWR
    device_type_id = DeviceTypeID_bike_power

    def __init__(self, master=True):
        super().__init__(master)
        self.interleave = None
        self.accumulated_power = None
        self.event_count = None
        self.initialize()

    def initialize(self):
        self.interleave = 0
        self.accumulated_power = 0
        self.event_count = 0

    def broadcast_message_from_trainer(self, TacxTrainer: clsTacxTrainer):
        return broadcast_message(TacxTrainer.CurrentPower, TacxTrainer.Cadence)

    def _broadcast_message(self, interleave: int, CurrentPower: float, Cadence: float):
        Cadence = int(min(0xFF, Cadence))
        CurrentPower = int(max(0, min(0x0FFF, CurrentPower)))  # 2021-02-19
        if interleave == 61:  # Transmit page 0x52 = 82
            page = Page82.page(channel_PWR)

        elif interleave == 120:  # Transmit page 0x50 = 80
            page = Page80.page(
                channel_PWR,
                0xFF,
                0xFF,
                HWrevision_PWR,
                Manufacturer_garmin,
                ModelNumber_PWR,
            )

        elif interleave == 121:  # Transmit page 0x51 = 81
            page = Page81.page(
                channel_PWR,
                0xFF,
                SWrevisionSupp_PWR,
                SWrevisionMain_PWR,
                SerialNumber_PWR,
            )

        else:
            self.event_count += 1
            self.accumulated_power += max(0, CurrentPower)  # No decrement allowed

            self.event_count = int(self.event_count) & 0xFF  # roll-over at 255
            self.accumulated_power = (
                int(self.accumulated_power) & 0xFFFF
            )  # roll-over at 65535

            page = PWRPage16.page(
                channel_PWR,
                self.event_count,
                Cadence,
                self.accumulated_power,
                CurrentPower,
            )

        return AntMessage.compose(msgID_BroadcastData, page)


pwr = AntPWR()
Interleave = pwr.interleave


def BroadcastMessage(*args):
    """Used for compatibility with old implementation, to be updated."""
    global Interleave
    pwr.interleave = Interleave
    rtn = pwr.broadcast_message(*args)
    Interleave = pwr.interleave
    return rtn


def Initialize():
    pwr.initialize()
