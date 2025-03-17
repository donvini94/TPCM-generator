FROM ubuntu:20.04

# Update
RUN apt update && apt upgrade -y && apt-get update && apt-get upgrade -y

# Install Java 17
RUN apt install -y openjdk-21-jdk openjdk-21-jre

# Install UI dependencies
RUN apt-get install -y --fix-missing python3 python3-pip

RUN pip3 install pyecore>=0.15.2 textx>=4.1.0

COPY . tpcm-generator/
RUN chmod -R a+rwx tpcm-generator

WORKDIR /tpcm-generator

ENTRYPOINT [ "python3", "main.py", "--models", "10", "--convert" ]
