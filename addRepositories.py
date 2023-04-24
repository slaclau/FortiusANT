import distro
import fileinput
import subprocess
import sys

codename = distro.codename()

if codename == "focal":
    subprocess.run(["sudo", "add-apt-repository", "ppa:jyrki-pulliainen/dh-virtualenv"])

v = sys.version_info.minor

if v > 9:
    with open("/etc/apt/sources.list", "a") as file:
        file.write("deb https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu jammy main")
    subprocess.run(["apt-key", "adv", "--keyserver", "keyserver.ubuntu.com", "--recv-keys",     "F23C5A6CF475977595C89F51BA6932366A755776"])