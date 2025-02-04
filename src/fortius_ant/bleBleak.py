# -------------------------------------------------------------------------------
# Description
# -------------------------------------------------------------------------------
# The bleak library enables python programs to access Bluetooth Low Energy
# as a client. In out context, a Cycling Training Program is a client and the
# Tacx Trainer is the server (FTMS FiTness Machine Server)
#
# In the FortiusAnt context, we do not need to create a client, because CTP's
# (like Trainer Road and Zwift) are the client. The reason to have this program
# is to be able to debug FortiusAnt (ble-mode). This could be done using standard
# test-programs. But coding a test-client, exactly to the functionality we need,
# makes us understand how ble works and allows us to test each individual
# element of the interface.
#
# This program does the following:
# 1. findBLEdevices() check what ble-FTMS devices are alive
# 2. serverInspection() prints all data of the FTMS device that is found
#  2a. Open the server as client
#  2b. Print the server, service, characteristics and descriptions structure
#  Then:
#  2c. Register to receive notifications and indications
#      Notifications are messages that are sent on server-initiative
#      Indications   are responses to actions we do
#  2d. The we simulate a CTP.
#      We send a request to the server and wait for a response in a sequence:
#    2dI.   Request Control = ask permission that we are allowed to proceed
#    2dII.  Start           = start a training session
#    2dIII. Power/GradeMode = request trainer to provide a resistance, either
#                             expressed in Watt or Slope%
#    2dIV.  Stop            = end training session
#    2dV.   Reset           = release access
#  2e. Unregister notifications and indications
#
# This program can be used as follows:
# 1. Start FortiusAnt.py -g -a -s -b (gui, autostart, simulation, bluetooth)
#       FortiusAnt will now listen for commands, no trainer is required (-s)
#       and dispplay what is going on on the user-interface
# 2. Start bleBleak.py
#       You will see that "a CTP" session is running, requesting:
#       325 Watt, 5%, 324 Watt, 4%, ..., 320 Watt, 0%, 50Watt
#
# And of course, in this way, we can automatically test FortiusAnt in ble-mode
#
# NOTES:
# - The code is quite lineair and not in classes; the code is not intended to
#   provide a basis for usages in larger environments but serves as a demo/test
#   only
# -------------------------------------------------------------------------------
# Author        https://github.com/WouterJD
#               wouter.dubbeldam@xs4all.nl
# -------------------------------------------------------------------------------
# Version info
# -------------------------------------------------------------------------------
__version__ = "2022-12-28"
# 2022-12-28    bleak does no longer support __version__
# 2022-03-21    Made available to kevincar/bless as example; small modifications
# 2022-03-16    bleBleak.py works on Windows 10
#               - sometimes the BLE dongle must be reset (remove/insert)
#               - sometimes indications are not received
#                   This SEEMS to have gone since Try/Except is used (?)
# 2022-03-16    retries in discovery and finding client introduced.
# 2022-03-14    read_gatt_char() accepts UUID or HANDLE,
#               Tests with Tacx NEO show that duplicate UUID's exist, so
#                   handle is used as input.
# 2022-02-22    bleBleak.py works on rpi0W with raspbian v10 buster
# 2022-02-21    Version rebuilt to be able to validate the FortiusAnt/BLE
#               implementation and I expect you could 'look' at an existing
#               Tacx-trainer as well, but did not try that.
#
#               FortiusAnt/BLE using NodeJS does not transmit:
#               - the trainer speed in the FTMS
#
# 2020-12-18    First version, obtained from: " hbldh\bleak"
#               Service Explorer
#               ----------------
#               An example showing how to access and print out the services,
#               characteristics anddescriptors of a connected GATT server.
#
#               Created on 2019-03-25 by hbldh <henrik.blidh@nedomkull.com>
# -------------------------------------------------------------------------------
import asyncio
import logging
import os
import struct
from socket import timeout

from bleak import BleakClient, discover

# from bleak import __version__ as bleakVersion      # No longer supported; #408
# print("bleak = %s" % bleakVersion)


if True:
    BlessExample = False
    # ---------------------------------------------------------------------------
    # Import in the FortiusAnt context
    # ---------------------------------------------------------------------------
    import fortius_ant.bleConstants as bc
    from fortius_ant.bleBlessClass import clsBleServer
    from fortius_ant.constants import UseBluetooth, mode_Grade, mode_Power
    from fortius_ant.logfile import HexSpace

else:
    BlessExample = True
    # ---------------------------------------------------------------------------
    # Import and Constants for bless example context
    # ---------------------------------------------------------------------------
    import FTMSconstants as bc
    from FTMSconstants import HexSpace

