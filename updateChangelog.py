import distro
import fileinput
import subprocess

codename = distro.codename()

version = subprocess.check_output(["git", "describe", "--tags", "--always", "--long",
        "--match", f"[[:digit:]]*", "--exclude", "*ubuntu*"]).strip()
ubuntu_version = subprocess.check_output(["git", "describe", "--tags", "--always", "--long",
        "--match", f"[[:digit:]]*"]).strip()
ubuntu_tag = subprocess.check_output(["git", "describe", "--tags", "--always", "--abbrev=0",
        "--match", f"[[:digit:]]*"]).strip()

for line in fileinput.input("debian/changelog", inplace = True):
    print(line.replace(") replaceme", "~" + codename + ") " + codename), end = "")
    print(line.replace(") ubuntutag", ubuntu_version), end = "")
