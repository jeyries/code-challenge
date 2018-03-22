

sudo apt-get update
sudo apt-get install -y python

sudo apt-get install -y nano curl wget

# install C

sudo apt-get install -y build-essential

# install Node.js

curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs

# install Java

sudo apt-get install -y openjdk-7-jdk

# install Swift

sudo apt-get install -y clang libicu-dev

wget https://swift.org/builds/swift-4.0.3-release/ubuntu1404/swift-4.0.3-RELEASE/swift-4.0.3-RELEASE-ubuntu14.04.tar.gz
tar xzf swift-4.0.3-RELEASE-ubuntu14.04.tar.gz
sudo mv swift-4.0.3-RELEASE-ubuntu14.04 /opt/swift
export PATH="${PATH}":/opt/swift/usr/bin

# run : swiftc hello.swift


