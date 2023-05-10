"""Interface with usb dongle."""
import os
import threading
import time
import queue

import usb.core
from usb.core import NoBackendError, USBError


from fortius_ant import debug, logfile, antMessage
from fortius_ant.antMessage import (
    AntMessage,
    Message4A,
    Message4D,
    msgID_Capabilities,
    msgID_ANTversion,
)


class Dongle:
    """Encapsulate dongle functionality."""

    device = None

    def __init__(self, device_id: int | None = None):
        """Create a dongle class with the required device id."""
        self.device_id = device_id
        self.messages: queue.Queue = queue.Queue()
        self.cycplus = False

        self.thread: threading.Thread = None
        self.thread_active = False

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
            self.reset(device)
            time.sleep(0.500)
            if debug.on(debug.Function):
                logfile.Write("GetDongle - Read answer")
            if debug.on(debug.Function):
                logfile.Write("GetDongle - Check for an ANT+ reply")
            try:
                message = device.read(0x81, 5)
                (
                    synch,
                    length,
                    message_id,
                ) = AntMessage.decompose(
                    message
                )[0:3]
                if (
                    synch == 0xA4
                    and length == 0x01
                    and message_id == antMessage.msgID_StartUp
                ):
                    return True

            except usb.core.USBError as e:
                if debug.on(debug.Data1 | debug.Function):
                    logfile.Write(f"GetDongle - Exception: {e}")
        return False

    def reset(self, device=None):
        """Send reset command to dongle."""
        if device is None and self.device is not None:
            self._write(Message4A.create())
        elif device is not None:
            device.write(0x01, Message4A.create())

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
        parsed_response = AntMessage.decompose_to_dict(response)
        if parsed_response["id"] == msgID_Capabilities:
            print(parsed_response["info"])

        self._write(Message4D.create(id=msgID_ANTversion))
        response = self._read(100)
        parsed_response = AntMessage.decompose_to_dict(response)
        if parsed_response["id"] == msgID_ANTversion:
            print(parsed_response["info"])

    def _write(self, message):
        if self.device is not None:
            return self.device.write(0x01, message)
        raise NoDongle

    def _read(self, num_bytes: int):
        if self.device is not None:
            return self.device.read(0x81, num_bytes)
        raise NoDongle


class NoDongle(Exception):
    """Raised when no physical dongle is set."""
