VERSION=$(git describe --tags --always --long --match f"[[:digit:]]* --exclude *ubuntu*)
echo $VERSION
echo "__version__ = $VERSION" >> fortius_ant/snapversion.py
