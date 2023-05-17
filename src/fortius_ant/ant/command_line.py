"""Command line test program."""

import logging

from fortius_ant.ant import dongle, interface
from fortius_ant.ant.data import sport
from fortius_ant.ant.plus import hrm, scs

usb_dongle = None
testing = False


def set_debug_level(level: int):
    logging.getLogger().setLevel(level)


def test(type, master=True, fixed_values=False):
    global usb_dongle, testing
    assert not testing
    usb_dongle = dongle.USBDongle()
    usb_dongle.startup()
    device_number = 1 if master else 0
    if type == "hrm":
        intf = hrm.AntHRM(master=master, device_number=device_number)
    elif type == "scs":
        intf = scs.AntSCS(master=master, device_number=device_number)
    sport_data = sport.SportData()
    if master:
        sport_data.simulate(fixed_values=fixed_values)
        intf.data_source = sport_data
    else:
        intf.data_target = sport_data
    usb_dongle.start_read_thread()
    usb_dongle.start_handler_thread()
    usb_dongle.configure_channel(intf)
    testing = True


def stop_test():
    global usb_dongle, testing
    assert testing
    assert usb_dongle.release()
    usb_dongle = None
    testing = False


def test2():
    global usb_dongle, testing
    assert not testing
    usb_dongle = dongle.USBDongle()
    usb_dongle.startup()
    intf = interface.AntInterface(master=False)
    intf.channel_frequency = 60
    intf.channel_period = 4096
    intf.device_type_id = 81
    usb_dongle.start_read_thread()
    intf.channel_search_timeout = 255
    usb_dongle.start_handler_thread()
    usb_dongle.configure_channel(intf)
    testing = True
