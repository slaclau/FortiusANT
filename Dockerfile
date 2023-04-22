ARG DISTRIBUTION=latest
FROM ubuntu:$DISTRIBUTION
ADD . ~/fortius-ant
RUN if [ "$DISTRIBUTION" = "focal" ]; then add-apt-repository ppa:jyrki-pulliainen/dh-virtualenv; fi
RUN apt-get update; apt-get install python3; \
export useSystemPython=$(python3 useSystemPython.py); \
if [ "$useSystemPython" = "yes" ]; \
then export ver=3; else export ver=3.9; fi; \
apt-get install python$ver python$ver-dev python$ver-distutils python$ver-venv \
python$ver setup.py bdist_wheel --dist-dir=pip_local; \
python$ver -m pip download \
--destination-directory pip_local \
-r requirements.txt