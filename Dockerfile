# Elevator
#
# VERSION               0.7

FROM ubuntu
MAINTAINER Oleiade "tcrevon@gmail.com"

# Set up and update repositories
RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe multiverse" > /etc/apt/sources.list
RUN echo "deb http://deb.oleiade.com/debian oneiric main" >> /etc/apt/sources.list
RUN gpg --keyserver keyserver.ubuntu.com --recv-key 92EDE36B
RUN gpg -a --export 92EDE36B | apt-key add -
RUN apt-get update

# Install dependencies
RUN apt-get install -qq -y nano wget
RUN apt-get install -qq -y git mercurial
RUN apt-get install -qq -y build-essential pkg-config
RUN apt-get install -qq -y libleveldb1 libleveldb-dev libzmq3 libzmq3-dev

# Install Go compiler 1.1
RUN wget http://go.googlecode.com/files/go1.1.linux-amd64.tar.gz
RUN tar xfz go1.1.linux-amd64.tar.gz
RUN mv go /usr/local/go
RUN ln -s /usr/local/go/bin/go /usr/bin/

# Pull and build elevator
RUN git clone https://github.com/oleiade/Elevator /home/elevator/
RUN cd /home/elevator && git checkout -b refactor/go origin/refactor/go
RUN cd /home/elevator && make


# Update system config
RUN cp /home/elevator/bin/elevator /usr/local/bin
RUN echo "PATH=$PATH:/usr/local/bin" >> /etc/environment

# Prepare elevator filesystem endoints
RUN mkdir /var/lib/elevator /etc/elevator
RUN touch /var/log/elevator.log
RUN cp /home/elevator/conf/elevator.conf /etc/elevator

# Start elevator on image run
CMD ["elevator", "-d",  "&"]