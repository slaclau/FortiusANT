ARG DISTRIBUTION=latest
FROM ubuntu:$DISTRIBUTION
RUN mkdir /fortius-ant; cd /fortius-ant
WORKDIR /fortius-ant
ADD . /fortius-ant
RUN apt-get update; apt-get install -y software-properties-common devscripts equivs python3-pip
RUN echo "deb https://ppa.launchpadcontent.net/jyrki-pulliainen/dh-virtualenv/ubuntu focal main" >> /etc/apt/sources.list; \
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B325B03CAA406734D572BE2970140AA7D3AFD0F6; \
echo "deb https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu jammy main" >> /etc/apt/sources.list; \
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776; \
apt-get update;
RUN mk-build-deps -i -t "apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends -y"
RUN if [ "$useSystemPython" = "yes" ]; \
then export ver=3; else export ver=3.9; fi; \
python$ver updateChangelog.py; \
python$ver wxPython-source.py; \
mkdir pip_local; \
python$ver setup.py bdist_wheel --dist-dir=pip_local; \
python$ver -m pip download \
--destination-directory pip_local \
-r requirements.txt
RUN dpkg-buildpackage