# -------------------------------------------------------------------------------
# Status mar 2022:
# -------------------------------------------------------------------------------
# Notes on Windows 10 Pro, version 21H2, build 19044.1526
#                          Windows Feature Experience Pack 120.2212.4170.0
# - no BLE device: "await discover()" does not return devices and no error.
# - standard "Thinkpad bluetooth 4.0" adaptor: indications are not received
# - Realtek Bluetooth 5.0 adaptor:             same
#
# When indications are not received, the simulation loop does not work
# -------------------------------------------------------------------------------
# Tested on:
# 1. Raspberry rpi0W with Raspbian version (10) buster
# 2. Windows 10 (for version see above)
# --> bleBleak.py works; sample output added to end-of-this-file.
# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
# ADDRESSES: Returned by findBLEdevices()
# -------------------------------------------------------------------------------
global ADDRESSES
ADDRESSES = []  # The address appears appear to change continuously

# -------------------------------------------------------------------------------
# Status-fields of the Fitness Machine
# -------------------------------------------------------------------------------
global cadence, hrm, power, speed, status
cadence, hrm, power, speed, status = (0, 0, 0, 0, "initial")

# -------------------------------------------------------------------------------
# FitnessMachineControlPoint indicated response fields
# -------------------------------------------------------------------------------
global ResultCode, ResultCodeText
ResultCode, ResultCodeText = (None, None)


# -------------------------------------------------------------------------------
# f i n d B L E D e v i c e s
# -------------------------------------------------------------------------------
# Input:    bleak devices
#
# Function  Discover existing devices and return list of addresses
#
# Output:   ADDRESSES
# -------------------------------------------------------------------------------
async def findBLEdevices():
    global ADDRESSES
    print("-------------------------------")
    print(" Discover existing BLE devices ")
    print("-------------------------------")
    retry = 5
    while retry:
        devices = await discover()
        if len(devices):
            break
        else:
            retry -= 1
            print("No devices found, retry")

    for d in devices:
        # print('d -----------------------------')
        # print('\n'.join("%s: %s" % item for item in vars(d).items()))
        # print('d --------------------------end')
        ftms = True  # Defines what to do with unknown devices
        try:
            # The following are NOT fitness machines (saves inspection time)
            if "Forerunner" in d.name or "Garmin" in d.name:
                ftms = False

            # The following ARE fitness machines
            if (
                bc.sFitnessMachineUUID in d.metadata["uuids"]
                or "FortiusANT" in d.name
                or d.name == "Unknown"
                or d.name[:3] == "LT-"
            ):
                ftms = True

        except Exception as e:
            pass
        if ftms:
            ADDRESSES.append(d.address)  # It's a candidate, more checks later
            print(d, "will be inspected")
        else:
            print(d)


# -------------------------------------------------------------------------------
# s e r v e r I n s p e c t i o n
# -------------------------------------------------------------------------------
# Input:    address
#
# Function  Inspect structure of the provided server
#
# Output:   Console
# -------------------------------------------------------------------------------
async def serverInspection(address):
    print("---------------------------------------------------")
    print(" Inspect BLE-device with address %s" % address)
    print("---------------------------------------------------")
    retry = 5
    while retry:
        try:
            async with BleakClient(address) as client:  # , timeout=100
                await serverInspectionSub(client)
            break
        except Exception as e:
            if "TimeoutError" in str(type(e)):
                print("Timeout, retry")
                retry -= 1
            else:
                print(type(e), e)
                break


