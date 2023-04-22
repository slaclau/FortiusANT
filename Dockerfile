ARG DISTRIBUTION=latest
FROM ubuntu:$DISTRIBUTION
ADD . ~/fortius-ant
RUN if [ "$DISTRIBUTION" = "focal" ]; then sudo add-apt-repository ppa:jyrki-pulliainen/dh-virtualenv; sudo apt update; fi