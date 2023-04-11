import distro
import fileinput
import subprocess

codename = distro.codename()

version = subprocess.check_output(["git", "describe", "--tags", "--always", "--long",
        "--match", f"[[:digit:]]*", "--exclude", "*ubuntu*"]).strip().decode("utf-8")
ubuntu_version = subprocess.check_output(["git", "describe", "--tags", "--always", "--long",
        "--match", f"[[:digit:]]*"]).strip().decode("utf-8")
ubuntu_tag = subprocess.check_output(["git", "describe", "--tags", "--always", "--abbrev=0",
        "--match", f"[[:digit:]]*"]).strip().decode("utf-8")

for line in fileinput.input("debian/changelog", inplace = True):
    print(line.replace(") replaceme", "~" + codename + ") " + codename), end = "")

for line in fileinput.input("debian/changelog", inplace = True):
    print(line.replace(") ubuntutag", ubuntu_version), end = "")
