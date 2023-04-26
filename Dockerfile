ARG DISTRIBUTION=latest
FROM ubuntu:$DISTRIBUTION
ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir /fortius-ant; cd /fortius-ant
WORKDIR /fortius-ant
ADD . /fortius-ant
RUN apt-get update; apt-get install -y software-properties-common devscripts equivs python3-pip python3-distro

RUN python3 addRepositories.py; apt-get update;
RUN mk-build-deps -i -t "apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends -y"
RUN export useSystemPython=$(python3 useSystemPython.py); \
if [ "$useSystemPython" = "yes" ]; \
then export ver=3; else export ver=3.9; fi; \
apt-get install -y python$ver; \
python$ver updateChangelog.py; \
echo "" >> wxPython-source.txt \
mkdir pip_local; \
python$ver -m pip install -U setuptools attrdict; \
python$ver setup.py bdist_wheel --dist-dir=pip_local; \
python$ver -m pip download \
--destination-directory pip_local \
-r requirements.txt
RUN mkdir /output; 
CMD dpkg-buildpackage; cp ../fortius-ant* /output/
