FROM ubuntu:20.04

# Update
RUN apt update && apt upgrade -y && apt-get update && apt-get upgrade -y

# Install Java 17
RUN apt install -y openjdk-21-jdk openjdk-21-jre

# Install UI dependencies
RUN apt-get install -y --fix-missing python3 python3-pip

RUN pip3 install pyecore>=0.15.2 textx>=4.1.0

# Copy only the files we need with appropriate permissions
COPY --chmod=755 SaveAs.jar /SaveAs.jar
COPY --chmod=755 *.py *.tpcm *.xtext tpcm-generator/
COPY --chmod=755 ecores/ tpcm-generator/ecores/
COPY --chmod=755 src/ tpcm-generator/src/
COPY --chmod=755 tests/ tpcm-generator/tests/
# Create output directory
RUN mkdir -p tpcm-generator/output && chmod 777 tpcm-generator/output

WORKDIR /tpcm-generator

ENTRYPOINT [ "python3", "main.py", "--models", "10", "--convert" ]
