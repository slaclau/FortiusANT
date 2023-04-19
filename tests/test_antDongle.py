from fortius_ant import antDongle
from usb.core import Device
import usb.backend
class Backend(usb.backend.IBackend):
    pass

def test_get_devices(mocker):
    mocker.patch("usb.core.find",return_value=[])
    ant_dongle = antDongle.clsAntDongle()
    print(vars(ant_dongle))
    assert ant_dongle.devAntDongle == None
    
    fake_device = mocker.Magic_Mock()
    mocker.patch("usb.core.find",return_value=fake_device)
    ant_dongle = antDongle.clsAntDongle()
    print(vars(ant_dongle))
    assert ant_dongle.devAntDongle == None