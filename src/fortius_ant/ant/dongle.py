"""Interface with usb dongle."""
from enum import Enum
import os
import threading
import time
import queue

import usb.core
from usb.core import NoBackendError, USBError


from fortius_ant import debug, logfile
from fortius_ant.ant.message import (
    Message4A,
    Message4D,
    AntMessage,
    AssignChannelMessage,
    UnassignChannelMessage,
    ChannelResponseMessage,
    StartupMessage,
    msgID_Capabilities,
    msgID_ANTversion,
    CapabilitiesMessage,
    VersionMessage,
    WrongMessageId,
    Id,
)

default_network_key = 0x45C372BDFB21A5B9
ant_plus_frequency = 57
power_0db = 0x03


class ChannelType(Enum):
    """Types of ant channel."""

    BidirectionalReceive = 0x00  # Slave
    BidirectionalTransmit = 0x10  # Master

    UnidirectionalReceiveOnly = 0x40  # Slave
    UnidirectionalTransmitOnly = 0x50  # Master

    SharedBidirectionalReceive = 0x20  # Slave
    SharedBidirectionalTransmit = 0x30  # Master


class Dongle:
    """Encapsulate dongle functionality."""

    device = None
    max_channels = None
    max_networks = None
    ant_version = None
    last_reset_type = None
    channels = None

    def __init__(self, device_id: int | None = None):
        """Create a dongle class with the required device id."""
        self.device_id = device_id
        self.messages: queue.Queue = queue.Queue()
        self.cycplus = False

        self.thread: threading.Thread = None
        self.thread_active = False

    def startup(self):
        """Call to configure dongle and properties on startup."""
        self._get_dongle()
        self.calibrate()

    def configure_channel(self, interface):
        """Send channel configuration messages to the dongle."""
        network = 0
        if interface.network_key != default_network_key:
            raise NotImplementedError
        channel_number = self._get_next_channel()
        self.channels[channel_number] = interface
        interface.channel = channel_number
        self._write(
            AssignChannelMessage.create(
                channel=channel_number,
                type=interface.channel_type,
                network=network,
            )
        )
        response = self._read(100)
        response_dict = ChannelResponseMessage.to_dict(response)
        assert response_dict["channel"] == channel_number
        assert response_dict["id"] == Id.AssignChannel
        assert response_dict["code"] == ChannelResponseMessage.Code.RESPONSE_NO_ERROR

    def _get_next_channel(self):
        if self.channels is None:
            self.channels = [None] * self.max_channels
        channel = next(
            (i for i in range(0, self.max_channels) if self.channels[i] is None), -1
        )
        if channel == -1:
            raise NoMoreChannels
        return channel

    def _get_dongle(self) -> bool:
        self.cycplus = False

        # self.stop_read_thread()

        if self.device_id is None:
            dongles = {(4104, "Suunto"), (4105, "Garmin"), (4100, "Older")}
        else:
            dongles = {(self.device_id, "(provided)")}

        found_available_ant_stick = False

        for dongle in dongles:
            ant_pid = dongle[0]
            if debug.on(debug.Function):
                logfile.Write(f"_get_dongle - Check for dongle {ant_pid} {dongle[1]}")
            try:
                devices = usb.core.find(find_all=True, idProduct=ant_pid)
            except NoBackendError as e:
                logfile.Console(f"GetDongle - Exception: {e}")
            else:
                for self.device in devices:
                    if debug.on(debug.Function):
                        s = (
                            f"GetDongle - Try dongle: manufacturer="
                            f"{self.device.manufacturer}, product={self.device.product}"
                            f", vendor={hex(self.device.idVendor)}, product="
                            f"{hex(self.device.idProduct)}({self.device.idProduct})"
                        )
                        logfile.Console(s.replace("\0", ""))
                    if debug.on(debug.Data1 | debug.Function):
                        logfile.Print(self.device)

                    if os.name == "posix":
                        if debug.on(debug.Function):
                            logfile.Write("GetDongle - Detach kernel drivers")
                        for config in self.device:
                            for i in range(config.bNumInterfaces):
                                if self.device.is_kernel_driver_active(i):
                                    self.device.detach_kernel_driver(i)
                    if debug.on(debug.Function):
                        logfile.Write("GetDongle - Set configuration")
                    try:
                        self.device.set_configuration()
                        found_available_ant_stick = self._check_if_ant(self.device)
                        if found_available_ant_stick:
                            manufacturer = self.device.manufacturer
                            manufacturer = manufacturer.replace("\0", "")
                            if "CYCPLUS" in manufacturer:
                                self.cycplus = True
                            return True
                    except USBError as e:
                        if debug.on(debug.Function):
                            logfile.Write(f"USBError: {e}")
        self.device = None
        return found_available_ant_stick

    def _check_if_ant(self, device):
        for _ in range(2):
            if debug.on(debug.Function):
                logfile.Write("GetDongle - Send reset string to dongle")
            if self.reset(device):
                return True
        return False

    def reset(self, device=None):
        """Send reset command to dongle."""
        if device is None:
            device = self.device
        if device is not None:
            device.write(0x01, Message4A.create())

            time.sleep(0.500)
            if debug.on(debug.Function):
                logfile.Write("GetDongle - Read answer")
            if debug.on(debug.Function):
                logfile.Write("GetDongle - Check for an ANT+ reply")
            try:
                message = device.read(0x81, 5)
                message_dict = StartupMessage.to_dict(message)
                self.last_reset_type = message_dict["type"]
                return True

            except usb.core.USBError as e:
                if debug.on(debug.Data1 | debug.Function):
                    logfile.Write(f"GetDongle - Exception: {e}")
            except WrongMessageId:
                pass
        return False

    def reset_if_allowed(self):
        """Send reset command if not a CYCPLUS dongle."""
        if not self.cycplus:
            self.reset()

    def release(self):
        """Release dongle."""
        if self.device is not None:
            self.reset()
            for cfg in self.device:
                for intf in cfg:
                    if debug.on(debug.Function):
                        logfile.Write("AntDongle.release_interface()")
                    usb.util.release_interface(self.device, intf)
            if debug.on(debug.Function):
                logfile.Write("AntDongle.dispose_resources()")
            usb.util.dispose_resources(self.device)
            self.device = None
        return True

    def calibrate(self):
        """Send dongle configuration commands.

        First send a request for the dongle's capabilities.
        """
        self._write(Message4D.create(id=msgID_Capabilities))
        response = self._read(100)
        response_dict = CapabilitiesMessage.to_dict(response)
        self.max_channels = response_dict["max_channels"]
        self.max_networks = response_dict["max_networks"]

        self._write(Message4D.create(id=msgID_ANTversion))
        response = self._read(100)
        response_dict = VersionMessage.to_dict(response)
        self.ant_version = response_dict["version"]

    def _write(self, message):
        if self.device is not None:
            return self.device.write(0x01, message)
        raise NoDongle

    def _read(self, num_bytes: int):
        if self.device is not None:
            return self.device.read(0x81, num_bytes)
        raise NoDongle


class NoDongle(Exception):
    """Raise when no physical dongle is set."""


class NoMoreChannels(Exception):
    """Raise when all channels are in use."""


dongle = None


def test():
    from fortius_ant.ant.interface import AntInterface

    global dongle
    dongle = Dongle()
    dongle.startup()
    interface = AntInterface()
    dongle.configure_channel(interface)
