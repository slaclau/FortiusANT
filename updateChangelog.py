import distro
import fileinput
import subprocess

codename = distro.codename()

for line in fileinput.input("debian/changelog", inplace = True):
    print(line.replace(") replaceme", "~" + codename + ") " + codename), end = "")
version = subprocess.check_output(["git", "describe", "--tags", "--always", "--long",
        "--match", f"[[:digit:]]*", "--exclude", "*ubuntu*"]).strip()
print(version)
ubuntu_version = subprocess.check_output(["git", "describe", "--tags", "--always", "--long",
        "--match", f"[[:digit:]]*"]).strip()
print(ubuntu_version)
ubuntu_tag = subprocess.check_output(["git", "describe", "--tags", "--always", "--abbrev=0",
        "--match", f"[[:digit:]]*"]).strip()
print(ubuntu_tag)
