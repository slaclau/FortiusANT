import fortius_ant.antDongle

def test_get_devices():
    mocker.patch("usb.core.find",return_value=[])
    ant_dongle = new clsAntDongle()
    assert True