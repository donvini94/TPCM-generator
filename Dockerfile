
FROM	ubuntu:20.04
RUN	apt update \
	&& apt upgrade -y \
	&& apt-get update \
	&& apt-get upgrade -y
RUN	apt install -y openjdk-21-jdk openjdk-21-jre
RUN	apt-get install -y \
	--fix-missing \
	python3 \
	python3-pip
RUN	pip3 install pyecore>=0.15.2 textx>=4.1.0
COPY	SaveAs.jar	/SaveAs.jar
COPY	*.py	*.tpcm	*.xtext	tpcm-generator/
COPY	ecores/	tpcm-generator/ecores/
COPY	src/	tpcm-generator/src/
COPY	tests/	tpcm-generator/tests/
RUN	mkdir -p tpcm-generator/output \
	&& chmod 777 tpcm-generator/output
WORKDIR	/tpcm-generator
ENTRYPOINT	["python3","main.py","--models","10000","--convert"]
