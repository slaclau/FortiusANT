__all__ = [
    "antCTRL",
    "antDongle",
    "antFE",
    "antHRM",
    "antPWR",
    "antSCS",
    "bleBleak",
    "bleBlessClass",
    "bleBless",
    "bleConstants",
    "bleDongle",
    "constants",
    "debug",
    "ExplorAntCommand",
    "ExplorAnt",
    "FortiusAntBody",
    "FortiusAntCommand",
    "FortiusAntGui",
    "FortiusAnt",
    "fxload",
    "logfile",
    "RadarGraph",
    "raspberry",
    "settings",
    "structConstants",
    "TCXexport",
    "TestMultiprocessing",
    "usbTrainer",
]

from . import _version
__version__ = _version.get_versions()['version']
__shortversion__ = _version.get_versions()['version'].strip("+")[0]
