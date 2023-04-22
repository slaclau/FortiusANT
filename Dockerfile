ARG DISTRIBUTION=latest
FROM ubuntu:$DISTRIBUTION
ADD . ~/fortius-ant
RUN if [ "$DISTRIBUTION" = "focal" ]; then sudo add-apt-repository ppa:jyrki-pulliainen/dh-virtualenv; sudo apt update; fi
RUN export useSystemPython=$(python3 useSystemPython.py); if [ "$useSystemPython" = "yes" ]; then export ver=3; else export ver=3.9; fi; python$ver setup.py bdist_wheel --dist-dir=pip_local; \
python$ver -m pip download \
--destination-directory pip_local \
-r requirements.txt