async def serverInspectionSub(client):
    print("Connected: ", client.is_connected)
    # print('client -----------------------------')
    # print('\n'.join("%s: %s" % item for item in vars(client).items()))
    # print('client --------------------------end')

    # ---------------------------------------------------------------------------
    # Get Generic Access Profile
    # This service is not always available in client.services, but the
    # characteristics can always be retrieved.
    # See issue https://github.com/hbldh/bleak/issues/782
    # ---------------------------------------------------------------------------
    try:
        sServiceDeviceName = await client.read_gatt_char(bc.cDeviceNameUUID)
        sServiceDeviceName = sServiceDeviceName.decode("ascii")
        if sServiceDeviceName == "":
            sServiceDeviceName = "<Empty>"
        print("%s=%s" % (bc.cDeviceNameName, sServiceDeviceName))
    except Exception as e:
        sServiceDeviceName = "<Unknown name>"
        print("Characteristic %s error=%s" % (bc.cDeviceNameName, e))

    try:
        Appearance = await client.read_gatt_char(bc.cAppearanceUUID)
        print("%s=%s" % (bc.cAppearanceName, Appearance))
    except Exception as e:
        Appearance = None
        print("Characteristic %s error=%s" % (bc.cAppearanceName, e))

    # ---------------------------------------------------------------------------
    # Check whether this service is a Fitness Machine
    # by inspecting the FitnessMachineFeature characteristic.
    # ---------------------------------------------------------------------------
    bFitnessMachine = False
    sFitnessMachine = "NOT "

    try:
        value = bytes(await client.read_gatt_char(bc.cFitnessMachineFeatureUUID))
    except Exception as e:
        print("Characteristic %s error=%s" % (bc.cFitnessMachineFeatureName, e))
        value = None
    else:
        # -----------------------------------------------------------------------
        # If present with expected length (otherwise unpack crashes)
        # check if the expected flagsd are present.
        # -----------------------------------------------------------------------
        if len(value) == 8:
            tuple = struct.unpack(bc.little_endian + bc.unsigned_long * 2, value)
            cFitnessMachineFeatureFlags1 = tuple[0]
            cFitnessMachineFeatureFlags2 = tuple[1]

            if (
                cFitnessMachineFeatureFlags1 & bc.fmf_CadenceSupported
                and cFitnessMachineFeatureFlags1 & bc.fmf_PowerMeasurementSupported
                and cFitnessMachineFeatureFlags2 & bc.fmf_PowerTargetSettingSupported
                and cFitnessMachineFeatureFlags2
                & bc.fmf_IndoorBikeSimulationParametersSupported
            ):
                bFitnessMachine = True
                sFitnessMachine = ""

    print(
        "%s: This is %sa matching Fitness Machine"
        % (sServiceDeviceName, sFitnessMachine)
    )

    # ---------------------------------------------------------------------------
    # Inspect the Fitness Machine and print all details
    # ---------------------------------------------------------------------------
    if bFitnessMachine:
        # -----------------------------------------------------------------------
        # Inspect all services of the server
        # -----------------------------------------------------------------------
        for service in client.services:
            s = "Service: %s" % service
            s = s.replace(bc.BluetoothBaseUUIDsuffix, "-...")  # Always the same
            print(s)
            # -------------------------------------------------------------------
            # Inspect all characteristics of the service
            # -------------------------------------------------------------------
            for char in service.characteristics:
                # ---------------------------------------------------------------
                # Print characteristic, properties and value
                # ---------------------------------------------------------------
                if "read" in char.properties:
                    # -----------------------------------------------------------
                    # Use handle, which is unique by definition.
                    # (Tacx Neo caused duplicate uuid)
                    # -----------------------------------------------------------
                    try:
                        value = bytes(await client.read_gatt_char(char.handle))
                    except Exception as e:
                        value = e
                elif "notify" in char.properties:
                    value = "(N/A: Wait for notification)"  # Initiated by server
                elif "indicate" in char.properties and "write" in char.properties:
                    value = "(N/A: Wait for indication)"  # Requested by client
                else:
                    value = "(N/A; not readable)"

                if char.uuid == bc.cDeviceNameUUID:
                    s = (
                        '"' + value.decode("ascii") + '"'
                    )  # Device name should be printable
                else:
                    s = HexSpace(value)

                # ---------------------------------------------------------------
                # Get description, if known in our context
                # ---------------------------------------------------------------
                uuid = str(char.uuid)
                if uuid == bc.cDeviceNameUUID:
                    descr = bc.cDeviceNameName
                elif uuid == bc.cAppearanceUUID:
                    descr = bc.cAppearanceName

                elif uuid == bc.cFitnessMachineFeatureUUID:
                    descr = bc.cFitnessMachineFeatureName
                elif uuid == bc.cIndoorBikeDataUUID:
                    descr = bc.cIndoorBikeDataName
                elif uuid == bc.cFitnessMachineStatusUUID:
                    descr = bc.cFitnessMachineStatusName
                elif uuid == bc.cFitnessMachineControlPointUUID:
                    descr = bc.cFitnessMachineControlPointName
                elif uuid == bc.cSupportedPowerRangeUUID:
                    descr = bc.cSupportedPowerRangeName
                elif uuid == bc.cHeartRateMeasurementUUID:
                    descr = bc.cHeartRateMeasurementUUID
                else:
                    descr = "?"

                # ---------------------------------------------------------------
                # And print
                # ---------------------------------------------------------------
                s = (
                    "\tCharacteristic: uuid=%-12s (handle: %3s): %-30s, props=%s, value=%s"
                    % (char.uuid, char.handle, descr, char.properties, s)
                )
                s = s.replace(bc.BluetoothBaseUUIDsuffix, "-...")  # Always the same
                print(s)

                # ---------------------------------------------------------------
                # Inspect and print FitnessMachineFeature characteristic
                # (not used, but could be when implementing a real collector)
                # ---------------------------------------------------------------
                if char.uuid == bc.cFitnessMachineFeatureUUID and len(value) == 8:
                    tuple = struct.unpack(
                        bc.little_endian + bc.unsigned_long * 2, value
                    )
                    cFitnessMachineFeatureFlags1 = tuple[0]
                    cFitnessMachineFeatureFlags2 = tuple[1]

                    print("\t\tSupported: ", end="")
                    if cFitnessMachineFeatureFlags1 & bc.fmf_CadenceSupported:
                        print("Cadence, ", end="")
                    if (
                        cFitnessMachineFeatureFlags1
                        & bc.fmf_HeartRateMeasurementSupported
                    ):
                        print("HRM, ", end="")
                    if cFitnessMachineFeatureFlags1 & bc.fmf_PowerMeasurementSupported:
                        print("PowerMeasurement, ", end="")
                    if (
                        cFitnessMachineFeatureFlags2
                        & bc.fmf_PowerTargetSettingSupported
                    ):
                        print("PowerTargetSetting, ", end="")
                    if (
                        cFitnessMachineFeatureFlags2
                        & bc.fmf_IndoorBikeSimulationParametersSupported
                    ):
                        print("IndoorBikeSimulation", end="")
                    print(".")

                # ---------------------------------------------------------------
                # Inspect all descriptors of the characteristic
                # ---------------------------------------------------------------
                for descriptor in char.descriptors:
                    if descriptor.uuid != bc.CharacteristicUserDescriptionUUID:
                        try:
                            value = bytes(
                                await client.read_gatt_descriptor(descriptor.handle)
                            )
                        except Exception as e:
                            value = e

                        # Does not seem to provide much additional information,
                        # So commented, perhaps for later use
                        # print("\t\tDescriptor: ", descriptor.uuid, 'value=', HexSpace(value))

        # -----------------------------------------------------------------------
        # Now receive notifications and indications
        # -----------------------------------------------------------------------
        print("Register notifications")
        try:
            await client.start_notify(
                bc.cFitnessMachineStatusUUID, notificationFitnessMachineStatus
            )
        except Exception as e:
            print("Registration failed", e)

        try:
            await client.start_notify(
                bc.cHeartRateMeasurementUUID, notificationHeartRateMeasurement
            )
        except Exception as e:
            print("Registration failed", e)

        try:
            await client.start_notify(
                bc.cIndoorBikeDataUUID, notificationIndoorBikeData
            )
        except Exception as e:
            print("Registration failed", e)

        print("Register indications")
        try:
            await client.start_notify(
                bc.cFitnessMachineControlPointUUID, indicationFitnessMachineControlPoint
            )
        except Exception as e:
            print("Registration failed", e)

        print("------------------------------------------------------")
        print(" Start simulation of a Cycling Training Program (CTP) ")
        print("------------------------------------------------------")
        global ResultCode, ResultCodeText
        mode = bc.fmcp_RequestControl  # ControlPoint opcodes are used
        PowerMode = 0x0100  # Additional mode (no opcode)
        GradeMode = 0x0200
        StopMode = 0x0300
        waitmode = 0x1000  # Range outside opcodes, to indicate waiting
        CountDown = 5  # Number of cycles between PowerMode / GradeMode
        timeout = 10  # Initial value for wait
        wait = timeout  # Waiting for confirmation of response
        ResultCode = None  # No response received
        while True:
            if mode >= waitmode:
                # ---------------------------------------------------------------
                # mode contains the next step to be done + waitmode
                # Check the ResultCode first and act accordingly
                # ---------------------------------------------------------------
                if ResultCode == None:
                    print("Waiting for response on FitnessMachineControlPoint request")
                    wait -= 1  # Keep waiting
                    if not wait:
                        print("Timeout on waiting!!")
                        mode = StopMode  # Stop the loop

                elif ResultCode == bc.fmcp_Success:
                    # print('ResultCode = success, proceed')
                    mode = mode - waitmode  # Proceed with next action

                    # -----------------------------------------------------------
                    # Prepare for next wait mode
                    # -----------------------------------------------------------
                    ResultCode = None
                    wait = timeout

                else:
                    print(
                        "Error: FitnessMachineControlPoint request failed with ResultCode = %s (%s)"
                        % (ResultCode, ResultCodeText)
                    )
                    break

            elif mode == StopMode:
                # ---------------------------------------------------------------
                print("Stop collector loop")
                # ---------------------------------------------------------------
                break

            elif mode == bc.fmcp_RequestControl:
                # ---------------------------------------------------------------
                print("Request control, so that commands can be sent")
                # ---------------------------------------------------------------
                info = struct.pack(
                    bc.little_endian + bc.unsigned_char, bc.fmcp_RequestControl
                )
                await client.write_gatt_char(bc.cFitnessMachineControlPointUUID, info)

                # Wait for response and prepare next mode
                mode = bc.fmcp_StartOrResume + waitmode

            elif mode == bc.fmcp_StartOrResume:
                # ---------------------------------------------------------------
                print("Start training session")
                # ---------------------------------------------------------------
                info = struct.pack(
                    bc.little_endian + bc.unsigned_char, bc.fmcp_StartOrResume
                )
                await client.write_gatt_char(bc.cFitnessMachineControlPointUUID, info)

                # Wait for response and next mode
                mode = PowerMode + waitmode

            elif mode == PowerMode:
                CountDown -= 1
                if CountDown:
                    TargetPower = 320 + CountDown  # Watts
                else:
                    TargetPower = 50  # Watts, final power
                # ---------------------------------------------------------------
                print("Switch to PowerMode, %sW" % TargetPower)
                # ---------------------------------------------------------------
                info = struct.pack(
                    bc.little_endian + bc.unsigned_char + bc.unsigned_short,
                    bc.fmcp_SetTargetPower,
                    TargetPower,
                )
                await client.write_gatt_char(bc.cFitnessMachineControlPointUUID, info)

                # Wait for response and prepare next mode
                if CountDown:
                    mode = GradeMode + waitmode
                else:
                    mode = bc.fmcp_StopOrPause + waitmode

            elif mode == GradeMode:
                TargetGrade = CountDown  # % inclination
                windspeed = 0
                crr = 0.004  # rolling resistance coefficient
                cw = 0.51  # wind resistance coefficient
                # ---------------------------------------------------------------
                print("Switch to GradeMode, %s%%" % TargetGrade)
                # ---------------------------------------------------------------
                TargetGrade = int(TargetGrade * 100)  # Resolution 0.01
                windspeed = int(windspeed * 1000)  # Resolution 0.001
                crr = int(crr * 10000)  # Resolution 0.0001
                cw = int(cw * 100)  # Resolution 0.01
                info = struct.pack(
                    bc.little_endian
                    + bc.unsigned_char
                    + bc.short
                    + bc.short
                    + bc.unsigned_char
                    + bc.unsigned_char,
                    bc.fmcp_SetIndoorBikeSimulation,
                    windspeed,
                    TargetGrade,
                    crr,
                    cw,
                )
                await client.write_gatt_char(bc.cFitnessMachineControlPointUUID, info)

                # Wait for response and prepare next mode
                mode = PowerMode + waitmode

            elif mode == bc.fmcp_StopOrPause:
                # ---------------------------------------------------------------
                print("Stop training session")
                # ---------------------------------------------------------------
                info = struct.pack(
                    bc.little_endian + bc.unsigned_char, bc.fmcp_StopOrPause
                )
                await client.write_gatt_char(bc.cFitnessMachineControlPointUUID, info)

                # Wait for response and prepare next mode
                mode = bc.fmcp_Reset + waitmode

            elif mode == bc.fmcp_Reset:
                # ---------------------------------------------------------------
                print("Release control / reset")
                # ---------------------------------------------------------------
                info = struct.pack(bc.little_endian + bc.unsigned_char, bc.fmcp_Reset)
                await client.write_gatt_char(bc.cFitnessMachineControlPointUUID, info)

                # Wait for response and prepare next mode
                mode = StopMode + waitmode

            else:
                # ---------------------------------------------------------------
                print("Unknown mode %s" % mode)
                # ---------------------------------------------------------------

            # -------------------------------------------------------------------
            # Pause for a second before next action done
            # (If next action is wait, only 0.1 second)
            # -------------------------------------------------------------------
            if mode >= waitmode:
                await asyncio.sleep(0.1)  # When waiting, short timeout
            else:
                await asyncio.sleep(1)  # Next action after a second

        # -----------------------------------------------------------------------
        # Stop receiving notifications and indications
        # -----------------------------------------------------------------------
        print("Unregister notifications")
        try:
            await client.stop_notify(bc.cFitnessMachineStatusUUID)
        except Exception as e:
            pass
        try:
            await client.stop_notify(bc.cHeartRateMeasurementUUID)
        except Exception as e:
            pass
        try:
            await client.stop_notify(bc.cIndoorBikeDataUUID)
        except Exception as e:
            pass

        print("Unregister indications")
        try:
            await client.stop_notify(bc.cFitnessMachineControlPointUUID)
        except Exception as e:
            pass


