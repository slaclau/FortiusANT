from fortius_ant import antDongle
from usb.core import Device

def test_get_devices(mocker):
    mocker.patch("usb.core.find",return_value=[])
    ant_dongle = antDongle.clsAntDongle()
    print(vars(ant_dongle))
    assert ant_dongle.devAntDongle == None
    
    mocker.patch("usb.core.find",return_value=Device("dev",None))
    ant_dongle = antDongle.clsAntDongle()
    print(vars(ant_dongle))
    assert ant_dongle.devAntDongle == None