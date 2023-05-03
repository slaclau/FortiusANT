"""Provide interface for communicating as ANT+ speed and cadence sensor."""
# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2023-04-16"
# 2023-04-16    Rewritten in class based fashion
# 2023-04-15    Improve flake8 compliance
# 2020-12-27    Rollover more according specification
# 2020-06-16    Modified: device-by-zero due to zero Cadence/SpeedKmh
# 2020-06-09    First version, based upon antHRM.py
# -------------------------------------------------------------------------------
from fortius_ant.antInterface import AntInterface
from fortius_ant.antMessage import AntMessage, msgID_BroadcastData
from fortius_ant.antPage import SCSPage
from fortius_ant.usbTrainer import clsTacxTrainer

channel_SCS = 3  # ANT+ Channel for Speed Cadence Sensor
DeviceTypeID_bike_speed_cadence = 121

class AntSCS(AntInterface):
    """Interface for communicating as a speed and cadence sensor."""

    interleave_reset = 0
    channel = channel_SCS
    device_type_id = DeviceTypeID_bike_speed_cadence

    def __init__(self, master=True):
        super().__init__(master)
        self.pedal_echo_previous_count = None  # There is no previous
        self.cadence_event_time = None  # Initiate the even variables
        self.cadence_event_count = None
        self.speed_event_time = None
        self.speed_event_count = None
        self.initialize()

    def initialize(self):
        self.pedal_echo_previous_count = 0  # There is no previous
        self.cadence_event_time = 0  # Initiate the even variables
        self.cadence_event_count = 0
        self.speed_event_time = 0
        self.speed_event_count = 0

    def broadcast_message_from_trainer(self, TacxTrainer: clsTacxTrainer):
        return broadcast_message(
            TacxTrainer.PedalEchoTime,
            TacxTrainer.PedalEchoCount,
            TacxTrainer.SpeedKmh,
            TacxTrainer.Cadence,
        )

    def _broadcast_message(
        self, interleave: int, _PedalEchoTime, PedalEchoCount, SpeedKmh, Cadence
    ):
        if (
            PedalEchoCount != self.pedal_echo_previous_count
            and Cadence > 0
            and SpeedKmh > 0
        ):
            # ---------------------------------------------------------------------
            # Cadence variables
            # Based upon the number of pedal-cycles that are done and the given
            # cadence, calculate the elapsed time.
            # _PedalEchoTime is not used, because that give rounding errors and
            # an instable reading.
            # ---------------------------------------------------------------------
            PedalCycles = PedalEchoCount - self.pedal_echo_previous_count
            ElapsedTime = (
                PedalCycles / Cadence * 60
            )  # count / count/min * seconds/min = seconds
            self.cadence_event_time += ElapsedTime * 1024  # 1/1024 seconds
            self.cadence_event_count += PedalCycles

            # ---------------------------------------------------------------------
            # Speed variables
            # First calculate how many wheel-cycles can be done
            # Then (based upon rounded #of cycles) calculate the elapsed time
            # ---------------------------------------------------------------------
            Circumference = 2.096  # Note: SimulANT has 2.070 as default
            WheelCadence = (
                SpeedKmh / 3.6 / Circumference
            )  # km/hr / kseconds/hr / meters  = cycles/s
            WheelCycles = round(
                ElapsedTime * WheelCadence, 0
            )  # seconds * /s                  = cycles

            ElapsedTime = WheelCycles / SpeedKmh * 3.6 * Circumference
            self.speed_event_time += ElapsedTime * 1024
            self.speed_event_count += WheelCycles

        # -------------------------------------------------------------------------
        # Rollover after 0xffff
        # -------------------------------------------------------------------------
        self.cadence_event_time = (
            int(self.cadence_event_time) & 0xFFFF
        )  # roll-over at 65535 = 64 seconds
        self.cadence_event_count = (
            int(self.cadence_event_count) & 0xFFFF
        )  # roll-over at 65535
        self.speed_event_time = (
            int(self.speed_event_time) & 0xFFFF
        )  # roll-over at 65535 = 64 seconds
        self.speed_event_count = (
            int(self.speed_event_count) & 0xFFFF
        )  # roll-over at 65535

        # -------------------------------------------------------------------------
        # Prepare for next event
        # -------------------------------------------------------------------------
        self.pedal_echo_previous_count = PedalEchoCount

        # -------------------------------------------------------------------------
        # Compose message
        # -------------------------------------------------------------------------
        page = SCSPage.page(
            channel_SCS,
            self.cadence_event_time,
            self.cadence_event_count,
            self.speed_event_time,
            self.speed_event_count,
        )
        return AntMessage.compose(msgID_BroadcastData, page)


scs = AntSCS()
Interleave = scs.interleave


def BroadcastMessage(*args):
    """Used for compatibility with old implementation, to be updated."""
    global Interleave
    scs.interleave = Interleave
    rtn = scs.broadcast_message(*args)
    Interleave = scs.interleave
    return rtn


def Initialize():
    scs.initialize()