# -------------------------------------------------------------------------------
# n o t i f i c a t i o n   A N D   i n d i c a t i o n   H a n d l e r s
# -------------------------------------------------------------------------------
# Input:    handle, data
#
# Function  Notification handler to print the notified data
#
# Output:   Console
#           HeartRateMeasurement; hrm
#           IndoorBikeData;       cadence, hrm, speed, power
# -------------------------------------------------------------------------------
def indicationFitnessMachineControlPoint(handle, data):
    global ResultCode, ResultCodeText

    if len(data) >= 1:
        ResponseCode = int(data[0])  # Always 0x80
    if len(data) >= 2:
        RequestCode = int(data[1])  # The requested OpCode
    if len(data) >= 3:
        ResultCode = int(data[2])  # e.g. fmcp_Success
    # ResponseParameter not implemented, variable format

    if ResultCode == bc.fmcp_Success:
        ResultCodeText = "Succes"
    elif ResultCode == bc.fmcp_OpCodeNotSupported:
        ResultCodeText = "OpCodeNotSupported"
    elif ResultCode == bc.fmcp_InvalidParameter:
        ResultCodeText = "InvalidParameter"
    elif ResultCode == bc.fmcp_OperationFailed:
        ResultCodeText = "OperationFailed"
    elif ResultCode == bc.fmcp_ControlNotPermitted:
        ResultCodeText = "ControlNotPermitted"
    else:
        ResultCodeText = "?"

    if True:  # For debugging only
        print(
            "%s %s %s ResponseCode=%s RequestCode=%s ResultCode=%s(%s)"
            % (
                handle,
                bc.cFitnessMachineControlPointName,
                HexSpace(data),
                ResponseCode,
                RequestCode,
                ResultCode,
                ResultCodeText,
            )
        )


