from fortius_ant import antDongle

def test_get_devices(mocker):
    mocker.patch("usb.core.find",return_value=[])
    ant_dongle = antDongle.clsAntDongle()
    print(ant_dongle.getmembers())
    assert False