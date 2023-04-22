ARG DISTRIBUTION=latest
FROM ubuntu:$DISTRIBUTION
RUN mkdir /fortius-ant; cd /fortius-ant
WORKDIR /fortius-ant
ADD . /fortius-ant
RUN apt-get update; apt-get install -y software-properties-common
RUN if [ "$DISTRIBUTION" = "focal" ]; then add-apt-repository ppa:jyrki-pulliainen/dh-virtualenv; fi
RUN apt-get update; apt-get install -y python3; \
export useSystemPython=$(python3 useSystemPython.py); \
if [ "$useSystemPython" = "yes" ]; \
then export ver=3; else export ver=3.9; add-apt-repository ppa:deadsnakes/ppa; sed -i "s/$DISTRIBUTION/jammy/g" /etc/apt/sources.list.d/*ubuntu*; fi; \
apt-get update; \
apt-get install -y python$ver python$ver-dev python$ver-distutils python$ver-venv; \
python$ver setup.py bdist_wheel --dist-dir=pip_local; \
python$ver -m pip download \
--destination-directory pip_local \
-r requirements.txt
RUN apt-get install -y debhelper dh-virtualenv libgstreamer-plugins-base1.0-0 libnotify4 libsdl2-2.0-0 libwebkit2gtk-4.0-dev libjavascriptcoregtk-4.0-dev libegl-dev