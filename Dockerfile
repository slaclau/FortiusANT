ARG DISTRIBUTION=latest
FROM ubuntu:$DISTRIBUTION
ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir /fortius-ant; cd /fortius-ant
WORKDIR /fortius-ant
ADD . /fortius-ant
RUN apt-get update; apt-get install -y software-properties-common devscripts equivs python3-pip; python3 -m pip install distro

RUN python3 addRepositories.py; apt-get update;
RUN mk-build-deps -i -t "apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends -y"
RUN if [ "$useSystemPython" = "yes" ]; \
then export ver=3; else export ver=3.9; fi; \
apt-get install -y python$ver
python$ver updateChangelog.py; \
python$ver wxPython-source.py; \
mkdir pip_local; \
python$ver -m pip install -U setuptools; \
python$ver setup.py bdist_wheel --dist-dir=pip_local; \
python$ver -m pip download \
--destination-directory pip_local \
-r requirements.txt
RUN dpkg-buildpackage