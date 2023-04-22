import distro


def main():
    if len(sys.argv) > 0:
        version = sys.argv[0]
    else: 
        version = int(distro.major_version())
    if version >= 22:
        lts = "22.04"
    elif version >= 20:
        lts = "20.04"
    elif version >= 18:
        lts = "18.04"
    else:
        print("wxPython needs to be built from source")
        lts = None
    if lts != None:
        wheels_url = (
            "https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-"
            + lts
            + "/"
        )
        print("wxPython will be installed from " + wheels_url)
        f = open("wxPython-source.txt", "w+")
        f.write("-f " + wheels_url)


if __name__ == "__main__":
    main()
