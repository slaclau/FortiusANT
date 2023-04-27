| Checks |
| ------ |
| [![linting](https://github.com/slaclau/FortiusANT/actions/workflows/linting.yaml/badge.svg)](https://github.com/slaclau/FortiusANT/actions/workflows/linting.yaml) |
| [![deptry](https://github.com/slaclau/FortiusANT/actions/workflows/deptry.yaml/badge.svg)](https://github.com/slaclau/FortiusANT/actions/workflows/deptry.yaml) |
| [![pytest](https://github.com/slaclau/FortiusANT/actions/workflows/pytest.yaml/badge.svg)](https://github.com/slaclau/FortiusANT/actions/workflows/pytest.yaml) |
| [![Test pip install](https://github.com/slaclau/FortiusANT/actions/workflows/pip-install.yaml/badge.svg)](https://github.com/slaclau/FortiusANT/actions/workflows/pip-install.yaml) |
| [![Build debian packages](https://github.com/slaclau/FortiusANT/actions/workflows/build-debian.yaml/badge.svg)](https://github.com/slaclau/FortiusANT/actions/workflows/build-debian.yaml) |
| [![Build snap](https://github.com/slaclau/FortiusANT/actions/workflows/build-snap.yaml/badge.svg)](https://github.com/slaclau/FortiusANT/actions/workflows/build-snap.yaml) |

| Code quality |
| ------------ |
| <a href="https://slaclau.github.io/FortiusANT/coverage/"><img src="https://api.codeclimate.com/v1/badges/7f4bf90311079edc43aa/test_coverage" /></a> |

| Available versions |
| ------------------ |
| ![Upstream version](https://img.shields.io/github/v/release/slaclau/FortiusANT?label=Upstream%20version) |
| ![Ubuntu package version](https://img.shields.io/github/v/tag/slaclau/FortiusANT?label=Ubuntu%20Package) |
| ![Snap edge version](https://img.shields.io/endpoint?url=https%3A%2F%2Fslaclau.pythonanywhere.com%2Fsnap%2Fedge) |
| ![Snap beta version](https://img.shields.io/endpoint?url=https%3A%2F%2Fslaclau.pythonanywhere.com%2Fsnap%2Fbeta) |

# FortiusANT
FortiusANT enables a pre-smart Tacx trainer (usb- or ANT-connected) to communicate with TrainerRoad, Rouvy or Zwift through ANT.

FortiusANT is running on the computer (Windows, Linux or MacOS) where the trainer is connected and broadcasts the ANT+ signal, using a dongle, to another computer or tablet.
You might also run TrainerRoad or Zwift on the same computer and then two ANT+ dongles on the same computer are required.

## Supported Tacx trainers
USB: Tacx Flow, Fortius, i-Flow, i-Magic with T1902, T1904, T1932, T1942 head units

ANT: Tacx Vortex, Genius, Bushido (with T1982 head unit)

Bushido support is still *experimental* at this time (please consider providing feedback in https://github.com/WouterJD/FortiusANT/issues/117).

## Communication with Trainer Road, Rouvy, Zwift and others
Communication with a Cycling Training Program (CTP) can be done using an ANT- or BLE-dongle (BLE = Bluetooth Low Energy)

The CTP can be run on another computer or Smartphone.

**ANT dongles made by CYCPLUS (identical-looking ones sold as Anself and probably others) have been known to cause problems.** Refer to issue #61 (#97, #207 and others)

# User manual and version information
Refer [wiki](https://github.com/WouterJD/FortiusANT/wiki) first, then ask questions raising an issue. Succes!

For inspiration, visit the [Raspberry Pi Hall of Fame](https://github.com/WouterJD/FortiusANT/wiki/Raspberry-Pi-Hall-of-Fame) and [The Tacx Training Cave](https://github.com/WouterJD/FortiusANT/wiki/The-Tacx-Training-Cave)

![image](https://raw.githubusercontent.com/WouterJD/FortiusANT/master/supportfiles/FortiusAntWorld.jpg)

# Installation

FortiusANT is available as a deb package built for Ubuntu focal or jammy as well as a snap. These packages include all Python dependencies.

## .deb installation

Run the following command:
```bash
sudo add-apt-repository ppa:slaclau/ppa
sudo apt update
sudo apt install fortius-ant
```

To obtain the latest prerelease version use the following instead:
```bash
sudo add-apt-repository ppa:slaclau/ppa-pre
sudo apt update
sudo apt install fortius-ant
```

To obtain the latest development version use the following instead:
```bash
sudo add-apt-repository ppa:slaclau/ppa-develop
sudo apt update
sudo apt install fortius-ant
```

Formal releases are also available from [GitHub](https://github.com/slaclau/FortiusANT/releases/latest).

## snap installation

Snap installation is currently work in progress, full releases are available in the snapcraft beta channel:
```bash
sudo snap install --beta --devmode fortius-ant
```

Prereleases are available in the edge channel:
```bash
sudo snap install --edge --devmode fortius-ant
```

# License

GPLv3

Copyright (c) 2020 [Wouter Dubbeldam](https://github.com/WouterJD). Please have a look at the [LICENSE](LICENSE) for more details.

# Sponsor
[![Custom badge](https://github.com/WouterJD/FortiusANT/blob/master/pythoncode/sponsor36.bmp)](https://github.com/sponsors/WouterJD)

If you like to use FortiusAnt; please leave a note on the [put yourself on the FortiusAnt map](https://github.com/WouterJD/FortiusANT/issues/14) page; thereby a sponsorship would be another great acknowledgement! Questions, problems and suggestions can be reported as an issue on github.
