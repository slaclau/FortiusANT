"""Interfaces for communicating as and with Tacx Bushido trainers."""
from fortius_ant.ant.plus.interface import AntPlusInterface
from fortius_ant.ant.interface import default_network_key


class BushidoBrake(AntPlusInterface):
    """Interface for communicating as and with Tacx Bushido brakes."""

    channel_frequency = 60
    channel_period = 4096
    device_type_id = 81
    channel_search_timeout = 255
    network_key = default_network_key

    def __init__(self, master=True, device_number=0):
        super().__init__(master=master, device_number=device_number)
        if self.master:
            self.logfile = open("Bushido.txt", "w")
        else:
            self.logfile = open("Bushido_slave.txt", "w")

    def _handle_broadcast_data(self, data_page_number: int, info: bytes):
        self.logfile.write(info)

    def _handle_acknowledged_data(self, data_page_number: int, info: bytes):
        self.logfile.write(info)


class BushidoHeadUnit(AntPlusInterface):
    channel_frequency = 60
    channel_period = 4096
    device_type_id = 82
    channel_search_timeout = 255
    network_key = default_network_key

    def __init__(self, master=True, device_number=0):
        super().__init__(master=master, device_number=device_number)
        if self.master:
            self.logfile = open("BushidoHU.txt", "w")
        else:
            self.logfile = open("BushidoHU_slave.txt", "w")

    def _handle_broadcast_data(self, data_page_number: int, info: bytes):
        self.logfile.write(info)

    def _handle_acknowledged_data(self, data_page_number: int, info: bytes):
        self.logfile.write(info)
