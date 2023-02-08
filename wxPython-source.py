import distro

def main():
    version = int(distro.major_version())
    if version >= 22:
        lts = "22.04"
    elif version >= 20:
        lts = "20.04"
    elif version >= 18:
        lts = "18.04"
    else:
        print("wxPython needs to be built from sourcw")
        lts = None
    print(lts)
    wheels_url = "https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-" + lts + "/"
    print(wheels_url)
    
    f = open("wxPython-source.txt","w+")
    f.write("-f " + wheels_url)

if __name__ == "__main__":
    main()