def notificationFitnessMachineStatus(handle, data):
    global status
    OpCode = int(data[0])
    # ResponseParameter not implemented, variable format

    if OpCode == bc.fms_Reset:
        status = "Reset"
    elif OpCode == bc.fms_FitnessMachineStoppedOrPausedByUser:
        status = "Stopped"  # or Paused
    elif OpCode == bc.fms_FitnessMachineStartedOrResumedByUser:
        status = "Started"  # or Resumed
    elif OpCode == bc.fms_TargetPowerChanged:
        status = "Power mode"
    elif OpCode == bc.fms_IndoorBikeSimulationParametersChanged:
        status = "Grade mode"
    else:
        status = "?"

    notificationPrint(handle, bc.cFitnessMachineStatusName, data)


def notificationHeartRateMeasurement(handle, data):
    global cadence, hrm, speed, power
    if len(data) == 2:
        tuple = struct.unpack(bc.little_endian + bc.unsigned_char * 2, data)
        flags = tuple[0]
        hrm = tuple[1]
    else:
        print("Error in notificationHeartRateMeasurement(): unexpected data length")

    notificationPrint(handle, bc.cHeartRateMeasurementName, data)


def notificationIndoorBikeData(handle, data):
    global cadence, hrm, speed, power

    if len(data) in (
        4,
        6,
        8,
        10,
    ):  # All flags should be implemented; only this set done!!
        tuple = struct.unpack(
            bc.little_endian + bc.unsigned_short * int(len(data) / 2), data
        )
        flags = tuple[0]
        speed = tuple[1] / 100  # always present, transmitted in 0.01 km/hr
        n = 2
        if flags & bc.ibd_InstantaneousCadencePresent:
            cadence = int(tuple[n] / 2)  # Because transmitted in BLE in half rpm
            n += 1
        if flags & bc.ibd_InstantaneousPowerPresent:
            power = tuple[n]
            n += 1
        if flags & bc.ibd_HeartRatePresent:
            hrm = tuple[n]
            n += 1
    else:
        print("Error in notificationIndoorBikeData(): unexpected data length")

    notificationPrint(handle, bc.cIndoorBikeDataName, data)


