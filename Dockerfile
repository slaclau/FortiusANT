ARG DISTRIBUTION=latest
FROM ubuntu:$DISTRIBUTION
RUN mkdir /fortius-ant; cd /fortius-ant
WORKDIR /fortius-ant
ADD . /fortius-ant
RUN apt-get update; apt-get install -y software-properties-common devscripts
RUN add-apt-repository ppa:jyrki-pulliainen/dh-virtualenv;
RUN echo "deb https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu jammy main" >> /etc/apt/sources.list; \
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776; \
apt-get update;
RUN mk-build-deps -i
USER 1000:1000
RUN if [ "$useSystemPython" = "yes" ]; \
then export ver=3; else export ver=3.9; fi; \
python$ver setup.py bdist_wheel --dist-dir=pip_local; \
python$ver -m pip download \
--destination-directory pip_local \
-r requirements.txt