"""Provide interface for communicating as ANT+ fitness equipment."""
# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2023-04-16"
# 2023-04-16    Rewritten in class based fashion
# 2023-04-15    Improve flake8 compliance
# 2020-12-28    accumulated_power not negative
# 2020-12-27    Interleave and EventCount more according specification
#               see comment in antPWR.py for more info.
# 2020-05-07    devAntDongle not needed, not used
# 2020-05-07    pylint error free
# 2020-02-18    First version, split-off from FortiusAnt.py
# -------------------------------------------------------------------------------
import time

from fortius_ant.antDongle import (
    msgUnpage48_BasicResistance,
    msgUnpage49_TargetPower,
    msgUnpage50_WindResistance,
    msgUnpage51_TrackResistance,
    msgPage54_FE_Capabilities,
    msgUnpage55_UserConfiguration,
    msgUnpage70_RequestDataPage,
    msgPage71_CommandStatus,
)
from fortius_ant.antInterface import AntInterface, UnknownDataPage, UnsupportedPage
from fortius_ant.antMessage import AntMessage, Manufacturer_tacx, msgID_BroadcastData
from fortius_ant.antPage import Page80, Page81, Page82, FEPage16, FEPage25
from fortius_ant import debug, logfile

ModelNumber_FE = 2875  # short antifier-value=0x8385, Tacx Neo=2875
SerialNumber_FE = 19590705  # int   1959-7-5
HWrevision_FE = 1  # char
SWrevisionMain_FE = 1  # char
SWrevisionSupp_FE = 1  # char

channel_FE = 0  # ANT+ channel for Fitness Equipment
DeviceTypeID_fitness_equipment = 17


