"""Interface with usb dongle."""
import os
import threading
import time
import queue

import usb.core

from fortius_ant import debug, logfile
from fortius_ant.antMessage import AntMessage, Message4A

class Dongle():
    """Encapsulate dongle functionality."""

    device = None

    def __init__(self, device_id: int | None = None):
        """Create a dongle class with the required device id."""
        self.device_id = device_id
        self.messages = queue.Queue()
        self.cycplus = False

        self.thread: threading.Thread = None
        self.thread_active = False

    def _get_dongle(self) -> bool:
        self.cycplus = False

        # self.stop_read_thread()

        if self.device_id == None:
            dongles = {(4104, "Suunto"), (4105, "Garmin"), (4100, "Older")}
        else:
            dongles = {(self.device_id, "(provided)")}

        found_available_ant_stick = False

        for dongle in dongles:
            ant_pid = dongle[0]
            if debug.on(debug.Function):
                logfile.Write(
                    f"_get_dongle - Check for dongle {ant_pid} {dongle[1]}"
                )
            try:
                devices = usb.core.find(find_all=True, idProduct=ant_pid)
            except Exception as e:
                logfile.Console(f"GetDongle - Exception: {e}")
            else:
                for self.device in devices:
                    if debug.on(debug.Function):
                        s = (
                            "GetDongle - Try dongle: manufacturer=%7s, product=%15s, vendor=%6s, product=%6s(%s)"
                            % (
                                self.device.manufacturer,
                                self.device.product,
                                hex(self.device.idVendor),
                                hex(self.device.idProduct),
                                self.device.idProduct,
                            )
                        )
                        logfile.Console(s.replace("\0", ""))
                    if debug.on(debug.Data1 | debug.Function):
                        logfile.Print(self.device)

                    try:
                        if os.name == "posix":
                            if debug.on(debug.Function):
                                logfile.Write("GetDongle - Detach kernel drivers")
                            for config in self.device:
                                for i in range(config.bNumInterfaces):
                                    if self.device.is_kernel_driver_active(i):
                                        self.device.detach_kernel_driver(i)
                        if debug.on(debug.Function):
                            logfile.Write("GetDongle - Set configuration")
                        self.device.set_configuration()

                        for _ in range(2):
                            if debug.on(debug.Function):
                                logfile.Write("GetDongle - Send reset string to dongle")
                            self.device.write(0x01, Message4A.create())
                            time.sleep(0.500)
                            if debug.on(debug.Function):
                                logfile.Write("GetDongle - Read answer")
                            self.read(False)

                            if debug.on(debug.Function):
                                logfile.Write("GetDongle - Check for an ANT+ reply")
                            while True:
                                try:
                                    s = self.messages.get(False)
                                    (
                                        synch,
                                        length,
                                        message_id,
                                    ) = AntMessage.decompose(s)[0:3]
                                    if synch == 0xA4 and length == 0x01 and message_id == 0x6F:
                                        found_available_ant_stick = True
                                        manufacturer = self.device.manufacturer
                                        manufacturer = manufacturer.replace("\0", "")
                                        if "CYCPLUS" in manufacturer:
                                        self.cycplus = True

                                        break

                    except usb.core.USBError as e:  # cannot write to ANT dongle
                        if debug.on(debug.Data1 | debug.Function):
                            logfile.Write("GetDongle - Exception: %s" % e)

                    except Exception as e:
                        logfile.Console("GetDongle - Exception: %s" % e)

                    if found_available_ant_stick:
                        break

            if found_available_ant_stick:
                break

        if not found_available_ant_stick:
            self.device = None
        return found_available_ant_stick
