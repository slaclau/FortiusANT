import sys

def main():
    minor = sys.version_info[1]
    if minor < 10:
        print("python3")
    else:
        print("python3.9")
if __name__ == "__main__":
    main()
