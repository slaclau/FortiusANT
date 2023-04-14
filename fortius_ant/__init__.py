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

__version__ = _version.get_versions()["version"]
__shortversion__ = _version.get_versions()["version"].split("+")[0]
__packageversion__ = ""
__packagetype__ = ""
try:
    from . import _snapversion

    __packageversion__ = _snapversion.__version__
    __packagetype__ = "snap"
except:
    pass
try:
    from . import _debversion

    __packageversion__ = _debversion.__version__
    __packagetype__ = "deb"
except:
    pass