# -------------------------------------------------------------------------------
# n o t i f i c a t i o n P r i n t
# -------------------------------------------------------------------------------
# Input:    globals
#
# Function  After receiving a notification or indication, print info on FTMS
#
# Output:   printed info
# -------------------------------------------------------------------------------
def notificationPrint(handle, uuidName, data):
    global cadence, hrm, speed, power, status

    print(
        "%s %-22s %-25s status=%-10s speed=%4.1f cadence=%3s power=%4s hrm=%3s"
        % (
            handle,
            uuidName,
            HexSpace(data),
            status,
            round(speed, 1),
            cadence,
            power,
            hrm,
        )
    )


if __name__ == "__main__":
    # ---------------------------------------------------------------------------
    # Introduction
    # ---------------------------------------------------------------------------
    print(
        "bleBleak.py is used to show the characteristics of a running FTMS (Fitness Machine Service)."
    )
    print(
        "FortiusAnt (BLE) provides such an FTMS and a Cycling Training Program is a client for that service."
    )
    print(
        "Note that, when a CTP is active, FortiusAnt will not be discovered because it is in use."
    )
    print("")
    print("After having displayed the characteristics, a CTP-simulation is done.")
    print(
        "- Commands are sent to the FTMS: RequestControl, Start, Power/Grade, Stop and Reset"
    )
    print(
        "- PowerMode/GradeMode is done 5 times, setting the different targets alternatingly"
    )
    print("While performing above requests, the results from the FTMS are displayed.")
    print("")
    print("In this way, the FortiusAnt BLE-interface can be tested:")
    print("First start FortiusAnt with -g -a -s -b to activate BLE and simulation-mode")
    print("Then  start bleBleak to print the characteristics and execute the test")

    # ---------------------------------------------------------------------------
    # Initialize logger, currently straight print() used
    # Logging for bleak can be activated here
    # ---------------------------------------------------------------------------
    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.INFO)
    # logging.basicConfig(level=logging.DEBUG)

    # ---------------------------------------------------------------------------
    # First discover ADDRESSES of all possible fitness machines (1 expected)
    # ---------------------------------------------------------------------------
    asyncio.run(findBLEdevices())

    # ---------------------------------------------------------------------------
    # Now show all details of the FTMS
    # ---------------------------------------------------------------------------
    for a in ADDRESSES:
        asyncio.run(serverInspection(a))

