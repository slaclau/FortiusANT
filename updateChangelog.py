import distro
import fileinput
import subprocess

codename = distro.codename()

for line in fileinput.input("debian/changelog", inplace = True):
    print(line.replace(") replaceme", "~" + codename + ") " + codename), end = "")
version = subprocess.check_output(["git", "describe", "--tags", "--dirty", "--always", "--long",
        "--match", f"[[:digit:]]*", "--exclude", "*ubuntu*"]).strip()
print(version)
ubuntu_version = subprocess.check_output(["git", "describe", "--tags", "--dirty", "--always", "--long",
        "--match", f"[[:digit:]]*"]).strip()
print(ubuntu_version)