class AntFE(AntInterface):
    """Interface for communicating as an ANT+ Fitness Equipment."""

    interleave_reset = 256
    channel = channel_FE
    device_type_id = DeviceTypeID_fitness_equipment

    def __init__(self, master=True):
        super().__init__(master)
        self.interleave = None
        self.event_count = None
        self.accumulated_power = None
        self.accumulated_time = None
        self.distance_travelled = None
        self.accumulated_last_time = None
        self.initialize()

    def initialize(self):
        """Initialize values to zero."""
        super().initialize()
        self.interleave = 0
        self.event_count = 0
        self.accumulated_power = 0
        self.accumulated_time = 0
        self.distance_travelled = 0
        self.accumulated_last_time = time.time()

    def broadcast_message(self, *args):
        """Assemble the message to be sent."""
        message = self._broadcast_message(self.interleave, *args)
        self.interleave += 1
        if self.interleave == self.interleave_reset:
            self.interleave = 0
        return message

    def broadcast_message_from_trainer(self):
        """Broadcast trainer data as ANT+ FE device."""
        return self.broadcast_message(
            self.trainer.Cadence,
            self.trainer.CurrentPower,
            self.trainer.SpeedKmh,
            self.trainer.HeartRate,
        )

    def _broadcast_message(  # noqa PLW221
        self, interleave: int, Cadence, CurrentPower, SpeedKmh, HeartRate
    ):
        CurrentPower = max(0, CurrentPower)  # Not negative
        CurrentPower = min(4093, CurrentPower)  # Limit to 4093
        Cadence = min(253, Cadence)  # Limit to 253

        if interleave % 64 in (
            30,
            31,
        ):  # After 10 blocks of three messages, then 2 = 32 messages
            # -----------------------------------------------------------------------
            # Send first and second manufacturer's info packet
            #      FitSDKRelease_20.50.00.zip
            #      profile.xlsx
            #      D00001198_-_ANT+_Common_Data_Pages_Rev_3.1%20.pdf
            #      page 28 byte 4,5,6,7- 15=dynastream, 89=tacx
            # -----------------------------------------------------------------------
            # comment = "(Manufacturer's info packet)"
            page = Page80.page(
                channel_FE,
                0xFF,
                0xFF,
                HWrevision_FE,
                Manufacturer_tacx,
                ModelNumber_FE,
            )

        elif interleave % 64 in (
            62,
            63,
        ):  # After 10 blocks of three messages, then 2 = 32 messages
            # -----------------------------------------------------------------------
            # Send first and second product info packet
            # -----------------------------------------------------------------------
            # comment = "(Product info packet)"
            page = Page81.page(
                channel_FE,
                0xFF,
                SWrevisionSupp_FE,
                SWrevisionMain_FE,
                SerialNumber_FE,
            )

        elif interleave % 3 == 0:
            # -----------------------------------------------------------------------
            # Send general fe data every 3 packets
            # -----------------------------------------------------------------------
            t = time.time()
            ElapsedTime = t - self.accumulated_last_time  # time since previous event
            self.accumulated_last_time = t
            self.accumulated_time += ElapsedTime * 4  # in 0.25s

            Speed = SpeedKmh * 1000 / 3600  # convert SpeedKmh to m/s
            Speed = Speed * 1000
            Speed = int(min(0xFFFF, Speed))
            Distance = ElapsedTime * Speed  # meters
            self.distance_travelled += Distance  # meters
            HeartRate = int(min(0xFF, HeartRate))

            self.accumulated_time = (
                int(self.accumulated_time) & 0xFF
            )  # roll-over at 255 (64 seconds)
            self.distance_travelled = (
                int(self.distance_travelled) & 0xFF
            )  # roll-over at 255

            # comment = "(General fe data)"
            page = FEPage16.page(
                channel_FE,
                self.accumulated_time,
                self.distance_travelled,
                Speed,
                HeartRate,
            )

        else:
            self.event_count += 1
            self.accumulated_power += max(0, CurrentPower)  # No decrement allowed

            self.event_count = int(self.event_count) & 0xFF  # roll-over at 255
            self.accumulated_power = (
                int(self.accumulated_power) & 0xFFFF
            )  # roll-over at 65535

            # -----------------------------------------------------------------------
            # Send specific trainer data
            # -----------------------------------------------------------------------
            # comment = "(Specific trainer data)"
            page = FEPage25.page(
                channel_FE,
                self.event_count,
                Cadence,
                self.accumulated_power,
                CurrentPower,
            )
        # -------------------------------------------------------------------------
        # Return message to be sent
        # -------------------------------------------------------------------------
        return AntMessage.compose(msgID_BroadcastData, page)

    def _handle_broadcast_message(self, data_page_number: int, info: bytes):
        pass

    def _handle_aknowledged_message(self, data_page_number, info):
        self.received_data.ant_event = True
        self.received_data.CTP_command_time = time.time()
        # -------------------------------------------------------
        # Data page 48 (0x30) Basic resistance
        # -------------------------------------------------------
        if data_page_number == 48:
            # logfile.Console('Data page 48 Basic mode not implemented')
            # I never saw this appear anywhere (2020-05-08)
            # TargetMode            = mode_Basic
            # TargetGradeFromDongle = 0
            # TargetPowerFromDongle = ant.msgUnpage48_BasicResistance(info) * 1000
            # n % of maximum of 1000Watt

            # 2020-11-04 as requested in issue 119
            # The percentage is used to calculate grade 0...20%
            Grade = msgUnpage48_BasicResistance(info) * 20

            # Implemented for Magnetic Brake:
            # - grade is NOT shifted with GradeShift (here never negative)
            # - but is reduced with factor
            # - and is NOT reduced with factorDH since never negative
            Grade *= self.clv.GradeFactor

            self.trainer.SetGrade(Grade)
            self.trainer.SetRollingResistance(0.004)
            self.trainer.SetWind(0.51, 0.0, 1.0)

            # Update "last command" data in case page 71 is requested later
            self.p71_LastReceivedCommandID = data_page_number
            # wrap around after 254 (255 = no command received)
            self.p71_SequenceNr = (self.p71_SequenceNr + 1) % 255
            self.p71_CommandStatus = 0  # successfully processed
            # echo raw command data (cannot use unpage, unpage does unit conversion etc)
            self.p71_Data2 = 0xFF
            self.p71_Data3 = 0xFF
            self.p71_Data4 = info[8]  # target resistance
            return None
        # -------------------------------------------------------
        # Data page 49 (0x31) Target Power
        # -------------------------------------------------------
        if data_page_number == 49:
            self.trainer.SetPower(msgUnpage49_TargetPower(info))
            TargetPowerTime = time.time()
            if self.clv.PowerMode and debug.on(debug.Application):
                logfile.Write("PowerMode: TargetPower info received - timestamp set")

            # Update "last command" data in case page 71 is requested later
            self.p71_LastReceivedCommandID = data_page_number
            # wrap around after 254 (255 = no command received)
            self.p71_SequenceNr = (self.p71_SequenceNr + 1) % 255
            self.p71_CommandStatus = 0  # successfully processed
            # echo raw command data (cannot use unpage, unpage does unit conversion etc)
            self.p71_Data2 = 0xFF
            self.p71_Data3 = info[7]  # target power (LSB)
            self.p71_Data4 = info[8]  # target power (MSB)
            return None
        # -------------------------------------------------------
        # Data page 50 (0x32) Wind Resistance
        # -------------------------------------------------------
        if data_page_number == 50:
            (
                WindResistance,
                WindSpeed,
                DraftingFactor,
            ) = msgUnpage50_WindResistance(info)
            self.trainer.SetWind(WindResistance, WindSpeed, DraftingFactor)

            # Update "last command" data in case page 71 is requested later
            self.p71_LastReceivedCommandID = data_page_number
            # wrap around after 254 (255 = no command received)
            self.p71_SequenceNr = (self.p71_SequenceNr + 1) % 255
            self.p71_CommandStatus = 0  # successfully processed
            # echo raw command data (cannot use unpage, unpage does unit conversion etc)
            self.p71_Data2 = info[6]  # wind resistance coefficient
            self.p71_Data3 = info[7]  # wind speed
            self.p71_Data4 = info[8]  # drafting factor
            return None
        # -------------------------------------------------------
        # Data page 51 (0x33) Track resistance
        # -------------------------------------------------------
        if data_page_number == 51:
            if self.clv.PowerMode and (time.time() - TargetPowerTime) < 30:
                # -----------------------------------------------
                # In PowerMode, TrackResistance is ignored
                #       (for xx seconds after the last power-command)
                # So if TrainerRoad is used simultaneously with
                #       Zwift/Rouvythe power commands from TR
                #       take precedence over Zwift/Rouvy and a
                #       power-training can be done while riding
                #       a Zwift/Rouvy simulation/video!
                # When TrainerRoad is finished, the Track
                #       resistance is active again
                # -----------------------------------------------
                self.received_data.PowerModeActive = " [P]"
                if debug.on(debug.Application):
                    logfile.Write("PowerMode: Grade info ignored")
            else:
                (
                    Grade,
                    RollingResistance,
                ) = msgUnpage51_TrackResistance(info)

                # -----------------------------------------------
                # Implemented when implementing Magnetic Brake:
                # [-] grade is shifted with GradeShift (-10% --> 0) ]
                # - then reduced with factor (can be re-adjusted with Virtual Gearbox)
                # - and reduced with factorDH (for downhill only)
                #
                # GradeAdjust is valid for all configurations!
                #
                # GradeShift is not expected to be used anymore,
                # and only left from earliest implementations
                # to avoid it has to be re-introduced in future again.
                # -----------------------------------------------
                Grade += self.clv.GradeShift
                Grade *= self.clv.GradeFactor
                if Grade < 0:
                    Grade *= self.clv.GradeFactorDH

                self.trainer.SetGrade(Grade)
                self.trainer.SetRollingResistance(RollingResistance)
                self.received_data.PowerModeActive = ""

            # Update "last command" data in case page 71 is requested later
            self.p71_LastReceivedCommandID = data_page_number
            # wrap around after 254 (255 = no command received)
            self.p71_SequenceNr = (self.p71_SequenceNr + 1) % 255
            self.p71_CommandStatus = 0  # successfully processed
            # echo raw command data (cannot use unpage, unpage does unit conversion etc)
            self.p71_Data2 = info[6]  # target grade (LSB)
            self.p71_Data3 = info[7]  # target grade (MSB)
            self.p71_Data4 = info[8]  # rolling resistance coefficient
            return None
        # -------------------------------------------------------
        # Data page 55 User configuration
        # -------------------------------------------------------
        if data_page_number == 55:
            (
                UserWeight,
                BicycleWeight,
                BicycleWheelDiameter,
                GearRatio,
            ) = msgUnpage55_UserConfiguration(info)
            self.trainer.SetUserConfiguration(
                UserWeight,
                BicycleWeight,
                BicycleWheelDiameter,
                GearRatio,
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
            if RequestedPageNumber == 54:
                # Capabilities;
                # bit 0 = Basic mode
                # bit 1 = Target/Power/Ergo mode
                # bit 2 = Simulation/Restance/Slope mode
                info = msgPage54_FE_Capabilities(
                    self.channel, 0xFF, 0xFF, 0xFF, 0xFF, 1000, 0x07
                )

            elif RequestedPageNumber == 71:
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

            elif RequestedPageNumber == 80:
                info = Page80.page(
                    self.channel,
                    0xFF,
                    0xFF,
                    HWrevision_FE,
                    Manufacturer_tacx,
                    ModelNumber_FE,
                )

            elif RequestedPageNumber == 81:
                info = Page81.page(
                    self.channel,
                    0xFF,
                    SWrevisionSupp_FE,
                    SWrevisionMain_FE,
                    SerialNumber_FE,
                )

            elif RequestedPageNumber == 82:
                info = Page82.page(self.channel)

            else:
                raise UnsupportedPage(RequestedPageNumber)

            if info is not False:
                data = []
                d = AntMessage.compose(msgID_BroadcastData, info)
                while NrTimes:
                    data.append(d)
                    NrTimes -= 1
                return (data, False, False, False)
            return None
        # -------------------------------------------------------
        # Data page 252 ????
        # -------------------------------------------------------
        if data_page_number == 252 and debug.on(debug.Data1):
            logfile.Write(f"FE data page 252 ignored. info={logfile.HexSpace(info)}")
            return None
        # -------------------------------------------------------
        # Other data pages
        # -------------------------------------------------------
        raise UnknownDataPage(data_page_number)


fe = AntFE()
Interleave = fe.interleave


def BroadcastTrainerDataMessage(*args):
    """Used for compatibility with old implementation, to be updated."""
    global Interleave
    fe.interleave = Interleave
    rtn = fe.broadcast_message(*args)
    Interleave = fe.interleave
    return rtn


def Initialize():
    fe.initialize()
