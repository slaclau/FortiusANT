import distro
import fileinput

codename = distro.codename()

for line in fileinput.input("debian/changelog", inplace = True):
    print(line.replace("replace_me", codename), end = "")
