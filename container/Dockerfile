FROM ubuntu:xenial
LABEL maintainer="Julien Eyriès <julien@eyries.fr>"
LABEL Description="Docker Container for the Code Challenge"

USER root
WORKDIR /root

# Update Ubuntu Software repository
RUN apt-get update

# Install python 
RUN apt-get install -y python-minimal

# Install usefull packages
RUN apt-get install -y \
 nano \
 curl \
 wget \
 apt-transport-https \
 zip \
 unzip

# Install GCC 5.4.0
RUN apt-get install -y \
 build-essential

# Install Python 2.7.12
RUN apt-get install -y \
 python \
 python-pip 

# Install Python 3.5.2 
RUN apt-get install -y \
 python3 \
 python3-pip 

# Install Python requirements
RUN pip3 install \
 numpy

# Install Java 1.8.0
RUN apt-get install -y \
 openjdk-8-jre-headless \
 openjdk-8-jdk-headless

# Install Node.js 4.2.6
RUN apt-get install -y \
 nodejs

# install Swift 4.0.3
RUN apt-get -q install -y \
    make \
    libc6-dev \
    clang-3.8 \
    curl \
    libedit-dev \
    libpython2.7 \
    libicu-dev \
    libssl-dev \
    libxml2 \
    tzdata \
    git \
    libcurl4-openssl-dev \
    pkg-config \
    && update-alternatives --quiet --install /usr/bin/clang clang /usr/bin/clang-3.8 100 \
    && update-alternatives --quiet --install /usr/bin/clang++ clang++ /usr/bin/clang++-3.8 100 

RUN SWIFT_URL=https://swift.org/builds/swift-4.0.3-release/ubuntu1604/swift-4.0.3-RELEASE/swift-4.0.3-RELEASE-ubuntu16.04.tar.gz \
    && curl -fSsL $SWIFT_URL -o swift.tar.gz \
    && tar -xzf swift.tar.gz --directory / --strip-components=1 \
    && rm -r swift.tar.gz \
    && chmod -R o+r /usr/lib/swift 

# Install Go 1.9.3
RUN GO_URL=https://dl.google.com/go/go1.9.3.linux-amd64.tar.gz \
    && curl -fSsL $GO_URL -o go.tar.gz \
    && tar -xzf go.tar.gz --directory /opt \
    && rm -r go.tar.gz 

# Install Scala 2.11.6
RUN apt-get install -y \
 scala

# Install Kotlin 1.2.21
ENV KOTLIN_VERSION=1.2.21 \
 KOTLIN_HOME=/usr/local/kotlin

RUN wget -k "https://github.com/JetBrains/kotlin/releases/download/v${KOTLIN_VERSION}/kotlin-compiler-${KOTLIN_VERSION}.zip"  && \
 unzip "kotlin-compiler-${KOTLIN_VERSION}.zip" && \
 mkdir -p "${KOTLIN_HOME}" && \
 mv "kotlinc/bin" "kotlinc/lib" "${KOTLIN_HOME}" && \
 rm ${KOTLIN_HOME}/bin/*.bat && \
 chmod +x ${KOTLIN_HOME}/bin/* && \
 ln -s "${KOTLIN_HOME}/bin/"* "/usr/bin/" && \
 rm -rf kotlinc "kotlin-compiler-${KOTLIN_VERSION}.zip"

# Install PHP 7.0.22
RUN apt-get install -y \
 php

# Install Ruby 2.3.1
RUN apt-get install -y \
 ruby

# Already installed : 
# Perl 5.22.1
# Bash 4.3.48

# Add the chimp user
RUN useradd -d /home/chimp -m -s /bin/bash chimp
USER chimp
WORKDIR /home/chimp

# Copy chimp script
COPY chimp.py .



