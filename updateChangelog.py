import distro
import fileinput
import subprocess

if len(sys.argv) > 0:
    codename = sys.argv[0]
else: 
    codename = distro.codename()

version = (
    subprocess.check_output(
        [
            "git",
            "describe",
            "--tags",
            "--always",
            "--match",
            f"[[:digit:]]*",
            "--exclude",
            "*ubuntu*",
        ]
    )
    .strip()
    .decode("utf-8")
)
ubuntu_version = (
    subprocess.check_output(
        ["git", "describe", "--tags", "--always", "--match", f"[[:digit:]]*"]
    )
    .strip()
    .decode("utf-8")
)
ubuntu_tag = (
    subprocess.check_output(
        [
            "git",
            "describe",
            "--tags",
            "--always",
            "--abbrev=0",
            "--match",
            f"[[:digit:]]*",
        ]
    )
    .strip()
    .decode("utf-8")
)

for line in fileinput.input("debian/changelog", inplace=True):
    print(line.replace(") replaceme", "~" + codename + ") " + codename), end="")

for line in fileinput.input("debian/changelog", inplace=True):
    print(line.replace(ubuntu_tag, ubuntu_version), end="")

with open("src/fortius_ant/_debversion.py", "x") as f:
    f.write('__version__ = "' + ubuntu_version + "~" + codename + '"')