"""

SAMPLE OUTPUT:
==============

-------------------------------
 Discover existing BLE devices
-------------------------------
No devices found, retry
B8:27:EB:0B:EA:62: Unknown will be inspected
---------------------------------------------------
 Inspect BLE-device with address B8:27:EB:0B:EA:62
---------------------------------------------------
Connected:  True
Device Name=rpiServer
Appearance=bytearray(b'\x00\x00')
rpiServer: This is a matching Fitness Machine
Service: 00001800-... (Handle: 1): Generic Access Profile
        Characteristic: uuid=00002a00-... (handle:   2): Device Name                   , props=['read'], value="rpiServer"
        Characteristic: uuid=00002a01-... (handle:   4): Appearance                    , props=['read'], value="00 00"
Service: 00001801-... (Handle: 6): Generic Attribute Profile
        Characteristic: uuid=00002a05-... (handle:   7): ?                             , props=['indicate'], value="(N/A; not readable)"
Service: 00001826-... (Handle: 331): Fitness Machine
        Characteristic: uuid=00002acc-... (handle: 332): Fitness Machine Feature       , props=['read'], value="02 40 00 00 08 20 00 00"
                Supported: Cadence, PowerMeasurement, PowerTargetSetting, IndoorBikeSimulation.
        Characteristic: uuid=00002ad2-... (handle: 334): Indoor Bike Data              , props=['notify'], value="(N/A: Wait for notification)"
        Characteristic: uuid=00002ada-... (handle: 337): Fitness Machine Status        , props=['notify'], value="(N/A: Wait for notification)"
        Characteristic: uuid=00002ad9-... (handle: 340): Fitness Machine Control Point , props=['write', 'indicate'], value="(N/A: Wait for indication)"
        Characteristic: uuid=00002ad8-... (handle: 343): Supported Power Range         , props=['read'], value="00 00 e8 03 01 00"
Register notifications
Registration failed Characteristic 00002a37-0000-1000-8000-00805f9b34fb not found!
Register indications
------------------------------------------------------
 Start simulation of a Cycling Training Program (CTP)
------------------------------------------------------
Request control, so that commands can be sent
340 Fitness Machine Control Point "80 00 01" ResponseCode=128 RequestCode=0 ResultCode=1(Succes)
334 Indoor Bike Data       "44 00 fc 53 e6 00 3b 01" status=initial    speed=215.0 cadence=115 power= 315 hrm=  0
Start training session
337 Fitness Machine Status "04"                      status=Started    speed=215.0 cadence=115 power= 315 hrm=  0
340 Fitness Machine Control Point "80 07 01" ResponseCode=128 RequestCode=7 ResultCode=1(Succes)
334 Indoor Bike Data       "44 00 60 54 e8 00 3c 01" status=Started    speed=216.0 cadence=116 power= 316 hrm=  0
Switch to PowerMode, 324W
337 Fitness Machine Status "08 44 01"                status=Power mode speed=216.0 cadence=116 power= 316 hrm=  0
340 Fitness Machine Control Point "80 05 01" ResponseCode=128 RequestCode=5 ResultCode=1(Succes)
334 Indoor Bike Data       "44 00 c4 54 ea 00 3d 01" status=Power mode speed=217.0 cadence=117 power= 317 hrm=  0
Switch to GradeMode, 4%
337 Fitness Machine Status "12 00 00 90 01 28 33"    status=Grade mode speed=217.0 cadence=117 power= 317 hrm=  0
340 Fitness Machine Control Point "80 11 01" ResponseCode=128 RequestCode=17 ResultCode=1(Succes)
334 Indoor Bike Data       "44 00 28 55 ec 00 3e 01" status=Grade mode speed=218.0 cadence=118 power= 318 hrm=  0
Switch to PowerMode, 323W
337 Fitness Machine Status "08 43 01"                status=Power mode speed=218.0 cadence=118 power= 318 hrm=  0
340 Fitness Machine Control Point "80 05 01" ResponseCode=128 RequestCode=5 ResultCode=1(Succes)
334 Indoor Bike Data       "44 00 8c 55 ee 00 3f 01" status=Power mode speed=219.0 cadence=119 power= 319 hrm=  0
Switch to GradeMode, 3%
340 Fitness Machine Control Point "80 11 01" ResponseCode=128 RequestCode=17 ResultCode=1(Succes)
337 Fitness Machine Status "12 00 00 2c 01 28 33"    status=Grade mode speed=219.0 cadence=119 power= 319 hrm=  0
334 Indoor Bike Data       "44 00 f0 55 f0 00 40 01" status=Grade mode speed=220.0 cadence=120 power= 320 hrm=  0
Switch to PowerMode, 322W
337 Fitness Machine Status "08 42 01"                status=Power mode speed=220.0 cadence=120 power= 320 hrm=  0
340 Fitness Machine Control Point "80 05 01" ResponseCode=128 RequestCode=5 ResultCode=1(Succes)
334 Indoor Bike Data       "44 00 54 56 f2 00 41 01" status=Power mode speed=221.0 cadence=121 power= 321 hrm=  0
Switch to GradeMode, 2%
337 Fitness Machine Status "12 00 00 c8 00 28 33"    status=Grade mode speed=221.0 cadence=121 power= 321 hrm=  0
340 Fitness Machine Control Point "80 11 01" ResponseCode=128 RequestCode=17 ResultCode=1(Succes)
334 Indoor Bike Data       "44 00 b8 56 f4 00 42 01" status=Grade mode speed=222.0 cadence=122 power= 322 hrm=  0
Switch to PowerMode, 321W
334 Indoor Bike Data       "44 00 1c 57 f6 00 43 01" status=Grade mode speed=223.0 cadence=123 power= 323 hrm=  0
337 Fitness Machine Status "08 41 01"                status=Power mode speed=223.0 cadence=123 power= 323 hrm=  0
340 Fitness Machine Control Point "80 05 01" ResponseCode=128 RequestCode=5 ResultCode=1(Succes)
334 Indoor Bike Data       "44 00 80 57 f8 00 44 01" status=Power mode speed=224.0 cadence=124 power= 324 hrm=  0
Switch to GradeMode, 1%
337 Fitness Machine Status "12 00 00 64 00 28 33"    status=Grade mode speed=224.0 cadence=124 power= 324 hrm=  0
340 Fitness Machine Control Point "80 11 01" ResponseCode=128 RequestCode=17 ResultCode=1(Succes)
334 Indoor Bike Data       "44 00 e4 57 fa 00 45 01" status=Grade mode speed=225.0 cadence=125 power= 325 hrm=  0
Switch to PowerMode, 50W
337 Fitness Machine Status "08 32 00"                status=Power mode speed=225.0 cadence=125 power= 325 hrm=  0
340 Fitness Machine Control Point "80 05 01" ResponseCode=128 RequestCode=5 ResultCode=1(Succes)
334 Indoor Bike Data       "44 00 48 58 fc 00 46 01" status=Power mode speed=226.0 cadence=126 power= 326 hrm=  0
Stop training session
337 Fitness Machine Status "02"                      status=Stopped    speed=226.0 cadence=126 power= 326 hrm=  0
340 Fitness Machine Control Point "80 08 01" ResponseCode=128 RequestCode=8 ResultCode=1(Succes)
334 Indoor Bike Data       "44 00 ac 58 fe 00 47 01" status=Stopped    speed=227.0 cadence=127 power= 327 hrm=  0
Release control / reset
337 Fitness Machine Status "01"                      status=Reset      speed=227.0 cadence=127 power= 327 hrm=  0
340 Fitness Machine Control Point "80 01 01" ResponseCode=128 RequestCode=1 ResultCode=1(Succes)
334 Indoor Bike Data       "44 00 10 59 00 01 48 01" status=Reset      speed=228.0 cadence=128 power= 328 hrm=  0
Stop collector loop
Unregister notifications
Unregister indications

"""
